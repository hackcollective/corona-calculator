import datetime
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple

import pandas as pd

GITHUB_REPO = "https://github.com/CSSEGISandData/COVID-19.git"
REPO_DIRPATH = "COVID-19"
DAILY_REPORTS_DIRPATH = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports"

OUTPUT_PATH = "data/latest_disease_data.csv"
LOG_PATH = "data/latest_fetch.log"
DATESTRING_FORMAT = "%Y%m%d%H%M"


def execute_shell_command(command: List[str]):
    return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode("utf-8")


def get_latest_filepath(csv_filepaths: List[str]) -> Tuple[str, int, int, int]:
    """
    Returns the file info for the latest CSV file report.
    Example filename: 03-13-2020.csv
    Returns a tuple of (fpath, year, month, day) for the latest report.
    """
    file_infos = []
    for fpath in csv_filepaths:
        stem_split = fpath.stem.split("-")
        month = int(stem_split[0])
        day = int(stem_split[1])
        year = int(stem_split[2])
        file_infos.append((fpath, year, month, day))
    # Sort the file info list
    file_infos = sorted(file_infos, key=lambda t: (t[1], t[2], t[3]))
    return file_infos[-1]


if __name__ == "__main__":
    # Clone the JHU COVID GitHub repo (takes about a minute)
    cmd = ["git", "clone", GITHUB_REPO]
    execute_shell_command(cmd)

    # Go to daily reports directory and fetch all CSV files
    csv_filepaths = Path(DAILY_REPORTS_DIRPATH).glob("*.csv")
    # Get the filepath for latest report
    latest_filepath, year, month, day = get_latest_filepath(csv_filepaths)
    print(year, month, day, latest_filepath)

    # Read the report into a pandas df
    df = pd.read_csv(latest_filepath)
    # Aggregate the country stats
    country_stats_df = df.groupby("Country/Region").agg(
        {"Confirmed": "sum", "Deaths": "sum", "Recovered": "sum"}
    )

    # Drop countries for which we have no demographic data
    country_stats_df.drop(
        [
            "Brunei",
            "Cruise Ship",
            "French Guiana",
            "Guadeloupe",
            "Holy See",
            "Martinique",
            "North Macedonia",
            "Reunion",
        ],
        inplace=True,
    )

    # Write out the country stats to output path
    # The CSV file contains 4 columns:
    ## 1) Country/Region, 2) Confirmed, 3)	Deaths, 4) Recovered
    country_stats_df.to_csv(OUTPUT_PATH, index=True)
    with open(LOG_PATH, "w") as f:
        f.write(datetime.datetime.now().strftime(DATESTRING_FORMAT))

    # # Remove GitHub repo directory
    shutil.rmtree(REPO_DIRPATH)

import datetime
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from s3_utils import upload_file

GITHUB_REPO = "https://github.com/CSSEGISandData/COVID-19.git"
REPO_DIRPATH = "COVID-19"
DAILY_REPORTS_DIRPATH = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports"

DATESTRING_FORMAT = "%Y%m%d%H%M"


def execute_shell_command(command: List[str]):
    return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode("utf-8")


def get_latest_filepath(csv_filepaths: List[Path]) -> Tuple[Path, int, int, int]:
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
    csv_filepaths = list(Path(DAILY_REPORTS_DIRPATH).glob("*.csv"))
    # Get the filepath for latest report
    latest_filepath, year, month, day = get_latest_filepath(csv_filepaths)

    # Read the report into a pandas df
    df = pd.read_csv(latest_filepath)
    # Aggregate the country stats
    country_stats_df = df.groupby("Country/Region").agg(
        {"Confirmed": "sum", "Deaths": "sum", "Recovered": "sum"}
    )

    data = country_stats_df.to_csv().encode()

    success = upload_file(data, "latest_disease_data.csv")

    if success:
        print(f"Results pushed to S3.")
    else:
        print("Push to S3 failed")

    # # Remove GitHub repo directory
    shutil.rmtree(REPO_DIRPATH)
    print("Clean up done.")

import datetime
import pickle
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple

import pandas as pd

from s3_utils import upload_file

GITHUB_REPO = "https://github.com/CSSEGISandData/COVID-19.git"
REPO_DIRPATH = "COVID-19"
DAILY_REPORTS_DIRPATH = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports"


def execute_shell_command(command: List[str]):
    return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode("utf-8")


def get_full_and_latest_table(csv_filepaths: List[Path]):
    """
    Returns two dataframes - full table (all dates), table of the latest date
    """
    total_df = None

    for fpath in csv_filepaths:
        stem_split = fpath.stem.split("-")
        month = int(stem_split[0])
        day = int(stem_split[1])
        year = int(stem_split[2])
        
        curr_df = pd.read_csv(fpath)
        country_stats_df = curr_df.groupby("Country/Region").agg(
            {"Confirmed": "sum", "Deaths": "sum", "Recovered": "sum"}
        )
        
        country_stats_df["Country/Region"] = country_stats_df.index
        country_stats_df["Date"] = datetime.datetime(year, month, day)
        
        if total_df is None:
            total_df = country_stats_df
        else:
            total_df = total_df.append(country_stats_df, ignore_index=True)

    ## Clean data
    # replacing Mainland china with just China
    total_df['Country/Region'] = total_df['Country/Region'].replace('Mainland China', 'China')

    # sort by date, then country name
    total_df = total_df.sort_values(['Date', 'Country/Region'])
    total_df = total_df.reset_index(drop=True)

    ## Latest date table
    latest_date_df = total_df[total_df['Date'] == max(total_df['Date'])].reset_index(drop=True)

    return total_df, latest_date_df


if __name__ == "__main__":
    # Clone the JHU COVID GitHub repo (takes about a minute)
    cmd = ["git", "clone", GITHUB_REPO]
    execute_shell_command(cmd)

    # Go to daily reports directory and fetch all CSV files
    csv_filepaths = list(Path(DAILY_REPORTS_DIRPATH).glob("*.csv"))
    # Get the full and latest table
    full_df, latest_df = get_full_and_latest_table(csv_filepaths)

    save_dict_pickle = {
        "full_table": full_df,
        "latest_table": latest_df
    }

    pickle_byte_obj = pickle.dumps(save_dict_pickle)

    success = upload_file(pickle_byte_obj, "full_and_latest_disease_data_dict_pkl")

    if success:
        print(f"Results pushed to S3.")
    else:
        print("Push to S3 failed")

    # # Remove GitHub repo directory
    shutil.rmtree(REPO_DIRPATH)
    print("Clean up done.")

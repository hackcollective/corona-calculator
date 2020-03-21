import datetime
import os
import pickle
import shutil
import subprocess
from io import BytesIO
from pathlib import Path
from typing import List

import boto3
import pandas as pd
from botocore.exceptions import ClientError

from data.preprocessing import preprocess_bed_data

_S3_ACCESS_KEY = os.environ.get("AWSAccessKeyId", "").replace("\r", "")
_S3_SECRET_KEY = os.environ.get("AWSSecretKey", "").replace("\r", "")
_S3_BUCKET_NAME = "coronavirus-calculator-data"
_S3_DISEASE_DATA_OBJ_NAME = "full_and_latest_disease_data_dict_v2"


DISEASE_DATA_GITHUB_REPO = "https://github.com/CSSEGISandData/COVID-19.git"
REPO_DIRPATH = "COVID-19"
DAILY_REPORTS_DIRPATH = "COVID-19/csse_covid_19_data/csse_covid_19_daily_reports"

_DATA_DIR = Path(__file__).parent
_DEMOGRAPHICS_DATA_PATH = _DATA_DIR / "demographics.csv"
_BED_DATA_PATH = _DATA_DIR / "world_bank_bed_data.csv"
_AGE_DATA_PATH = _DATA_DIR / "age_data.csv"
DEMOGRAPHIC_DATA = pd.read_csv(_DEMOGRAPHICS_DATA_PATH, index_col="Country/Region")
BED_DATA = preprocess_bed_data(_BED_DATA_PATH)
AGE_DATA = pd.read_csv(_AGE_DATA_PATH, index_col="Age Group")


def execute_shell_command(command: List[str]):
    return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode("utf-8")


def get_full_and_latest_dataframes_from_csv(csv_filepaths: List[Path]):
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

        country_stats_df.reset_index(inplace=True)
        country_stats_df["Date"] = datetime.datetime(year=year, month=month, day=day)

        if total_df is None:
            total_df = country_stats_df
        else:
            total_df = total_df.append(country_stats_df, ignore_index=True)

    ## Clean data
    # replacing Mainland china with just China
    total_df["Country/Region"] = total_df["Country/Region"].replace(
        "Mainland China", "China"
    )
    total_df["Country/Region"] = total_df["Country/Region"].replace(
        "US", "United States"
    )

    # sort by date, then country name
    total_df = total_df.sort_values(["Date", "Country/Region"])

    ## Latest date table
    latest_date_df = total_df[total_df["Date"] == max(total_df["Date"])]

    # Set country as index
    latest_date_df = latest_date_df.set_index("Country/Region")
    total_df = total_df.set_index("Country/Region")

    return total_df, latest_date_df


def download_data():
    """
     Clone the JHU COVID GitHub repo (takes about a minute) and return paths to CSVs.
    """
    cmd = ["git", "clone", DISEASE_DATA_GITHUB_REPO]
    execute_shell_command(cmd)

    # Go to daily reports directory and fetch all CSV files
    csv_filepaths = list(Path(DAILY_REPORTS_DIRPATH).glob("*.csv"))

    # Get the full and latest table
    full_df, latest_df = get_full_and_latest_dataframes_from_csv(csv_filepaths)
    data_object = {"full_table": full_df, "latest_table": latest_df}
    # # Remove GitHub repo directory
    shutil.rmtree(REPO_DIRPATH)
    print("Cleaned up.")

    return data_object


def _configure_s3_client():
    # Upload the file
    s3_client = boto3.client(
        "s3", aws_access_key_id=_S3_ACCESS_KEY, aws_secret_access_key=_S3_SECRET_KEY
    )
    return s3_client


def upload_data_to_s3(data: bytes, object_name: str = _S3_DISEASE_DATA_OBJ_NAME):
    """
    Upload a file to an S3 bucket
    :param data: Bytes to upload.
    :param object_name: S3 object name.
    :return: True if file was uploaded, else False
    """
    buf = BytesIO(data)
    s3_client = _configure_s3_client()
    try:
        s3_client.put_object(Body=buf, Bucket=_S3_BUCKET_NAME, Key=object_name)
    except ClientError as e:
        print(e)
        return False
    return True


def download_data_from_s3(object_name: str = _S3_DISEASE_DATA_OBJ_NAME):
    """
    Download a file from S3 bucket.
    :param object_name: Name of object to download.
    :return: Object bytes and date last modified.
    """
    s3_client = _configure_s3_client()
    try:
        download = s3_client.get_object(Key=object_name, Bucket=_S3_BUCKET_NAME)
    except ClientError:
        return None
    content = download["Body"].read()

    # e.g. Sunday 30 November 2014
    last_modified = download["LastModified"].strftime("%A %d %B %Y, %H:%M %Z")
    return content, last_modified


def build_country_data(demographic_data=DEMOGRAPHIC_DATA, bed_data=BED_DATA):
    # Try to download from S3, else download from JHU
    objects = download_data_from_s3()
    if objects is None:
        data_dict = download_data()
        last_modified = datetime.datetime.now()
    else:
        data_dict_pkl_bytes, last_modified = objects
        data_dict = pickle.loads(data_dict_pkl_bytes)

    full_disease_data, latest_disease_data = (
        data_dict["full_table"],
        data_dict["latest_table"],
    )

    # Rename name "US" to "United States" in demographics data to match bed data
    demographic_data = demographic_data.rename(index={"US": "United States"})
    demographic_data = demographic_data.merge(bed_data, on="Country/Region")
    demographic_data["Num Hospital Beds"] = (
        demographic_data["Latest Bed Estimate"] * demographic_data["Population"]
    )

    country_data = latest_disease_data.merge(demographic_data, on="Country/Region")
    country_data = country_data.loc[
        :, ["Confirmed", "Deaths", "Recovered", "Population", "Num Hospital Beds"]
    ]

    # Check that all of the countries in our selectable dropdown are also present in the full data
    assert set(latest_disease_data.index.unique()).issubset(
        set(full_disease_data.index.unique())
    )

    return country_data.to_dict(orient="index"), last_modified, full_disease_data

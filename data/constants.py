"""
Range estimates for various epidemiology constants.
Data gathered from https://github.com/midas-network/COVID-19/tree/master/parameter_estimates/2019_novel_coronavirus
and https://www.mdpi.com/2077-0383/9/2/462/htm
Parameter bounds were subjectively chosen from positively peer-reviewed estimates.
"""

import datetime
from io import StringIO
from pathlib import Path

import pandas as pd

from data.process_bed_data import preprocess_bed_data
from s3_utils import download_file

_DEMOGRAPHICS_DATA_PATH = Path(__file__).parent / "demographics.csv"
_BED_DATA_PATH = Path(__file__).parent / "world_bank_bed_data.csv"

DEMOGRAPHIC_DATA = pd.read_csv(_DEMOGRAPHICS_DATA_PATH, index_col="Country/Region")
BED_DATA = preprocess_bed_data(_BED_DATA_PATH)


def build_country_data(demographic_data=DEMOGRAPHIC_DATA, bed_data=BED_DATA):
    disease_data_bytes = download_file("latest_disease_data.csv")
    disease_data = pd.read_csv(
        StringIO(disease_data_bytes.decode()), index_col="Country/Region"
    )
    print(disease_data.index)
    # Rename name "US" to "United States" in disease and demographics data to match bed data
    disease_data = disease_data.rename(index={"US": "United States"})
    demographic_data = demographic_data.rename(index={"US": "United States"})

    country_data = disease_data.merge(demographic_data, on="Country/Region")

    # Beds are per 1000 people so we need to calculate absolute

    bed_data = bed_data.merge(demographic_data, on="Country/Region")

    bed_data["Num Hospital Beds"] = (
        bed_data["Latest Bed Estimate"] * bed_data["Population"] / 1000
    )

    country_data = country_data.merge(
        bed_data[["Num Hospital Beds"]], on="Country/Region"
    )
    return country_data


COUNTRY_DATA = build_country_data(demographic_data=DEMOGRAPHIC_DATA, bed_data=BED_DATA)


class Countries:
    country_data = COUNTRY_DATA.to_dict(orient="index")
    countries = list(country_data.keys())
    default_selection = countries.index("United States")


"""
SIR model constants
"""


class RemovalRate:
    min = 1 / 7
    default = 1 / 10  # Recovery period around 10 days
    max = 1 / 14


class TransmissionRatePerContact:
    # Probability of a contact between carrier and susceptible leading to infection
    min = 0.01
    default = (
        0.018
    )  # Found using binomial distribution in Wuhan scenario: 14 contacts per day, 10 infectious days, 2.5 average people infected.
    max = 0.022


class AverageDailyContacts:
    min = 0
    max = 100
    default = 20


"""
Health care constants
"""


class AscertainmentRate:
    # Proportion of true cases diagnosed
    min = 0.05
    max = 0.25
    default = 0.1


class MortalityRate:
    min = 0.005
    max = 0.05
    default = 0.01


class HospitalizationRate:
    # Cases requiring hospitalization
    min = 0.1
    max = 0.2
    default = 0.15


class VentilationRate:
    # Cases requiring ICU care
    # From chart 18 https://medium.com/@tomaspueyo/coronavirus-act-today-or-people-will-die-f4d3d9cd99ca
    min = 0.01
    max = 0.02
    default = 0.015


if __name__ == "__main__":
    df = join_source_data()

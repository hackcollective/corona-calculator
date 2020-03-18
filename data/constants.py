"""
Range estimates for various epidemiology constants. Currently only default values are used.
For sources, please visit https://www.notion.so/Modelling-d650e1351bf34ceeb97c82bd24ae04cc
"""

import datetime
from io import StringIO
from pathlib import Path

import pandas as pd

from data.preprocessing import preprocess_bed_data
from s3_utils import download_file

_DATA_DIR = Path(__file__).parent
_DEMOGRAPHICS_DATA_PATH = _DATA_DIR / "demographics.csv"
_BED_DATA_PATH = _DATA_DIR / "world_bank_bed_data.csv"
_AGE_DATA_PATH = _DATA_DIR / "age_data.csv"

DEMOGRAPHIC_DATA = pd.read_csv(_DEMOGRAPHICS_DATA_PATH, index_col="Country/Region")
BED_DATA = preprocess_bed_data(_BED_DATA_PATH)
AGE_DATA = pd.read_csv(_AGE_DATA_PATH, index_col="Age Group")


def build_country_data(demographic_data=DEMOGRAPHIC_DATA, bed_data=BED_DATA):
    disease_data_bytes, last_modified = download_file("latest_disease_data.csv")
    disease_data = pd.read_csv(
        StringIO(disease_data_bytes.decode()), index_col="Country/Region"
    )
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
    return country_data.to_dict(orient="index"), last_modified


class Countries:
    def __init__(self, timestamp):
        self.country_data, self.last_modified = build_country_data()
        self.countries = list(self.country_data.keys())
        self.default_selection = self.countries.index("Canada")
        self.timestamp = timestamp

    @property
    def stale(self):
        delta = datetime.datetime.utcnow() - self.timestamp
        return delta > datetime.timedelta(hours=1)


class AgeData:
    data = AGE_DATA


"""
SIR model constants
"""


class RecoveryRate:
    default = 1 / 10  # Recovery period around 10 days


class MortalityRate:
    # Take weighted average of death rate across age groups. This assumes each age group is equally likely to
    # get infected, which may not be exact, but is an assumption we need to make for further analysis,
    # notably segmenting deaths by age group.
    default = (AgeData.data.Proportion * AgeData.data.Mortality).sum()


class CriticalDeathRate:
    # Death rate of critically ill patients who don't have access to a hospital bed.
    min = 0.01
    max = 1.0
    default = 0.5


class TransmissionRatePerContact:
    # Probability of a contact between carrier and susceptible leading to infection.
    # Found using binomial distribution in Wuhan scenario: 14 contacts per day, 10 infectious days, 2.5 average people infected.
    default = 0.018


class AverageDailyContacts:
    min = 0
    max = 100
    default = 20


"""
Health care constants
"""


class AscertainmentRate:
    # Proportion of true cases diagnosed
    default = 0.1


class HospitalizationRate:
    # Cases requiring hospitalization. We multiply by the ascertainment rate because our source got their estimate
    # from the reported cases, whereas we will be using it with total cases.
    default = 0.19 * AscertainmentRate.default

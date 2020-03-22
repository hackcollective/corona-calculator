"""
Range estimates for various epidemiology constants. Currently only default values are used.
For sources, please visit https://www.notion.so/Modelling-d650e1351bf34ceeb97c82bd24ae04cc
"""

from enum import Enum
import datetime

from data.utils import AGE_DATA, build_country_data


class Countries:
    def __init__(self, timestamp):
        self.country_data, self.last_modified, self.historical_country_data = (
            build_country_data()
        )
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
    # This is the max reported from Wuhan:
    # https://wwwnc.cdc.gov/eid/article/26/6/20-0233_article
    default = 0.122


class TransmissionRatePerContact:
    # Probability of a contact between carrier and susceptible leading to infection.
    # Found using binomial distribution in Wuhan scenario: 14 contacts per day, 10 infectious days, 2.5 average people infected.
    default = 0.018


class AverageDailyContacts:
    min = 0
    max = 50
    default = 15


"""
Health care constants
"""


class ReportingRate:
    # Proportion of true cases diagnosed
    default = 0.14

class AsymptomaticRate:
    # Proportion of true cases showing no symptoms
    # The number comes from a study led on passengers of the Diamond Princess Cruise, in Japan
    # We assume this figure stands true for the rest of the world
    # https://www.eurosurveillance.org/content/10.2807/1560-7917.ES.2020.25.10.2000180
    default = 17.9

class HospitalizationRate:
    # Cases requiring hospitalization. We multiply by the ascertainment rate because our source got their estimate
    # from the reported cases, whereas we will be using it with total cases.
    default = 0.19 * ReportingRate.default

class InfectionState(Enum):
    ASYMPTOMATIC_UNDIAGNOSED = "asymptomatic_undiagnosed"
    ASYMPTOMATIC_DIAGNOSED = "asymptomatic_diagnosed"
    SYMPTOMATIC_UNDIAGNOSED = "symptomatic_undiagnosed"
    SYMPTOMATIC_DIAGNOSED = "symptomatic_diagnosed"

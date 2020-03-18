from pathlib import Path

import numpy as np
import pandas as pd

_BED_DATA_PATH = Path(__file__).parent / "world_bank_bed_data.csv"
_MORTALITY_DATA_PATH = Path(__file__).parent / "mortality_and_hospitalization_by_age.csv"
_GLOBAL_AGE_DISTRIBUTION_DATA_PATH = Path(__file__).parent / '/PopulationAgeSex-20200317101235.xlsx'

def _get_latest_bed_estimate(row):
    non_empty_estimates = [float(x) for x in row.values if float(x) > 0]
    try:
        return non_empty_estimates[-1]
    except IndexError:
        return np.nan


def preprocess_bed_data(path=_BED_DATA_PATH):
    df = pd.read_csv(path, header=2)
    df.rename({"Country Name": "Country/Region"}, axis=1, inplace=True)
    df.drop(["Country Code", "Indicator Name", "Indicator Code"], axis=1, inplace=True)
    df.set_index("Country/Region", inplace=True)
    df["Latest Bed Estimate"] = df.apply(_get_latest_bed_estimate, axis=1)

    # Rename countries to match demographics and disease data
    df = df.rename(
        index={
            "Iran, Islamic Rep.": "Iran",
            "Korea, Rep.": "Korea, South",
            "Russian Federation": "Russia",
            "Egypt, Arab Rep.": "Egypt",
            "Slovak Republic": "Slovakia",
            "Congo, Dem. Rep.": "Congo (Kinshasa)",
            # "Brunei Darussalam": "Brunei",
        }
    )

    return df


def process_mortality_by_demographics(path=_MORTALITY_DATA_PATH):
    df = pd.read_csv(path, header=0, skipfooter=3)
    df.set_index('Age group', inplace=True)

    # Data is in percentages, convert them to fraction
    df = df.apply(lambda x: x/100)

    # Critical care is as a % of hospitalized cases
    df['Critical Care'] *= df['Hospitalization']

    # Subtract those cases
    df['Hospitalization'] -= df['Critical Care']

    # Infection fatality is not a % of hospitalized cases, so we should subtract it from critical care, under the
    # assumption that everybody who dies was in critical care first
    df['Critical Care'] -= df['Infection Fatality']

    # Add a new column which is infected but not hospitalized, dead, or in critical care
    df['Mild Infection'] = 1 - (df['Hospitalization'] + df['Critical Care'] + df['Infection Fatality'])

    # Convert back to percentages
    df *= 100

    # Unset for melt
    df.reset_index(inplace=True)

    # Go from wide to long for plotly express
    df = pd.melt(df, id_vars=['Age group'],
                 value_vars=['Hospitalization',
                             'Critical Care',
                             'Infection Fatality',
                             'Mild Infection'],
                 var_name='Outcome',
                 value_name='Percentage')

    return df


def global_demographics_by_age(path=_GLOBAL_AGE_DISTRIBUTION_DATA_PATH):
    """
    Demographics by age for the whole world, from https://population.un.org/wpp/DataQuery/.
    We could use the tool to obtain country-specific demographic information but that would involve
    lots of data normalization and adding a large data file, so let's approximate with global
    demographics for now.
    """
    # TODO read in the data
    # TODO normalize to the same ranges as our mortality data
    pass


def apply_demographic_distribution_to_mortality_data(df_mortality, df_demographics):
    # TODO combine the two to obtain absolute mortality and hospitalization numbers
    pass

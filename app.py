import datetime

import streamlit as st

import graphing
import models
from data import constants
from fetch_live_data import DATESTRING_FORMAT, LOG_PATH

# estimates from https://github.com/midas-network/COVID-19/tree/master/parameter_estimates/2019_novel_coronavirus


class Sidebar:
    country = st.sidebar.selectbox(
        "What country do you live in?", options=constants.Countries.countries
    )

    if country:
        country_data = constants.Countries.country_data[country]
        with open(LOG_PATH) as f:
            date_last_fetched = f.read()
            date_last_fetched = datetime.datetime.strptime(
                date_last_fetched, DATESTRING_FORMAT
            )
        st.sidebar.markdown(
            f'As of **{date_last_fetched}**, there are **{country_data["Confirmed"]}** confirmed cases in {country}.'
        )
        st.sidebar.markdown(
            f'The population of {country} is **{int(country_data["Population"]):,}**'
        )

    contact_rate = st.sidebar.slider(
        label="Number of people infected people come into contact with daily",
        min_value=constants.AverageDailyContacts.min,
        max_value=constants.AverageDailyContacts.max,
        value=constants.AverageDailyContacts.default,
    )

    num_days_for_prediction = st.sidebar.slider(
        label="Number of days for prediction", min_value=50, max_value=365, value=100
    )

    number_of_beds = st.sidebar.slider(
        label="Number of hospital beds available",
        min_value=100,
        max_value=1_000_000,
        value=100_000,
    )
    number_of_ventilators = st.sidebar.slider(
        label="Number of ventilators available",
        min_value=100,
        max_value=1_000_000,
        value=100_000,
    )


def run_app():
    st.title("Corona Calculator")
    st.write(
        "The critical factor for controlling spread is how many others infected people interact with each day. "
        "This has a dramatic effect upon the dynamics of the disease."
    )
    Sidebar()
    country = Sidebar.country
    number_cases_confirmed = constants.Countries.country_data[country]["Confirmed"]
    population = constants.Countries.country_data[country]["Population"]

    sir_model = models.SIRModel(
        constants.TransmissionRatePerContact.default,
        Sidebar.contact_rate,
        constants.RemovalRate.default,
    )
    true_cases_estimator = models.TrueInfectedCasesModel(
        constants.AscertainmentRate.default
    )
    death_toll_model = models.DeathTollModel(constants.MortalityRate.default)
    hospitalization_model = models.HospitalizationModel(
        constants.HospitalizationRate.default, constants.VentilationRate.default
    )

    df = models.get_predictions(
        true_cases_estimator,
        sir_model,
        death_toll_model,
        hospitalization_model,
        number_cases_confirmed,
        population,
        Sidebar.num_days_for_prediction,
    )

    # Split df into hospital and non-hospital stats
    df_base = df[~df.Status.isin(["Hospitalized", "Ventilated"])]
    base_graph = graphing.infection_graph(df_base)
    st.write(base_graph)

    hospital_graph = graphing.hospitalization_graph(
        df[df.Status.isin(["Infected", "Hospitalized", "Ventilated"])],
        Sidebar.number_of_beds,
        Sidebar.number_of_ventilators,
    )

    st.title("How will this affect my healthcare system?")
    st.write(
        "The important variable for hospitals is the peak number of people who require hospitalization"
        " and ventilation at any one time"
    )
    st.write(hospital_graph)
    peak_occupancy = df.loc[df.Status == "Hospitalized"]["Forecast"].max()
    percent_beds_at_peak = min(100 * Sidebar.number_of_beds / peak_occupancy, 100)

    peak_ventilation = df.loc[df.Status == "Ventilated"]["Forecast"].max()
    percent_ventilators_at_peak = min(
        100 * Sidebar.number_of_ventilators / peak_ventilation, 100
    )

    st.markdown(
        f"At peak, ** {percent_beds_at_peak:.1f} % ** of people who need a bed in hospital have one"
    )
    st.markdown(
        f"At peak, ** {percent_ventilators_at_peak:.1f} % ** of people who need a ventilator have one"
    )


if __name__ == "__main__":
    run_app()

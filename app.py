from dataclasses import dataclass

import streamlit as st

import graphing
import models
from data import constants

# estimates from https://github.com/midas-network/COVID-19/tree/master/parameter_estimates/2019_novel_coronavirus


@dataclass
class sidebar:
    area_population = st.sidebar.number_input(
        "Population in your area (million)", min_value=1, step=1
    )
    number_cases_confirmed = st.sidebar.number_input(
        "Confirmed cases in your area", min_value=1, step=10
    )
    transmission_probability = st.sidebar.slider(
        label="Probability of a sick person infecting a susceptible person upon contact",
        min_value=constants.TransmissionRatePerContact.min,
        max_value=constants.TransmissionRatePerContact.max,
        value=constants.TransmissionRatePerContact.default,
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

    # Don't know if we want to present doubling time here or R or something else
    # estimated_doubling_time = st.sidebar.slider(label='Estimated time (days) for number of infected people to double', min_value=1, max_value=10, value=5)
    # symptom_delay =  st.sidebar.slider(label='Time between infection and symptoms being displayed', min_value=1, max_value=10, value=5)
    # diagnostic_delay = st.sidebar.slider(label='Time between being tested and receiving a diagnosis', min_value=1, max_value=10, value=3)
    # https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30195-X/fulltext
    # mortality_rate = st.sidebar.slider(label='% mortality rate', min_value=0., step=.1, max_value=50., value=5.)
    # hospitalization_rate = st.sidebar.slider(label='% of cases requiring hospitalization', min_value=0., max_value=100., step=.5, value=5.)
    # ventilator_rate = st.sidebar.slider(label='% of cases requiring a ventilator',min_value=0., max_value=100., step=.5, value=1.)
    # num_beds = st.sidebar.slider(label='Number of hospital beds available', min_value=100, max_value=1000000, value=100000)
    # stay_in_hospital = st.sidebar.slider(label='How many days people stay in hospital', min_value=3, max_value=20, value=12)


def run_app():
    st.title("Corona Calculator")
    sidebar()
    sir_model = models.SIRModel(
        sidebar.transmission_probability,
        sidebar.contact_rate,
        constants.RemovalRate.default,
    )
    true_cases_estimator = models.TrueInfectedCasesModel(
        constants.AscertainmentRate.default
    )
    death_toll_model = models.DeathTollModel(constants.MortalityRate.default)
    df = models.get_predictions(
        true_cases_estimator,
        sir_model,
        death_toll_model,
        sidebar.number_cases_confirmed,
        sidebar.area_population * 1000000,
        sidebar.num_days_for_prediction,
    )

    figure = graphing.infection_graph(df)
    st.write(figure)


if __name__ == "__main__":
    run_app()

import datetime
from dataclasses import dataclass

import streamlit as st

import graphing
import models
from data import constants

# estimates from https://github.com/midas-network/COVID-19/tree/master/parameter_estimates/2019_novel_coronavirus

# TODO make this accurate
data_last_fetched = datetime.datetime.today().date()


class Sidebar:
    country = st.sidebar.selectbox(
        "What country do you live in?", options=constants.Countries.countries
    )

    if country:
        country_data = constants.Countries.country_data[country]
        st.sidebar.markdown(
            f'As of **{data_last_fetched}**, there are **{country_data["Confirmed"]}** confirmed cases in {country} and '
            f'the population is **{int(country_data["Population"]):,}**'
        )

    transmission_probability = constants.TransmissionRatePerContact.default

    contact_rate = st.sidebar.slider(
        label="Number of people infected people come into contact with daily",
        min_value=constants.AverageDailyContacts.min,
        max_value=constants.AverageDailyContacts.max,
        value=constants.AverageDailyContacts.default,
    )

    horizon = {'3  months': 90,
               '6 months': 180,
               '12  months': 365}
    _num_days_for_prediction = st.sidebar.radio(label="What period of time would you like to predict for?",
                                                options=list(horizon.keys()),
                                                index=0)

    num_days_for_prediction = horizon[_num_days_for_prediction]

    #
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

    Sidebar()
    country = Sidebar.country
    number_cases_confirmed = constants.Countries.country_data[country]["Confirmed"]
    population = constants.Countries.country_data[country]["Population"]
    num_hospital_beds = constants.Countries.country_data[country]["Num Hospital Beds"]

    # We don't have this for now
    # num_ventilators = constants.Countries.country_data[country]["Num Ventilators"]

    sir_model = models.SIRModel(
        Sidebar.transmission_probability,
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

    st.write("The number of reported cases radically underestimates the true cases. The extent depends upon"
             "your country's testing strategy. Using numbers from Japan, we estimate the true number of cases "
             "is:")

    fig = graphing.plot_true_versus_confirmed(number_cases_confirmed, true_cases_estimator.predict(number_cases_confirmed))
    st.write(fig)
    st.write(
        "The critical factor for controlling spread is how many others infected people interact with each day. "
        "This has a dramatic effect upon the dynamics of the disease."
    )
    df_base = df[~df.Status.isin(["Need Hospitalization", "Need Ventilation"])]
    base_graph = graphing.infection_graph(df_base)
    st.write(base_graph)

    hospital_graph = graphing.hospitalization_graph(
        df[df.Status.isin(["Infected", "Need Hospitalization"])],
        num_hospital_beds,
        None
    )

    st.title("How will this affect my healthcare system?")
    st.write(
        "The important variable for hospitals is the peak number of people who require hospitalization"
        " and ventilation at any one time."
    )

    # Do some rounding to avoid beds sounding too precise!
    st.write(f'Your country has around **{round(num_hospital_beds / 100) * 100}** beds. Bear in mind that most of these '
             'are probably already in use for people sick for other reasons.')

    st.write(hospital_graph)
    peak_occupancy = df.loc[df.Status == "Need Hospitalization"]["Forecast"].max()
    percent_beds_at_peak = min(100 * num_hospital_beds / peak_occupancy, 100)

    # peak_ventilation = df.loc[df.Status == "Ventilated"]["Forecast"].max()
    # percent_ventilators_at_peak = min(
    #     100 * Sidebar.number_of_ventilators / peak_ventilation, 100
    # )

    st.markdown(
        f"At peak, **{peak_occupancy:,}** people will need hospital beds. ** {percent_beds_at_peak:.1f} % ** of people "
        f"who need a bed in hospital will have access to one given current resources."
    )
    # st.markdown(
    #     f"At peak, ** {percent_ventilators_at_peak:.1f} % ** of people who need a ventilator have one"
    # )


if __name__ == "__main__":
    run_app()

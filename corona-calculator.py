import datetime

import streamlit as st

import graphing
import models
from data import constants
from interface.elements import reported_vs_true_cases
from utils import COLOR_MAP, generate_html

# estimates from https://github.com/midas-network/COVID-19/tree/master/parameter_estimates/2019_novel_coronavirus


class Sidebar:
    def __init__(self, countries):
        country = st.sidebar.selectbox(
            "What country do you live in?",
            options=countries.countries,
            index=countries.default_selection,
        )
        self.country = country

        transmission_probability = constants.TransmissionRatePerContact.default
        country_data = countries.country_data[country]
        date_last_fetched = countries.last_modified

        st.sidebar.markdown(
            body=generate_html(
                text=f"Latest statistics from ", line_height=0, font_family="Arial"
            ),
            unsafe_allow_html=True,
        )

        st.sidebar.markdown(
            body=generate_html(
                text=f"{date_last_fetched}",
                bold=True,
                color=COLOR_MAP["pink"],
                line_height=0,
            ),
            unsafe_allow_html=True,
        )

        st.sidebar.markdown(
            body=generate_html(
                text=f'Population: {int(country_data["Population"]):,}<br>Infected: {country_data["Confirmed"]}<br>'
                f'Recovered: {country_data["Recovered"]}<br>Dead: {country_data["Deaths"]}',
                line_height=0,
                font_family="Arial",
                font_size="0.9rem",
                tag="p",
            ),
            unsafe_allow_html=True,
        )
        # Horizontal divider line
        st.sidebar.markdown("-------")

        st.sidebar.markdown(
            f"We're using an estimated transmission probability of {transmission_probability * 100:.1f}%"
        )

        self.contact_rate = st.sidebar.slider(
            label="Number of people infected people come into contact with daily",
            min_value=constants.AverageDailyContacts.min,
            max_value=constants.AverageDailyContacts.max,
            value=constants.AverageDailyContacts.default,
        )

        horizon = {
            "3  months": 90,
            "6 months": 180,
            "12  months": 365,
            "24 months": 730,
        }
        _num_days_for_prediction = st.sidebar.radio(
            label="What period of time would you like to predict for?",
            options=list(horizon.keys()),
            index=1,
        )

        self.num_days_for_prediction = horizon[_num_days_for_prediction]


@st.cache
def _fetch_country_data():
    timestamp = datetime.datetime.utcnow()
    return constants.Countries(timestamp=timestamp)


def run_app():
    # Get cached country data
    countries = _fetch_country_data()

    if countries.stale:
        st.caching.clear_cache()
        countries = _fetch_country_data()

    st.markdown(
        body=generate_html(text=f"Corona Calculator", bold=True, tag="h2"),
        unsafe_allow_html=True,
    )
    st.markdown(
        body=generate_html(
            text="The goal of this data viz is to help you visualize what is the impact "
            "of having infected people entering in contact with other people<hr>",
            tag="h4",
        ),
        unsafe_allow_html=True,
    )

    sidebar = Sidebar(countries)
    country = sidebar.country
    country_data = countries.country_data[country]
    number_cases_confirmed = country_data["Confirmed"]
    population = country_data["Population"]
    num_hospital_beds = country_data["Num Hospital Beds"]

    # We don't have this for now
    # num_ventilators = constants.Countries.country_data[country]["Num Ventilators"]

    sir_model = models.SIRModel(
        constants.TransmissionRatePerContact.default,
        sidebar.contact_rate,
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
        sidebar.num_days_for_prediction,
    )

    reported_vs_true_cases(number_cases_confirmed, true_cases_estimator.predict(number_cases_confirmed))

    st.write(
        "The number of reported cases radically underestimates the true cases, because people do not show symptoms for "
        "several days, not everybody gets tested, and the tests take a few days to  return results. "
        "The extent depends upon your country's testing strategy."
        " We estimated the above using numbers from Japan ([source](https://www.ncbi.nlm.nih.gov/pubmed/32033064))."
    )

    st.subheader("How will the disease spread?")
    st.write(
        "The critical factor for controlling spread is how many others infected people interact with each day. "
        "This has a dramatic effect upon the dynamics of the disease. "
    )
    st.write(
        "**Play with the slider to the left to see how this changes the dynamics of disease spread**"
    )

    df_base = df[~df.Status.isin(["Need Hospitalization", "Need Ventilation"])]
    base_graph = graphing.infection_graph(df_base,
                                          max(0.5*population, df.Forecast.max()))
    st.write(base_graph)

    # TODO: psteeves can you confirm total number of deaths should change? Not clear to me why this would be
    # apart from herd immunity?
    # st.write('Note how the speed of spread affects both the *peak number of cases* and the *total number of deaths*.')

    hospital_graph = graphing.hospitalization_graph(
        df[df.Status.isin(["Infected", "Need Hospitalization"])], num_hospital_beds,
        max(0.5*population, df.Forecast.max())
    )

    st.subheader("How will this affect my healthcare system?")
    st.write(
        "The important variable for hospitals is the peak number of people who require hospitalization"
        " and ventilation at any one time."
    )

    # Do some rounding to avoid beds sounding too precise!
    st.write(
        f"Your country has around **{round(num_hospital_beds / 100) * 100:,}** beds. Bear in mind that most of these "
        "are probably already in use for people sick for other reasons."
    )
    st.write(
        "It's hard to know how many ventilators are present per country, but there will certainly be a worldwide "
        "shortage. Many countries are scrambling to buy them [(source)](https://www.reuters.com/article/us-health-coronavirus-draegerwerk-ventil/germany-italy-rush-to-buy-life-saving-ventilators-as-manufacturers-warn-of-shortages-idUSKBN210362)."
    )

    st.write(hospital_graph)
    peak_occupancy = df.loc[df.Status == "Need Hospitalization"]["Forecast"].max()
    percent_beds_at_peak = min(100 * num_hospital_beds / peak_occupancy, 100)

    # peak_ventilation = df.loc[df.Status == "Ventilated"]["Forecast"].max()
    # percent_ventilators_at_peak = min(
    #     100 * Sidebar.number_of_ventilators / peak_ventilation, 100
    # )

    st.markdown(
        f"At peak, **{peak_occupancy:,}** people will need hospital beds. ** {percent_beds_at_peak:.1f} % ** of people "
        f"who need a bed in hospital will have access to one given your country's historical resources. This does "
        f"not take into account any special measures that may have been taken in the last few months."
    )
    # st.markdown(
    #     f"At peak, ** {percent_ventilators_at_peak:.1f} % ** of people who need a ventilator have one"
    # )


if __name__ == "__main__":
    run_app()

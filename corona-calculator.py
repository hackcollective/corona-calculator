import datetime

import streamlit as st

import graphing
import models
from data import constants
from interface import css
from interface.elements import reported_vs_true_cases
from utils import COLOR_MAP, generate_html, graph_warning

# estimates from https://github.com/midas-network/COVID-19/tree/master/parameter_estimates/2019_novel_coronavirus

NOTION_MODELLING_DOC = (
    "https://www.notion.so/coronahack/Modelling-d650e1351bf34ceeb97c82bd24ae04cc"
)
MEDIUM_BLOGPOST = "https://medium.com/@archydeberker/should-i-go-to-brunch-an-interactive-tool-for-covid-19-curve-flattening-6ab6a914af0"


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
                text=f"Statistics refreshed as of ",
                line_height=0,
                font_family="Arial",
                font_size="12px",
            ),
            unsafe_allow_html=True,
        )

        st.sidebar.markdown(
            body=generate_html(
                text=f"{date_last_fetched}",
                bold=True,
                # color=COLOR_MAP["pink"],
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
            body=generate_html(
                text=f"Play with the numbers",
                line_height=0,
                color=COLOR_MAP["pink"],
                bold=True,
                font_size="16px",
            ),
            unsafe_allow_html=True,
        )

        st.sidebar.markdown(
            body=generate_html(
                text=f"Change the degree of social distancing to see the effect upon disease "
                f"spread and access to hospital beds.",
                line_height=0,
                font_size="12px",
            )
            + "<br>",
            unsafe_allow_html=True,
        )

        self.contact_rate = st.sidebar.slider(
            label="How many people does an infected individual meet on a daily basis?",
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

        st.sidebar.markdown(
            body=generate_html(
                text=f"We're using an estimated transmission probability of {transmission_probability * 100:.1f}%,"
                f" see our <a href='https://www.notion.so/coronahack/Modelling-d650e1351bf34ceeb97c82bd24ae04cc'> methods for details</a>.",
                line_height=0,
                font_size="10px",
            ),
            unsafe_allow_html=True,
        )

        self.num_days_for_prediction = horizon[_num_days_for_prediction]


@st.cache
def _fetch_country_data():
    timestamp = datetime.datetime.utcnow()
    return constants.Countries(timestamp=timestamp)


def run_app():

    css.hide_menu()
    css.limit_plot_size()

    # Get cached country data
    countries = _fetch_country_data()

    if countries.stale:
        st.caching.clear_cache()
        countries = _fetch_country_data()

    st.markdown(
        body=generate_html(text=f"Corona Calculator", bold=True, tag="h1"),
        unsafe_allow_html=True,
    )
    st.markdown(
        body=generate_html(
            tag="h2",
            text="A tool to help you visualize the impact of social distancing <br>",
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        body=generate_html(
            text="<strong>Disclaimer:</strong> <em>The creators of this application are not healthcare professionals. "
            "The illustrations provided were estimated using best available data but might not accurately reflect reality.</em>",
            color="gray",
            font_size="12px",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        body=generate_html(
            tag="h4",
            text=f"<u><a href=\"{NOTION_MODELLING_DOC}\" target=\"_blank\" style=color:{COLOR_MAP['pink']};>"
            "Methodology</a></u> <span> &nbsp;&nbsp;&nbsp;&nbsp</span>"
            f"<u><a href=\"{MEDIUM_BLOGPOST}\" target=\"_blank\" style=color:{COLOR_MAP['pink']};>"
            "Blogpost</a> </u>"
            "<hr>",
        ),
        unsafe_allow_html=True,
    )

    sidebar = Sidebar(countries)
    country = sidebar.country
    country_data = countries.country_data[country]
    number_cases_confirmed = country_data["Confirmed"]
    population = country_data["Population"]
    num_hospital_beds = country_data["Num Hospital Beds"]

    sir_model = models.SIRModel(
        transmission_rate_per_contact=constants.TransmissionRatePerContact.default,
        contact_rate=sidebar.contact_rate,
        recovery_rate=constants.RecoveryRate.default,
        normal_death_rate=constants.MortalityRate.default,
        critical_death_rate=constants.CriticalDeathRate.default,
        hospitalization_rate=constants.HospitalizationRate.default,
        hospital_capacity=num_hospital_beds,
    )
    true_cases_estimator = models.TrueInfectedCasesModel(
        constants.AscertainmentRate.default
    )

    df = models.get_predictions(
        true_cases_estimator,
        sir_model,
        number_cases_confirmed,
        population,
        sidebar.num_days_for_prediction,
    )

    reported_vs_true_cases(
        number_cases_confirmed, true_cases_estimator.predict(number_cases_confirmed)
    )

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
    base_graph = graphing.infection_graph(df_base, df.Forecast.max())
    st.warning(graph_warning)
    st.write(base_graph)

    hospital_graph = graphing.hospitalization_graph(
        df[df.Status.isin(["Infected", "Need Hospitalization"])],
        num_hospital_beds,
        max(num_hospital_beds, df.Forecast.max()),
    )

    st.write(
        "Note that we use a fixed estimate of the mortality rate here, of 1% [(source)](https://institutefordiseasemodeling.github.io/nCoV-public/analyses/first_adjusted_mortality_estimates_and_risk_assessment/2019-nCoV-preliminary_age_and_time_adjusted_mortality_rates_and_pandemic_risk_assessment.html). "
        "In reality, the mortality rate will be highly dependent upon the load upon the healthcare system and "
        "the availability of treatment. Some estimates ([like this one](https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30195-X/fulltext)) are closer to 6%."
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

    st.warning(graph_warning)
    st.write(hospital_graph)
    peak_occupancy = df.loc[df.Status == "Need Hospitalization"]["Forecast"].max()
    percent_beds_at_peak = min(100 * num_hospital_beds / peak_occupancy, 100)


    st.markdown(
        f"At peak, **{peak_occupancy:,}** people will need hospital beds. ** {percent_beds_at_peak:.1f} % ** of people "
        f"who need a bed in hospital will have access to one given your country's historical resources. This does "
        f"not take into account any special measures that may have been taken in the last few months."
    )


if __name__ == "__main__":
    run_app()

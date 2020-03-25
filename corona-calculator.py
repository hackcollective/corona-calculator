import datetime

import streamlit as st

import data.countries
import graphing
import models
import utils
from data import constants
from data.utils import check_if_aws_credentials_present
from interface import css
from interface.elements import reported_vs_true_cases
from utils import COLOR_MAP, generate_html, graph_warning

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
            body=generate_html(text=f"{date_last_fetched}", bold=True, line_height=0),
            unsafe_allow_html=True,
        )

        st.sidebar.markdown(
            body=generate_html(
                text=f'Population: {int(country_data["Population"]):,}<br>Infected: {int(country_data["Confirmed"]):,}<br>'
                f'Recovered: {int(country_data["Recovered"]):,}<br>Dead: {int(country_data["Deaths"]):,}',
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

        st.sidebar.markdown(
            body=generate_html(
                text=f"How many people does an individual [...] meet on a daily basis?",
                line_height=0,
                font_size="12px",
            )
            + "<br>",
            unsafe_allow_html=True,
        )

        slider_person_descriptions = {
            constants.SymptomState.ASYMPTOMATIC : "without symptoms",
            constants.SymptomState.SYMPTOMATIC : "with symptoms",
        }

        self.contact_rate = {
            state : st.sidebar.slider(
                label=description,
                min_value=constants.AverageDailyContacts.min,
                max_value=constants.AverageDailyContacts.max,
                value=constants.AverageDailyContacts.default,
            ) 
            for state, description in slider_person_descriptions.items()
        }

        st.sidebar.markdown(
            body=generate_html(
                text=f"We're using an estimated transmission probability of {transmission_probability * 100:.1f}%. "
                f"This probability is diminished by 45% for asymptomatic cases, "
                f" see our <a href='https://www.notion.so/coronahack/Modelling-d650e1351bf34ceeb97c82bd24ae04cc'> methods for details</a>.",
                line_height=0,
                font_size="10px",
            ),
            unsafe_allow_html=True,
        )


@st.cache
def _fetch_country_data():
    check_if_aws_credentials_present()
    timestamp = datetime.datetime.utcnow()
    return data.countries.Countries(timestamp=timestamp)


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
    _historical_df = countries.historical_country_data
    historical_data = _historical_df.loc[_historical_df.index == country]
    number_cases_confirmed = country_data["Confirmed"]
    population = country_data["Population"]
    num_hospital_beds = country_data["Num Hospital Beds"]

    st.subheader(f"How has the disease spread in {country}?")
    st.write(
        "The number of reported cases radically underestimates the true cases, because people do not show symptoms for "
        "several days, not everybody gets tested, and the tests take a few days to return results. "
        "The extent depends upon your country's testing strategy."
        " This estimate (14% reporting) is from China ([source](https://science.sciencemag.org/content/early/2020/03/13/science.abb3221))."
    )
    # Estimate true cases
    true_cases_estimator = models.TrueInfectedCasesModel(
        constants.ReportingRate.default
    )
    estimated_true_cases = true_cases_estimator.predict(number_cases_confirmed)

    reported_vs_true_cases(int(number_cases_confirmed), estimated_true_cases)

    st.markdown(
        f"Given the prevalence of the infection in your country, the probability of being infected at this time is "
        f"**{estimated_true_cases / population:.3%}**. Even if you show no symptoms, the probability of being infected is "
        f"**{models.get_probability_of_infection_give_asymptomatic(population, estimated_true_cases, constants.AsymptomaticRate.default):.3%}**. "
        f"Note that these probabilities are on a country-wide basis and so may not apply to your situation."
    )

    # Plot historical data
    fig = graphing.plot_historical_data(historical_data)
    st.write(fig)

    true_cases_estimator = models.TrueInfectedCasesModel(
        constants.ReportingRate.default
    )
    asymptomatic_cases_estimator = models.AsymptomaticCasesModel(
        constants.AsymptomaticRate.default
    )

    contact_rate = sidebar.contact_rate

    sir_model_2 = models.AsymptomaticSIRModel(
        transmission_rate_per_contact=constants.TransmissionRatePerContact.default_per_symptom_state,
        contact_rate=contact_rate,
        asymptomatic_cases_model=asymptomatic_cases_estimator,
        recovery_rate=constants.RecoveryRate.default,
        normal_death_rate=constants.MortalityRate.default,
        critical_death_rate=constants.CriticalDeathRate.default,
        hospitalization_rate=constants.HospitalizationRate.default,
        hospital_capacity=num_hospital_beds
    )

    df = models.get_predictions(
        cases_estimator=true_cases_estimator,
        sir_model=sir_model_2,
        num_diagnosed=number_cases_confirmed,
        num_recovered=country_data["Recovered"],
        num_deaths=country_data["Deaths"],
        area_population=population,
    )

    st.subheader("How will my actions affect the spread?")
    st.write(
        "The critical factor for controlling spread is how many others infected people interact with each day. "
        "This has a dramatic effect upon the dynamics of the disease. "
    )
    st.write(
        "**Play with the slider to the left to see how this changes the dynamics of disease spread**"
    )

    df_base = df[~df.Status.isin(["Need Hospitalization"])]
    base_graph = graphing.infection_graph(df_base, df_base.Forecast.max())
    st.warning(graph_warning)
    st.write(base_graph)

    st.subheader("How will this affect my healthcare system?")
    st.write(
        "The important variable for hospitals is the peak number of people who require hospitalization"
        " and ventilation at any one time."
    )

    # Do some rounding to avoid beds sounding too precise!
    approx_num_beds = round(num_hospital_beds / 100) * 100
    st.write(
        f"Your country has around **{approx_num_beds:,}** beds. Bear in mind that most of these "
        "are probably already in use for people sick for other reasons."
    )
    st.write(
        "It's hard to know exactly how many ventilators are present per country, but there will certainly be a worldwide "
        "shortage. Many countries are scrambling to buy them [(source)](https://www.reuters.com/article/us-health-coronavirus-draegerwerk-ventil/germany-italy-rush-to-buy-life-saving-ventilators-as-manufacturers-warn-of-shortages-idUSKBN210362)."
    )

    peak_occupancy = df.loc[df.Status == "Need Hospitalization"]["Forecast"].max()
    percent_beds_at_peak = min(100 * num_hospital_beds / peak_occupancy, 100)

    num_beds_comparison_chart = graphing.num_beds_occupancy_comparison_chart(
        num_beds_available=approx_num_beds, max_num_beds_needed=peak_occupancy
    )

    st.write(num_beds_comparison_chart)

    st.markdown(
        f"At peak, **{int(peak_occupancy):,}** people will need hospital beds. ** {percent_beds_at_peak:.1f}% ** of people "
        f"who need a bed in hospital will have access to one given your country's historical resources. This does "
        f"not take into account any special measures that may have been taken in the last few months."
    )

    st.subheader("How severe will the impact be?")

    num_dead = df[df.Status == "Dead"].Forecast.iloc[-1]
    num_recovered = df[df.Status == "Recovered"].Forecast.iloc[-1]
    st.markdown(
        f"If the average person in your country adopts the selected behavior, we estimate that **{int(num_dead):,}** "
        f"people will die."
    )

    st.markdown(
        f"The graph above below a breakdown of casualties and hospitalizations by age group."
    )

    outcomes_by_age_group = models.get_status_by_age_group(num_dead, num_recovered)
    fig = graphing.age_segregated_mortality(
        outcomes_by_age_group.loc[:, ["Dead", "Need Hospitalization"]]
    )
    st.write(fig)

    st.write(
        f"Parameters by age group, including demographic distribution, are [worldwide numbers](https://population.un.org/wpp/DataQuery/) "
        f"so they may be slightly different in your country."
    )
    st.write(
        f"We've used mortality rates from this [recent paper from Imperial College](https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf?fbclid=IwAR3TzdPTcLiOZN5r2dMd6_08l8kG0Mmr0mgP3TdzimpqB8H96T47ECBUfTM). "
        f"However, we've adjusted them according to the [maximum mortality rate recorded in Wuhan](https://wwwnc.cdc.gov/eid/article/26/6/20-0233_article)"
        f" when your country's hospitals are overwhelmed: if more people who need them lack hospital beds, more people will die."
    )
    st.write("<hr>", unsafe_allow_html=True)
    st.write(
        "Like this? [Click here to share it on Twitter](https://ctt.ac/u5U39), and "
        "[let us know your feedback via Google Form](https://forms.gle/J6ZFFgh4rVQm4y8G7)"
    )

    utils.insert_github_logo()


if __name__ == "__main__":

    run_app()

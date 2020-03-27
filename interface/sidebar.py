import streamlit as st

from data import constants
from utils import generate_html, COLOR_MAP


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
            constants.SymptomState.ASYMPTOMATIC: "without symptoms",
            constants.SymptomState.SYMPTOMATIC: "with symptoms",
        }

        self.contact_rate = {
            state: st.sidebar.slider(
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
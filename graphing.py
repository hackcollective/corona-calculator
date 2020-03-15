import pandas as pd
import plotly.express as px


def example_graph():
    df = px.data.iris()
    fig = px.scatter(df, x="sepal_width", y="sepal_length")
    return fig


def infection_graph(df):
    fig = px.line(df, x="Days", y="Forecast", color="Status")
    # fig.add_scatter(df, x='Days', y='Patients in Hospital')
    # fig.add_scatter(df, x='Days', y='Deaths')

    return fig


def hospitalization_graph(df, number_of_beds, number_of_ventilators):
    # Add in the number of beds and number of ventilators to the df
    days = list(df.Days.unique())
    n_days = len(days)

    bed_df = pd.DataFrame(
        {
            "Days": days,
            "Forecast": [number_of_beds] * n_days,
            "Status": ["Number of Beds"] * n_days,
        }
    )

    ventilator_df = pd.DataFrame(
        {
            "Days": days,
            "Forecast": [number_of_ventilators] * n_days,
            "Status": ["Number of Ventilators"] * n_days,
        }
    )

    fig = px.line(df, x="Days", y="Forecast", color="Status")
    fig.add_scatter(
        x=bed_df.Days,
        y=bed_df.Forecast,
        name="Number of Beds",
        fill="tozeroy",
        opacity=0.1,
        fillcolor="rgba(255,0,0,.1)",
    )
    fig.add_scatter(
        x=ventilator_df.Days,
        y=ventilator_df.Forecast,
        name="Number of Ventilators",
        fill="tozeroy",
        opacity=0.1,
        fillcolor="rgba(0,255,0,.1)",
    )

    return fig

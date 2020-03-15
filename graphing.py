import pandas as pd
import plotly.express as px


def plot_true_versus_confirmed(confirmed, predicted):
    df = pd.DataFrame(
        {
            "Status": ["Confirmed", "Predicted"],
            "Cases": [confirmed, predicted],
            "Color": ["b", "r"],
        }
    )
    fig = px.bar(df, x="Status", y="Cases", color="Color", template='plotly_white')
    fig.layout.update(showlegend=False)

    return fig


def infection_graph(df):
    fig = px.line(df, x="Days", y="Forecast", color="Status", template='plotly_white')
    # fig.add_scatter(df, x='Days', y='Patients in Hospital')
    # fig.add_scatter(df, x='Days', y='Deaths')

    return fig


def hospitalization_graph(df, number_of_beds, number_of_ventilators=None):
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

    fig = px.line(df, x="Days", y="Forecast", color="Status", template='plotly_white')
    fig.add_scatter(
        x=bed_df.Days,
        y=bed_df.Forecast,
        name="Number of Beds",
        fill="tozeroy",
        opacity=0.1,
        fillcolor="rgba(255,0,0,.1)",
        line={"color": "rgba(255,0,0,.5)"},
    )


    return fig

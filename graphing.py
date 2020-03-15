import pandas as pd
import plotly.express as px

TEMPLATE = "plotly_white"


def plot_true_versus_confirmed(confirmed, predicted):
    df = pd.DataFrame(
        {
            "Status": ["Confirmed", "Predicted"],
            "Cases": [confirmed, predicted],
            "Color": ["b", "r"],
        }
    )
    fig = px.bar(df, x="Status", y="Cases", color="Color", template=TEMPLATE)
    fig.layout.update(showlegend=False)

    return fig


def infection_graph(df, y_max):
    fig = px.line(df, x="Days", y="Forecast", color="Status", template=TEMPLATE)
    fig.update_yaxes(range=[0, y_max])
    return fig


def hospitalization_graph(df, number_of_beds, y_max):
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

    fig = px.line(df, x="Days", y="Forecast", color="Status", template=TEMPLATE)
    fig.add_scatter(
        x=bed_df.Days,
        y=bed_df.Forecast,
        name="Number of Beds",
        fill="tozeroy",
        opacity=0.1,
        fillcolor="rgba(255,0,0,.1)",
        line={"color": "rgba(255,0,0,.5)"},
    )
    fig.update_yaxes(range=[0, y_max])
    return fig

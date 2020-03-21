import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import COLOR_MAP

TEMPLATE = "plotly_white"

def _set_title(fig):
    fig.layout.update(title=dict(y=0.9, x=0.5, xanchor='center', yanchor='top'))

def _set_legends(fig):
    fig.layout.update(legend=dict(x=0, y=-0.05))
    fig.layout.update(legend_orientation="h")


def plot_historical_data(df):
    # Convert wide to long

    df = pd.melt(df,
                 id_vars='Date',
                 value_vars=['Confirmed', 'Deaths', 'Recovered'],
                 var_name='Status',
                 value_name='Number',
                 )

    fig = px.scatter(df, x='Date', y='Number', color='Status', template=TEMPLATE, opacity=0.8   )

    _set_legends(fig)

    return fig


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


def infection_graph(df, y_max, contact_rate):

    # We cannot explicitly set graph width here, have to do it as injected css: see interface.css
    fig = go.Figure(layout=dict(template=TEMPLATE))

    susceptible, infected, recovered = df.loc[df.Status =='Susceptible'], df.loc[df.Status =='Infected'], df.loc[df.Status =='Recovered']
    fig.add_scatter(x=susceptible.Days, y=susceptible.Forecast,
                    fillcolor=COLOR_MAP['susceptible'],
                    fill='tozeroy',
                    mode='lines',
                    line=dict(width=0),
                    name='Uninfected',
                    opacity=.5)

    fig.add_scatter(x=recovered.Days,
                    y=recovered.Forecast,
                    fillcolor=COLOR_MAP['recovered'],
                    fill='tozeroy',
                    mode='lines',
                    line=dict(width=0),
                        name='Recovered',
                    opacity=.5)

    fig.add_scatter(x=infected.Days,
                    y=infected.Forecast,
                    fillcolor='#FFA000',
                    fill='tozeroy',
                    mode='lines',
                    line=dict(width=0),
                    name='Infected',
                    opacity=.5)
    fig.update_yaxes(range=[0, y_max])
    fig.layout.update(xaxis_title="Number of days from now")
    fig.layout.update(title=dict(text=f"Disease spread<br>when meeting {int(contact_rate)} people per day"))
    _set_legends(fig)
    _set_title(fig)

    return fig


def age_segregated_mortality(df):
    df = df.rename(index={ag: "0-30" for ag in ["0-9", "10-19", "20-29"]}).reset_index()
    df = pd.melt(df, id_vars="Age Group", var_name="Status", value_name="Forecast")
    # Add up values for < 30
    df = (
        df.groupby(["Age Group", "Status"])
        .sum()
        .reset_index(1)
        .sort_values(by="Status", ascending=False)
    )

    df['Status'] = df['Status'].apply(lambda x: {'Need Hospitalization': 'Hospitalized'}.get(x, x))

    fig = px.bar(
        df,
        x=df.index,
        y="Forecast",
        color="Status",
        template=TEMPLATE,
        opacity=0.7,
        color_discrete_sequence=["pink", "red"],
        barmode='group',
    )
    fig.layout.update(
        xaxis_title="",
        yaxis_title="",
        font=dict(family="Arial", size=15, color=COLOR_MAP["default"]),
        title=dict(text=f"Casualties and hospitalizations by age group<br>when meeting {int(contact_rate)} people per day"),
    )
    _set_legends(fig)
    _set_title(fig)
    return fig


def num_beds_occupancy_comparison_chart(num_beds_available, max_num_beds_needed):
    """
    A horizontal bar chart comparing # of beds available compared to 
    max number number of beds needed
    """
    num_beds_available, max_num_beds_needed = int(num_beds_available), int(max_num_beds_needed)

    df = pd.DataFrame(
        {
            "Label": ["Total Beds ", "Peak Occupancy "],
            "Value": [num_beds_available, max_num_beds_needed],
            "Text": [f"{num_beds_available:,}  ", f"{max_num_beds_needed:,}  "],
            "Color": ["b", "r"],
        },
    )
    fig = px.bar(
        df,
        x="Value",
        y="Label",
        color="Color",
        text="Text",
        orientation="h",
        opacity=0.7,
        template=TEMPLATE,
        height=300,
    )

    fig.layout.update(
        showlegend=False,
        xaxis_title="",
        xaxis_showticklabels=False,
        yaxis_title="",
        yaxis_showticklabels=True,
        font=dict(family="Arial", size=15, color=COLOR_MAP["default"]),
        title=dict(text=f"Peak Occupancy<br>when meeting {int(contact_rate)} people per day"),
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    _set_title(fig)
    return fig
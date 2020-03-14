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

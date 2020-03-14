import plotly.express as px


def example_graph():
    df = px.data.iris()
    fig = px.scatter(df, x="sepal_width", y="sepal_length")
    return fig


def infection_graph(df):
    fig = px.scatter(df, x='Days', y='Confirmed Cases')
    fig.add_scatter(df, x='Days', y='Actual Cases')
    fig.add_scatter(df, x='Days', y='Patients in Hospital')
    fig.add_scatter(df, x='Days', y='Deaths')
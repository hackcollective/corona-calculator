import plotly.express as px


def example_graph():
    df = px.data.iris()
    fig = px.scatter(df, x="sepal_width", y="sepal_length")
    return fig
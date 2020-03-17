import streamlit as st


# This module uses markdown with unsafe HTML injection to inject styles we want
# See https://discuss.streamlit.io/t/are-you-using-html-in-markdown-tell-us-why/96/53

def _inject(css):
    st.markdown(css, unsafe_allow_html=True)


def hide_menu():
    hide_menu_style = """
        <style>

        #MainMenu {visibility: hidden;}
        
    </style>
        """
    _inject(hide_menu_style)


def limit_plot_size(limit='95vw'):
    """
    In browsers that are smaller than 700px (the streamlit column size),
    set the min width of graphs `limit`.
    """

    plot_style = """
            <style>
         @media screen and (max-width:7000px)  {
         .js-plotly-plot, .plotly, .plot-container 
        {min-width:""" + limit + """;
        max-width:300px;}
        }
        </style>
        """

    _inject(plot_style)

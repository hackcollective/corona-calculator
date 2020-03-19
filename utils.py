import streamlit as st

_SUSCEPTIBLE_COLOR = 'rgba(230,230,230,.4)'
_RECOVERED_COLOR = 'rgba(180,200,180,.4)'

COLOR_MAP = {"default": "#262730", "pink": "#E22A5B", "purple": "#985FFF",
             'susceptible': _SUSCEPTIBLE_COLOR,
             'recovered': _RECOVERED_COLOR}

def generate_html(
    text,
    color=COLOR_MAP["default"],
    bold=False,
    font_family=None,
    font_size=None,
    line_height=None,
    tag="div",
):
    if bold:
        text = f"<strong>{text}</strong>"
    css_style = f"color:{color};"
    if font_family:
        css_style += f"font-family:{font_family};"
    if font_size:
        css_style += f"font-size:{font_size};"
    if line_height:
        css_style += f"line-height:{line_height};"

    return f"<{tag} style={css_style}>{text}</{tag}>"


graph_warning = "Please be aware the scale of this graph changes!"


def insert_github_logo():
    st.markdown('<br>'
                '<div style="text-align: center;">'
                '<a href="https://github.com/archydeberker/corona-calculator"> '
                '<img src="https://image.flaticon.com/icons/png/128/1051/1051326.png" width=64>'
                ' </img>'
                '</a> </div>', unsafe_allow_html=True)
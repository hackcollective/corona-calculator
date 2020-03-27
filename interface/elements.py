import streamlit as st


def reported_vs_true_cases(num_cases_confirmed, num_cases_estimated):
    _border_color = "light-gray"
    _number_format = "font-size:35px; font-style:bold;"
    _cell_style = f" border: 2px solid {_border_color}; border-bottom:2px solid white; margin:10px"
    st.markdown(
        f"<table style='width: 100%; font-size:14px;  border: 0px solid gray; border-spacing: 10px;  border-collapse: collapse;'> "
        f"<tr> "
        f"<td style='{_cell_style}'> Confirmed Cases</td> "
        f"<td style='{_cell_style}'> Estimated True Cases </td>"
        "</tr>"
        f"<tr style='border: 2px solid {_border_color}'> "
        f"<td style='border-right: 2px solid {_border_color}; border-spacing: 10px; {_number_format + 'font-color:red'}' > {int(num_cases_confirmed):,}</td> "
        f"<td style='{_number_format + 'color:red'}'> {int(num_cases_estimated):,} </td>"
        "</tr>"
        "</table>"
        "<br>",
        unsafe_allow_html=True,
    )

    # Calls to streamlit render immediately, no need to return anything

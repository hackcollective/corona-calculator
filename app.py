import streamlit as st
import graphing

# estimates from https://github.com/midas-network/COVID-19/tree/master/parameter_estimates/2019_novel_coronavirus

def sidebar():
    number_cases_confirmed = st.sidebar.number_input('Confirmed cases in your area', min_value=1, step=10)

    estimated_doubling_time = st.sidebar.slider(label='Doubling time', min_value=1, max_value=10, value=5)

    presentation_delay =  st.sidebar.slider(label='Time between infection and '
                                                  'symptoms', min_value=1, max_value=10, value=5)

    testing_delay = st.sidebar.slider(label='Time between symptoms '
                                                 'diagnosis', min_value=1, max_value=10, value=3)



def run_app():
    st.title('Corona Calculator')
    st.write('Graphs and analysis will go here')
    sidebar()
    figure = graphing.example_graph()
    st.write(figure)

if __name__ == '__main__':
    run_app()

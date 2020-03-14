import numpy as np
import pandas as pd


def case_prediction_df(current_cases, doubling_time, symptom_delay, diagnostic_delay, max_days):
    #TODO @psteeves use the SIR model to make this proper (max_days)

    # For now, just assume exponential growth
    time = range(0, max_days)

    def calculate_growth(time_step):
        return current_cases * 2**(time_step / doubling_time)

    confirmed_cases = [calculate_growth(t) for t in time]

    # TODO work out true cases properly via ascertainment rate
    actual_cases = [calculate_growth(t+symptom_delay+diagnostic_delay) for t in time]

    # Have to use this rather clunky format to make plotly express happy

    return pd.DataFrame(np.array([2*list(time),
                                  confirmed_cases + actual_cases,
                                  ['Confirmed']*max_days + ['Actual']*max_days
                                  ]).T,
                        columns=['Days', 'Cases', 'Estimate'])


if __name__ == '__main__':
    df = case_prediction_df(1,5,2,2)
    pd.wide_to_long(df, stubnames=["Confirmed"], i='Days', j="Source")
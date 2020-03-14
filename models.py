import numpy as np
import pandas as pd


def case_prediction_df(current_cases, doubling_time):

    # For now, just assume exponential growth
    time = range(0, 100)

    def calculate_growth(time_step):
        return current_cases * 2**(time_step / doubling_time)

    cases = [calculate_growth(t) for t in time]

    return pd.DataFrame(np.array([time, cases]).T,
                        columns=['Days', 'Cases'])

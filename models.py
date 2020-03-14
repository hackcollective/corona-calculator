import pandas as pd


def get_predictions(cases_estimator, sir_model, num_diagnosed, area_population, max_days):

    true_cases = cases_estimator.predict(num_diagnosed)

    # For now assume removed starts at 0. Doesn't have a huge effect on the model
    predictions = sir_model.predict(
        susceptible=area_population - true_cases,
        infected=true_cases,
        removed=0,
        time_steps=max_days,
    )
    S, I, R = predictions.values()

    num_entries = max_days + 1
    # Have to use the long format to make plotly express happy
    df = pd.DataFrame(
        {
            "Days": list(range(num_entries)) * 3,
            "Forecast": S + I + R,
            "Status": ["Susceptible"] * num_entries
            + ["Infected"] * num_entries
            + ["Removed"] * num_entries,
        }
    )
    return df


class TrueInfectedCasesEstimator:
    """
    Used to estimate total number of true infected persons based on either number of diagnosed cases or number of deaths.
    """

    def __init__(self, ascertainment_rate):
        """
        :param ascertainment_rate: Ratio of diagnosed to true number of infected persons.
        """
        self._ascertainment_rate = ascertainment_rate

    def predict(self, diagnosed_cases):
        return diagnosed_cases / self._ascertainment_rate


class SIRModel:
    def __init__(self, transmission_rate_per_contact, contact_rate, removal_rate):
        """
        :param transmission_rate_per_contact: Prob of contact between infected and susceptible leading to infection.
        :param contact_rate: Mean number of daily contacts between an infected individual and susceptible people.
        :param removal_rate: Rate of removal of infected individuals (death or recovery)
        """
        self._infection_rate = transmission_rate_per_contact * contact_rate
        self._removal_rate = removal_rate

    def predict(self, susceptible, infected, removed, time_steps=100):
        """
        Run simulation.
        :param susceptible: Number of susceptible people in population.
        :param infected: Number of infected people in population.
        :param removed: Number of recovered people in population.
        :param time_steps: Time steps to run simulation for
        :return: List of values for S, I, R over time steps
        """
        population = susceptible + infected + removed

        S = [susceptible]
        I = [infected]
        R = [removed]

        for t in range(time_steps):
            s_t = S[-1] - self._infection_rate * I[-1] * S[-1] / population
            i_t = (
                I[-1]
                + self._infection_rate * I[-1] * S[-1] / population
                - self._removal_rate * I[-1]
            )
            r_t = R[-1] + self._removal_rate * I[-1]

            S.append(s_t)
            I.append(i_t)
            R.append(r_t)

        return {"S": S, "I": I, "R": R}


if __name__ == "__main__":
    df = get_predictions(1, 5, 2, 2)
    pd.wide_to_long(df, stubnames=["Confirmed"], i="Days", j="Source")

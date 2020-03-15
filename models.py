import itertools

import numpy as np
import pandas as pd

_STATUSES_TO_SHOW = ["Infected", "Deaths", "Hospitalized", "Ventilated"]


def get_predictions(
    cases_estimator,
    sir_model,
    death_toll_model,
    hospitalization_model,
    num_diagnosed,
    area_population,
    max_days,
):

    true_cases = cases_estimator.predict(num_diagnosed)

    # For now assume removed starts at 0. Doesn't have a huge effect on the model
    predictions = sir_model.predict(
        susceptible=area_population - true_cases,
        infected=true_cases,
        removed=0,
        time_steps=max_days,
    )
    predictions["Deaths"] = death_toll_model.predict(predictions["Infected"])
    predictions["Hospitalized"], predictions[
        "Ventilated"
    ] = hospitalization_model.predict(predictions["Infected"])
    num_entries = max_days + 1

    # Have to use the long format to make plotly express happy
    df = pd.DataFrame(
        {
            "Days": list(range(num_entries)) * len(_STATUSES_TO_SHOW),
            "Forecast": list(
                itertools.chain.from_iterable(
                    predictions[status] for status in _STATUSES_TO_SHOW
                )
            ),
            "Status": list(
                itertools.chain.from_iterable(
                    [status] * num_entries for status in _STATUSES_TO_SHOW
                )
            ),
        }
    )
    return df


class TrueInfectedCasesModel:
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


class DeathTollModel:
    """
    Given a list of points in time representing the infected persons in a population and the mortality rate
    of the disease, compute the cumulative death toll.
    """

    def __init__(self, mortality_rate):
        self._mortality_rate = mortality_rate

    def predict(self, num_infected_cases):
        """
        :param num_infected_cases: List of ints representing number of infected cases over time.
        :return: Cumulative death toll over time.
        """
        deaths = [
            np.random.binomial(n, self._mortality_rate) for n in num_infected_cases
        ]
        return np.cumsum(deaths).tolist()


class HospitalizationModel:
    def __init__(self, hospitalization_rate, ventilation_rate):
        """
        :param hospitalization_rate: Fraction of cases of people going into hospital
        :param ventilation_rate: Fraction of cases in which people need a ventilator
        """
        self._hospitalization_rate = hospitalization_rate
        self._ventilation_rate = ventilation_rate

    def predict(self, num_infected_cases):
        """

        :param num_infected_cases: List of ints representing number of infected cases over time.
        :return: tuple of hospitalized and ventilated patients over time
        """
        hospitalized = [
            np.random.binomial(n, self._hospitalization_rate)
            for n in num_infected_cases
        ]

        ventilated = [
            np.random.binomial(n, self._ventilation_rate) for n in num_infected_cases
        ]

        return hospitalized, ventilated


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

        S = [round(susceptible)]
        I = [round(infected)]
        R = [round(removed)]

        for t in range(time_steps):
            s_t = S[-1] - self._infection_rate * I[-1] * S[-1] / population
            i_t = (
                I[-1]
                + self._infection_rate * I[-1] * S[-1] / population
                - self._removal_rate * I[-1]
            )
            r_t = R[-1] + self._removal_rate * I[-1]

            S.append(round(s_t))
            I.append(round(i_t))
            R.append(round(r_t))

        return {"Susceptible": S, "Infected": I, "Removed": R}

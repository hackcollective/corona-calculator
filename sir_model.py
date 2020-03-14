class SIRModel:
    def __init__(self, transmission_rate_per_contact, contact_rate, removal_rate):
        """
        :param transmission_rate_per_contact: Prob of contact between infected and susceptible leading to infection.
        :param contact_rate: Mean number of daily contacts between an infected individual and susceptible people.
        :param removal_rate: Rate of removal of infected individuals (death or recovery)
        """
        self._infection_rate = transmission_rate_per_contact * contact_rate
        self._removal_rate = removal_rate

    def run(self, susceptible, infected, removed, time_steps=100):
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

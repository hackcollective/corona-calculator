"""
Range estimates for various epidemiology constants.
Data gathered from https://github.com/midas-network/COVID-19/tree/master/parameter_estimates/2019_novel_coronavirus
and https://www.mdpi.com/2077-0383/9/2/462/htm
Parameter bounds were subjectively chosen from positively peer-reviewed estimates.
"""


"""
SIR model constants
"""


class RemovalRate:
    min = 1 / 10
    default = 1 / 10  # Recovery period around 10 days
    max = 1 / 10


class TransmissionRatePerContact:
    # Probability of a contact between carrier and susceptible leading to infection
    min = 0.017857142857142856
    default = (
        0.018
    )  # Found using binomial distribution in Wuhan scenario: 14 contacts per day, 10 infectious days, 2.5 average people infected.
    max = 0.02


class AverageDailyContacts:
    min = 0
    max = 100
    default = 20


"""
Health care constants
"""


class AscertainmentRate:
    # Proportion of true cases diagnosed
    min = 0.05
    max = 0.25
    default = 0.1


class MortalityRate:
    min = 0.005
    max = 0.05
    default = 0.01


class SevereInfectionRate:
    # Cases requiring hospitalization
    min = 0.05
    max = 0.02
    default = 0.2

"""
Range estimates for various epidemiology constants.
Data gathered from https://github.com/midas-network/COVID-19/tree/master/parameter_estimates/2019_novel_coronavirus
and https://www.mdpi.com/2077-0383/9/2/462/htm
Parameter bounds were subjectively chosen from positively peer-reviewed estimates.
"""

# SIR model constants

REMOVAL_RATE = [1 / 10, 1 / 5]  # Recovery period between 5 and 10 days
TRANSMISSION_RATE_PER_CONTACT = (
    0.017857142857142856
)  # Found using binomial distribution in Wuhan scenario: 14 contacts per day, 10 infectious days, 2.5 average people infected.

# Health care constants

ASCERTAINMENT_RATE = [0.05, 0.25]  # Cases being identified
MORTALITY_RATE = [0.005, 0.05]
SEVERE_INFECTION_RATE = [0.05, 0.2]  # Cases requiring hospitalization

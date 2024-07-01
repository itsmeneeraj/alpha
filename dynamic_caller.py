import numpy as np
import pandas as pd

# Function to get user input
def get_user_input():
    initial_wealth = float(input("Enter the initial wealth: "))
    target_wealth = float(input("Enter the target wealth: "))
    investment_horizon = int(input("Enter the investment horizon in years: "))
    time_steps = int(input("Enter the number of time steps: "))
    risk_tolerance = input("Enter risk tolerance (high, moderate, low): ")
    return initial_wealth, target_wealth, investment_horizon, time_steps, risk_tolerance

# Get user inputs
initial_wealth, target_wealth, investment_horizon, time_steps, risk_tolerance = get_user_input()

# Import the function from the first part
from EF_FR import get_best_return_and_risk

# Get best return and risk based on user risk tolerance
best_return, best_risk = get_best_return_and_risk(risk_tolerance)

# Define parameters
mu = best_return   # Expected return from previous program
sigma = best_risk  # Risk (volatility) from previous program

# Discretize state space
wealth_levels = np.linspace(0, target_wealth, num=21)  # Discretize wealth into 21 levels
time_intervals = np.linspace(0, investment_horizon, num=time_steps+1)  # Discretize time

# Define utility function (e.g., exponential utility)
def utility_function(wealth):
    return np.log(wealth + 1)  # Avoid log(0)

# Initialize value function array
value_function = np.zeros((len(wealth_levels), len(time_intervals)))

# Set terminal condition
value_function[:, -1] = utility_function(wealth_levels)

# Define function to compute next wealth using GBM
def next_wealth(wealth, allocation, mu, sigma, dt):
    return wealth * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.normal())

# Backward induction
for t in reversed(range(len(time_intervals) - 1)):
    for w in range(len(wealth_levels)):
        expected_values = []
        for allocation in np.linspace(0, 1, num=11):  # Different allocations from 0 to 100%
            next_w = next_wealth(wealth_levels[w], allocation, mu, sigma, time_intervals[1] - time_intervals[0])
            next_w_index = np.searchsorted(wealth_levels, next_w, side='right') - 1
            next_w_index = min(next_w_index, len(wealth_levels) - 1)
            expected_value = value_function[next_w_index, t + 1]
            expected_values.append(expected_value)
        value_function[w, t] = np.max(expected_values)

# Extract optimal policy
optimal_policy = np.zeros((len(wealth_levels), len(time_intervals) - 1))
for t in range(len(time_intervals) - 1):
    for w in range(len(wealth_levels)):
        allocation_values = []
        for allocation in np.linspace(0, 1, num=11):
            next_w = next_wealth(wealth_levels[w], allocation, mu, sigma, time_intervals[1] - time_intervals[0])
            next_w_index = np.searchsorted(wealth_levels, next_w, side='right') - 1
            next_w_index = min(next_w_index, len(wealth_levels) - 1)
            expected_value = value_function[next_w_index, t + 1]
            allocation_values.append(expected_value)
        optimal_policy[w, t] = np.linspace(0, 1, num=11)[np.argmax(allocation_values)]

# Output the optimal policy
optimal_policy_df = pd.DataFrame(optimal_policy, columns=[f'Time {t}' for t in range(len(time_intervals) - 1)], index=wealth_levels)
print(optimal_policy_df)

# Save the optimal policy to an Excel file
optimal_policy_df.to_excel("optimal_policy.xlsx", sheet_name='Optimal Policy')

print("Optimal policy saved to 'optimal_policy.xlsx'.")

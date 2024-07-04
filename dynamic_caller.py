import numpy as np
import pandas as pd

# Function to get user data from Excel sheet
def get_user_data(file_path):
    return pd.read_excel(file_path)

# Import the function from the second program (assuming the second program is saved as EF_FR.py)
from EF_FR import get_best_return_and_risk

# Define utility function (e.g., exponential utility)
def utility_function(wealth):
    return np.log(wealth + 1)  # Avoid log(0)

# Define function to compute next wealth using Geometric Brownian Motion (GBM)
def next_wealth(wealth, allocation, mu, sigma, dt):
    return wealth * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.normal())

# Read user data
user_data = get_user_data('user_goals.xlsx')

# DataFrame to store monthly investment needed for each client
monthly_investment_needed_df = pd.DataFrame(columns=['Client', 'Monthly Investment Needed'])

# Loop through each user
monthly_investment_needed_list = []
for index, user in user_data.iterrows():
    client_name = user['Client']
    initial_wealth = user['Monthly Investment Capacity'] * 12  # Assuming the initial wealth is 12 times the monthly investment
    target_wealth = user['Goal Amount']
    investment_horizon = user['Goal Time Horizon']
    risk_tolerance = user['Risk Tolerance']
    time_steps = investment_horizon  # Monthly steps

    # Get best return, risk, and portfolio weights based on user risk tolerance
    best_return, best_risk, portfolio_weights = get_best_return_and_risk(risk_tolerance)

    # Define parameters
    mu = best_return   # Expected return from previous program
    sigma = best_risk  # Risk (volatility) from previous program

    # Discretize state space
    wealth_levels = np.linspace(0, target_wealth, num=21)  # Discretize wealth into 21 levels
    time_intervals = np.linspace(0, investment_horizon, num=time_steps+1)  # Discretize time

    # Initialize value function array
    value_function = np.zeros((len(wealth_levels), len(time_intervals)))

    # Set terminal condition
    value_function[:, -1] = utility_function(wealth_levels)

    # Backward induction to compute the value function
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

    # Save the optimal policy to an Excel file
    optimal_policy_df.to_excel(f"optimal_policy_{index}.xlsx", sheet_name='Optimal Policy')
    print(f"Optimal policy saved to 'optimal_policy_{index}.xlsx'.")

    # Align portfolio weights with stock symbols
    stock_symbols = pd.read_excel('indian_stock_symbols.xlsx')['Symbol'].tolist()
    portfolio_weights = np.array(portfolio_weights)
    if portfolio_weights.ndim == 1:
        portfolio_weights = portfolio_weights.reshape(1, -1)

    if portfolio_weights.shape[1] != len(stock_symbols):
        raise ValueError(f"Shape of portfolio_weights {portfolio_weights.shape} does not match number of stock symbols {len(stock_symbols)}.")

    portfolio_weights_df = pd.DataFrame(portfolio_weights, columns=stock_symbols)
    portfolio_weights_df.to_excel(f"portfolio_weights_{index}.xlsx", sheet_name='Portfolio Weights')
    print(f"Portfolio weights saved to 'portfolio_weights_{index}.xlsx'.")

    # Calculate investment in each stock over the years
    investment_over_years = np.zeros((investment_horizon + 1, len(stock_symbols)))
    for t in range(investment_horizon + 1):
        allocation_index = min(t, len(optimal_policy_df.columns) - 1)  # Ensure index is within bounds
        max_policy_value = optimal_policy_df.iloc[:, allocation_index].max()
        investment_over_years[t] = max_policy_value * portfolio_weights

    investment_over_years_df = pd.DataFrame(investment_over_years, columns=stock_symbols, index=[f'Year {i}' for i in range(investment_horizon + 1)])
    investment_over_years_df.to_excel(f"investment_over_years_{index}.xlsx", sheet_name='Investment Over Years')
    print(f"Investment over years saved to 'investment_over_years_{index}.xlsx'.")

    # # Calculate monthly investment needed using investment over years
    # total_investment_needed = target_wealth - investment_over_years_df.sum().sum()
    # monthly_investment_needed = total_investment_needed / (investment_horizon * 12)
    # monthly_investment_needed_list.append({'Client': client_name, 'Monthly Investment Needed': monthly_investment_needed})

# # Save the monthly investment needed for each client to an Excel file
# monthly_investment_needed_df = pd.DataFrame(monthly_investment_needed_list)
# monthly_investment_needed_df.to_excel("monthly_investment_needed.xlsx", sheet_name='Monthly Investment Needed')
# print("Monthly investment needed saved to 'monthly_investment_needed.xlsx'.")

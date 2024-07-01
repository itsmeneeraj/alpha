import numpy as np
import pandas as pd

# Define constants and parameters
T = 10  # Time horizon in years
G = 200000  # Target wealth
W0 = 100000  # Initial wealth
monthly_cash_flow = 1000  # Monthly Cash Flow
n_assets = 2  # Number of assets (Equity & Debt)
mu = np.array([0.07, 0.12]) / 12  # Expected monthly returns (Nifty500 and Bond Yield)
sigma = np.array([0.1, 0.2]) / np.sqrt(12)  # Monthly volatilities (Nifty500 and Bond Yield)
corr_matrix = np.array([[1, 0.3], [0.2, 0.5]])  # Correlation matrix
cov_matrix = np.outer(sigma, sigma) * corr_matrix  # Covariance matrix

# Time and wealth discretization
months = T * 12  # Total Number of months
time_steps = np.arange(0, months + 1)
wealth_grid = np.linspace(0, 2 * G, 100)

# Initialize dynamic programming table
dp_table = np.zeros((len(time_steps), len(wealth_grid)))
dp_table[-1, :] = (wealth_grid >= G).astype(int)  # Final step

# Initialize the table to store the best allocation
allocation_table = np.zeros((len(time_steps), len(wealth_grid)))

# Backward recursion
for t in reversed(range(months)):
    for i, W in enumerate(wealth_grid):
        max_prob = 0
        best_allocation = 0
        for a in np.linspace(0, 1, 11):  # Portfolio allocations
            # Portfolio mean and variance
            portfolio_mu = a * mu[0] + (1 - a) * mu[1]
            portfolio_sigma = np.sqrt(a**2 * sigma[0]**2 + (1 - a)**2 * sigma[1]**2 + 2 * a * (1 - a) * cov_matrix[0, 1])
            
            # Expected wealth at next time step
            expected_wealth = (W + monthly_cash_flow) * np.exp((portfolio_mu - 0.5 * portfolio_sigma**2) + portfolio_sigma * np.random.normal(0, 1))
            j = np.searchsorted(wealth_grid, expected_wealth, side='right') - 1
            j = np.clip(j, 0, len(wealth_grid) - 1)
            
            # Probability of reaching goal
            prob = dp_table[t + 1, j]
            if prob > max_prob:
                max_prob = prob
                best_allocation = a
        
        dp_table[t, i] = max_prob
        allocation_table[t, i] = best_allocation

# Optimal strategy
optimal_strategy = []
for t in range(months):
    for i, W in enumerate(wealth_grid):
        equity_allocation = allocation_table[t, i]
        debt_allocation = 1 - equity_allocation
        optimal_strategy.append((t, W, equity_allocation, debt_allocation))

# Convert optimal_strategy to a DataFrame
df_optimal_strategy = pd.DataFrame(optimal_strategy, columns=['Time', 'Wealth', 'Equity Allocation', 'Debt Allocation'])

# Save the DataFrame to an Excel file
output_file_path = '/Users/neeraj/Desktop/BAI/Python/dynamic_programming/optimal_strategy.xlsx'
df_optimal_strategy.to_excel(output_file_path, index=False)

print("Optimal strategy saved to:", output_file_path)
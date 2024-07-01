import pandas as pd

# Load the data from the file
#file_path = '/mnt/data/bond_yield_data.csv'  # Adjust the file path as needed
#df = pd.read_csv(file_path, parse_dates=['Date'], dayfirst=True)
#hist_bond_yield_
df = pd.read_excel('Historical_Debt.xlsx')

# Calculate daily returns
# The pct_change method calculates the percentage change between the current and prior element, giving daily returns.
df['Return'] = df['Price'].pct_change()

# Drop the first row which has NaN return
df = df.dropna()

# Calculate expected daily return
# The mean of the daily returns is calculated using the mean method.
expected_daily_return = df['Return'].mean()

# Get the total number of trading days in the dataset
total_trading_days = len(df)
print(f"Total Trading Days in consideration: {total_trading_days}")

# Calculate the number of years in the dataset
# The total number of years is calculated by finding the difference between the start and end dates and 
# dividing by the approximate number of days in a year (365.25).
start_date = df['Date'].min()
end_date = df['Date'].max()
total_years = (end_date - start_date).days / 365.25  # Approximate number of days in a year
print(f"Total Years in consideration: {total_years}")

# Calculate the annualized return
# The expected annual return is calculated by compounding the daily returns over the total number of trading days and 
# adjusting for the total number of years in the dataset.
expected_annual_return = ((1 + expected_daily_return) ** total_trading_days) ** (1 / total_years) - 1

# Convert the annualized return to a percentage
expected_annual_return_percentage = expected_annual_return * 100

print(f"Expected Daily Return: {expected_daily_return:.6f}")
print(f"Expected Annual Return: {expected_annual_return:.6f}")
print(f"Expected Annual Return Percentage: {expected_annual_return_percentage:.2f}%")

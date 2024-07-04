import numpy as np
import pandas as pd
import cvxpy as cp
import matplotlib.pyplot as plt
import yfinance as yf

def get_best_return_and_risk(risk_tolerance):
    # Load stock symbols from an Excel file
    '''
    This function reads an Excel file containing stock symbols.
    It cleans up the symbols by stripping any extra spaces.
    It appends .NS to each symbol to indicate they are from the National Stock Exchange of India.
    It returns a list of cleaned stock symbols.
    '''
    stock_symbols_df = pd.read_excel('indian_stock_symbols.xlsx')
    stock_symbols_df['Symbol'] = stock_symbols_df['Symbol'].astype(str).str.strip()
    stock_symbols = stock_symbols_df['Symbol'].tolist()

    # Add '.NS' suffix to each valid stock symbol for Yahoo Finance compatibility
    stock_NS = [stock + '.NS' for stock in stock_symbols if isinstance(stock, str) and stock and stock.lower() != 'nan']

    # Fetch data for all stock symbols
    '''
    This function fetches historical stock data for each symbol from Yahoo Finance.
    It retrieves adjusted closing prices for the last 5 years (We can increase this to 10 years or 15 years).
    It stores the data in a dictionary and converts it into a DataFrame.
    '''
    all_data = {}
    for symbol in stock_NS:
        print(f"Fetching data for {symbol}...")
        try:
            data_temp = yf.download(symbol, period='5y', interval='1d')['Adj Close']
            if not data_temp.empty:
                all_data[symbol] = data_temp
            else:
                print(f"No data found for {symbol}, skipping...")
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    # Create a DataFrame from the fetched data
    data = pd.DataFrame(all_data)

    # Calculate daily returns and drop missing values
    returns = data.pct_change().dropna()

    # Calculate annualized mean returns and covariance matrix
    '''
    This function calculates the percentage change in stock prices to get monthly returns.
    It calculates the mean returns and covariance matrix and annualizes them by multiplying by 12.
    It returns the mean returns and the covariance matrix.
    '''
    mean_returns = returns.mean() * 12
    cov_matrix = returns.cov() * 12

    # Function to optimize portfolio for a given target return
    '''
    This function sets up and solves an optimization problem to minimize the portfolio's risk (variance) for a given target return.
    It uses convex optimization with constraints that ensure the sum of weights is 1, expected return is at least the target return, and weights are non-negative.
    It returns the optimized weights.
    '''
    def optimize_portfolio(target_return, mean_returns, cov_matrix):
        N = len(mean_returns)  # Number of assets
        w = cp.Variable(N)  # Portfolio weights
        objective = cp.Minimize(cp.quad_form(w, cov_matrix))  # Minimize portfolio variance
        constraints = [
            cp.sum(w) == 1,  # Full investment constraint
            w @ mean_returns >= target_return,  # Target return constraint
            w >= 0  # No short selling constraint
        ]
        problem = cp.Problem(objective, constraints)
        problem.solve()
        return w.value

    # Calculate the efficient frontier
    '''
    This function calculates the efficient frontier by optimizing the portfolio for a range of target returns.
    It stores the risks, returns, and weights for each optimized portfolio.
    '''

    target_returns = np.linspace(mean_returns.min(), mean_returns.max(), 50)
    portfolio_risks = []
    portfolio_returns = []
    portfolio_weights = []

    for tr in target_returns:
        optimal_weights = optimize_portfolio(tr, mean_returns, cov_matrix)
        portfolio_risks.append(np.sqrt(optimal_weights @ cov_matrix @ optimal_weights))  # Portfolio risk
        portfolio_returns.append(optimal_weights @ mean_returns)  # Portfolio return
        portfolio_weights.append(optimal_weights)

    # Plot the efficient frontier
    plt.figure(figsize=(10, 6))
    plt.plot(portfolio_risks, portfolio_returns, 'o-')
    plt.xlabel('Risk (Standard Deviation)')
    plt.ylabel('Return')
    plt.title('Efficient Frontier')
    plt.show()

    # Function to provide the best portfolio based on user risk tolerance
    '''
    Based on user input, index is selected for high/moderate or low return.
    '''

    def get_best_portfolio(risk_tolerance):
        if (risk_tolerance == 'high'):
            index = np.argmax(portfolio_returns)
        elif (risk_tolerance == 'moderate'):
            index = np.argmin(np.abs(np.array(portfolio_returns) - np.mean(portfolio_returns)))
        elif (risk_tolerance == 'low'):
            index = np.argmin(portfolio_risks)
        else:
            raise ValueError("Risk tolerance must be 'high', 'moderate', or 'low'.")
        
        return portfolio_weights[index], portfolio_returns[index], portfolio_risks[index]

    # Get best portfolio based on user risk tolerance
    best_weights, best_return, best_risk = get_best_portfolio(risk_tolerance)

    return best_return, best_risk, best_weights

# Example usage:
# user_risk_tolerance = 'moderate'  # Replace with user input: 'high', 'moderate', or 'low'
# best_return, best_risk, best_weights = get_best_return_and_risk(user_risk_tolerance)
# print(f"Best Return: {best_return}, Best Risk: {best_risk}, Best Weights: {best_weights}")

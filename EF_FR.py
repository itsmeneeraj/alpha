import numpy as np
import pandas as pd
import cvxpy as cp
import matplotlib.pyplot as plt
import yfinance as yf

def get_best_return_and_risk(risk_tolerance):
    # Load stock symbols
    stock_symbols_df = pd.read_excel('indian_stock_symbols.xlsx')
    stock_symbols_df['Symbol'] = stock_symbols_df['Symbol'].astype(str).str.strip()
    stock_symbols = stock_symbols_df['Symbol'].tolist()

    # Add '.NS' suffix to each valid stock symbol
    stock_NS = [stock + '.NS' for stock in stock_symbols if isinstance(stock, str) and stock and stock.lower() != 'nan']

    # Fetch data for all stock symbols
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

    data = pd.DataFrame(all_data)

    # Calculate monthly returns
    returns = data.pct_change().dropna()

    # Calculate annualized mean returns and covariance matrix
    mean_returns = returns.mean() * 12
    cov_matrix = returns.cov() * 12

    # Function to optimize portfolio for a given target return
    def optimize_portfolio(target_return, mean_returns, cov_matrix):
        N = len(mean_returns)
        w = cp.Variable(N)
        objective = cp.Minimize(cp.quad_form(w, cov_matrix))
        constraints = [
            cp.sum(w) == 1,  # Full investment constraint
            w @ mean_returns >= target_return,  # Target return constraint
            w >= 0  # No short selling constraint
        ]
        problem = cp.Problem(objective, constraints)
        problem.solve()
        return w.value

    # Calculate the efficient frontier
    target_returns = np.linspace(mean_returns.min(), mean_returns.max(), 50)
    portfolio_risks = []
    portfolio_returns = []
    portfolio_weights = []

    for tr in target_returns:
        optimal_weights = optimize_portfolio(tr, mean_returns, cov_matrix)
        portfolio_risks.append(np.sqrt(optimal_weights @ cov_matrix @ optimal_weights))
        portfolio_returns.append(optimal_weights @ mean_returns)
        portfolio_weights.append(optimal_weights)

    # Plot the efficient frontier
    plt.figure(figsize=(10, 6))
    plt.plot(portfolio_risks, portfolio_returns, 'o-')
    plt.xlabel('Risk (Standard Deviation)')
    plt.ylabel('Return')
    plt.title('Efficient Frontier')
    plt.show()

    # Function to provide the best portfolio based on user risk tolerance
    def get_best_portfolio(risk_tolerance):
        if risk_tolerance == 'high':
            index = np.argmax(portfolio_returns)
        elif risk_tolerance == 'moderate':
            index = np.argmin(np.abs(np.array(portfolio_returns) - np.mean(portfolio_returns)))
        elif risk_tolerance == 'low':
            index = np.argmin(portfolio_risks)
        else:
            raise ValueError("Risk tolerance must be 'high', 'moderate', or 'low'.")
        
        return portfolio_weights[index], portfolio_returns[index], portfolio_risks[index]

    # Get best portfolio based on user risk tolerance
    best_weights, best_return, best_risk = get_best_portfolio(risk_tolerance)

    return best_return, best_risk

# Example usage:
# user_risk_tolerance = 'moderate'  # Replace with user input: 'high', 'moderate', or 'low'
# best_return, best_risk = get_best_return_and_risk(user_risk_tolerance)
# print(f"Best Return: {best_return}, Best Risk: {best_risk}")

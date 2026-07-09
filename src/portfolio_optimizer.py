import pandas as pd
import numpy as np
from scipy.optimize import minimize
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def optimize_portfolio(melted_df, risk_free_rate=0.04, num_simulations=2000):
    """
    Applies Modern Portfolio Theory (MPT) to calculate optimal asset allocations
    and simulate portfolios along the Efficient Frontier.
    
    Parameters:
    - melted_df (pd.DataFrame): Input DataFrame with columns [Date, Ticker, Close, Daily_Return]
    - risk_free_rate (float): Annual risk-free rate of return (default: 4%)
    - num_simulations (int): Number of random portfolios to simulate for the Efficient Frontier.
    
    Returns:
    - tuple: (metrics_df, frontier_df)
      - metrics_df: Data containing weights and portfolio metrics for Max Sharpe, Min Volatility, and Individual Assets.
      - frontier_df: Simulated portfolios (Return, Volatility, Sharpe) for scatter plot.
    """
    logging.info("Pivot stock data for return and covariance calculations...")
    
    # Reshape from long to wide format (daily returns)
    pivot_df = melted_df.pivot(index='Date', columns='Ticker', values='Daily_Return')
    
    # Check for empty columns or missing tickers
    tickers = pivot_df.columns.tolist()
    num_assets = len(tickers)
    
    if num_assets < 2:
        raise ValueError("Portfolio optimization requires at least 2 tickers.")
        
    # Calculate annualized expected returns and covariance matrix
    # Standard: 252 trading days in a year
    daily_mean_returns = pivot_df.mean()
    cov_matrix = pivot_df.cov()
    
    annual_returns = daily_mean_returns * 252
    annual_cov = cov_matrix * 252
    
    logging.info(f"Annualized Asset Returns:\n{annual_returns}")
    
    # Helper to calculate portfolio performance
    def portfolio_perf(weights):
        p_return = np.sum(annual_returns * weights)
        p_volatility = np.sqrt(np.dot(weights.T, np.dot(annual_cov, weights)))
        p_sharpe = (p_return - risk_free_rate) / p_volatility if p_volatility > 0 else 0
        return p_return, p_volatility, p_sharpe
        
    # 1. Max Sharpe Ratio Optimization
    def neg_sharpe(weights):
        _, _, sharpe = portfolio_perf(weights)
        return -sharpe
        
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    bounds = tuple((0.0, 1.0) for _ in range(num_assets))
    init_weights = num_assets * [1.0 / num_assets]
    
    logging.info("Optimizing for Maximum Sharpe Ratio...")
    opt_sharpe = minimize(neg_sharpe, init_weights, method='SLSQP', bounds=bounds, constraints=constraints)
    max_sharpe_weights = opt_sharpe.x
    max_sharpe_ret, max_sharpe_vol, max_sharpe_ratio = portfolio_perf(max_sharpe_weights)
    
    # 2. Min Volatility Optimization
    def portfolio_vol(weights):
        _, vol, _ = portfolio_perf(weights)
        return vol
        
    logging.info("Optimizing for Minimum Volatility...")
    opt_vol = minimize(portfolio_vol, init_weights, method='SLSQP', bounds=bounds, constraints=constraints)
    min_vol_weights = opt_vol.x
    min_vol_ret, min_vol_vol, min_vol_ratio = portfolio_perf(min_vol_weights)
    
    # Prepare metrics dataframe
    metrics_records = []
    
    # Add Max Sharpe weights
    for i, ticker in enumerate(tickers):
        metrics_records.append({
            'Portfolio_Type': 'Max Sharpe',
            'Ticker': ticker,
            'Weight': max_sharpe_weights[i],
            'Portfolio_Return': max_sharpe_ret,
            'Portfolio_Volatility': max_sharpe_vol,
            'Portfolio_Sharpe': max_sharpe_ratio
        })
        
    # Add Min Volatility weights
    for i, ticker in enumerate(tickers):
        metrics_records.append({
            'Portfolio_Type': 'Min Volatility',
            'Ticker': ticker,
            'Weight': min_vol_weights[i],
            'Portfolio_Return': min_vol_ret,
            'Portfolio_Volatility': min_vol_vol,
            'Portfolio_Sharpe': min_vol_ratio
        })
        
    # Add Individual Assets as 100% weights
    for i, ticker in enumerate(tickers):
        # Create weights where index i is 1, rest are 0
        asset_weights = np.zeros(num_assets)
        asset_weights[i] = 1.0
        asset_ret, asset_vol, asset_sharpe = portfolio_perf(asset_weights)
        
        # Add weights for this specific asset's sub-portfolio
        # (This helps Power BI visualize single-asset benchmarks)
        for j, inner_ticker in enumerate(tickers):
            metrics_records.append({
                'Portfolio_Type': f'Asset: {ticker}',
                'Ticker': inner_ticker,
                'Weight': 1.0 if inner_ticker == ticker else 0.0,
                'Portfolio_Return': asset_ret,
                'Portfolio_Volatility': asset_vol,
                'Portfolio_Sharpe': asset_sharpe
            })
            
    metrics_df = pd.DataFrame(metrics_records)
    
    # 3. Simulate portfolios for the Efficient Frontier
    logging.info(f"Simulating {num_simulations} random portfolios...")
    sim_returns = []
    sim_volatilities = []
    sim_sharpe_ratios = []
    
    # Seed for reproducibility
    np.random.seed(42)
    
    for _ in range(num_simulations):
        # Generate random weights
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        
        p_ret, p_vol, p_sharpe = portfolio_perf(weights)
        
        sim_returns.append(p_ret)
        sim_volatilities.append(p_vol)
        sim_sharpe_ratios.append(p_sharpe)
        
    frontier_df = pd.DataFrame({
        'Simulated_Portfolio_ID': np.arange(1, num_simulations + 1),
        'Volatility': sim_volatilities,
        'Expected_Return': sim_returns,
        'Sharpe_Ratio': sim_sharpe_ratios
    })
    
    logging.info("Optimization and simulations complete.")
    return metrics_df, frontier_df

if __name__ == "__main__":
    # Test run with mock data
    np.random.seed(0)
    dates = pd.date_range(start="2024-01-01", periods=100)
    tickers = ["AAPL", "MSFT", "GOOGL"]
    
    records = []
    for ticker in tickers:
        base_price = 150 + np.random.randn() * 10
        # Generate daily returns
        returns = np.random.normal(loc=0.0005, scale=0.015, size=100)
        prices = base_price * (1 + returns).cumprod()
        
        for date, price, ret in zip(dates, prices, returns):
            records.append({
                'Date': date,
                'Ticker': ticker,
                'Close': price,
                'Daily_Return': ret
            })
            
    df = pd.DataFrame(records)
    metrics, frontier = optimize_portfolio(df)
    print("Metrics preview:")
    print(metrics.head(10))
    print("\nFrontier preview:")
    print(frontier.head(5))

import yfinance as yf
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_stock_data(tickers, start_date, end_date):
    """
    Fetches historical stock adjusted close prices for a list of tickers.
    
    Parameters:
    - tickers (list): List of stock ticker symbols.
    - start_date (str): Start date in 'YYYY-MM-DD' format.
    - end_date (str): End date in 'YYYY-MM-DD' format.
    
    Returns:
    - pd.DataFrame: Tabular DataFrame with columns [Date, Ticker, Close, Daily_Return]
    """
    logging.info(f"Fetching historical data for tickers: {tickers} from {start_date} to {end_date}")
    
    # yfinance download
    try:
        data = yf.download(tickers, start=start_date, end=end_date, group_by='column')
    except Exception as e:
        logging.error(f"Error fetching data from yfinance: {e}")
        raise e
        
    if data.empty:
        raise ValueError("No data retrieved from yfinance. Please check the tickers and dates.")
    
    # Handle Adj Close vs Close. We prefer Adj Close if available, otherwise Close.
    close_col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
    
    # yfinance output structure depends on whether single or multiple tickers are passed
    if len(tickers) == 1:
        ticker = tickers[0]
        # For a single ticker, yfinance returns columns like Open, High, Low, Close, Adj Close, Volume
        prices_df = pd.DataFrame(data[close_col])
        prices_df.columns = [ticker]
    else:
        # For multiple tickers, yfinance returns a MultiIndex column DataFrame e.g. (Adj Close, AAPL)
        prices_df = data[close_col]
    
    # Reset index to get 'Date' as a column
    prices_df = prices_df.reset_index()
    
    # Melt the DataFrame from wide to long format
    # Wide: Date | AAPL | MSFT | TSLA
    # Long: Date | Ticker | Close
    melted_df = prices_df.melt(id_vars=['Date'], var_name='Ticker', value_name='Close')
    
    # Sort by Ticker and Date
    melted_df = melted_df.sort_values(by=['Ticker', 'Date']).reset_index(drop=True)
    
    # Calculate daily returns
    logging.info("Calculating daily returns...")
    melted_df['Daily_Return'] = melted_df.groupby('Ticker')['Close'].pct_change()
    
    # Fill first-day NaN values with 0
    melted_df['Daily_Return'] = melted_df['Daily_Return'].fillna(0)
    
    logging.info(f"Successfully fetched and processed {len(melted_df)} records.")
    return melted_df

if __name__ == "__main__":
    # Quick test execution
    tickers = ["AAPL", "MSFT", "GOOGL"]
    df = fetch_stock_data(tickers, "2024-01-01", "2024-06-01")
    print(df.head(10))
    print(df.tail(10))

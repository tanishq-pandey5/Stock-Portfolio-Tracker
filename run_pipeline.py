import os
import sys
from datetime import datetime, timedelta
import logging

# Ensure root directory is in the Python search path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data_fetcher import fetch_stock_data
from src.sentiment_analyzer import analyze_sentiment
from src.portfolio_optimizer import optimize_portfolio

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    # 1. Define configuration parameters
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "JPM", "V", "DIS"]
    
    # Calculate start and end dates (last 2 years of historical data)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=2 * 365)).strftime('%Y-%m-%d')
    
    risk_free_rate = 0.04
    num_simulations = 2000
    
    # Output directory
    output_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_dir, exist_ok=True)
    
    logging.info("Starting Stock Portfolio Optimizer & Sentiment Tracker Pipeline...")
    logging.info(f"Configuration:\n- Tickers: {tickers}\n- Period: {start_date} to {end_date}\n- Risk-Free Rate: {risk_free_rate}\n- Simulations: {num_simulations}")
    
    # 2. Fetch stock price data
    try:
        logging.info("==========================================")
        logging.info("STEP 1: Fetching historical stock prices...")
        logging.info("==========================================")
        stock_df = fetch_stock_data(tickers, start_date, end_date)
        stock_csv_path = os.path.join(output_dir, "stock_prices.csv")
        stock_df.to_csv(stock_csv_path, index=False)
        logging.info(f"Saved stock prices to {stock_csv_path}")
    except Exception as e:
        logging.error(f"Failed to fetch stock prices: {e}")
        sys.exit(1)
        
    # 3. Analyze news sentiment
    try:
        logging.info("==========================================")
        logging.info("STEP 2: Fetching and analyzing news sentiment...")
        logging.info("==========================================")
        sentiment_df = analyze_sentiment(tickers)
        sentiment_csv_path = os.path.join(output_dir, "news_sentiment.csv")
        sentiment_df.to_csv(sentiment_csv_path, index=False)
        logging.info(f"Saved news sentiment data to {sentiment_csv_path}")
    except Exception as e:
        logging.error(f"Failed to run sentiment analysis: {e}")
        # Continue the pipeline even if sentiment fails, as we can still optimize the portfolio
        sentiment_df = None
        
    # 4. Optimize portfolio and run simulations
    try:
        logging.info("==========================================")
        logging.info("STEP 3: Optimizing portfolio weights...")
        logging.info("==========================================")
        metrics_df, frontier_df = optimize_portfolio(stock_df, risk_free_rate=risk_free_rate, num_simulations=num_simulations)
        
        metrics_csv_path = os.path.join(output_dir, "portfolio_metrics.csv")
        metrics_df.to_csv(metrics_csv_path, index=False)
        logging.info(f"Saved portfolio metrics to {metrics_csv_path}")
        
        frontier_csv_path = os.path.join(output_dir, "efficient_frontier.csv")
        frontier_df.to_csv(frontier_csv_path, index=False)
        logging.info(f"Saved efficient frontier simulations to {frontier_csv_path}")
    except Exception as e:
        logging.error(f"Failed to optimize portfolio: {e}")
        sys.exit(1)
        
    logging.info("==========================================")
    logging.info("Pipeline executed successfully!")
    logging.info("All outputs generated in the 'data/' folder.")
    logging.info("==========================================")

if __name__ == "__main__":
    main()

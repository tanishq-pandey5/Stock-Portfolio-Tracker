import feedparser
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ensure NLTK VADER lexicon is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    logging.info("NLTK VADER lexicon not found. Downloading...")
    nltk.download('vader_lexicon', quiet=True)

def analyze_sentiment(tickers):
    """
    Fetches news headlines for a list of tickers from Yahoo Finance RSS feeds
    and performs VADER sentiment analysis on each headline.
    
    Parameters:
    - tickers (list): List of stock ticker symbols.
    
    Returns:
    - pd.DataFrame: DataFrame containing columns [Ticker, Date, Headline, Link, Sentiment_Score, Sentiment_Label]
    """
    logging.info("Initializing VADER Sentiment Analyzer...")
    sia = SentimentIntensityAnalyzer()
    
    all_news = []
    
    for ticker in tickers:
        logging.info(f"Fetching RSS feed for ticker: {ticker}")
        rss_url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
        
        try:
            feed = feedparser.parse(rss_url)
        except Exception as e:
            logging.error(f"Error reading RSS feed for {ticker}: {e}")
            continue
            
        entries = feed.entries
        logging.info(f"Retrieved {len(entries)} articles for {ticker}")
        
        for entry in entries:
            headline = entry.get('title', '')
            link = entry.get('link', '')
            
            # Parse publication date
            published_str = entry.get('published', '')
            # Try parsing typical RSS date format
            published_dt = None
            if published_str:
                try:
                    # RSS dates are often like: "Thu, 09 Jul 2026 06:12:00 +0000" or similar
                    # feedparser's published_parsed is more reliable
                    struct_time = entry.get('published_parsed')
                    if struct_time:
                        published_dt = datetime.fromtimestamp(time.mktime(struct_time))
                except Exception:
                    pass
            
            # Fallback if parsing fails
            if not published_dt:
                published_dt = datetime.now()
            
            # Run VADER sentiment analysis on headline
            scores = sia.polarity_scores(headline)
            compound_score = scores['compound']
            
            # Categorize sentiment label
            if compound_score >= 0.05:
                label = 'Positive'
            elif compound_score <= -0.05:
                label = 'Negative'
            else:
                label = 'Neutral'
                
            all_news.append({
                'Ticker': ticker,
                'Date': published_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'Headline': headline,
                'Link': link,
                'Sentiment_Score': compound_score,
                'Sentiment_Label': label
            })
            
    # If no news collected, return an empty DataFrame with the correct schema
    if not all_news:
        logging.warning("No news headlines were retrieved for any ticker.")
        return pd.DataFrame(columns=['Ticker', 'Date', 'Headline', 'Link', 'Sentiment_Score', 'Sentiment_Label'])
        
    news_df = pd.DataFrame(all_news)
    logging.info(f"Successfully processed sentiment for {len(news_df)} articles.")
    return news_df

if __name__ == "__main__":
    # Test run
    df = analyze_sentiment(["AAPL", "TSLA"])
    print(df.head(10))

# Stock Portfolio Optimizer & Sentiment Tracker

A dynamic, data-driven application that blends Modern Portfolio Theory (MPT) and News Sentiment Analysis using a Python data pipeline and Power BI interactive dashboards.

## System Architecture

```mermaid
graph TD
    A[Yahoo Finance API] -->|Historical Prices| B[Python Pipeline]
    C[Yahoo Finance RSS] -->|News Headlines| B
    B -->|data_fetcher.py| D[(stock_prices.csv)]
    B -->|sentiment_analyzer.py| E[(news_sentiment.csv)]
    B -->|portfolio_optimizer.py| F[(portfolio_metrics.csv)]
    B -->|portfolio_optimizer.py| G[(efficient_frontier.csv)]
    D & E & F & G -->|Import CSVs| H[Power BI Dashboard]
```

---

## Getting Started

### 1. Prerequisites
Make sure you have Python 3.8+ installed on your system.

### 2. Installation
Install the necessary python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Running the Pipeline
Run the orchestrator script to fetch the latest stock data, news sentiment, and generate portfolio optimization configurations:
```bash
python run_pipeline.py
```
This script dynamically calculates dates for the past 2 years and outputs four files into the `data/` directory:
- `data/stock_prices.csv`: Adjusted closing prices and daily return rates.
- `data/news_sentiment.csv`: News headlines, links, publication times, and VADER sentiment scores.
- `data/portfolio_metrics.csv`: Optimal asset weights and portfolio stats for Max Sharpe, Min Volatility, and Individual Benchmarks.
- `data/efficient_frontier.csv`: Volatility, Return, and Sharpe ratios for 2,000 simulated random portfolios.

---

## Power BI Dashboard Implementation Guide

Follow these steps to build an interactive, premium-grade dashboard.

### STEP 1: Import the Data
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Select and load each of the four CSV files from the `data/` folder:
   - `efficient_frontier.csv`
   - `news_sentiment.csv`
   - `portfolio_metrics.csv`
   - `stock_prices.csv`

### STEP 2: Configure the Data Model (Relationships)
Go to the **Model View** in Power BI and configure the relationships:
1. Connect `portfolio_metrics` to `stock_prices`:
   * **Relationship:** `portfolio_metrics(Ticker)` to `stock_prices(Ticker)`
   * **Cardinality:** Many-to-Many (or One-to-Many if you build a unique Tickers master table).
2. Connect `news_sentiment` to `stock_prices`:
   * **Relationship:** `news_sentiment(Ticker)` to `stock_prices(Ticker)`
3. Keep `efficient_frontier` standalone as it represents simulated macro portfolios.

---

### STEP 3: Designing the Visual Pages

#### Page 1: Portfolio Optimization & Efficient Frontier
Make this page look premium (dark background with vibrant gradient theme recommended).
* **Efficient Frontier Scatter Chart:**
  * **Visual Type:** Scatter Chart
  * **X-Axis:** `Volatility` (Don't summarize)
  * **Y-Axis:** `Expected_Return` (Don't summarize)
  * **Values (Details):** `Simulated_Portfolio_ID`
  * **Legend/Color By:** `Sharpe_Ratio`
  * *Insight:* This plots the classic "Efficient Frontier" curve where the top boundary represents the best return for a given risk level.
* **Optimal Allocation Donut Chart:**
  * **Visual Type:** Donut Chart
  * **Legend:** `Ticker`
  * **Values:** `Weight`
  * **Slicer:** Add a Slicer for `Portfolio_Type` (e.g. filter by "Max Sharpe" or "Min Volatility" to see weights change dynamically).
* **Portfolio Metrics Cards:**
  * Use card visuals to show:
    * `Portfolio_Return` (Formula: `AVERAGE(Portfolio_Return)`)
    * `Portfolio_Volatility` (Formula: `AVERAGE(Portfolio_Volatility)`)
    * `Portfolio_Sharpe` (Formula: `AVERAGE(Portfolio_Sharpe)`)

#### Page 2: News Sentiment Tracker
Analyze recent events and news indicators affecting stock performance.
* **Market Sentiment Gauge:**
  * Create a DAX measure:
    ```dax
    Average Sentiment = AVERAGE(news_sentiment[Sentiment_Score])
    ```
  * Add a **Gauge Visual** using `Average Sentiment` (Target value: `1.0`, Minimum: `-1.0`, Maximum: `1.0`).
* **Sentiment Distribution Bar Chart:**
  * **Visual Type:** Stacked Bar Chart
  * **Y-Axis:** `Ticker`
  * **X-Axis:** Count of `Headline`
  * **Legend:** `Sentiment_Label` (Positive = Green, Neutral = Gray, Negative = Red)
* **Headline News Table:**
  * **Columns:** `Date`, `Ticker`, `Headline`, `Sentiment_Score`, `Link`
  * *Pro Tip:* Go to the `Link` column properties and set **Data Category** to **Web URL** to make the headlines clickable.

#### Page 3: Asset Comparison & Trends
Overlay sentiment trends with price trends.
* **Return vs. Volatility Scatter Chart:**
  * **Visual Type:** Scatter Chart (for individual assets)
  * **Filter:** Set filter where `Portfolio_Type` starts with `Asset:`
  * **X-Axis:** `Portfolio_Volatility`
  * **Y-Axis:** `Portfolio_Return`
  * **Values (Details):** `Portfolio_Type` (Individual assets)
* **Price History Line Chart:**
  * **Visual Type:** Line Chart
  * **X-Axis:** `Date`
  * **Y-Axis:** `Close`
  * **Legend:** `Ticker`

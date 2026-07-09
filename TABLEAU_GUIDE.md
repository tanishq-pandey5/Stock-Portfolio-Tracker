# Tableau Dashboard Implementation Guide

Yes, Tableau runs natively on macOS and is an excellent tool for visualizing these datasets. Since our Python pipeline exports clean CSV files, you can build a premium, interactive dashboard in Tableau Desktop or Tableau Public.

---

## STEP 1: Connect Your Data Sources

1. Open **Tableau**.
2. Under **Connect**, click **Text File** and select `stock_prices.csv` from `/Users/tanishqpandey/Documents/Projects/Stock Portfolio Tracker/data/`.
3. In the canvas area, drag `portfolio_metrics.csv` and `news_sentiment.csv` to connect them to `stock_prices.csv`.
   * Tableau will automatically create logical relationships (represented by "noodles") linking them via the **`Ticker`** field.
4. Click **Add** next to Connections (or click the Tableau icon to go to Sheet 1) and create a **New Data Source** pointing to `efficient_frontier.csv` as a standalone table.

---

## STEP 2: Build the Sheets (Visualizations)

### Sheet 1: Efficient Frontier (Scatter Plot)
* **Data Source:** Select `efficient_frontier`.
* **Setup:**
  1. Drag `Volatility` to **Columns**.
  2. Drag `Expected Return` to **Rows**.
  3. *Note: If Tableau aggregates it into a single dot, go to the top menu: **Analysis** -> uncheck **Aggregate Measures**.*
  4. Drag `Simulated Portfolio ID` to **Detail** on the Marks card.
  5. Drag `Sharpe Ratio` to **Color** on the Marks card.
  6. Click **Color** ➔ **Edit Colors** ➔ Choose a diverging gradient (e.g., *Red-Blue Diverging* or *Orange-Blue Diverging*).

### Sheet 2: Optimal Asset Allocations (Donut/Bar Chart)
* **Data Source:** Select `portfolio_metrics`.
* **Setup:**
  1. Drag `Ticker` to **Columns** (or **Color** if building a Pie Chart).
  2. Drag `Weight` to **Rows** (set aggregation to `SUM`).
  3. Drag `Portfolio Type` to the **Filters** card. 
     * Right-click `Portfolio Type` in filters and select **Show Filter**.
     * Change the filter type to **Single Value (List)** or **Single Value (Dropdown)**.
  4. *Interaction:* Toggling the filter between `Max Sharpe` and `Min Volatility` will show how asset weights shift.

### Sheet 3: News Sentiment Distribution
* **Data Source:** Select `news_sentiment`.
* **Setup:**
  1. Drag `Ticker` to **Rows**.
  2. Drag `Sentiment Label` to **Columns**.
  3. Drag `Headline` to **Text** or **Columns** (change measure to **Count**).
  4. Drag `Sentiment Label` to **Color**.
     * Map colors: `Positive` = Green, `Neutral` = Gray, `Negative` = Red.

### Sheet 4: Live News Table & Clickable Links
* **Data Source:** Select `news_sentiment`.
* **Setup:**
  1. Drag `Date`, `Ticker`, `Headline`, `Sentiment Score`, and `Link` to **Rows**.
  2. To make the URL clickable:
     * In your final dashboard, go to the top menu: **Dashboard** ➔ **Actions** ➔ **Add Action** ➔ **Go to URL**.
     * Set the source sheet to Sheet 4, run action on **Select**, and insert the `<Link>` field as the URL.

---

## STEP 3: Create the Dashboard

1. Click the **New Dashboard** tab.
2. Set the Size to **Automatic** or a custom desktop layout (e.g., `1200 x 800`).
3. Drag **Sheet 1 (Efficient Frontier)** and **Sheet 2 (Asset Allocations)** side-by-side at the top.
4. Drag **Sheet 3 (Sentiment)** and **Sheet 4 (News Table)** below them.
5. Add text cards showing the Overall Portfolio return/risk for the selected portfolio type.

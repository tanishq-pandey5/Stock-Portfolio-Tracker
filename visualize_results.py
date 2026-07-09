import os
import pandas as pd
import matplotlib

# Use interactive backend on your Mac, fall back to headless 'Agg' in background environments
if os.environ.get('DISPLAY') is None and os.environ.get('TERM_PROGRAM') is None:
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns

# Set style for professional look
sns.set_theme(style="whitegrid")

def plot_dashboard():
    # Define paths
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    frontier_path = os.path.join(data_dir, "efficient_frontier.csv")
    metrics_path = os.path.join(data_dir, "portfolio_metrics.csv")
    sentiment_path = os.path.join(data_dir, "news_sentiment.csv")
    
    # Check if files exist
    if not (os.path.exists(frontier_path) and os.path.exists(metrics_path) and os.path.exists(sentiment_path)):
        print("Data files not found. Please run 'python run_pipeline.py' first.")
        return
        
    # Load data
    df_frontier = pd.read_csv(frontier_path)
    df_metrics = pd.read_csv(metrics_path)
    df_sentiment = pd.read_csv(sentiment_path)
    
    # Create a figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle("Stock Portfolio Analytics Dashboard (Python Preview)", fontsize=18, fontweight='bold', y=1.02)
    
    # ----------------------------------------------------
    # Subplot 1: Efficient Frontier
    # ----------------------------------------------------
    ax1 = axes[0]
    scatter = ax1.scatter(
        df_frontier['Volatility'], 
        df_frontier['Expected_Return'], 
        c=df_frontier['Sharpe_Ratio'], 
        cmap='RdYlBu', 
        alpha=0.5, 
        edgecolors='none'
    )
    fig.colorbar(scatter, ax=ax1, label='Sharpe Ratio')
    
    # Highlight Max Sharpe & Min Volatility portfolios on the frontier
    df_max_sharpe = df_metrics[df_metrics['Portfolio_Type'] == 'Max Sharpe'].iloc[0]
    df_min_vol = df_metrics[df_metrics['Portfolio_Type'] == 'Min Volatility'].iloc[0]
    
    ax1.scatter(df_max_sharpe['Portfolio_Volatility'], df_max_sharpe['Portfolio_Return'], color='red', marker='*', s=200, label='Max Sharpe')
    ax1.scatter(df_min_vol['Portfolio_Volatility'], df_min_vol['Portfolio_Return'], color='black', marker='X', s=150, label='Min Volatility')
    
    ax1.set_title("Efficient Frontier Curve", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Annualized Volatility (Risk)", fontsize=12)
    ax1.set_ylabel("Annualized Expected Return", fontsize=12)
    ax1.legend(loc='best')
    
    # ----------------------------------------------------
    # Subplot 2: Portfolio Allocation Weights
    # ----------------------------------------------------
    ax2 = axes[1]
    # Filter to show only Max Sharpe and Min Volatility allocations
    df_weights = df_metrics[df_metrics['Portfolio_Type'].isin(['Max Sharpe', 'Min Volatility'])]
    
    sns.barplot(
        data=df_weights, 
        x='Ticker', 
        y='Weight', 
        hue='Portfolio_Type', 
        ax=ax2, 
        palette={'Max Sharpe': '#1f77b4', 'Min Volatility': '#aec7e8'}
    )
    ax2.set_title("Optimal Portfolio Allocations", fontsize=14, fontweight='bold')
    ax2.set_xlabel("Ticker", fontsize=12)
    ax2.set_ylabel("Allocation Weight (1.0 = 100%)", fontsize=12)
    ax2.set_ylim(0, 1.0)
    ax2.legend(title='Portfolio Type')
    
    # ----------------------------------------------------
    # Subplot 3: News Sentiment Distribution
    # ----------------------------------------------------
    ax3 = axes[2]
    # Calculate count of sentiment per ticker
    df_sent_count = df_sentiment.groupby(['Ticker', 'Sentiment_Label']).size().reset_index(name='Count')
    
    sns.barplot(
        data=df_sent_count, 
        x='Ticker', 
        y='Count', 
        hue='Sentiment_Label', 
        ax=ax3,
        palette={'Positive': '#2ca02c', 'Neutral': '#7f7f7f', 'Negative': '#d62728'}
    )
    ax3.set_title("Ticker News Sentiment Profile", fontsize=14, fontweight='bold')
    ax3.set_xlabel("Ticker", fontsize=12)
    ax3.set_ylabel("Article Count", fontsize=12)
    ax3.legend(title='Sentiment')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save dashboard preview as image
    preview_img = os.path.join(data_dir, "python_dashboard_preview.png")
    plt.savefig(preview_img, dpi=300, bbox_inches='tight')
    print(f"Dashboard preview saved as image: {preview_img}")
    
    # Show plot
    plt.show()

if __name__ == "__main__":
    plot_dashboard()

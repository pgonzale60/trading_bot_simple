import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime


def plot_simple_results(data, strategy_results=None):
    """
    Create a simple price chart with moving averages.

    Args:
        data: Backtrader data feed or pandas DataFrame
        strategy_results: Optional strategy results for buy/sell signals
    """
    # If data is from yfinance (pandas DataFrame)
    if hasattr(data, 'index'):
        df = data
    else:
        # Convert backtrader data to DataFrame for plotting
        dates = []
        prices = []
        for i in range(len(data)):
            dates.append(data.datetime.date(i))
            prices.append(data.close[i])

        df = pd.DataFrame({
            'Close': prices,
            'Date': dates
        }).set_index('Date')

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot closing prices
    ax.plot(df.index, df['Close'], label='Close Price', linewidth=1, color='black')

    # Calculate and plot moving averages
    sma_10 = df['Close'].rolling(window=10).mean()
    sma_30 = df['Close'].rolling(window=30).mean()

    ax.plot(df.index, sma_10, label='10-day SMA', linewidth=1, color='blue', alpha=0.7)
    ax.plot(df.index, sma_30, label='30-day SMA', linewidth=1, color='red', alpha=0.7)

    # Format the plot
    ax.set_title('Trading Bot - SMA Crossover Strategy', fontsize=16)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Format dates on x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()


def print_performance_summary(initial_cash, final_value, num_trades=None):
    """
    Print a nicely formatted performance summary.
    """
    profit = final_value - initial_cash
    profit_pct = (profit / initial_cash) * 100

    print("\n" + "="*50)
    print("           PERFORMANCE SUMMARY")
    print("="*50)
    print(f"Initial Capital:     ${initial_cash:,.2f}")
    print(f"Final Value:         ${final_value:,.2f}")
    print(f"Total Profit/Loss:   ${profit:,.2f}")
    print(f"Return:              {profit_pct:.2f}%")

    if num_trades:
        print(f"Number of Trades:    {num_trades}")
        if num_trades > 0:
            print(f"Profit per Trade:    ${profit/num_trades:.2f}")

    print("="*50)

    # Performance interpretation
    if profit_pct > 10:
        print("🎉 Great performance!")
    elif profit_pct > 0:
        print("✅ Profitable strategy")
    elif profit_pct > -5:
        print("⚠️  Small loss - could be improved")
    else:
        print("❌ Poor performance - strategy needs work")

    print("="*50)
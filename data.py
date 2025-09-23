import yfinance as yf
import backtrader as bt
from datetime import datetime, timedelta


def get_stock_data(symbol='AAPL', start_date=None, end_date=None):
    """
    Fetch stock data from Yahoo Finance and convert to Backtrader format.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
        start_date: Start date as string 'YYYY-MM-DD' or None for 2 years ago
        end_date: End date as string 'YYYY-MM-DD' or None for today

    Returns:
        Backtrader data feed
    """
    # Set default dates if not provided
    if end_date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    if start_date is None:
        start_date = end_date - timedelta(days=730)  # 2 years ago
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')

    # Download data from Yahoo Finance
    print(f"Downloading {symbol} data from {start_date.date()} to {end_date.date()}...")

    stock = yf.Ticker(symbol)
    df = stock.history(start=start_date, end=end_date)

    if df.empty:
        raise ValueError(f"No data found for symbol {symbol}")

    print(f"Downloaded {len(df)} days of data")

    # Convert to Backtrader data feed
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # Use index as datetime
        open='Open',
        high='High',
        low='Low',
        close='Close',
        volume='Volume',
        openinterest=None
    )

    return data
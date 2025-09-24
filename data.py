import yfinance as yf
import backtrader as bt
import os
import json
import pandas as pd
from datetime import datetime, timedelta


def get_cache_filename(symbol, start_date, end_date, cache_dir='data_cache'):
    """Generate cache filename for stock data."""
    os.makedirs(cache_dir, exist_ok=True)
    start_str = start_date.strftime('%Y%m%d')
    end_str = end_date.strftime('%Y%m%d')
    return os.path.join(cache_dir, f"{symbol}_{start_str}_{end_str}.json")


def load_cached_data(cache_file):
    """Load cached stock data from JSON file."""
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
            # Convert back to DataFrame
            df = pd.DataFrame(data['data'])
            df.index = pd.to_datetime(data['index'])
            df.index.name = 'Date'
            # Ensure proper column names (yfinance format)
            if 'Open' not in df.columns and 'open' in df.columns:
                df = df.rename(columns=str.title)
            return df, data['cached_date']
    except Exception as e:
        print(f"⚠ Failed to load cache: {e}")
        return None, None


def save_data_to_cache(df, cache_file):
    """Save stock data to cache file."""
    try:
        # Convert DataFrame to JSON-serializable format
        data_dict = {}
        for col in df.columns:
            data_dict[col] = df[col].tolist()

        cache_data = {
            'data': data_dict,
            'index': df.index.strftime('%Y-%m-%d').tolist(),
            'cached_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        print(f"💾 Data cached to {cache_file}")
    except Exception as e:
        print(f"⚠ Failed to save cache: {e}")


def is_cache_valid(cache_file, max_age_hours=6):
    """Check if cached data is still valid (not too old)."""
    if not os.path.exists(cache_file):
        return False

    try:
        # Check file modification time
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        return file_age.total_seconds() < (max_age_hours * 3600)
    except:
        return False


def get_stock_data(symbol='AAPL', start_date=None, end_date=None, use_cache=True, max_cache_age_hours=6):
    """
    Fetch stock data from Yahoo Finance and convert to Backtrader format.
    Uses caching to avoid repeated downloads.

    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
        start_date: Start date as string 'YYYY-MM-DD' or None for 2 years ago
        end_date: End date as string 'YYYY-MM-DD' or None for today
        use_cache: Whether to use cached data if available
        max_cache_age_hours: Maximum age of cached data in hours

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

    cache_file = get_cache_filename(symbol, start_date, end_date)
    df = None

    # Try to load from cache first
    if use_cache and is_cache_valid(cache_file, max_cache_age_hours):
        df, cached_date = load_cached_data(cache_file)
        if df is not None:
            print(f"📂 Using cached {symbol} data ({len(df)} days, cached: {cached_date})")

    # Download fresh data if cache miss or disabled
    if df is None:
        print(f"⬇️ Downloading {symbol} data from {start_date.date()} to {end_date.date()}...")

        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date)

        if df.empty:
            raise ValueError(f"No data found for symbol {symbol}")

        print(f"Downloaded {len(df)} days of data")

        # Save to cache if enabled
        if use_cache:
            save_data_to_cache(df, cache_file)

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
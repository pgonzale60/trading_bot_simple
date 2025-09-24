#!/usr/bin/env python3
"""
Simple test script to verify the trading bot works.
"""

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")

    try:
        import yfinance as yf
        print("✓ yfinance")
    except ImportError as e:
        print(f"✗ yfinance: {e}")
        assert False, f"Failed to import yfinance: {e}"

    try:
        import backtrader as bt
        print("✓ backtrader")
    except ImportError as e:
        print(f"✗ backtrader: {e}")
        assert False, f"Failed to import backtrader: {e}"

    try:
        import pandas as pd
        print("✓ pandas")
    except ImportError as e:
        print(f"✗ pandas: {e}")
        assert False, f"Failed to import pandas: {e}"

    try:
        import matplotlib.pyplot as plt
        print("✓ matplotlib")
    except ImportError as e:
        print(f"✗ matplotlib: {e}")
        assert False, f"Failed to import matplotlib: {e}"


def test_data_fetch():
    """Test if we can fetch stock data."""
    print("\nTesting data fetch...")

    try:
        from data import get_stock_data
        # Test with a small date range
        data = get_stock_data('AAPL', '2024-01-01', '2024-01-31')
        print("✓ Data fetch successful")
        assert data is not None, "Data fetch returned None"
    except Exception as e:
        print(f"✗ Data fetch failed: {e}")
        assert False, f"Data fetch failed: {e}"


def test_strategy():
    """Test if strategy can be imported and initialized."""
    print("\nTesting strategy...")

    try:
        from strategies import SMAStrategy
        import backtrader as bt

        # Create a simple test
        cerebro = bt.Cerebro()
        cerebro.addstrategy(SMAStrategy)
        print("✓ Strategy setup successful")
    except Exception as e:
        print(f"✗ Strategy test failed: {e}")
        assert False, f"Strategy test failed: {e}"


def main():
    """Run all tests."""
    print("="*50)
    print("    TRADING BOT - SYSTEM CHECK")
    print("="*50)

    all_tests_passed = True

    # Run tests
    if not test_imports():
        all_tests_passed = False

    if not test_data_fetch():
        all_tests_passed = False

    if not test_strategy():
        all_tests_passed = False

    # Summary
    print("\n" + "="*50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Trading bot is ready to use.")
        print("\nTo run the bot:")
        print("python main.py")
        print("python main.py --symbol GOOGL --short 5 --long 20")
    else:
        print("❌ SOME TESTS FAILED. Check the environment setup.")
        print("\nTo fix issues:")
        print("micromamba activate trading-bot-simple")
        print("micromamba install -c conda-forge pandas matplotlib")
        print("pip install yfinance backtrader")

    print("="*50)


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Generate deterministic test fixtures for unit tests.
This script runs the trading strategies with fixed seeds and saves the results
as JSON fixtures that can be used for deterministic testing.
"""

import json
import numpy as np
import pandas as pd
import backtrader as bt
from strategies import SMAStrategy, RSIStrategy, MACDStrategy, BollingerBandsStrategy, BuyAndHoldStrategy
from optimizer import ParameterOptimizer
from multi_asset_tester import MultiAssetTester
import warnings
warnings.filterwarnings('ignore')


class MockData:
    """Create deterministic mock market data for testing."""

    @staticmethod
    def create_trending_data(days=100, start_price=100, trend=0.001, seed=42):
        """Create deterministic trending price data."""
        np.random.seed(seed)
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')

        # Create trending prices with deterministic pattern
        prices = []
        price = start_price
        for i in range(days):
            # Add trend and deterministic noise with more variation
            noise = np.sin(i * 0.1) * 0.02 + np.cos(i * 0.15) * 0.01  # More variation
            daily_change = trend + noise
            # Add some randomness based on seed to ensure sufficient variation
            if i % 7 == 0:  # Weekly variation
                daily_change += 0.005 * (1 if (i // 7) % 2 == 0 else -1)
            price = price * (1 + daily_change)
            prices.append(max(price, 1))

        # Create OHLCV data with more realistic spreads
        df = pd.DataFrame({
            'Open': [p * (0.99 + 0.02 * np.sin(i * 0.2)) for i, p in enumerate(prices)],
            'High': [p * (1.01 + 0.02 * abs(np.sin(i * 0.3))) for i, p in enumerate(prices)],
            'Low': [p * (0.98 - 0.01 * abs(np.cos(i * 0.25))) for i, p in enumerate(prices)],
            'Close': prices,
            'Volume': [500000 + int(i * 1000) + int(10000 * abs(np.sin(i * 0.1))) for i in range(days)]
        }, index=dates)

        return df

    @staticmethod
    def create_sideways_data(days=100, start_price=100, seed=42):
        """Create deterministic sideways/ranging price data."""
        np.random.seed(seed)
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')

        prices = []
        for i in range(days):
            # Deterministic oscillation around start price
            oscillation = np.sin(i * 0.2) * 0.15 + np.cos(i * 0.1) * 0.1
            price = start_price * (1 + oscillation)
            prices.append(max(price, 1))

        df = pd.DataFrame({
            'Open': [p * 0.995 for p in prices],
            'High': [p * 1.02 for p in prices],
            'Low': [p * 0.98 for p in prices],
            'Close': prices,
            'Volume': [300000 + int(i * 500) for i in range(days)]
        }, index=dates)

        return df


def run_strategy_test(strategy_class, data, **params):
    """Run a strategy test and return metrics."""
    np.random.seed(42)  # Ensure deterministic behavior

    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_class, **params)

    # Convert pandas DataFrame to Backtrader data feed
    bt_data = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(bt_data)

    cerebro.broker.setcash(10000)
    cerebro.broker.setcommission(commission=0.001)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    # Run backtest
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()

    # Extract trade analysis
    strategy_result = results[0]
    trades = strategy_result.analyzers.trades.get_analysis()
    drawdown = strategy_result.analyzers.drawdown.get_analysis()

    return {
        'initial_value': 10000,
        'final_value': final_value,
        'return_pct': ((final_value - 10000) / 10000) * 100,
        'total_trades': trades.get('total', {}).get('closed', 0) if isinstance(trades, dict) else (getattr(getattr(trades, 'total', None), 'closed', 0) if hasattr(trades, 'total') else 0),
        'max_drawdown': drawdown.get('max', {}).get('drawdown', 0) if isinstance(drawdown, dict) else (getattr(getattr(drawdown, 'max', None), 'drawdown', 0) if hasattr(drawdown, 'max') else 0),
    }


def generate_fixtures():
    """Generate all test fixtures."""
    np.random.seed(42)  # Global seed

    fixtures = {}

    # Create test data
    trending_data = MockData.create_trending_data(days=100, trend=0.001, seed=42)
    sideways_data = MockData.create_sideways_data(days=100, seed=42)

    print("Generating strategy test fixtures...")

    # Test SMA Strategy on trending data
    sma_trending = run_strategy_test(SMAStrategy, trending_data, short_period=10, long_period=30)
    fixtures['sma_trending'] = sma_trending
    print(f"SMA Trending: {sma_trending}")

    # Test SMA Strategy on sideways data
    sma_sideways = run_strategy_test(SMAStrategy, sideways_data, short_period=10, long_period=30)
    fixtures['sma_sideways'] = sma_sideways
    print(f"SMA Sideways: {sma_sideways}")

    # Test RSI Strategy
    rsi_sideways = run_strategy_test(RSIStrategy, sideways_data, rsi_period=14, rsi_low=30, rsi_high=70)
    fixtures['rsi_sideways'] = rsi_sideways
    print(f"RSI Sideways: {rsi_sideways}")

    # Test MACD Strategy
    macd_trending = run_strategy_test(MACDStrategy, trending_data, fast_ema=12, slow_ema=26, signal_ema=9)
    fixtures['macd_trending'] = macd_trending
    print(f"MACD Trending: {macd_trending}")

    # Test Bollinger Bands Strategy
    bb_trending = run_strategy_test(BollingerBandsStrategy, trending_data, period=20, devfactor=2.0)
    fixtures['bollinger_bands_trending'] = bb_trending
    print(f"Bollinger Bands: {bb_trending}")

    # Test Buy and Hold Strategy
    buy_hold_trending = run_strategy_test(BuyAndHoldStrategy, trending_data)
    fixtures['buy_and_hold_trending'] = buy_hold_trending
    print(f"Buy and Hold: {buy_hold_trending}")

    # Test parameter combinations for optimizer
    print("\\nGenerating optimizer fixtures...")

    # Mock parameter optimization results with deterministic values
    param_results = []
    combinations = [(5, 20), (5, 30), (10, 20), (10, 30)]
    base_returns = [15.0, 5.0, 5.0, 10.0]  # Predictable returns

    for i, (short, long) in enumerate(combinations):
        result = {
            'strategy': 'SMA',
            'short_period': short,
            'long_period': long,
            'return_pct': base_returns[i],
            'total_trades': 2 + i,
            'winning_trades': 1 + (i // 2),
            'losing_trades': max(0, i - 1),
            'win_rate': (1 + (i // 2)) / (2 + i) * 100 if (2 + i) > 0 else 0,
            'sharpe_ratio': 1.0 + (i * 0.1),
            'max_drawdown': 5.0 + i,
            'avg_trade': 100.0 + (i * 10)
        }
        param_results.append(result)

    fixtures['optimizer_sma_parameters'] = param_results
    print(f"Optimizer parameters: {len(param_results)} combinations")

    # Generate performance metrics fixture (252 days, SMA 5/20)
    print("\\nGenerating performance metrics fixture...")
    performance_data = MockData.create_trending_data(days=252, trend=0.0005, seed=42)
    sma_perf_result = run_strategy_test(
        SMAStrategy,
        performance_data,
        short_period=5,
        long_period=20
    )
    fixtures['sma_performance_252days'] = sma_perf_result
    print(f"SMA Performance (252d): {sma_perf_result}")

    # Add data validation fixtures
    fixtures['trending_data_stats'] = {
        'days': len(trending_data),
        'start_price': float(trending_data['Close'].iloc[0]),
        'end_price': float(trending_data['Close'].iloc[-1]),
        'min_price': float(trending_data['Close'].min()),
        'max_price': float(trending_data['Close'].max()),
        'mean_volume': int(trending_data['Volume'].mean())
    }

    fixtures['sideways_data_stats'] = {
        'days': len(sideways_data),
        'start_price': float(sideways_data['Close'].iloc[0]),
        'end_price': float(sideways_data['Close'].iloc[-1]),
        'min_price': float(sideways_data['Close'].min()),
        'max_price': float(sideways_data['Close'].max()),
        'mean_volume': int(sideways_data['Volume'].mean())
    }

    return fixtures


def main():
    """Generate and save fixtures."""
    print("Generating deterministic test fixtures...")

    fixtures = generate_fixtures()

    # Save to JSON file
    fixture_file = 'tests/fixtures.json'
    with open(fixture_file, 'w') as f:
        json.dump(fixtures, f, indent=2)

    print(f"\\n✓ Fixtures saved to {fixture_file}")
    print(f"✓ Generated {len(fixtures)} fixture sets")

    # Print summary
    print("\\nFixture summary:")
    for key, value in fixtures.items():
        if isinstance(value, dict) and 'return_pct' in value:
            print(f"  {key}: {value['return_pct']:.2f}% return, {value['total_trades']} trades")
        elif isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {type(value).__name__}")


if __name__ == '__main__':
    main()
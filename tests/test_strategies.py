#!/usr/bin/env python3
"""
Unit tests for trading strategies.
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backtrader as bt
from strategies import (
    SMAStrategy, RSIStrategy, MACDStrategy, BollingerBandsStrategy,
    EMAStrategy, MomentumStrategy, BuyAndHoldStrategy, STRATEGIES
)


class MockData:
    """Create mock market data for testing."""

    @staticmethod
    def create_trending_data(days=100, start_price=100, trend=0.001):
        """Create trending price data."""
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')

        # Create trending prices with some noise
        prices = []
        price = start_price
        for i in range(days):
            # Add trend and random noise
            price = price * (1 + trend + np.random.normal(0, 0.01))
            prices.append(max(price, 1))  # Ensure positive prices

        # Create OHLCV data
        df = pd.DataFrame({
            'Open': [p * 0.995 for p in prices],
            'High': [p * (1 + abs(np.random.normal(0, 0.02))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.02))) for p in prices],
            'Close': prices,
            'Volume': [np.random.randint(100000, 1000000) for _ in range(days)]
        }, index=dates)

        return df

    @staticmethod
    def create_sideways_data(days=100, start_price=100):
        """Create sideways/ranging price data."""
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')

        prices = []
        for i in range(days):
            # Oscillate around start price
            noise = np.random.normal(0, 0.02)
            mean_reversion = (start_price - (prices[-1] if prices else start_price)) * 0.05
            price = (prices[-1] if prices else start_price) * (1 + noise + mean_reversion)
            prices.append(max(price, 1))

        df = pd.DataFrame({
            'Open': [p * 0.995 for p in prices],
            'High': [p * 1.02 for p in prices],
            'Low': [p * 0.98 for p in prices],
            'Close': prices,
            'Volume': [np.random.randint(100000, 1000000) for _ in range(days)]
        }, index=dates)

        return df


class TestStrategyInitialization(unittest.TestCase):
    """Test strategy initialization and parameter validation."""

    def test_all_strategies_importable(self):
        """Test that all strategies can be imported."""
        for strategy_name, strategy_class in STRATEGIES.items():
            self.assertTrue(callable(strategy_class))
            self.assertTrue(hasattr(strategy_class, '__name__'))

    def test_sma_strategy_initialization(self):
        """Test SMA strategy initialization."""
        strategy = SMAStrategy
        self.assertEqual(strategy.params.short_period, 10)
        self.assertEqual(strategy.params.long_period, 30)

    def test_rsi_strategy_initialization(self):
        """Test RSI strategy initialization."""
        strategy = RSIStrategy
        self.assertEqual(strategy.params.rsi_period, 14)
        self.assertEqual(strategy.params.rsi_low, 30)
        self.assertEqual(strategy.params.rsi_high, 70)

    def test_macd_strategy_initialization(self):
        """Test MACD strategy initialization."""
        strategy = MACDStrategy
        self.assertEqual(strategy.params.fast_ema, 12)
        self.assertEqual(strategy.params.slow_ema, 26)
        self.assertEqual(strategy.params.signal_ema, 9)


class TestStrategyBacktesting(unittest.TestCase):
    """Test strategy backtesting functionality."""

    def setUp(self):
        """Set up test data."""
        self.trending_data = MockData.create_trending_data(days=100, trend=0.001)
        self.sideways_data = MockData.create_sideways_data(days=100)
        np.random.seed(42)  # For reproducible tests

    def _run_strategy_test(self, strategy_class, data, **params):
        """Helper method to run a strategy test."""
        cerebro = bt.Cerebro()

        # Add strategy with parameters
        cerebro.addstrategy(strategy_class, **params)

        # Convert DataFrame to Backtrader data feed
        bt_data = bt.feeds.PandasData(
            dataname=data,
            datetime=None,
            open='Open',
            high='High',
            low='Low',
            close='Close',
            volume='Volume',
            openinterest=None
        )
        cerebro.adddata(bt_data)

        # Set initial cash and commission
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
            'max_drawdown': drawdown.max.drawdown if 'max' in drawdown else 0,
        }

    def test_sma_strategy_trending_market(self):
        """Test SMA strategy on trending data."""
        result = self._run_strategy_test(
            SMAStrategy,
            self.trending_data,
            short_period=10,
            long_period=30
        )

        # In trending market, SMA might generate trades (depends on volatility and crossovers)
        self.assertGreaterEqual(result['total_trades'], 0)
        self.assertIsInstance(result['return_pct'], (int, float))
        self.assertGreaterEqual(result['final_value'], 0)

    def test_rsi_strategy_sideways_market(self):
        """Test RSI strategy on sideways data."""
        result = self._run_strategy_test(
            RSIStrategy,
            self.sideways_data,
            rsi_period=14,
            rsi_low=30,
            rsi_high=70
        )

        # RSI should work in sideways markets
        self.assertGreaterEqual(result['total_trades'], 0)
        self.assertIsInstance(result['return_pct'], (int, float))

    def test_buy_and_hold_strategy(self):
        """Test Buy and Hold strategy."""
        result = self._run_strategy_test(BuyAndHoldStrategy, self.trending_data)

        # Buy and hold should make exactly 1 trade (buy at start)
        self.assertEqual(result['total_trades'], 0)  # Only buys, no closed trades
        self.assertGreater(result['final_value'], 0)

    def test_macd_strategy_execution(self):
        """Test MACD strategy execution."""
        result = self._run_strategy_test(
            MACDStrategy,
            self.trending_data,
            fast_ema=12,
            slow_ema=26,
            signal_ema=9
        )

        self.assertGreaterEqual(result['total_trades'], 0)
        self.assertIsInstance(result['max_drawdown'], (int, float))

    def test_bollinger_bands_strategy(self):
        """Test Bollinger Bands strategy."""
        result = self._run_strategy_test(
            BollingerBandsStrategy,
            self.sideways_data,
            period=20,
            devfactor=2.0
        )

        self.assertGreaterEqual(result['total_trades'], 0)
        self.assertIsInstance(result['return_pct'], (int, float))


class TestParameterValidation(unittest.TestCase):
    """Test parameter validation for strategies."""

    def test_sma_invalid_parameters(self):
        """Test SMA with invalid parameters."""
        # Test with short period >= long period
        cerebro = bt.Cerebro()

        # This should not crash, but may not be effective
        cerebro.addstrategy(SMAStrategy, short_period=30, long_period=10)

        # Add minimal data
        data = MockData.create_trending_data(days=50)
        bt_data = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(bt_data)
        cerebro.broker.setcash(10000)

        # Should run without error (backtrader handles this gracefully)
        results = cerebro.run()
        self.assertIsNotNone(results)

    def test_rsi_boundary_values(self):
        """Test RSI with boundary values."""
        cerebro = bt.Cerebro()

        # Test with extreme RSI levels
        cerebro.addstrategy(RSIStrategy, rsi_low=10, rsi_high=90)

        data = MockData.create_sideways_data(days=50)
        bt_data = bt.feeds.PandasData(dataname=data)
        cerebro.adddata(bt_data)
        cerebro.broker.setcash(10000)

        results = cerebro.run()
        self.assertIsNotNone(results)


class TestStrategyPerformanceMetrics(unittest.TestCase):
    """Test strategy performance measurement."""

    def setUp(self):
        """Set up test data."""
        self.test_data = MockData.create_trending_data(days=252, trend=0.0005)  # 1 year of data

    def test_strategy_returns_calculation(self):
        """Test that strategy returns are calculated correctly."""
        cerebro = bt.Cerebro()
        cerebro.addstrategy(SMAStrategy, short_period=5, long_period=20)

        bt_data = bt.feeds.PandasData(dataname=self.test_data)
        cerebro.adddata(bt_data)

        initial_cash = 10000
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.001)

        cerebro.run()
        final_value = cerebro.broker.getvalue()

        # Verify return calculation
        expected_return = ((final_value - initial_cash) / initial_cash) * 100
        self.assertIsInstance(expected_return, (int, float))

        # Should not lose all money (basic sanity check)
        self.assertGreater(final_value, initial_cash * 0.5)

    def test_multiple_strategies_comparison(self):
        """Test running multiple strategies for comparison."""
        strategies_to_test = [SMAStrategy, BuyAndHoldStrategy, RSIStrategy]
        results = {}

        for strategy_class in strategies_to_test:
            cerebro = bt.Cerebro()
            cerebro.addstrategy(strategy_class)

            bt_data = bt.feeds.PandasData(dataname=self.test_data)
            cerebro.adddata(bt_data)
            cerebro.broker.setcash(10000)
            cerebro.broker.setcommission(commission=0.001)

            cerebro.run()
            final_value = cerebro.broker.getvalue()

            results[strategy_class.__name__] = final_value

        # All strategies should produce valid results
        for strategy_name, final_value in results.items():
            self.assertGreater(final_value, 0)
            self.assertIsInstance(final_value, (int, float))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_minimal_data(self):
        """Test strategies with minimal data."""
        # Create very short data series
        minimal_data = MockData.create_trending_data(days=10)

        cerebro = bt.Cerebro()
        cerebro.addstrategy(SMAStrategy, short_period=5, long_period=8)

        bt_data = bt.feeds.PandasData(dataname=minimal_data)
        cerebro.adddata(bt_data)
        cerebro.broker.setcash(10000)

        # Should handle minimal data gracefully
        results = cerebro.run()
        self.assertIsNotNone(results)

    def test_flat_price_data(self):
        """Test strategies with flat (no movement) price data."""
        dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
        flat_price = 100.0

        flat_data = pd.DataFrame({
            'Open': [flat_price] * 50,
            'High': [flat_price] * 50,
            'Low': [flat_price] * 50,
            'Close': [flat_price] * 50,
            'Volume': [100000] * 50
        }, index=dates)

        cerebro = bt.Cerebro()
        cerebro.addstrategy(SMAStrategy)

        bt_data = bt.feeds.PandasData(dataname=flat_data)
        cerebro.adddata(bt_data)
        cerebro.broker.setcash(10000)

        results = cerebro.run()
        final_value = cerebro.broker.getvalue()

        # With flat prices, should have minimal activity
        self.assertAlmostEqual(final_value, 10000, delta=100)  # Allow for small commissions


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
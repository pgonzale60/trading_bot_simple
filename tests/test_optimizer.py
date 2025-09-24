#!/usr/bin/env python3
"""
Unit tests for parameter optimization functionality.
"""

import json
import unittest
import sys
import os
import pandas as pd
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimizer import ParameterOptimizer


def load_fixtures():
    """Load test fixtures from JSON file."""
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures.json')
    if os.path.exists(fixture_path):
        with open(fixture_path, 'r') as f:
            return json.load(f)
    return {}


class TestParameterOptimizer(unittest.TestCase):
    """Test ParameterOptimizer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = ParameterOptimizer(
            symbol='AAPL',
            start_date='2023-01-01',
            cash=10000
        )
        self.fixtures = load_fixtures()

        # Create mock data
        self.mock_data = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'High': [105.0, 106.0, 107.0, 108.0, 109.0],
            'Low': [99.0, 100.0, 101.0, 102.0, 103.0],
            'Close': [104.0, 105.0, 106.0, 107.0, 108.0],
            'Volume': [1000000, 1100000, 1200000, 1300000, 1400000]
        }, index=pd.date_range('2023-01-01', periods=5, freq='D'))

    def test_initialization(self):
        """Test ParameterOptimizer initialization."""
        self.assertEqual(self.optimizer.symbol, 'AAPL')
        self.assertEqual(self.optimizer.start_date, '2023-01-01')
        self.assertEqual(self.optimizer.cash, 10000)
        self.assertEqual(self.optimizer.results, [])
        self.assertIsNone(self.optimizer.data)

    @patch('optimizer.get_stock_data')
    def test_load_data_success(self, mock_get_data):
        """Test successful data loading."""
        mock_get_data.return_value = self.mock_data

        result = self.optimizer.load_data()

        self.assertTrue(result)
        self.assertIsNotNone(self.optimizer.data)
        mock_get_data.assert_called_once_with('AAPL', '2023-01-01')

    @patch('optimizer.get_stock_data')
    def test_load_data_failure(self, mock_get_data):
        """Test data loading failure."""
        mock_get_data.side_effect = Exception("Network error")

        result = self.optimizer.load_data()

        self.assertFalse(result)
        self.assertIsNone(self.optimizer.data)

    def test_run_backtest(self):
        """Test running a single backtest."""
        self.optimizer.data = MagicMock()

        # Mock Backtrader components
        with patch('optimizer.bt.Cerebro') as mock_cerebro_class:
            mock_cerebro = MagicMock()
            mock_cerebro.broker.getvalue.return_value = 11000  # 10% gain
            mock_cerebro_class.return_value = mock_cerebro

            # Mock strategy result with analyzers
            mock_result = MagicMock()
            mock_trades = {
                'total': {'closed': 5},
                'won': {'total': 3, 'pnl': {'average': 200}},
                'lost': {'total': 2}
            }
            mock_result.analyzers.trades.get_analysis.return_value = mock_trades
            mock_result.analyzers.sharpe.get_analysis.return_value = {'sharperatio': 1.5}
            mock_result.analyzers.drawdown.get_analysis.return_value = {'max': {'drawdown': 5.0}}

            mock_cerebro.run.return_value = [mock_result]

            # Test backtest execution
            from strategies import SMAStrategy
            result = self.optimizer._run_backtest(SMAStrategy, short_period=10, long_period=30)

            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertEqual(result['initial_value'], 10000)
            self.assertEqual(result['final_value'], 11000)
            self.assertEqual(result['return_pct'], 10.0)
            self.assertEqual(result['total_trades'], 5)
            self.assertEqual(result['winning_trades'], 3)
            self.assertEqual(result['losing_trades'], 2)
            self.assertEqual(result['win_rate'], 60.0)  # 3/5 * 100
            self.assertEqual(result['sharpe_ratio'], 1.5)
            self.assertEqual(result['max_drawdown'], 5.0)

    def test_sma_parameter_testing(self):
        """Test SMA parameter optimization."""
        self.optimizer.data = MagicMock()

        # Mock the _run_backtest method with deterministic fixture-based results
        expected_results = self.fixtures.get('optimizer_sma_parameters', [])
        result_lookup = {(r['short_period'], r['long_period']): r for r in expected_results}

        def mock_run_backtest(strategy_class, **params):
            # Return specific fixture values based on parameters
            short = params.get('short_period', 10)
            long = params.get('long_period', 30)

            # Use fixture data if available, otherwise fallback to default
            if (short, long) in result_lookup:
                fixture_result = result_lookup[(short, long)]
                return {
                    'initial_value': 10000,
                    'final_value': 10000 * (1 + fixture_result['return_pct']/100),
                    'profit': 10000 * (fixture_result['return_pct']/100),
                    'return_pct': fixture_result['return_pct'],
                    'total_trades': fixture_result['total_trades'],
                    'winning_trades': fixture_result['winning_trades'],
                    'losing_trades': fixture_result['losing_trades'],
                    'win_rate': fixture_result['win_rate'],
                    'sharpe_ratio': fixture_result['sharpe_ratio'],
                    'max_drawdown': fixture_result['max_drawdown'],
                    'avg_trade': fixture_result['avg_trade']
                }
            else:
                # Fallback for parameters not in fixtures
                return_pct = 5.0
                return {
                    'initial_value': 10000,
                    'final_value': 10000 * (1 + return_pct/100),
                    'profit': 10000 * (return_pct/100),
                    'return_pct': return_pct,
                    'total_trades': 5,
                    'winning_trades': 3,
                    'losing_trades': 2,
                    'win_rate': 60.0,
                    'sharpe_ratio': 1.5,
                    'max_drawdown': 5.0,
                    'avg_trade': 100.0
                }

        self.optimizer._run_backtest = mock_run_backtest

        # Test parameter optimization
        results = self.optimizer.test_sma_parameters(
            short_periods=[5, 10],
            long_periods=[20, 30]
        )

        # Should test valid combinations only (short < long)
        self.assertEqual(len(results), 4)  # (5,20), (5,30), (10,20), (10,30)

        # Validate specific results against fixtures if available
        if expected_results:
            for result in results:
                expected = next((r for r in expected_results if
                               r['short_period'] == result['short_period'] and
                               r['long_period'] == result['long_period']), None)
                if expected:
                    self.assertEqual(result['return_pct'], expected['return_pct'])
                    self.assertEqual(result['total_trades'], expected['total_trades'])
                    self.assertEqual(result['winning_trades'], expected['winning_trades'])
                    self.assertEqual(result['losing_trades'], expected['losing_trades'])
                    self.assertEqual(result['win_rate'], expected['win_rate'])
                    self.assertEqual(result['sharpe_ratio'], expected['sharpe_ratio'])
                    self.assertEqual(result['max_drawdown'], expected['max_drawdown'])
                    self.assertEqual(result['avg_trade'], expected['avg_trade'])

        # Verify result structure
        for result in results:
            self.assertIn('strategy', result)
            self.assertIn('short_period', result)
            self.assertIn('long_period', result)
            self.assertIn('return_pct', result)
            self.assertEqual(result['strategy'], 'SMA')

    def test_analyze_results(self):
        """Test results analysis."""
        # Create mock results
        mock_results = [
            {
                'strategy': 'SMA',
                'params': 'SMA(5,20)',
                'return_pct': 15.0,
                'total_trades': 8,
                'win_rate': 62.5,
                'sharpe_ratio': 1.8,
                'max_drawdown': 4.0
            },
            {
                'strategy': 'SMA',
                'params': 'SMA(10,30)',
                'return_pct': 10.0,
                'total_trades': 5,
                'win_rate': 60.0,
                'sharpe_ratio': 1.5,
                'max_drawdown': 5.0
            },
            {
                'strategy': 'SMA',
                'params': 'SMA(15,50)',
                'return_pct': 5.0,
                'total_trades': 3,
                'win_rate': 66.7,
                'sharpe_ratio': 1.2,
                'max_drawdown': 3.0
            }
        ]

        # Test analysis (suppress print output)
        with patch('builtins.print'):
            result_df = self.optimizer.analyze_results(mock_results)

        # Verify result is sorted by return_pct descending
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), 3)

        returns = result_df['return_pct'].tolist()
        self.assertEqual(returns, [15.0, 10.0, 5.0])

    def test_analyze_empty_results(self):
        """Test analysis with empty results."""
        with patch('builtins.print'):
            result = self.optimizer.analyze_results([])

        self.assertIsNone(result)

    @patch('optimizer.ParameterOptimizer.load_data')
    @patch('optimizer.ParameterOptimizer.test_sma_parameters')
    @patch('optimizer.ParameterOptimizer.analyze_results')
    def test_quick_test(self, mock_analyze, mock_test_sma, mock_load_data):
        """Test quick test functionality."""
        # Mock successful data loading
        mock_load_data.return_value = True

        # Mock SMA testing results
        mock_sma_results = [
            {'strategy': 'SMA', 'return_pct': 10.0},
            {'strategy': 'SMA', 'return_pct': 8.0}
        ]
        mock_test_sma.return_value = mock_sma_results

        # Mock analysis result
        mock_analyze.return_value = pd.DataFrame(mock_sma_results)

        # Run quick test
        result = self.optimizer.quick_test()

        # Verify methods were called
        mock_load_data.assert_called_once()
        mock_test_sma.assert_called_once()
        mock_analyze.assert_called_once_with(mock_sma_results)

        # Verify result
        self.assertIsInstance(result, pd.DataFrame)

    @patch('optimizer.ParameterOptimizer.load_data')
    def test_quick_test_data_failure(self, mock_load_data):
        """Test quick test with data loading failure."""
        # Mock failed data loading
        mock_load_data.return_value = False

        result = self.optimizer.quick_test()

        # Should return None when data loading fails
        self.assertIsNone(result)


class TestParameterValidation(unittest.TestCase):
    """Test parameter validation in optimization."""

    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = ParameterOptimizer('TEST', '2023-01-01', 10000)

    def test_invalid_parameter_combinations(self):
        """Test handling of invalid parameter combinations."""
        self.optimizer.data = MagicMock()

        # Mock _run_backtest to track calls
        call_log = []

        def mock_run_backtest(strategy_class, **params):
            call_log.append(params)
            return {
                'initial_value': 10000,
                'final_value': 10500,
                'profit': 500,
                'return_pct': 5.0,
                'total_trades': 1,
                'winning_trades': 1,
                'losing_trades': 0,
                'win_rate': 100.0,
                'sharpe_ratio': 1.0,
                'max_drawdown': 0.0,
                'avg_trade': 500.0
            }

        self.optimizer._run_backtest = mock_run_backtest

        # Test with invalid combinations (short >= long)
        results = self.optimizer.test_sma_parameters(
            short_periods=[10, 20, 30],
            long_periods=[10, 20, 30]
        )

        # Should only test valid combinations where short < long
        valid_combinations = [
            {'short_period': 10, 'long_period': 20},
            {'short_period': 10, 'long_period': 30},
            {'short_period': 20, 'long_period': 30}
        ]

        self.assertEqual(len(call_log), 3)
        for expected in valid_combinations:
            self.assertIn(expected, call_log)

    def test_empty_parameter_ranges(self):
        """Test with empty parameter ranges."""
        self.optimizer.data = MagicMock()

        # Test with empty short periods
        results = self.optimizer.test_sma_parameters(
            short_periods=[],
            long_periods=[20, 30]
        )

        self.assertEqual(len(results), 0)

        # Test with empty long periods
        results = self.optimizer.test_sma_parameters(
            short_periods=[10, 15],
            long_periods=[]
        )

        self.assertEqual(len(results), 0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in optimization."""

    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = ParameterOptimizer('TEST', '2023-01-01', 10000)

    def test_backtest_exception_handling(self):
        """Test handling of exceptions during backtesting."""
        self.optimizer.data = MagicMock()

        # Mock _run_backtest to raise exception
        def failing_backtest(strategy_class, **params):
            raise Exception("Backtest failed")

        self.optimizer._run_backtest = failing_backtest

        # Should handle exceptions gracefully
        with patch('builtins.print'):  # Suppress error output
            results = self.optimizer.test_sma_parameters(
                short_periods=[10],
                long_periods=[30]
            )

        # Should return empty results when all tests fail
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
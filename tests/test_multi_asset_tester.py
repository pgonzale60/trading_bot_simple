#!/usr/bin/env python3
"""
Unit tests for multi-asset testing functionality.
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_asset_tester import MultiAssetTester


class TestMultiAssetTester(unittest.TestCase):
    """Test MultiAssetTester functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary cache directory
        self.temp_cache_dir = tempfile.mkdtemp()
        self.tester = MultiAssetTester(
            start_date='2023-01-01',
            cash=10000,
            cache_dir=self.temp_cache_dir
        )

        # Create mock data
        self.mock_data = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0],
            'High': [105.0, 106.0, 107.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [104.0, 105.0, 106.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2023-01-01', periods=3, freq='D'))

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary cache directory
        shutil.rmtree(self.temp_cache_dir, ignore_errors=True)

    def test_initialization(self):
        """Test MultiAssetTester initialization."""
        self.assertEqual(self.tester.start_date, '2023-01-01')
        self.assertEqual(self.tester.cash, 10000)
        self.assertEqual(self.tester.cache_dir, self.temp_cache_dir)

        # Check that asset lists are populated
        self.assertGreater(len(self.tester.stock_symbols), 0)
        self.assertGreater(len(self.tester.crypto_symbols), 0)
        self.assertGreater(len(self.tester.all_symbols), 0)

        # Verify cache directory was created
        self.assertTrue(os.path.exists(self.temp_cache_dir))

    def test_cache_key_generation(self):
        """Test cache key generation."""
        # Test with parameters
        key1 = self.tester.get_cache_key('sma', {'short_period': 10, 'long_period': 30})
        key2 = self.tester.get_cache_key('sma', {'long_period': 30, 'short_period': 10})

        # Should be the same regardless of parameter order
        self.assertEqual(key1, key2)

        # Test without parameters
        key3 = self.tester.get_cache_key('buy_hold', {})
        self.assertIsInstance(key3, str)

    def test_cache_operations(self):
        """Test cache save and load operations."""
        symbol = 'TEST_SYMBOL'
        test_results = [
            {
                'strategy': 'SMA',
                'return_pct': 5.5,
                'total_trades': 10,
                'tested_at': '2023-01-01T00:00:00'
            }
        ]

        # Test save cache
        self.tester.save_cache(symbol, test_results)

        # Test load cache
        loaded_results = self.tester.load_cache(symbol)
        self.assertEqual(len(loaded_results), 1)
        self.assertEqual(loaded_results[0]['strategy'], 'SMA')
        self.assertEqual(loaded_results[0]['return_pct'], 5.5)

    def test_param_parsing(self):
        """Test parameter string parsing."""
        # Test valid parameter string
        param_string = "short_period=10, long_period=30, factor=2.5"
        parsed = self.tester._parse_params(param_string)

        expected = {
            'short_period': 10,
            'long_period': 30,
            'factor': 2.5
        }
        self.assertEqual(parsed, expected)

        # Test empty string
        empty_parsed = self.tester._parse_params("")
        self.assertEqual(empty_parsed, {})

        # Test invalid string
        invalid_parsed = self.tester._parse_params("invalid_format")
        self.assertEqual(invalid_parsed, {})

    @patch('multi_asset_tester.get_stock_data')
    def test_single_strategy_test(self, mock_get_data):
        """Test testing a single strategy on a single symbol."""
        # Mock data fetching
        mock_get_data.return_value = MagicMock()

        # Mock Backtrader cerebro
        with patch('multi_asset_tester.bt.Cerebro') as mock_cerebro_class:
            mock_cerebro = MagicMock()
            mock_cerebro.broker.getvalue.return_value = 11000  # 10% gain
            mock_cerebro_class.return_value = mock_cerebro

            # Mock analyzers
            mock_result = MagicMock()
            mock_trades = {'total': {'closed': 5}, 'won': {'total': 3}, 'lost': {'total': 2}}
            mock_result.analyzers.trades.get_analysis.return_value = mock_trades
            mock_result.analyzers.sharpe.get_analysis.return_value = {'sharperatio': 1.5}
            mock_result.analyzers.drawdown.get_analysis.return_value = {'max': {'drawdown': 5.0}}
            mock_result.analyzers.sqn.get_analysis.return_value = {'sqn': 2.0}

            mock_cerebro.run.return_value = [mock_result]

            # Test strategy execution
            result = self.tester.test_strategy_on_symbol('AAPL', 'sma', short_period=10, long_period=30)

            # Verify result structure
            self.assertIsNotNone(result)
            self.assertEqual(result['symbol'], 'AAPL')
            self.assertEqual(result['strategy'], 'SMA')
            self.assertEqual(result['return_pct'], 10.0)  # (11000-10000)/10000 * 100
            self.assertEqual(result['total_trades'], 5)

    def test_find_cached_result(self):
        """Test finding cached results."""
        cached_results = [
            {
                'strategy': 'SMA',
                'params': 'short_period=10, long_period=30',
                'return_pct': 5.0
            },
            {
                'strategy': 'RSI',
                'params': 'rsi_period=14, rsi_low=30, rsi_high=70',
                'return_pct': 3.0
            }
        ]

        # Test finding existing result
        found = self.tester.find_cached_result(cached_results, 'sma', {'short_period': 10, 'long_period': 30})
        self.assertIsNotNone(found)
        self.assertEqual(found['return_pct'], 5.0)

        # Test not finding result
        not_found = self.tester.find_cached_result(cached_results, 'macd', {'fast_ema': 12})
        self.assertIsNone(not_found)

    def test_asset_lists(self):
        """Test asset symbol lists."""
        # Check stock symbols
        self.assertIn('AAPL', self.tester.stock_symbols)
        self.assertIn('MSFT', self.tester.stock_symbols)
        self.assertIn('SPY', self.tester.stock_symbols)

        # Check crypto symbols
        self.assertIn('BTC-USD', self.tester.crypto_symbols)
        self.assertIn('ETH-USD', self.tester.crypto_symbols)

        # Check combined list
        self.assertEqual(
            len(self.tester.all_symbols),
            len(self.tester.stock_symbols) + len(self.tester.crypto_symbols)
        )

        # Verify no duplicates
        self.assertEqual(len(self.tester.all_symbols), len(set(self.tester.all_symbols)))

    def test_cache_file_naming(self):
        """Test cache file naming convention."""
        symbol = 'BTC-USD'
        cache_file = self.tester.get_cache_file(symbol)

        # Should replace hyphens with underscores
        self.assertIn('BTC_USD', cache_file)
        self.assertTrue(cache_file.endswith('.json'))
        self.assertIn(self.temp_cache_dir, cache_file)

    def test_clear_all_caches(self):
        """Test clearing all cache files."""
        # Create some cache files
        test_results = [{'test': 'data'}]
        self.tester.save_cache('AAPL', test_results)
        self.tester.save_cache('BTC-USD', test_results)

        # Verify files exist
        cache_files_before = [f for f in os.listdir(self.temp_cache_dir)
                             if f.startswith('results_') and f.endswith('.json')]
        self.assertGreater(len(cache_files_before), 0)

        # Clear caches
        self.tester.clear_all_caches()

        # Verify files are gone
        cache_files_after = [f for f in os.listdir(self.temp_cache_dir)
                            if f.startswith('results_') and f.endswith('.json')]
        self.assertEqual(len(cache_files_after), 0)


class TestMultiAssetAnalysis(unittest.TestCase):
    """Test multi-asset analysis functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_cache_dir = tempfile.mkdtemp()
        self.tester = MultiAssetTester(cache_dir=self.temp_cache_dir)

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_cache_dir, ignore_errors=True)

    def test_analyze_multi_asset_results(self):
        """Test analysis of multi-asset results."""
        # Create mock results
        mock_results = [
            {
                'symbol': 'AAPL',
                'asset_type': 'stock',
                'strategy': 'SMA',
                'return_pct': 10.0,
                'sharpe_ratio': 1.5,
                'max_drawdown': 5.0,
                'total_trades': 5,
                'win_rate': 60.0
            },
            {
                'symbol': 'BTC-USD',
                'asset_type': 'crypto',
                'strategy': 'RSI',
                'return_pct': 15.0,
                'sharpe_ratio': 2.0,
                'max_drawdown': 8.0,
                'total_trades': 8,
                'win_rate': 50.0
            },
            {
                'symbol': 'MSFT',
                'asset_type': 'stock',
                'strategy': 'SMA',
                'return_pct': 8.0,
                'sharpe_ratio': 1.2,
                'max_drawdown': 4.0,
                'total_trades': 4,
                'win_rate': 75.0
            }
        ]

        # Test analysis (would normally print results)
        with patch('builtins.print'):  # Suppress print output
            result_df = self.tester.analyze_multi_asset_results(mock_results)

        # Verify result is a DataFrame
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), 3)

        # Verify sorting (should be by return_pct descending)
        returns = result_df['return_pct'].tolist()
        self.assertEqual(returns, sorted(returns, reverse=True))

    def test_empty_results_analysis(self):
        """Test analysis with empty results."""
        with patch('builtins.print'):  # Suppress print output
            result = self.tester.analyze_multi_asset_results([])

        self.assertIsNone(result)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in multi-asset testing."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_cache_dir = tempfile.mkdtemp()
        self.tester = MultiAssetTester(cache_dir=self.temp_cache_dir)

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_cache_dir, ignore_errors=True)

    @patch('multi_asset_tester.get_stock_data')
    def test_data_fetch_failure(self, mock_get_data):
        """Test handling of data fetch failures."""
        # Mock data fetching to raise exception
        mock_get_data.side_effect = Exception("Network error")

        # Test should handle gracefully
        result = self.tester.test_strategy_on_symbol('INVALID', 'sma')
        self.assertIsNone(result)

    def test_invalid_cache_file(self):
        """Test handling of corrupted cache files."""
        # Create invalid JSON file
        cache_file = self.tester.get_cache_file('TEST')
        with open(cache_file, 'w') as f:
            f.write("invalid json content")

        # Should handle gracefully and return empty list
        results = self.tester.load_cache('TEST')
        self.assertEqual(results, [])

    def test_missing_cache_directory(self):
        """Test handling of missing cache directory."""
        # Remove cache directory
        shutil.rmtree(self.temp_cache_dir)

        # Should recreate directory on initialization
        new_tester = MultiAssetTester(cache_dir=self.temp_cache_dir)
        self.assertTrue(os.path.exists(self.temp_cache_dir))


if __name__ == '__main__':
    unittest.main(verbosity=2)
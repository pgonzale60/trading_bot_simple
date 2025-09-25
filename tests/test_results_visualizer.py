#!/usr/bin/env python3
"""
Unit tests for ResultsVisualizer

Tests key functionality including outlier detection, data loading,
and visualization components.
"""

import unittest
import pandas as pd
import numpy as np
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from results_visualizer import ResultsVisualizer


class TestResultsVisualizer(unittest.TestCase):
    """Test ResultsVisualizer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.visualizer = ResultsVisualizer(cache_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_cache_file(self, filename, results_data):
        """Helper to create test cache files."""
        cache_data = {"results": results_data}
        cache_path = os.path.join(self.temp_dir, filename)
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        return cache_path

    def test_load_empty_cache_directory(self):
        """Test loading from empty cache directory."""
        df = self.visualizer.load_all_cached_results()
        self.assertTrue(df.empty, "Should return empty DataFrame for empty cache")

    def test_load_nonexistent_cache_directory(self):
        """Test loading from nonexistent cache directory."""
        visualizer = ResultsVisualizer(cache_dir='/nonexistent/path')
        df = visualizer.load_all_cached_results()
        self.assertTrue(df.empty, "Should return empty DataFrame for nonexistent cache")

    def test_load_valid_cache_files(self):
        """Test loading valid cache files."""
        # Create test data
        test_results = [
            {
                'symbol': 'AAPL',
                'strategy': 'BUY_HOLD',
                'return_pct': 50.5,
                'win_rate': 65.0,
                'total_trades': 10
            },
            {
                'symbol': 'BTC-USD',
                'strategy': 'SMA',
                'return_pct': 200.0,
                'win_rate': 70.0,
                'total_trades': 15
            }
        ]

        # Create cache file
        self.create_test_cache_file('results_test_20250925.json', test_results)

        # Load and verify
        df = self.visualizer.load_all_cached_results()
        self.assertEqual(len(df), 2, "Should load 2 results")
        self.assertIn('AAPL', df['symbol'].values, "Should contain AAPL")
        self.assertIn('BTC-USD', df['symbol'].values, "Should contain BTC-USD")

    def test_load_corrupted_cache_file(self):
        """Test handling corrupted cache files."""
        # Create corrupted JSON file
        cache_path = os.path.join(self.temp_dir, 'results_corrupted.json')
        with open(cache_path, 'w') as f:
            f.write('{"results": [invalid json}')

        # Should handle gracefully
        df = self.visualizer.load_all_cached_results()
        self.assertTrue(df.empty, "Should handle corrupted files gracefully")

    def test_outlier_detection_logic(self):
        """Test outlier detection in strategy performance plotting."""
        # Create test DataFrame with extreme outlier
        test_data = {
            'symbol': ['AAPL', 'BTC-USD', 'UNI-USD', 'MSFT', 'ETH-USD'],
            'strategy': ['BUY_HOLD', 'BUY_HOLD', 'RSI', 'SMA', 'MACD'],
            'return_pct': [50.0, 200.0, 4500000.0, 75.0, 150.0],  # UNI-USD is extreme outlier
            'win_rate': [65.0, 70.0, 60.0, 80.0, 75.0],
            'total_trades': [10, 15, 8, 12, 14]
        }
        df = pd.DataFrame(test_data)

        # Test outlier detection
        p99 = df['return_pct'].quantile(0.99)
        extreme_outliers = df[df['return_pct'] > p99]

        self.assertGreater(p99, 1000.0, "99th percentile should be high with extreme outlier")
        self.assertEqual(len(extreme_outliers), 1, "Should detect exactly 1 extreme outlier")
        self.assertEqual(extreme_outliers.iloc[0]['symbol'], 'UNI-USD', "Should identify UNI-USD as outlier")

    def test_data_capping_for_visualization(self):
        """Test that extreme values are capped properly for visualization."""
        # Create test data with extreme values
        test_data = {
            'return_pct': [10.0, 50.0, 100.0, 4500000.0, 200.0]
        }
        df = pd.DataFrame(test_data)
        original_max = df['return_pct'].max()

        # Apply capping logic
        p99 = df['return_pct'].quantile(0.99)
        df_capped = df.copy()
        df_capped['return_pct'] = df_capped['return_pct'].clip(upper=p99)

        # Verify capping
        self.assertEqual(df_capped['return_pct'].max(), p99, "Should cap at 99th percentile")
        self.assertLess(df_capped['return_pct'].max(), original_max, "Capped values should be less than original max")

        # Test with larger dataset for more meaningful percentile
        large_data = {'return_pct': list(range(1, 101)) + [4500000.0]}  # 100 normal values + 1 outlier
        df_large = pd.DataFrame(large_data)
        p99_large = df_large['return_pct'].quantile(0.99)
        self.assertLess(p99_large, 1000.0, "99th percentile of larger dataset should be reasonable")

    @patch('matplotlib.pyplot.show')  # Prevent actual plot display
    @patch('matplotlib.pyplot.savefig')  # Mock file saving
    def test_plot_strategy_performance_with_outliers(self, mock_savefig, mock_show):
        """Test strategy performance plotting with extreme outliers."""
        # Create test data with outliers
        test_data = {
            'symbol': ['AAPL', 'UNI-USD', 'BTC-USD'],
            'strategy': ['BUY_HOLD', 'RSI', 'SMA'],
            'return_pct': [50.0, 4500000.0, 200.0],
            'win_rate': [65.0, 60.0, 70.0],
            'asset_type': ['stock', 'crypto', 'crypto']
        }
        df = pd.DataFrame(test_data)

        # Should not raise exception
        try:
            self.visualizer.plot_strategy_performance(df, 'test_plot.png')
            plot_succeeded = True
        except Exception as e:
            plot_succeeded = False
            print(f"Plot failed with error: {e}")

        self.assertTrue(plot_succeeded, "Should handle outliers without crashing")
        mock_savefig.assert_called_once_with('test_plot.png', dpi=300, bbox_inches='tight')

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_extreme_outliers(self, mock_savefig, mock_show):
        """Test extreme outliers plotting."""
        # Create test data with multiple outliers
        test_data = {
            'symbol': ['AAPL', 'UNI-USD', 'SOL-USD', 'DOGE-USD', 'BTC-USD'],
            'strategy': ['BUY_HOLD', 'RSI', 'BUY_HOLD', 'BUY_HOLD', 'SMA'],
            'return_pct': [50.0, 4500000.0, 15000.0, 5000.0, 200.0]
        }
        df = pd.DataFrame(test_data)

        # Should create extreme outliers plot
        try:
            self.visualizer.plot_extreme_outliers(df, 'outliers_test.png')
            plot_succeeded = True
        except Exception as e:
            plot_succeeded = False
            print(f"Extreme outliers plot failed: {e}")

        self.assertTrue(plot_succeeded, "Should create extreme outliers plot successfully")
        mock_savefig.assert_called_once_with('outliers_test.png', dpi=300, bbox_inches='tight')

    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrames."""
        empty_df = pd.DataFrame()

        # Should handle empty DataFrames gracefully
        try:
            with patch('matplotlib.pyplot.show'), patch('matplotlib.pyplot.savefig'):
                self.visualizer.plot_strategy_performance(empty_df)
                self.visualizer.plot_asset_performance(empty_df)
                self.visualizer.plot_extreme_outliers(empty_df)
            empty_handling_succeeded = True
        except Exception as e:
            empty_handling_succeeded = False
            print(f"Empty DataFrame handling failed: {e}")

        self.assertTrue(empty_handling_succeeded, "Should handle empty DataFrames without errors")

    def test_missing_columns_handling(self):
        """Test handling of DataFrames with missing expected columns."""
        # DataFrame missing 'symbol' column
        incomplete_df = pd.DataFrame({
            'strategy': ['BUY_HOLD', 'SMA'],
            'return_pct': [50.0, 75.0]
        })

        # Should handle missing columns gracefully
        try:
            with patch('matplotlib.pyplot.show'), patch('matplotlib.pyplot.savefig'):
                self.visualizer.plot_asset_performance(incomplete_df)
            missing_columns_handled = True
        except Exception as e:
            missing_columns_handled = False
            print(f"Missing columns handling failed: {e}")

        self.assertTrue(missing_columns_handled, "Should handle missing columns gracefully")

    def test_summary_report_generation(self):
        """Test summary report generation."""
        # Create comprehensive test data
        test_data = {
            'symbol': ['AAPL', 'BTC-USD', 'UNI-USD', 'MSFT'],
            'strategy': ['BUY_HOLD', 'SMA', 'RSI', 'MACD'],
            'return_pct': [50.0, 200.0, -10.0, 75.0],
            'win_rate': [65.0, 70.0, 45.0, 80.0],
            'total_trades': [10, 15, 8, 12]
        }
        df = pd.DataFrame(test_data)

        # Should generate summary without errors
        try:
            self.visualizer.create_summary_report(df)
            summary_succeeded = True
        except Exception as e:
            summary_succeeded = False
            print(f"Summary report generation failed: {e}")

        self.assertTrue(summary_succeeded, "Should generate summary report successfully")

    def test_performance_statistics_calculation(self):
        """Test performance statistics calculations."""
        test_data = {
            'return_pct': [10.0, -5.0, 25.0, -2.0, 15.0],
            'strategy': ['A', 'A', 'B', 'B', 'B']
        }
        df = pd.DataFrame(test_data)

        # Calculate statistics
        total_tests = len(df)
        profitable_tests = len(df[df['return_pct'] > 0])
        success_rate = profitable_tests / total_tests

        # Verify calculations
        self.assertEqual(total_tests, 5, "Should count all tests")
        self.assertEqual(profitable_tests, 3, "Should count profitable tests correctly")
        self.assertEqual(success_rate, 0.6, "Should calculate 60% success rate")

        # Strategy-level statistics
        strategy_stats = df.groupby('strategy')['return_pct'].agg(['mean', 'count'])
        self.assertEqual(strategy_stats.loc['A', 'count'], 2, "Strategy A should have 2 tests")
        self.assertEqual(strategy_stats.loc['B', 'count'], 3, "Strategy B should have 3 tests")


if __name__ == '__main__':
    unittest.main(verbosity=2)
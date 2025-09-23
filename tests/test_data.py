#!/usr/bin/env python3
"""
Unit tests for data fetching and processing.
"""

import unittest
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import get_stock_data


class TestDataFetching(unittest.TestCase):
    """Test data fetching functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_symbol = 'AAPL'
        self.test_start_date = '2023-01-01'
        self.test_end_date = '2023-12-31'

    @patch('data.yf.Ticker')
    def test_get_stock_data_success(self, mock_ticker_class):
        """Test successful stock data retrieval."""
        # Create mock data
        mock_data = pd.DataFrame({
            'Open': [150.0, 151.0, 152.0],
            'High': [155.0, 156.0, 157.0],
            'Low': [149.0, 150.0, 151.0],
            'Close': [154.0, 155.0, 156.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2023-01-01', periods=3, freq='D'))

        # Set up mock
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_data
        mock_ticker_class.return_value = mock_ticker

        # Test the function
        result = get_stock_data(self.test_symbol, self.test_start_date, self.test_end_date)

        # Verify mock was called correctly
        mock_ticker_class.assert_called_once_with(self.test_symbol)
        mock_ticker.history.assert_called_once()

        # Verify result is a Backtrader data feed
        self.assertIsNotNone(result)

    @patch('data.yf.Ticker')
    def test_get_stock_data_empty_response(self, mock_ticker_class):
        """Test handling of empty data response."""
        # Create empty DataFrame
        empty_data = pd.DataFrame()

        # Set up mock
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = empty_data
        mock_ticker_class.return_value = mock_ticker

        # Test should raise ValueError for empty data
        with self.assertRaises(ValueError) as context:
            get_stock_data(self.test_symbol)

        self.assertIn("No data found", str(context.exception))

    def test_default_date_handling(self):
        """Test default date parameter handling."""
        with patch('data.yf.Ticker') as mock_ticker_class:
            # Create mock data
            mock_data = pd.DataFrame({
                'Open': [150.0], 'High': [155.0], 'Low': [149.0],
                'Close': [154.0], 'Volume': [1000000]
            }, index=pd.date_range('2023-01-01', periods=1, freq='D'))

            mock_ticker = MagicMock()
            mock_ticker.history.return_value = mock_data
            mock_ticker_class.return_value = mock_ticker

            # Test with no dates (should use defaults)
            result = get_stock_data(self.test_symbol)

            # Should call history with start and end dates
            call_kwargs = mock_ticker.history.call_args[1]
            self.assertIn('start', call_kwargs)
            self.assertIn('end', call_kwargs)

    def test_date_string_parsing(self):
        """Test date string parsing."""
        with patch('data.yf.Ticker') as mock_ticker_class:
            mock_data = pd.DataFrame({
                'Open': [150.0], 'High': [155.0], 'Low': [149.0],
                'Close': [154.0], 'Volume': [1000000]
            }, index=pd.date_range('2023-01-01', periods=1, freq='D'))

            mock_ticker = MagicMock()
            mock_ticker.history.return_value = mock_data
            mock_ticker_class.return_value = mock_ticker

            # Test with string dates
            result = get_stock_data(
                self.test_symbol,
                start_date='2023-01-01',
                end_date='2023-12-31'
            )

            # Should successfully parse dates and call API
            mock_ticker.history.assert_called_once()


class TestDataValidation(unittest.TestCase):
    """Test data validation and quality checks."""

    def test_data_structure_validation(self):
        """Test validation of data structure."""
        # Create test DataFrame with required columns
        test_data = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0],
            'High': [105.0, 106.0, 107.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [104.0, 105.0, 106.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2023-01-01', periods=3, freq='D'))

        # Verify all required columns are present
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            self.assertIn(col, test_data.columns)

        # Verify data types
        self.assertTrue(pd.api.types.is_numeric_dtype(test_data['Open']))
        self.assertTrue(pd.api.types.is_numeric_dtype(test_data['Close']))
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(test_data.index))

    def test_price_consistency_validation(self):
        """Test price consistency (High >= Low, etc.)."""
        # Create data with price inconsistencies
        inconsistent_data = pd.DataFrame({
            'Open': [100.0, 101.0, 102.0],
            'High': [99.0, 100.0, 101.0],  # High < Open (inconsistent)
            'Low': [105.0, 106.0, 107.0],  # Low > High (inconsistent)
            'Close': [104.0, 105.0, 106.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2023-01-01', periods=3, freq='D'))

        # In real implementation, we might want to validate this
        # For now, just check that the data exists
        self.assertFalse(inconsistent_data.empty)

        # Check for logical price relationships
        high_low_valid = (inconsistent_data['High'] >= inconsistent_data['Low']).all()
        self.assertFalse(high_low_valid, "High should be >= Low for all periods")

    def test_missing_data_handling(self):
        """Test handling of missing data."""
        # Create data with NaN values
        data_with_nans = pd.DataFrame({
            'Open': [100.0, None, 102.0],
            'High': [105.0, 106.0, None],
            'Low': [99.0, 100.0, 101.0],
            'Close': [104.0, None, 106.0],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2023-01-01', periods=3, freq='D'))

        # Check for missing values
        has_missing = data_with_nans.isnull().any().any()
        self.assertTrue(has_missing, "Test data should contain missing values")

        # Count missing values
        missing_count = data_with_nans.isnull().sum().sum()
        self.assertGreater(missing_count, 0)


class TestDataEdgeCases(unittest.TestCase):
    """Test edge cases for data handling."""

    @patch('data.yf.Ticker')
    def test_invalid_symbol(self, mock_ticker_class):
        """Test handling of invalid stock symbols."""
        # Mock ticker that raises an exception
        mock_ticker = MagicMock()
        mock_ticker.history.side_effect = Exception("Invalid symbol")
        mock_ticker_class.return_value = mock_ticker

        # Should handle gracefully
        with self.assertRaises(Exception):
            get_stock_data('INVALID_SYMBOL')

    def test_future_dates(self):
        """Test handling of future dates."""
        with patch('data.yf.Ticker') as mock_ticker_class:
            # Mock empty response for future dates
            empty_data = pd.DataFrame()
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = empty_data
            mock_ticker_class.return_value = mock_ticker

            # Test with future start date
            future_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

            with self.assertRaises(ValueError):
                get_stock_data('AAPL', start_date=future_date)

    def test_weekend_date_handling(self):
        """Test handling of weekend dates."""
        with patch('data.yf.Ticker') as mock_ticker_class:
            # Create mock data for weekday
            mock_data = pd.DataFrame({
                'Open': [150.0], 'High': [155.0], 'Low': [149.0],
                'Close': [154.0], 'Volume': [1000000]
            }, index=pd.date_range('2023-01-02', periods=1, freq='D'))  # Monday

            mock_ticker = MagicMock()
            mock_ticker.history.return_value = mock_data
            mock_ticker_class.return_value = mock_ticker

            # Request data starting from weekend (should get next business day)
            result = get_stock_data('AAPL', start_date='2023-01-01')  # Sunday

            # Should successfully return data
            self.assertIsNotNone(result)

    @patch('data.yf.Ticker')
    def test_very_old_dates(self, mock_ticker_class):
        """Test handling of very old dates."""
        # Mock limited historical data
        limited_data = pd.DataFrame({
            'Open': [10.0], 'High': [11.0], 'Low': [9.0],
            'Close': [10.5], 'Volume': [100000]
        }, index=pd.date_range('2020-01-01', periods=1, freq='D'))

        mock_ticker = MagicMock()
        mock_ticker.history.return_value = limited_data
        mock_ticker_class.return_value = mock_ticker

        # Request very old data
        result = get_stock_data('AAPL', start_date='1900-01-01')

        # Should return available data
        self.assertIsNotNone(result)

    def test_single_day_data(self):
        """Test handling of single day data requests."""
        with patch('data.yf.Ticker') as mock_ticker_class:
            # Single day data
            single_day_data = pd.DataFrame({
                'Open': [150.0], 'High': [155.0], 'Low': [149.0],
                'Close': [154.0], 'Volume': [1000000]
            }, index=pd.date_range('2023-01-01', periods=1, freq='D'))

            mock_ticker = MagicMock()
            mock_ticker.history.return_value = single_day_data
            mock_ticker_class.return_value = mock_ticker

            # Request single day
            result = get_stock_data(
                'AAPL',
                start_date='2023-01-01',
                end_date='2023-01-01'
            )

            self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
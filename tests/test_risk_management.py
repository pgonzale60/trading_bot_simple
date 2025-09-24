#!/usr/bin/env python3
"""
Risk Management Unit Tests

Tests for the core risk management system that validates the transformation
from gambling to professional trading.

This replaces the old comprehensive test files with focused unit tests
that work with the existing CI/CD pipeline.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk_management import RiskManager, RiskLevel
from risk_config import RiskConfig, StrategyType


class MockBroker:
    """Mock broker for testing."""
    def __init__(self, cash):
        self._cash = cash
    def getvalue(self):
        return self._cash


class MockData:
    """Mock data for testing."""
    def __init__(self, name='AAPL'):
        self._name = name
    def __str__(self):
        return self._name


class MockStrategy:
    """Mock strategy for testing."""
    def __init__(self, cash=10000, symbol='AAPL'):
        self.broker = MockBroker(cash)
        self.data = MockData(symbol)


class TestRiskTransformation(unittest.TestCase):
    """Test that the system has been transformed from gambling to professional."""

    def test_risk_levels_are_professional(self):
        """Test that all risk levels are professional (not gambling)."""
        for level in [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]:
            config = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, level)
            risk_per_trade = config['risk_per_trade']

            # Critical: No gambling behavior (95% was dangerous)
            self.assertLessEqual(risk_per_trade, 0.03, f"{level.value} risk {risk_per_trade*100:.1f}% too high")
            self.assertGreaterEqual(risk_per_trade, 0.01, f"{level.value} risk {risk_per_trade*100:.1f}% too low")

    def test_position_sizing_is_controlled(self):
        """Test that position sizing is controlled across all risk levels."""
        for level in [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]:
            config = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, level)
            max_position = config['max_position_pct']

            # No single position should dominate the account
            self.assertLessEqual(max_position, 0.4, f"{level.value} max position {max_position*100:.1f}% too high")

    def test_stop_losses_are_configured(self):
        """Test that stop losses are configured for all strategies."""
        for level in [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]:
            config = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, level)

            self.assertIn('stop_loss_pct', config, f"{level.value} missing stop loss")
            self.assertGreater(config['stop_loss_pct'], 0, f"{level.value} stop loss not set")


class TestPositionSizing(unittest.TestCase):
    """Test position sizing functionality."""

    def setUp(self):
        """Set up test strategy."""
        self.strategy = MockStrategy(cash=10000)
        self.risk_manager = RiskManager(self.strategy, RiskLevel.MODERATE)

    def test_basic_position_sizing(self):
        """Test basic position sizing calculation."""
        entry_price = 100.0
        stop_price = 96.0  # 4% stop

        position_size = self.risk_manager.calculate_position_size(entry_price, stop_price)

        self.assertGreater(position_size, 0, "Should calculate a position")
        self.assertIsInstance(position_size, (int, float), "Should be numeric")

        # Risk should be controlled
        risk_per_share = entry_price - stop_price
        total_risk = position_size * risk_per_share
        risk_pct = total_risk / 10000

        self.assertLessEqual(risk_pct, 0.03, f"Risk {risk_pct*100:.1f}% too high")

    def test_crypto_fractional_support(self):
        """Test Bitcoin bug fix - crypto should support fractional positions."""
        crypto_strategy = MockStrategy(cash=10000, symbol='BTC-USD')
        crypto_risk_manager = RiskManager(crypto_strategy, RiskLevel.MODERATE)

        entry_price = 65000.0  # Expensive Bitcoin
        stop_price = 62400.0

        position_size = crypto_risk_manager.calculate_position_size(entry_price, stop_price)

        # Bitcoin should work now (was 0 before fix)
        self.assertGreater(position_size, 0, "Bitcoin should allow fractional positions")
        self.assertLess(position_size, 1.0, "Should be fractional for expensive crypto")

    def test_expensive_asset_protection(self):
        """Test protection against expensive assets."""
        entry_price = 500000.0  # Very expensive stock
        stop_price = 480000.0

        position_size = self.risk_manager.calculate_position_size(
            entry_price, stop_price, allow_fractional=False
        )

        # Should refuse to trade when too expensive
        self.assertEqual(position_size, 0, "Should not trade when position would risk too much")

    def test_zero_risk_protection(self):
        """Test protection against zero risk scenarios."""
        entry_price = 100.0
        stop_price = 100.0  # Same as entry = no risk

        position_size = self.risk_manager.calculate_position_size(entry_price, stop_price)

        self.assertEqual(position_size, 0, "Should return 0 for zero risk scenarios")


class TestStopLossCalculations(unittest.TestCase):
    """Test stop loss calculations."""

    def setUp(self):
        """Set up test strategy."""
        self.strategy = MockStrategy(cash=10000)
        self.risk_manager = RiskManager(self.strategy, RiskLevel.MODERATE)

    def test_long_position_stops(self):
        """Test stop loss for long positions."""
        entry_price = 100.0
        stop_price = self.risk_manager.get_stop_loss_price(entry_price, is_long=True)

        self.assertGreater(stop_price, 0, "Stop should be positive")
        self.assertLess(stop_price, entry_price, "Long stop should be below entry")

        # Should be reasonable percentage
        stop_pct = (entry_price - stop_price) / entry_price
        self.assertGreater(stop_pct, 0.01, "Stop should be at least 1%")
        self.assertLess(stop_pct, 0.15, "Stop should not be more than 15%")

    def test_short_position_stops(self):
        """Test stop loss for short positions."""
        entry_price = 100.0
        stop_price = self.risk_manager.get_stop_loss_price(entry_price, is_long=False)

        self.assertGreater(stop_price, entry_price, "Short stop should be above entry")

        # Should be reasonable percentage
        stop_pct = (stop_price - entry_price) / entry_price
        self.assertGreater(stop_pct, 0.01, "Stop should be at least 1%")
        self.assertLess(stop_pct, 0.15, "Stop should not be more than 15%")


class TestRiskLevelProgression(unittest.TestCase):
    """Test that risk levels progress correctly."""

    def test_risk_progression(self):
        """Test that risk levels increase: conservative < moderate < aggressive."""
        strategy = MockStrategy(cash=10000)

        conservative_rm = RiskManager(strategy, RiskLevel.CONSERVATIVE)
        moderate_rm = RiskManager(strategy, RiskLevel.MODERATE)
        aggressive_rm = RiskManager(strategy, RiskLevel.AGGRESSIVE)

        conservative_risk = conservative_rm.risk_params['risk_per_trade']
        moderate_risk = moderate_rm.risk_params['risk_per_trade']
        aggressive_risk = aggressive_rm.risk_params['risk_per_trade']

        self.assertLessEqual(conservative_risk, moderate_risk, "Conservative should be <= moderate")
        self.assertLessEqual(moderate_risk, aggressive_risk, "Moderate should be <= aggressive")
        self.assertLess(conservative_risk, aggressive_risk, "Conservative should be < aggressive")


class TestSystemTransformation(unittest.TestCase):
    """Test overall system transformation."""

    def test_gambling_to_professional_transformation(self):
        """Test complete transformation from gambling to professional."""
        # Historical gambling levels
        gambling_risk = 0.95  # 95% of account per trade

        # Test all current risk levels are much safer
        for level in [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]:
            config = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, level)
            current_risk = config['risk_per_trade']

            # Should be drastically reduced from gambling levels
            improvement = (gambling_risk - current_risk) / gambling_risk
            self.assertGreater(improvement, 0.9, f"{level.value} not sufficiently safer than gambling")

    def test_performance_potential_maintained(self):
        """Test that performance potential is maintained with risk control."""
        strategy = MockStrategy(cash=10000)
        risk_manager = RiskManager(strategy, RiskLevel.AGGRESSIVE)  # Highest performance

        entry_price = 100.0
        stop_price = 95.0

        position_size = risk_manager.calculate_position_size(entry_price, stop_price)
        position_value = position_size * entry_price

        # Should be able to take meaningful positions for performance
        self.assertGreater(position_size, 0, "Should be able to trade")
        self.assertGreater(position_value, 500, "Position should be meaningful for returns")
        self.assertLessEqual(position_value, 5000, "Position should be controlled")


if __name__ == '__main__':
    unittest.main(verbosity=2)
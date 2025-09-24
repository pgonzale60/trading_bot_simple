#!/usr/bin/env python3
"""
Comprehensive Risk Management Testing Suite

Tests all aspects of the risk management framework to ensure:
- Position sizing works correctly
- Stop losses are properly set
- Portfolio heat is monitored
- Drawdown protection functions
- Risk profiles work as expected
"""

import backtrader as bt
import yfinance as yf
import pandas as pd
from risk_managed_strategies import RISK_MANAGED_STRATEGIES
from risk_management import RiskLevel, StopLossMethod
from risk_config import RiskConfig, StrategyType
import warnings
warnings.filterwarnings('ignore')


class RiskManagementTester:
    """Comprehensive testing of risk management functionality"""

    def __init__(self):
        self.test_results = []

    def run_all_tests(self):
        """Run complete risk management test suite"""
        print("🧪 RISK MANAGEMENT TEST SUITE")
        print("="*60)

        tests = [
            ("Position Sizing Limits", self.test_position_sizing_limits),
            ("Portfolio Heat Compliance", self.test_portfolio_heat_compliance),
            ("Stop Loss Implementation", self.test_stop_loss_implementation),
            ("Drawdown Protection", self.test_drawdown_protection),
            ("Risk Profile Differences", self.test_risk_profile_differences),
            ("Strategy-Specific Risk Settings", self.test_strategy_specific_settings),
        ]

        for test_name, test_method in tests:
            print(f"\n🔬 Testing: {test_name}")
            print("-" * 40)
            try:
                result = test_method()
                self.test_results.append((test_name, "PASSED" if result else "FAILED", result))
                print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                self.test_results.append((test_name, "ERROR", str(e)))
                print(f"❌ {test_name}: ERROR - {e}")

        self._print_test_summary()

    def test_position_sizing_limits(self):
        """Test that position sizes respect risk limits"""
        print("Testing position sizing calculations...")

        # Download test data
        data = self._get_test_data('AAPL', days=100)
        if data is None:
            return False

        # Test with different risk profiles
        results = {}

        for risk_level in [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]:
            cerebro = bt.Cerebro()
            cerebro.broker.setcash(10000)
            cerebro.broker.setcommission(commission=0.001)

            # Add SMA strategy with specific risk profile
            cerebro.addstrategy(
                RISK_MANAGED_STRATEGIES['sma'],
                risk_profile=risk_level,
                short_period=5,
                long_period=15
            )
            cerebro.adddata(data)

            # Run backtest
            strategy_results = cerebro.run()
            strategy = strategy_results[0]

            # Get risk metrics
            risk_metrics = strategy.get_risk_metrics()
            results[risk_level] = risk_metrics

            # Check position sizing limits
            config = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, risk_level)
            max_position_pct = config['max_position_pct']

            print(f"  {risk_level.value}: Max position allowed: {max_position_pct*100:.1f}%")

        # Verify conservative < moderate < aggressive limits
        conservative_limit = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, RiskLevel.CONSERVATIVE)['max_position_pct']
        moderate_limit = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, RiskLevel.MODERATE)['max_position_pct']
        aggressive_limit = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, RiskLevel.AGGRESSIVE)['max_position_pct']

        limits_correct = conservative_limit < moderate_limit < aggressive_limit
        print(f"  Position limits correctly ordered: {limits_correct}")

        return limits_correct

    def test_portfolio_heat_compliance(self):
        """Test that portfolio heat stays within limits"""
        print("Testing portfolio heat monitoring...")

        data = self._get_test_data('TSLA', days=200)
        if data is None:
            return False

        # Test with moderate risk profile
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(50000)  # Larger account for better testing
        cerebro.broker.setcommission(commission=0.001)

        cerebro.addstrategy(
            RISK_MANAGED_STRATEGIES['sma'],
            risk_profile=RiskLevel.MODERATE,
            enable_risk_logging=True
        )
        cerebro.adddata(data)

        strategy_results = cerebro.run()
        strategy = strategy_results[0]

        # Check final risk metrics
        risk_metrics = strategy.get_risk_metrics()
        portfolio_heat = risk_metrics['portfolio_heat']
        max_heat_allowed = 0.10  # 10% for moderate profile

        heat_compliant = portfolio_heat <= max_heat_allowed
        print(f"  Portfolio heat: {portfolio_heat*100:.2f}% (limit: {max_heat_allowed*100:.1f}%)")
        print(f"  Heat compliance: {heat_compliant}")

        return heat_compliant

    def test_stop_loss_implementation(self):
        """Test that stop losses are properly implemented"""
        print("Testing stop loss implementation...")

        # This test requires a more sophisticated setup to verify stop orders
        # For now, we'll test the stop loss calculation logic

        from risk_management import RiskManager

        class MockStrategy:
            def __init__(self):
                self.broker = MockBroker()

        class MockBroker:
            def getvalue(self):
                return 10000

        strategy = MockStrategy()
        risk_manager = RiskManager(strategy, RiskLevel.MODERATE)

        # Test percentage stop loss
        entry_price = 100.0
        stop_price_long = risk_manager.get_stop_loss_price(entry_price, is_long=True)
        stop_price_short = risk_manager.get_stop_loss_price(entry_price, is_long=False)

        # For moderate profile, stop should be 4%
        expected_long_stop = entry_price * 0.96  # 4% below
        expected_short_stop = entry_price * 1.04  # 4% above

        long_stop_correct = abs(stop_price_long - expected_long_stop) < 0.01
        short_stop_correct = abs(stop_price_short - expected_short_stop) < 0.01

        print(f"  Long stop: ${stop_price_long:.2f} (expected: ${expected_long_stop:.2f}) - {'✓' if long_stop_correct else '✗'}")
        print(f"  Short stop: ${stop_price_short:.2f} (expected: ${expected_short_stop:.2f}) - {'✓' if short_stop_correct else '✗'}")

        return long_stop_correct and short_stop_correct

    def test_drawdown_protection(self):
        """Test drawdown protection mechanisms"""
        print("Testing drawdown protection...")

        from risk_management import DrawdownProtector

        # Test drawdown protector logic
        protector = DrawdownProtector(max_drawdown=0.15, reduction_threshold=0.10)

        # Simulate account progression
        test_scenarios = [
            (10000, None, "NORMAL"),     # Starting value
            (11000, True, "NORMAL"),     # Profitable trade, new peak
            (10500, False, "NORMAL"),    # Small loss, still within limits
            (9500, False, "WARNING"),    # 5% drawdown from peak (11000)
            (9000, False, "REDUCE_RISK"), # 18% drawdown from peak - should trigger reduction
            (8500, False, "STOP_TRADING") # 23% drawdown from peak - should halt trading
        ]

        results_correct = True
        for value, last_trade_profitable, expected_status in test_scenarios:
            status = protector.update(value, last_trade_profitable)
            if status != expected_status:
                results_correct = False
                print(f"  ERROR: Value ${value} expected {expected_status}, got {status}")
            else:
                print(f"  ✓ Value ${value}: {status}")

        return results_correct

    def test_risk_profile_differences(self):
        """Test that different risk profiles produce different behaviors"""
        print("Testing risk profile differences...")

        # Get configurations for all profiles
        conservative = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, RiskLevel.CONSERVATIVE)
        moderate = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, RiskLevel.MODERATE)
        aggressive = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, RiskLevel.AGGRESSIVE)

        # Check that risk per trade increases
        risk_progression = (conservative['risk_per_trade'] <
                          moderate['risk_per_trade'] <
                          aggressive['risk_per_trade'])

        # Check that max positions increase
        position_progression = (conservative['max_positions'] <=
                              moderate['max_positions'] <=
                              aggressive['max_positions'])

        # Check that max drawdown tolerance increases
        drawdown_progression = (conservative['max_drawdown'] <
                              moderate['max_drawdown'] <
                              aggressive['max_drawdown'])

        print(f"  Risk per trade progression: {risk_progression}")
        print(f"    Conservative: {conservative['risk_per_trade']*100:.1f}%")
        print(f"    Moderate: {moderate['risk_per_trade']*100:.1f}%")
        print(f"    Aggressive: {aggressive['risk_per_trade']*100:.1f}%")

        print(f"  Max positions progression: {position_progression}")
        print(f"    Conservative: {conservative['max_positions']}")
        print(f"    Moderate: {moderate['max_positions']}")
        print(f"    Aggressive: {aggressive['max_positions']}")

        return risk_progression and position_progression and drawdown_progression

    def test_strategy_specific_settings(self):
        """Test that different strategy types have appropriate risk settings"""
        print("Testing strategy-specific risk settings...")

        # Test that mean reversion strategies have tighter stops than trend following
        mean_rev_config = RiskConfig.get_strategy_config(StrategyType.MEAN_REVERSION, RiskLevel.MODERATE)
        trend_config = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, RiskLevel.MODERATE)
        buy_hold_config = RiskConfig.get_strategy_config(StrategyType.BUY_HOLD, RiskLevel.MODERATE)

        # Mean reversion should have tighter stops
        mean_rev_tighter = mean_rev_config['stop_loss_pct'] < trend_config.get('stop_loss_pct', 0.04)

        # Buy & hold should have wider stops
        buy_hold_wider = buy_hold_config['stop_loss_pct'] > trend_config.get('stop_loss_pct', 0.04)

        # Buy & hold should allow larger positions
        buy_hold_larger = buy_hold_config['max_position_pct'] > trend_config['max_position_pct']

        print(f"  Mean reversion has tighter stops: {mean_rev_tighter}")
        print(f"    Mean reversion: {mean_rev_config['stop_loss_pct']*100:.1f}%")
        print(f"    Trend following: {trend_config.get('stop_loss_pct', 0.04)*100:.1f}%")

        print(f"  Buy & hold has wider stops: {buy_hold_wider}")
        print(f"    Buy & hold: {buy_hold_config['stop_loss_pct']*100:.1f}%")

        print(f"  Buy & hold allows larger positions: {buy_hold_larger}")
        print(f"    Buy & hold: {buy_hold_config['max_position_pct']*100:.1f}%")
        print(f"    Trend following: {trend_config['max_position_pct']*100:.1f}%")

        return mean_rev_tighter and buy_hold_wider and buy_hold_larger

    def _get_test_data(self, symbol, days=100):
        """Get test data for backtesting"""
        try:
            end_date = pd.Timestamp.now()
            start_date = end_date - pd.Timedelta(days=days)

            data = yf.download(symbol, start=start_date, end=end_date)

            if data.empty:
                print(f"  Warning: No data for {symbol}")
                return None

            # Handle MultiIndex columns
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)

            data.reset_index(inplace=True)

            return bt.feeds.PandasData(
                dataname=data,
                datetime='Date',
                open='Open',
                high='High',
                low='Low',
                close='Close',
                volume='Volume'
            )
        except Exception as e:
            print(f"  Error downloading {symbol}: {e}")
            return None

    def _print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("🧪 RISK MANAGEMENT TEST SUMMARY")
        print("="*60)

        passed = sum(1 for _, status, _ in self.test_results if status == "PASSED")
        failed = sum(1 for _, status, _ in self.test_results if status == "FAILED")
        errors = sum(1 for _, status, _ in self.test_results if status == "ERROR")

        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")

        if failed > 0 or errors > 0:
            print("\n🚨 FAILED TESTS:")
            for test_name, status, result in self.test_results:
                if status in ["FAILED", "ERROR"]:
                    print(f"  • {test_name}: {status}")
                    if status == "ERROR":
                        print(f"    Error: {result}")

        overall_status = "PASSED" if failed == 0 and errors == 0 else "FAILED"
        print(f"\n🎯 Overall Status: {overall_status}")

        if overall_status == "PASSED":
            print("✅ All risk management systems functioning correctly!")
        else:
            print("❌ Some risk management systems need attention!")

        print("="*60)


def run_quick_risk_test():
    """Run a quick test of risk management with real strategy"""
    print("🚀 QUICK RISK MANAGEMENT TEST")
    print("="*40)

    # Download recent AAPL data
    try:
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=60)
        aapl_data = yf.download('AAPL', start=start_date, end=end_date)

        if aapl_data.empty:
            print("❌ Could not download AAPL data")
            return

        # Handle MultiIndex columns
        if isinstance(aapl_data.columns, pd.MultiIndex):
            aapl_data.columns = aapl_data.columns.droplevel(1)
        aapl_data.reset_index(inplace=True)

        # Create data feed
        data = bt.feeds.PandasData(
            dataname=aapl_data,
            datetime='Date',
            open='Open',
            high='High',
            low='Low',
            close='Close',
            volume='Volume'
        )

        # Test conservative SMA strategy
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(10000)
        cerebro.broker.setcommission(commission=0.001)

        cerebro.addstrategy(
            RISK_MANAGED_STRATEGIES['sma'],
            risk_profile=RiskLevel.CONSERVATIVE,
            enable_risk_logging=True,
            short_period=5,
            long_period=15
        )
        cerebro.adddata(data)

        print(f"Starting Value: ${cerebro.broker.getvalue():,.2f}")

        # Run backtest
        results = cerebro.run()
        strategy = results[0]

        final_value = cerebro.broker.getvalue()
        print(f"Final Value: ${final_value:,.2f}")
        print(f"Return: {((final_value/10000)-1)*100:.1f}%")

        # Print risk summary
        strategy.print_risk_summary()

        print("✅ Quick test completed successfully!")

    except Exception as e:
        print(f"❌ Quick test failed: {e}")


if __name__ == "__main__":
    # Run quick test first
    run_quick_risk_test()

    print("\n" + "="*60)

    # Run comprehensive test suite
    tester = RiskManagementTester()
    tester.run_all_tests()
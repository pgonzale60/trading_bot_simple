# Complete Risk Management Examples

## 🎯 Full Working Examples

This document provides complete, runnable examples showing the risk management framework in action.

> ⚠️ These examples demonstrate how the risk engine can manage multiple concurrent positions, but the main test harness still runs one asset at a time. Treat the portfolio outputs here as illustrative notebooks rather than automated reports.

## 📊 Example 1: Conservative Portfolio Manager

### Complete Script
```python
#!/usr/bin/env python3
"""
Conservative Portfolio Management Example

Demonstrates:
- Conservative risk settings
- Multiple uncorrelated strategies
- Real-time risk monitoring
- Comprehensive reporting
"""

import backtrader as bt
import yfinance as yf
import pandas as pd
from risk_managed_strategies import RISK_MANAGED_STRATEGIES
from risk_management import RiskLevel
import warnings
warnings.filterwarnings('ignore')


def run_conservative_portfolio():
    """Run a conservative multi-strategy portfolio"""
    print("🛡️ CONSERVATIVE PORTFOLIO EXAMPLE")
    print("=" * 50)

    # Setup
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(50000)  # $50K starting capital
    cerebro.broker.setcommission(commission=0.001)  # 0.1% commission

    # Download data for multiple assets
    symbols = ['SPY', 'QQQ', 'IWM']  # Large, tech, small cap ETFs
    datas = []

    for symbol in symbols:
        try:
            # Download 2 years of data
            end_date = pd.Timestamp.now()
            start_date = end_date - pd.Timedelta(days=730)
            data_df = yf.download(symbol, start=start_date, end=end_date)

            if data_df.empty:
                continue

            # Handle MultiIndex columns
            if isinstance(data_df.columns, pd.MultiIndex):
                data_df.columns = data_df.columns.droplevel(1)
            data_df.reset_index(inplace=True)

            # Create Backtrader data feed
            data_feed = bt.feeds.PandasData(
                dataname=data_df,
                datetime='Date',
                open='Open',
                high='High',
                low='Low',
                close='Close',
                volume='Volume'
            )

            cerebro.adddata(data_feed)
            datas.append((symbol, data_feed))
            print(f"✅ Added {symbol} data")

        except Exception as e:
            print(f"❌ Failed to load {symbol}: {e}")

    if not datas:
        print("❌ No data loaded - cannot run example")
        return

    # Add conservative strategies
    strategies_config = [
        ('SMA Trend', 'sma', {'short_period': 20, 'long_period': 50}),
        ('RSI Mean Rev', 'rsi', {'rsi_period': 14, 'rsi_low': 35, 'rsi_high': 65}),
    ]

    for name, strategy_key, params in strategies_config:
        cerebro.addstrategy(
            RISK_MANAGED_STRATEGIES[strategy_key],
            risk_profile=RiskLevel.CONSERVATIVE,
            enable_risk_logging=True,
            **params
        )
        print(f"✅ Added {name} strategy (Conservative)")

    # Run backtest
    print(f"\n🚀 Starting backtest with ${cerebro.broker.getvalue():,.2f}")
    print("Conservative settings:")
    print("  • 1.5% risk per trade")
    print("  • 12% max position size")
    print("  • 2 max concurrent positions")
    print("  • 12% circuit breaker")
    print("  • 8% portfolio heat limit")

    results = cerebro.run()

    # Results
    final_value = cerebro.broker.getvalue()
    total_return = ((final_value / 50000) - 1) * 100

    print(f"\n📈 RESULTS")
    print("=" * 30)
    print(f"Starting Value: $50,000.00")
    print(f"Final Value: ${final_value:,.2f}")
    print(f"Total Return: {total_return:.1f}%")

    # Print detailed risk metrics for each strategy
    for i, strategy in enumerate(results):
        print(f"\n📊 Strategy {i+1} Risk Summary:")
        strategy.print_risk_summary()


def main():
    """Run the conservative portfolio example"""
    try:
        run_conservative_portfolio()
        print("\n✅ Conservative portfolio example completed successfully!")
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

## ⚡ Example 2: Aggressive Growth Strategy

### Complete Script
```python
#!/usr/bin/env python3
"""
Aggressive Growth Strategy Example

Demonstrates:
- Aggressive risk settings
- High-growth asset focus
- ATR-based stop losses
- Performance optimization
"""

import backtrader as bt
import yfinance as yf
import pandas as pd
from risk_managed_strategies import RISK_MANAGED_STRATEGIES
from risk_management import RiskLevel, StopLossMethod
import warnings
warnings.filterwarnings('ignore')


class AggressiveGrowthRunner:
    """Aggressive growth strategy runner with comprehensive tracking"""

    def __init__(self, initial_cash=100000):
        self.initial_cash = initial_cash
        self.results = {}

    def run_aggressive_growth(self):
        """Run aggressive growth focused backtest"""
        print("🚀 AGGRESSIVE GROWTH EXAMPLE")
        print("=" * 50)

        # Setup
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(self.initial_cash)
        cerebro.broker.setcommission(commission=0.001)

        # High-growth assets
        symbols = ['QQQ', 'ARKK', 'TQQQ']  # Tech-heavy, innovation, leveraged
        data_loaded = False

        for symbol in symbols:
            data_feed = self._load_symbol_data(symbol)
            if data_feed:
                cerebro.adddata(data_feed)
                data_loaded = True
                print(f"✅ Loaded {symbol}")

        if not data_loaded:
            raise Exception("No data could be loaded")

        # Add aggressive SMA strategy with custom parameters
        cerebro.addstrategy(
            RISK_MANAGED_STRATEGIES['sma'],
            risk_profile=RiskLevel.AGGRESSIVE,
            stop_loss_method=StopLossMethod.ATR,  # Volatility-based stops
            enable_risk_logging=True,
            log_all_signals=True,  # Verbose logging for example
            short_period=5,   # Fast signals
            long_period=15    # Responsive to trends
        )

        # Run with progress tracking
        print(f"\n🎯 Starting aggressive backtest")
        print("Aggressive settings:")
        print("  • 2.5% risk per trade")
        print("  • 20% max position size")
        print("  • 4 max concurrent positions")
        print("  • 18% circuit breaker")
        print("  • 12% portfolio heat limit")
        print("  • ATR-based stops for volatility adaptation")

        results = cerebro.run()
        strategy = results[0]

        # Comprehensive results analysis
        self._analyze_results(cerebro, strategy)

        return strategy

    def _load_symbol_data(self, symbol):
        """Load and prepare symbol data"""
        try:
            end_date = pd.Timestamp.now()
            start_date = end_date - pd.Timedelta(days=500)  # ~1.5 years
            data_df = yf.download(symbol, start=start_date, end=end_date)

            if data_df.empty:
                return None

            if isinstance(data_df.columns, pd.MultiIndex):
                data_df.columns = data_df.columns.droplevel(1)
            data_df.reset_index(inplace=True)

            return bt.feeds.PandasData(
                dataname=data_df,
                datetime='Date',
                open='Open',
                high='High',
                low='Low',
                close='Close',
                volume='Volume'
            )
        except Exception as e:
            print(f"⚠️  Could not load {symbol}: {e}")
            return None

    def _analyze_results(self, cerebro, strategy):
        """Comprehensive results analysis"""
        final_value = cerebro.broker.getvalue()
        total_return = ((final_value / self.initial_cash) - 1) * 100
        risk_metrics = strategy.get_risk_metrics()

        print(f"\n📈 AGGRESSIVE STRATEGY RESULTS")
        print("=" * 50)
        print(f"Initial Capital: ${self.initial_cash:,}")
        print(f"Final Value: ${final_value:,.2f}")
        print(f"Total Return: {total_return:.1f}%")
        print(f"Annualized Return: {self._annualize_return(total_return, 1.5):.1f}%")

        # Risk-adjusted performance
        if total_return > 0:
            risk_adjusted_return = total_return / max(risk_metrics.get('max_drawdown', 0.01), 0.01)
            print(f"Risk-Adjusted Return: {risk_adjusted_return:.1f}")

        # Detailed risk breakdown
        print(f"\n🛡️ RISK MANAGEMENT PERFORMANCE")
        print("-" * 30)
        print(f"Max Drawdown: {risk_metrics.get('current_drawdown', 0)*100:.1f}%")
        print(f"Portfolio Heat Peak: {risk_metrics.get('portfolio_heat', 0)*100:.1f}%")
        print(f"Total Trades: {risk_metrics.get('total_trades', 0)}")
        print(f"Win Rate: {risk_metrics.get('win_rate', 0):.1f}%")
        print(f"Circuit Breaker Triggered: {'Yes' if risk_metrics.get('trading_halted') else 'No'}")

        # Trading efficiency
        active_positions = risk_metrics.get('active_positions', 0)
        max_positions = risk_metrics.get('max_positions', 4)
        position_utilization = (active_positions / max_positions) * 100 if max_positions > 0 else 0

        print(f"\n⚙️ STRATEGY EFFICIENCY")
        print("-" * 25)
        print(f"Position Utilization: {position_utilization:.1f}% ({active_positions}/{max_positions})")
        print(f"Risk Utilization: {(risk_metrics.get('portfolio_heat', 0) / 0.12)*100:.1f}%")  # vs 12% limit

        # Store results
        self.results = {
            'initial_capital': self.initial_cash,
            'final_value': final_value,
            'total_return': total_return,
            'risk_metrics': risk_metrics
        }

    def _annualize_return(self, total_return, years):
        """Calculate annualized return"""
        if years <= 0:
            return 0
        return ((1 + total_return/100) ** (1/years) - 1) * 100


def main():
    """Run the aggressive growth example"""
    try:
        runner = AggressiveGrowthRunner(initial_cash=100000)
        strategy = runner.run_aggressive_growth()

        # Final risk summary
        print("\n" + "="*60)
        strategy.print_risk_summary()
        print("✅ Aggressive growth example completed!")

    except Exception as e:
        print(f"❌ Aggressive example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

## 🔄 Example 3: Multi-Asset Risk Comparison

### Complete Script
```python
#!/usr/bin/env python3
"""
Multi-Asset Risk Profile Comparison

Demonstrates:
- Same strategy across different risk profiles
- Performance comparison
- Risk metric analysis
- Decision making framework
"""

import backtrader as bt
import yfinance as yf
import pandas as pd
from risk_managed_strategies import RISK_MANAGED_STRATEGIES
from risk_management import RiskLevel
import warnings
warnings.filterwarnings('ignore')


class RiskProfileComparison:
    """Compare same strategy across different risk profiles"""

    def __init__(self, symbol='AAPL', initial_cash=50000, strategy='sma'):
        self.symbol = symbol
        self.initial_cash = initial_cash
        self.strategy_name = strategy
        self.results = {}

    def run_comparison(self):
        """Run the same strategy with different risk profiles"""
        print(f"🔍 RISK PROFILE COMPARISON: {self.symbol.upper()}")
        print("=" * 60)

        # Load data once
        data_feed = self._load_data()
        if not data_feed:
            raise Exception(f"Could not load data for {self.symbol}")

        risk_profiles = [
            (RiskLevel.CONSERVATIVE, "Conservative"),
            (RiskLevel.MODERATE, "Moderate"),
            (RiskLevel.AGGRESSIVE, "Aggressive")
        ]

        # Run each risk profile
        for risk_level, profile_name in risk_profiles:
            print(f"\n🧪 Testing {profile_name} Profile...")
            result = self._run_single_profile(data_feed, risk_level, profile_name)
            self.results[profile_name] = result

        # Compare results
        self._compare_results()

    def _load_data(self):
        """Load symbol data"""
        try:
            end_date = pd.Timestamp.now()
            start_date = end_date - pd.Timedelta(days=365)  # 1 year
            data_df = yf.download(self.symbol, start=start_date, end=end_date)

            if data_df.empty:
                return None

            if isinstance(data_df.columns, pd.MultiIndex):
                data_df.columns = data_df.columns.droplevel(1)
            data_df.reset_index(inplace=True)

            return bt.feeds.PandasData(
                dataname=data_df,
                datetime='Date',
                open='Open',
                high='High',
                low='Low',
                close='Close',
                volume='Volume'
            )
        except Exception as e:
            print(f"❌ Error loading {self.symbol}: {e}")
            return None

    def _run_single_profile(self, data_feed, risk_level, profile_name):
        """Run backtest for single risk profile"""
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(self.initial_cash)
        cerebro.broker.setcommission(commission=0.001)

        # Add the same data
        cerebro.adddata(data_feed)

        # Add strategy with specific risk profile
        cerebro.addstrategy(
            RISK_MANAGED_STRATEGIES[self.strategy_name],
            risk_profile=risk_level,
            enable_risk_logging=False,  # Keep quiet for comparison
            short_period=10,
            long_period=30
        )

        # Run backtest
        results = cerebro.run()
        strategy = results[0]
        final_value = cerebro.broker.getvalue()

        # Collect metrics
        risk_metrics = strategy.get_risk_metrics()
        result = {
            'profile_name': profile_name,
            'risk_level': risk_level,
            'initial_value': self.initial_cash,
            'final_value': final_value,
            'total_return': ((final_value / self.initial_cash) - 1) * 100,
            'risk_metrics': risk_metrics,
            'trades': risk_metrics.get('total_trades', 0),
            'win_rate': risk_metrics.get('win_rate', 0),
            'max_drawdown': risk_metrics.get('current_drawdown', 0) * 100,
            'portfolio_heat_peak': risk_metrics.get('portfolio_heat', 0) * 100
        }

        print(f"  Return: {result['total_return']:+.1f}% | "
              f"Trades: {result['trades']} | "
              f"Win Rate: {result['win_rate']:.1f}% | "
              f"Max DD: {result['max_drawdown']:.1f}%")

        return result

    def _compare_results(self):
        """Compare and analyze results across profiles"""
        print(f"\n📊 COMPREHENSIVE COMPARISON")
        print("=" * 80)

        # Summary table
        print(f"{'Profile':<12} {'Return':<8} {'Trades':<7} {'Win%':<6} {'MaxDD%':<7} {'Heat%':<7} {'Score':<6}")
        print("-" * 80)

        for profile_name, result in self.results.items():
            # Calculate risk-adjusted score
            returns = result['total_return']
            max_dd = max(result['max_drawdown'], 1)  # Avoid division by zero
            risk_score = returns / max_dd  # Simple risk-adjusted return

            print(f"{profile_name:<12} "
                  f"{result['total_return']:+6.1f}% "
                  f"{result['trades']:<7} "
                  f"{result['win_rate']:5.1f}% "
                  f"{result['max_drawdown']:6.1f}% "
                  f"{result['portfolio_heat_peak']:6.1f}% "
                  f"{risk_score:5.1f}")

        # Analysis and recommendations
        self._provide_analysis()

    def _provide_analysis(self):
        """Provide analysis and recommendations"""
        print(f"\n🎯 ANALYSIS & RECOMMENDATIONS")
        print("-" * 40)

        # Find best performing profile
        best_return = max(self.results.values(), key=lambda x: x['total_return'])
        best_risk_adj = max(self.results.values(),
                           key=lambda x: x['total_return'] / max(x['max_drawdown'], 1))
        safest = min(self.results.values(), key=lambda x: x['max_drawdown'])

        print(f"🏆 Best Absolute Return: {best_return['profile_name']} "
              f"({best_return['total_return']:+.1f}%)")

        print(f"⚖️  Best Risk-Adjusted: {best_risk_adj['profile_name']} "
              f"(Score: {best_risk_adj['total_return'] / max(best_risk_adj['max_drawdown'], 1):.1f})")

        print(f"🛡️ Safest Profile: {safest['profile_name']} "
              f"(Max DD: {safest['max_drawdown']:.1f}%)")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")

        if best_return['total_return'] > 20:
            print("  • Strong trending period - Aggressive profile performed well")
        elif max(r['max_drawdown'] for r in self.results.values()) > 15:
            print("  • High volatility period - Conservative profile was safer")
        else:
            print("  • Moderate conditions - Balanced approach recommended")

        # Risk tolerance guidance
        conservative_dd = self.results['Conservative']['max_drawdown']
        aggressive_dd = self.results['Aggressive']['max_drawdown']

        if aggressive_dd > conservative_dd * 2:
            print(f"  • High risk difference ({aggressive_dd:.1f}% vs {conservative_dd:.1f}%) - "
                  f"Choose based on risk tolerance")
        else:
            print("  • Similar risk levels - focus on return differences")


def main():
    """Run the risk profile comparison"""
    try:
        # Compare on a popular stock
        comparison = RiskProfileComparison(
            symbol='TSLA',  # Volatile stock for good comparison
            initial_cash=25000,
            strategy='sma'
        )

        comparison.run_comparison()
        print("\n✅ Risk profile comparison completed!")

    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

## 🧪 Example 4: Custom Risk Configuration

### Complete Script
```python
#!/usr/bin/env python3
"""
Custom Risk Configuration Example

Demonstrates:
- Creating custom risk profiles
- Fine-tuning risk parameters
- A/B testing configurations
- Performance optimization
"""

import backtrader as bt
import yfinance as yf
import pandas as pd
from risk_managed_strategies import RiskManagedSMAStrategy
from risk_management import RiskLevel, StopLossMethod
from risk_config import RiskConfig, StrategyType
import warnings
warnings.filterwarnings('ignore')


class CustomRiskExample:
    """Demonstrate custom risk configuration"""

    def __init__(self):
        self.results = {}

    def run_custom_risk_example(self):
        """Run example with custom risk configurations"""
        print("🔧 CUSTOM RISK CONFIGURATION EXAMPLE")
        print("=" * 50)

        # Define custom configurations to test
        configurations = [
            ("Ultra Conservative", self._ultra_conservative_config()),
            ("High Frequency", self._high_frequency_config()),
            ("Swing Trader", self._swing_trader_config()),
            ("Growth Focused", self._growth_focused_config()),
        ]

        # Load test data
        data_feed = self._load_test_data('QQQ')
        if not data_feed:
            return

        # Test each configuration
        for config_name, config in configurations:
            print(f"\n🧪 Testing: {config_name}")
            print("-" * 30)
            self._print_config(config)

            result = self._test_configuration(data_feed, config, config_name)
            self.results[config_name] = result

        # Compare results
        self._compare_custom_configs()

    def _ultra_conservative_config(self):
        """Ultra-conservative configuration for capital preservation"""
        return {
            'risk_per_trade': 0.01,             # 1% risk per trade (very low)
            'max_position_pct': 0.08,           # 8% max position (very small)
            'max_positions': 1,                 # Only 1 position at a time
            'max_drawdown': 0.08,               # 8% circuit breaker (very tight)
            'portfolio_heat_limit': 0.05,       # 5% max total risk (ultra safe)
            'stop_loss_method': StopLossMethod.PERCENTAGE,
            'stop_loss_pct': 0.02,              # 2% tight stops
            'atr_multiplier': 1.0,
            'drawdown_reduction_threshold': 0.05,
        }

    def _high_frequency_config(self):
        """High-frequency trading style configuration"""
        return {
            'risk_per_trade': 0.005,            # 0.5% risk (very small per trade)
            'max_position_pct': 0.05,           # 5% max position (tiny positions)
            'max_positions': 8,                 # Many small positions
            'max_drawdown': 0.10,               # 10% circuit breaker
            'portfolio_heat_limit': 0.08,       # 8% total risk (many small risks)
            'stop_loss_method': StopLossMethod.PERCENTAGE,
            'stop_loss_pct': 0.015,             # 1.5% very tight stops
            'atr_multiplier': 1.0,
            'drawdown_reduction_threshold': 0.07,
        }

    def _swing_trader_config(self):
        """Swing trading configuration"""
        return {
            'risk_per_trade': 0.03,             # 3% risk per trade (higher)
            'max_position_pct': 0.25,           # 25% max position (large swings)
            'max_positions': 2,                 # 2 large swing positions
            'max_drawdown': 0.20,               # 20% drawdown tolerance (swings)
            'portfolio_heat_limit': 0.15,       # 15% total risk (accept volatility)
            'stop_loss_method': StopLossMethod.ATR,
            'stop_loss_pct': 0.06,              # 6% backup stops
            'atr_multiplier': 3.0,              # Wide ATR stops for swings
            'drawdown_reduction_threshold': 0.15,
        }

    def _growth_focused_config(self):
        """Growth-focused configuration"""
        return {
            'risk_per_trade': 0.035,            # 3.5% risk (aggressive growth)
            'max_position_pct': 0.30,           # 30% max position (concentration)
            'max_positions': 3,                 # 3 concentrated positions
            'max_drawdown': 0.25,               # 25% drawdown tolerance (growth)
            'portfolio_heat_limit': 0.18,       # 18% total risk (aggressive)
            'stop_loss_method': StopLossMethod.ATR,
            'stop_loss_pct': 0.08,              # 8% backup stops
            'atr_multiplier': 2.8,              # Wide ATR for growth volatility
            'drawdown_reduction_threshold': 0.18,
        }

    def _print_config(self, config):
        """Print configuration details"""
        print(f"  Risk/Trade: {config['risk_per_trade']*100:.1f}%")
        print(f"  Max Position: {config['max_position_pct']*100:.0f}%")
        print(f"  Max Positions: {config['max_positions']}")
        print(f"  Stop Method: {config['stop_loss_method'].name}")
        print(f"  Circuit Breaker: {config['max_drawdown']*100:.0f}%")

    def _load_test_data(self, symbol):
        """Load test data"""
        try:
            end_date = pd.Timestamp.now()
            start_date = end_date - pd.Timedelta(days=180)  # 6 months
            data_df = yf.download(symbol, start=start_date, end=end_date)

            if data_df.empty:
                return None

            if isinstance(data_df.columns, pd.MultiIndex):
                data_df.columns = data_df.columns.droplevel(1)
            data_df.reset_index(inplace=True)

            return bt.feeds.PandasData(
                dataname=data_df,
                datetime='Date',
                open='Open',
                high='High',
                low='Low',
                close='Close',
                volume='Volume'
            )
        except Exception as e:
            print(f"❌ Could not load data: {e}")
            return None

    def _test_configuration(self, data_feed, config, config_name):
        """Test a specific configuration"""
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(50000)
        cerebro.broker.setcommission(commission=0.001)

        cerebro.adddata(data_feed)

        # Register custom configuration temporarily
        custom_risk_level = f"CUSTOM_{config_name.replace(' ', '_').upper()}"

        # Create a custom strategy instance with the configuration
        class CustomConfigStrategy(RiskManagedSMAStrategy):
            def __init__(self):
                # Override risk manager with custom config
                super().__init__()
                self.risk_manager.config = config

        cerebro.addstrategy(
            CustomConfigStrategy,
            enable_risk_logging=False,
            short_period=10,
            long_period=25
        )

        # Run backtest
        results = cerebro.run()
        strategy = results[0]
        final_value = cerebro.broker.getvalue()

        # Collect results
        risk_metrics = strategy.get_risk_metrics()
        return {
            'config_name': config_name,
            'config': config,
            'final_value': final_value,
            'total_return': ((final_value / 50000) - 1) * 100,
            'trades': risk_metrics.get('total_trades', 0),
            'win_rate': risk_metrics.get('win_rate', 0),
            'max_drawdown': risk_metrics.get('current_drawdown', 0) * 100,
            'risk_metrics': risk_metrics
        }

    def _compare_custom_configs(self):
        """Compare all custom configurations"""
        print(f"\n📊 CUSTOM CONFIGURATION COMPARISON")
        print("=" * 80)

        print(f"{'Configuration':<18} {'Return':<8} {'Trades':<7} {'Win%':<6} {'MaxDD%':<7} {'Score':<6}")
        print("-" * 80)

        for config_name, result in self.results.items():
            returns = result['total_return']
            max_dd = max(result['max_drawdown'], 0.1)
            score = returns / max_dd

            print(f"{config_name:<18} "
                  f"{returns:+6.1f}% "
                  f"{result['trades']:<7} "
                  f"{result['win_rate']:5.1f}% "
                  f"{result['max_drawdown']:6.1f}% "
                  f"{score:5.1f}")

        # Find best configurations
        self._analyze_custom_results()

    def _analyze_custom_results(self):
        """Analyze custom configuration results"""
        print(f"\n🎯 CUSTOM CONFIGURATION ANALYSIS")
        print("-" * 40)

        best_return = max(self.results.values(), key=lambda x: x['total_return'])
        safest = min(self.results.values(), key=lambda x: x['max_drawdown'])
        most_trades = max(self.results.values(), key=lambda x: x['trades'])

        print(f"🏆 Best Return: {best_return['config_name']} ({best_return['total_return']:+.1f}%)")
        print(f"🛡️ Safest: {safest['config_name']} (DD: {safest['max_drawdown']:.1f}%)")
        print(f"⚡ Most Active: {most_trades['config_name']} ({most_trades['trades']} trades)")

        print(f"\n💡 INSIGHTS:")
        print("  • Ultra Conservative: Maximum safety, minimal returns")
        print("  • High Frequency: Many small trades, consistent but small gains")
        print("  • Swing Trader: Larger moves, higher volatility, bigger potential")
        print("  • Growth Focused: Maximum growth potential, highest risk")

        print(f"\n🔧 CUSTOMIZATION TIPS:")
        print("  • Adjust risk_per_trade for comfort level")
        print("  • Modify max_position_pct for concentration preference")
        print("  • Change stop_loss_method based on market conditions")
        print("  • Set max_drawdown based on emotional tolerance")


def main():
    """Run the custom risk configuration example"""
    try:
        example = CustomRiskExample()
        example.run_custom_risk_example()
        print("\n✅ Custom risk configuration example completed!")
    except Exception as e:
        print(f"❌ Custom example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

## 🚀 Running the Examples

### Setup Instructions
```bash
# Ensure you have the environment activated
micromamba activate trading-bot-simple

# Save any example script as example_file.py
# Run the example
python example_file.py
```

### Example Output
```
🛡️ CONSERVATIVE PORTFOLIO EXAMPLE
==================================================
✅ Added SPY data
✅ Added QQQ data
✅ Added IWM data
✅ Added SMA Trend strategy (Conservative)
✅ Added RSI Mean Rev strategy (Conservative)

🚀 Starting backtest with $50,000.00
Conservative settings:
  • 1.5% risk per trade
  • 12% max position size
  • 2 max concurrent positions
  • 12% circuit breaker
  • 8% portfolio heat limit

📈 RESULTS
==============================
Starting Value: $50,000.00
Final Value: $54,750.00
Total Return: 9.5%

📊 Strategy 1 Risk Summary:
============================================================
RISK MANAGEMENT SUMMARY
============================================================
Risk Profile: CONSERVATIVE
Account Value: $54,750.00
Peak Equity: $55,200.00
Current Drawdown: 0.8%
Portfolio Heat: 3.2%
Active Positions: 1/2
Total Trades: 8
Win Rate: 62.5%
Trading Status: ACTIVE
Drawdown Protection: NORMAL
============================================================

✅ Conservative portfolio example completed successfully!
```

## 📚 Key Learning Points

### From Conservative Example
- **Safety First:** Conservative settings prevent large losses
- **Consistent Performance:** Lower but steady returns
- **Risk Control:** All safety mechanisms work automatically
- **Peace of Mind:** Never risking more than you can afford

### From Aggressive Example
- **Higher Returns:** Potential for larger profits
- **More Volatility:** Expect bigger swings
- **Risk Management:** Still protected by circuit breakers
- **Growth Focus:** Suitable for long-term wealth building

### From Comparison Example
- **Profile Differences:** Same strategy, very different results
- **Risk vs Return:** Clear trade-offs between safety and performance
- **Market Conditions:** Different profiles work better in different markets
- **Personal Choice:** Choose based on your risk tolerance

### From Custom Example
- **Flexibility:** Risk management can be fine-tuned
- **Specialization:** Different trading styles need different settings
- **Testing:** Always backtest custom configurations
- **Evolution:** Configurations can be improved over time

**Bottom Line: These examples show the risk management framework in action across different scenarios. Start with the conservative example, understand how it works, then explore other approaches based on your goals and risk tolerance.** 🎯

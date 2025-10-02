# Risk Management Configuration Guide

## 🎯 Quick Start Configuration

### Option 1: Simple Strategy Setup
```python
from risk_managed_strategies import RISK_MANAGED_STRATEGIES
from risk_management import RiskLevel

# Get a risk-managed strategy
strategy = RISK_MANAGED_STRATEGIES['sma']

# Add to cerebro with risk profile
cerebro.addstrategy(strategy, risk_profile=RiskLevel.MODERATE)
```

### Option 2: Custom Configuration
```python
from risk_managed_strategies import RiskManagedSMAStrategy
from risk_management import RiskLevel, StopLossMethod

# Add strategy with custom parameters
cerebro.addstrategy(
    RiskManagedSMAStrategy,
    risk_profile=RiskLevel.AGGRESSIVE,
    stop_loss_method=StopLossMethod.ATR,
    enable_risk_logging=True,
    short_period=5,
    long_period=20
)
```

## ⚙️ Configuration Parameters Reference

### Risk Profile Parameters
```python
# Choose your risk appetite
risk_profile = RiskLevel.CONSERVATIVE  # 1.5% risk, tight stops
risk_profile = RiskLevel.MODERATE      # 2.0% risk, balanced
risk_profile = RiskLevel.AGGRESSIVE    # 2.5% risk, wider stops
```

### Stop Loss Method Configuration
```python
# Choose stop loss calculation method
stop_loss_method = StopLossMethod.PERCENTAGE      # Fixed % stops
stop_loss_method = StopLossMethod.ATR            # Volatility-based stops
stop_loss_method = StopLossMethod.SUPPORT_RESISTANCE  # Technical levels
```

### Logging and Monitoring
```python
enable_risk_logging = True     # Log risk metrics every 5 trades
log_all_signals = False        # Log rejected signals (verbose)
```

## 📊 Complete Configuration Matrix

### All Available Risk Configurations

#### CONSERVATIVE Profiles
```python
# Trend Following - Conservative
{
    'risk_per_trade': 0.015,           # 1.5% max risk per trade
    'max_position_pct': 0.12,          # 12% max single position
    'max_positions': 2,                # 2 concurrent positions max
    'max_drawdown': 0.12,              # 12% circuit breaker
    'portfolio_heat_limit': 0.08,      # 8% max total portfolio risk
    'stop_loss_method': StopLossMethod.ATR,
    'stop_loss_pct': 0.04,             # 4% backup percentage stop
    'atr_multiplier': 1.5,             # Conservative ATR multiplier
    'drawdown_reduction_threshold': 0.08,  # 8% drawdown triggers reduction
}

# Mean Reversion - Conservative
{
    'risk_per_trade': 0.015,           # 1.5% max risk per trade
    'max_position_pct': 0.10,          # 10% max single position (tighter)
    'max_positions': 2,                # 2 concurrent positions max
    'max_drawdown': 0.12,              # 12% circuit breaker
    'portfolio_heat_limit': 0.08,      # 8% max total portfolio risk
    'stop_loss_method': StopLossMethod.PERCENTAGE,
    'stop_loss_pct': 0.03,             # 3% tight stops for mean reversion
    'atr_multiplier': 1.0,             # Not used for percentage stops
    'drawdown_reduction_threshold': 0.08,
}

# Buy & Hold - Conservative
{
    'risk_per_trade': 0.015,           # 1.5% max risk per trade
    'max_position_pct': 0.25,          # 25% max position (larger for B&H)
    'max_positions': 1,                # 1 large position typical
    'max_drawdown': 0.15,              # 15% wider tolerance for B&H
    'portfolio_heat_limit': 0.08,      # 8% max total portfolio risk
    'stop_loss_method': StopLossMethod.PERCENTAGE,
    'stop_loss_pct': 0.08,             # 8% wide stops for long-term
    'atr_multiplier': 1.0,
    'drawdown_reduction_threshold': 0.10,
}
```

#### MODERATE Profiles
```python
# Trend Following - Moderate (DEFAULT)
{
    'risk_per_trade': 0.020,           # 2.0% max risk per trade
    'max_position_pct': 0.15,          # 15% max single position
    'max_positions': 3,                # 3 concurrent positions max
    'max_drawdown': 0.15,              # 15% circuit breaker
    'portfolio_heat_limit': 0.10,      # 10% max total portfolio risk
    'stop_loss_method': StopLossMethod.ATR,
    'stop_loss_pct': 0.04,             # 4% backup percentage stop
    'atr_multiplier': 2.0,             # Standard ATR multiplier
    'drawdown_reduction_threshold': 0.10,
}

# All other moderate profiles...
```

#### AGGRESSIVE Profiles
```python
# Trend Following - Aggressive
{
    'risk_per_trade': 0.025,           # 2.5% max risk per trade
    'max_position_pct': 0.20,          # 20% max single position
    'max_positions': 4,                # 4 concurrent positions max
    'max_drawdown': 0.18,              # 18% circuit breaker
    'portfolio_heat_limit': 0.12,      # 12% max total portfolio risk
    'stop_loss_method': StopLossMethod.ATR,
    'stop_loss_pct': 0.05,             # 5% backup percentage stop
    'atr_multiplier': 2.5,             # Aggressive ATR multiplier
    'drawdown_reduction_threshold': 0.12,
}

# All other aggressive profiles...
```

## 🔧 Advanced Configuration Options

### Custom Risk Configuration
```python
from risk_config import RiskConfig, StrategyType

# Create custom configuration
custom_config = {
    'risk_per_trade': 0.018,           # Custom 1.8% risk
    'max_position_pct': 0.14,          # Custom 14% max position
    'max_positions': 3,
    'max_drawdown': 0.16,              # Custom 16% drawdown limit
    'portfolio_heat_limit': 0.09,      # Custom 9% heat limit
    'stop_loss_method': StopLossMethod.PERCENTAGE,
    'stop_loss_pct': 0.045,            # Custom 4.5% stops
    'atr_multiplier': 2.2,
    'drawdown_reduction_threshold': 0.11,
}

# Register custom configuration
RiskConfig.register_custom_config(
    StrategyType.TREND_FOLLOWING,
    RiskLevel.CUSTOM,
    custom_config
)
```

### Environment-Based Configuration
```python
import os

def get_risk_profile_from_env():
    """Get risk profile from environment variable"""
    env_risk = os.getenv('TRADING_RISK_PROFILE', 'MODERATE').upper()

    if env_risk == 'CONSERVATIVE':
        return RiskLevel.CONSERVATIVE
    elif env_risk == 'AGGRESSIVE':
        return RiskLevel.AGGRESSIVE
    else:
        return RiskLevel.MODERATE

# Use in strategy configuration
cerebro.addstrategy(
    strategy,
    risk_profile=get_risk_profile_from_env()
)
```

### Configuration Validation
```python
def validate_risk_config(config: Dict[str, Any]) -> bool:
    """Validate risk configuration parameters"""

    # Risk per trade should be reasonable (0.5% to 5%)
    if not (0.005 <= config['risk_per_trade'] <= 0.05):
        raise ValueError(f"Risk per trade {config['risk_per_trade']*100:.1f}% outside safe range (0.5%-5%)")

    # Max position should be reasonable (5% to 50%)
    if not (0.05 <= config['max_position_pct'] <= 0.50):
        raise ValueError(f"Max position {config['max_position_pct']*100:.1f}% outside safe range (5%-50%)")

    # Portfolio heat should be reasonable (2% to 15%)
    if not (0.02 <= config['portfolio_heat_limit'] <= 0.15):
        raise ValueError(f"Portfolio heat {config['portfolio_heat_limit']*100:.1f}% outside safe range (2%-15%)")

    # Max drawdown should be reasonable (5% to 30%)
    if not (0.05 <= config['max_drawdown'] <= 0.30):
        raise ValueError(f"Max drawdown {config['max_drawdown']*100:.1f}% outside safe range (5%-30%)")

    return True
```

## 🎪 Configuration Examples

### Example 1: Conservative Day Trading Setup
```python
# Conservative setup for day trading with tight risk controls
cerebro = bt.Cerebro()
cerebro.broker.setcash(25000)
cerebro.broker.setcommission(commission=0.001)

# Add multiple conservative strategies
strategies = ['sma', 'rsi', 'macd']
for strategy_name in strategies:
    cerebro.addstrategy(
        RISK_MANAGED_STRATEGIES[strategy_name],
        risk_profile=RiskLevel.CONSERVATIVE,
        enable_risk_logging=True,
        log_all_signals=False  # Too verbose for multiple strategies
    )

# Conservative configuration will automatically:
# - Limit risk to 1.5% per trade
# - Allow max 2 concurrent positions
# - Set circuit breaker at 12% drawdown
# - Limit portfolio heat to 8%
```

### Example 2: Aggressive Growth Portfolio
```python
# Aggressive setup for growth-focused portfolio
cerebro = bt.Cerebro()
cerebro.broker.setcash(100000)
cerebro.broker.setcommission(commission=0.001)

# Single aggressive trend following strategy
cerebro.addstrategy(
    RISK_MANAGED_STRATEGIES['sma'],
    risk_profile=RiskLevel.AGGRESSIVE,
    stop_loss_method=StopLossMethod.ATR,  # Override default
    enable_risk_logging=True,
    short_period=10,
    long_period=30
)

# Aggressive configuration will automatically:
# - Allow risk up to 2.5% per trade
# - Allow max 4 concurrent positions
# - Set circuit breaker at 18% drawdown
# - Allow portfolio heat up to 12%
```

### Example 3: Multi-Asset Diversified Portfolio
```python
# Balanced setup across multiple asset classes
cerebro = bt.Cerebro()
cerebro.broker.setcash(50000)

# Different strategies for different assets
configs = [
    ('sma', 'stocks', RiskLevel.MODERATE),      # Stocks with SMA
    ('rsi', 'crypto', RiskLevel.CONSERVATIVE),  # Crypto with RSI (more careful)
    ('buy_hold', 'etfs', RiskLevel.AGGRESSIVE), # ETFs with buy & hold
]

for strategy_name, asset_class, risk_level in configs:
    cerebro.addstrategy(
        RISK_MANAGED_STRATEGIES[strategy_name],
        risk_profile=risk_level,
        enable_risk_logging=True,
        # Asset class could be used for further customization
    )
```

## 📊 Configuration Comparison Tool

```python
def compare_risk_profiles():
    """Compare different risk profile configurations"""

    print("🔍 RISK PROFILE COMPARISON")
    print("=" * 80)

    profiles = [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]
    strategy_type = StrategyType.TREND_FOLLOWING

    print(f"{'Metric':20} {'Conservative':>12} {'Moderate':>12} {'Aggressive':>12}")
    print("-" * 80)

    metrics = [
        ('Risk Per Trade', 'risk_per_trade', '%'),
        ('Max Position', 'max_position_pct', '%'),
        ('Max Positions', 'max_positions', ''),
        ('Max Drawdown', 'max_drawdown', '%'),
        ('Portfolio Heat', 'portfolio_heat_limit', '%'),
        ('Stop Loss %', 'stop_loss_pct', '%'),
    ]

    for metric_name, key, unit in metrics:
        values = []
        for profile in profiles:
            config = RiskConfig.get_strategy_config(strategy_type, profile)
            value = config[key]
            if unit == '%':
                values.append(f"{value*100:.1f}%")
            else:
                values.append(str(value))

        print(f"{metric_name:20} {values[0]:>12} {values[1]:>12} {values[2]:>12}")
```

**Output:**
```
🔍 RISK PROFILE COMPARISON
================================================================================
Metric               Conservative     Moderate   Aggressive
--------------------------------------------------------------------------------
Risk Per Trade            1.5%         2.0%         2.5%
Max Position             12.0%        15.0%        20.0%
Max Positions                2            3            4
Max Drawdown             12.0%        15.0%        18.0%
Portfolio Heat            8.0%        10.0%        12.0%
Stop Loss %               4.0%         4.0%         5.0%
```

## 🚀 Best Practices for Configuration

### DO ✅
- **Start Conservative:** Begin with CONSERVATIVE profile, upgrade as experience grows
- **Match Profile to Goals:** Use CONSERVATIVE for capital preservation, AGGRESSIVE for growth
- **Test Configurations:** Backtest extensively before live trading
- **Monitor Performance:** Track how configurations perform over time
- **Document Changes:** Keep record of configuration changes and reasons
- **Validate Settings:** Use validation functions to catch dangerous configurations

### DON'T ❌
- **Override Safety Limits:** Don't disable circuit breakers or heat limits
- **Use Extreme Settings:** Avoid >5% risk per trade or >30% drawdown limits
- **Change Frequently:** Don't tweak configurations based on recent performance
- **Ignore Warnings:** Pay attention to risk limit warnings
- **Mix Incompatible Settings:** Ensure all settings work together logically
- **Skip Testing:** Never go live with untested configurations

## 🔬 Configuration Testing

```python
def test_configuration_safety():
    """Test that all configurations are within safe ranges"""

    for strategy_type in StrategyType:
        for risk_level in RiskLevel:
            config = RiskConfig.get_strategy_config(strategy_type, risk_level)

            # Test risk limits
            assert config['risk_per_trade'] <= 0.03, f"Risk too high: {config['risk_per_trade']}"
            assert config['max_drawdown'] <= 0.20, f"Drawdown limit too high: {config['max_drawdown']}"
            assert config['portfolio_heat_limit'] <= 0.15, f"Heat limit too high: {config['portfolio_heat_limit']}"

            # Test logical consistency
            assert config['risk_per_trade'] <= config['portfolio_heat_limit'], \
                "Single trade risk exceeds portfolio heat limit"

            print(f"✅ {strategy_type.name}-{risk_level.name} configuration validated")

if __name__ == "__main__":
    test_configuration_safety()
```

## 📈 Configuration Performance Tracking

### Configuration Metrics Dashboard
```python
def track_configuration_performance(strategy_results):
    """Track how different configurations perform"""

    config_performance = {}

    for strategy in strategy_results:
        config_key = f"{strategy.strategy_type.name}-{strategy.risk_profile.name}"
        metrics = strategy.get_risk_metrics()

        config_performance[config_key] = {
            'total_return': metrics['total_return'],
            'max_drawdown': metrics['max_drawdown'],
            'sharpe_ratio': metrics['sharpe_ratio'],
            'total_trades': metrics['total_trades'],
            'win_rate': metrics['win_rate']
        }

    return config_performance
```

**Bottom Line: Proper configuration is the foundation of successful risk management. Start conservative, test thoroughly, and adjust based on experience and performance. The right configuration can mean the difference between consistent profits and account destruction.** ⚙️
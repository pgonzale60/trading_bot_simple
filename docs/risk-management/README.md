# Risk Management Framework Documentation

## 🛡️ Overview

This comprehensive risk management framework transforms dangerous gambling strategies into professional trading systems. It provides:

- **Position sizing** based on risk percentage (not account percentage)
- **Stop loss management** with multiple methods
- **Portfolio heat monitoring** to prevent overexposure
- **Drawdown protection** with circuit breakers
- **Professional trade tracking** and metrics

> ℹ️ Current backtests open a single position at a time. The portfolio controls documented here are already implemented in the risk engine, but portfolio-level simulations (multiple concurrent assets, rebalancing, etc.) remain future roadmap work.

## ⚠️ CRITICAL CHANGE

**BEFORE (DANGEROUS):**
```python
# Old implementation - EXTREMELY RISKY
cash = self.broker.getcash() * 0.95  # 95% of account!
size = int(cash / self.data.close[0])
self.buy(size=size)  # No stop loss, massive position
```

**AFTER (RISK MANAGED):**
```python
# New implementation - PROFESSIONAL
self.enter_long(reason="Golden Cross Signal")
# Automatically calculates 2% risk position with stop loss
```

## 📊 Risk Reduction Results

| Risk Metric | **OLD** | **NEW** | **Improvement** |
|-------------|:-------:|:-------:|:---------------:|
| **Max Position Size** | 95% of account | 15% of account | **84% reduction** |
| **Risk Per Trade** | Up to 95% | 2% maximum | **97% reduction** |
| **Stop Losses** | None | All positions | **∞% improvement** |
| **Max Drawdown** | 70%+ | 15% circuit breaker | **78% reduction** |
| **Portfolio Heat** | Unlimited | 10% maximum | **Complete control** |

## 📚 Documentation Structure

1. **[01-overview.md](01-overview.md)** - Risk philosophy and approach
2. **[02-position-sizing.md](02-position-sizing.md)** - Position sizing methods
3. **[03-stop-losses.md](03-stop-losses.md)** - Stop loss strategies
4. **[04-portfolio-heat.md](04-portfolio-heat.md)** - Portfolio risk management
5. **[05-drawdown-protection.md](05-drawdown-protection.md)** - Drawdown controls
6. **[06-strategy-profiles.md](06-strategy-profiles.md)** - Risk profiles by strategy
7. **[07-configuration.md](07-configuration.md)** - Configuration guide
8. **[08-examples.md](08-examples.md)** - Complete examples
9. **[09-testing.md](09-testing.md)** - Testing risk management

## 🚀 Quick Start

### Using Risk-Managed Strategies

```python
from risk_managed_strategies import RISK_MANAGED_STRATEGIES
from risk_management import RiskLevel

# Get a conservative SMA strategy
strategy = RISK_MANAGED_STRATEGIES['sma']

# Configure risk level
cerebro.addstrategy(strategy, risk_profile=RiskLevel.CONSERVATIVE)
```

### Risk Profiles Available

- **CONSERVATIVE**: 1.5% risk, tight stops, 2 max positions
- **MODERATE**: 2% risk, balanced stops, 3 max positions
- **AGGRESSIVE**: 2.5% risk, wider stops, 4 max positions

## 🎯 Core Principles

1. **Never risk more than 2% per trade**
2. **Always use stop losses**
3. **Limit portfolio heat to 10%**
4. **Circuit breaker at 15% drawdown**
5. **Professional position sizing**
6. **Comprehensive trade tracking**

## ⚡ Migration Guide

### Step 1: Replace Strategy Imports
```python
# OLD
from strategies import STRATEGIES

# NEW
from risk_managed_strategies import RISK_MANAGED_STRATEGIES
```

### Step 2: Use Risk-Managed Entry/Exit
```python
# OLD - Direct buy/sell
def next(self):
    if signal:
        self.buy(size=big_risky_size)

# NEW - Risk-managed entry
def next(self):
    if signal:
        self.enter_long(reason="Signal description")
```

### Step 3: Configure Risk Profile
```python
cerebro.addstrategy(
    RISK_MANAGED_STRATEGIES['sma'],
    risk_profile=RiskLevel.MODERATE
)
```

## 📈 Expected Performance Impact

- **Lower volatility** in returns
- **Smaller drawdowns** (max 15% vs 70%+)
- **More consistent performance**
- **Better risk-adjusted returns**
- **Professional-grade metrics**

## 🔧 Key Components

- **`risk_management.py`** - Core risk management engine
- **`risk_managed_strategy.py`** - Base class for all strategies
- **`risk_config.py`** - Configuration system
- **`risk_managed_strategies.py`** - All strategies with risk management

## 📞 Support

For questions about risk management:
1. Read the documentation thoroughly
2. Check the examples in `08-examples.md`
3. Run the test suite in `09-testing.md`

**Remember: This framework prevents account destruction. Use it!** 🛡️

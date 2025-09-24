# Strategy-Specific Risk Profiles

## 🎯 Core Principle: Different Strategies Need Different Risk Settings

Not all trading strategies are created equal. Each strategy type has unique characteristics that require tailored risk management settings.

## 📊 Strategy Classification System

### TREND_FOLLOWING
**Strategies:** SMA, MACD, EMA, Momentum
**Characteristics:**
- Longer holding periods
- Wider price swings expected
- Higher win rates when trending
- Larger drawdowns in choppy markets

### MEAN_REVERSION
**Strategies:** RSI, Bollinger Bands, Contrarian
**Characteristics:**
- Shorter holding periods
- Quick profit targets
- Higher win rates overall
- Smaller individual profits

### MOMENTUM
**Strategies:** Breakout, Momentum, Volume-based
**Characteristics:**
- Very quick moves expected
- High volatility positions
- Lower win rates, larger wins
- Requires tight timing

### BUY_HOLD
**Strategies:** Buy and Hold, DCA
**Characteristics:**
- Very long holding periods
- Weathering major market moves
- Single large position typical
- Long-term growth focus

## ⚙️ Risk Configuration Matrix

### CONSERVATIVE Risk Level

#### Trend Following (Conservative)
```python
{
    'risk_per_trade': 0.015,        # 1.5% risk per trade
    'max_position_pct': 0.12,       # 12% max position size
    'max_positions': 2,             # 2 concurrent positions
    'max_drawdown': 0.12,           # 12% circuit breaker
    'portfolio_heat_limit': 0.08,   # 8% max total risk
    'stop_loss_method': StopLossMethod.ATR,
    'stop_loss_pct': 0.04,          # 4% default stop
    'atr_multiplier': 1.5,          # Conservative ATR
}
```

#### Mean Reversion (Conservative)
```python
{
    'risk_per_trade': 0.015,        # 1.5% risk per trade
    'max_position_pct': 0.10,       # 10% max position (tighter)
    'max_positions': 2,             # 2 concurrent positions
    'max_drawdown': 0.12,           # 12% circuit breaker
    'portfolio_heat_limit': 0.08,   # 8% max total risk
    'stop_loss_method': StopLossMethod.PERCENTAGE,
    'stop_loss_pct': 0.03,          # 3% tight stops (mean reversion)
    'atr_multiplier': 1.0,          # Not used for percentage
}
```

#### Buy & Hold (Conservative)
```python
{
    'risk_per_trade': 0.015,        # 1.5% risk per trade
    'max_position_pct': 0.25,       # 25% max position (larger for B&H)
    'max_positions': 1,             # 1 large position typical
    'max_drawdown': 0.15,           # 15% drawdown (wider for B&H)
    'portfolio_heat_limit': 0.08,   # 8% max total risk
    'stop_loss_method': StopLossMethod.PERCENTAGE,
    'stop_loss_pct': 0.08,          # 8% wide stops (long-term)
    'atr_multiplier': 1.0,          # Not used
}
```

### MODERATE Risk Level

#### Trend Following (Moderate)
```python
{
    'risk_per_trade': 0.020,        # 2.0% risk per trade
    'max_position_pct': 0.15,       # 15% max position size
    'max_positions': 3,             # 3 concurrent positions
    'max_drawdown': 0.15,           # 15% circuit breaker
    'portfolio_heat_limit': 0.10,   # 10% max total risk
    'stop_loss_method': StopLossMethod.ATR,
    'stop_loss_pct': 0.04,          # 4% default stop
    'atr_multiplier': 2.0,          # Standard ATR
}
```

#### Mean Reversion (Moderate)
```python
{
    'risk_per_trade': 0.020,        # 2.0% risk per trade
    'max_position_pct': 0.12,       # 12% max position
    'max_positions': 3,             # 3 concurrent positions
    'max_drawdown': 0.15,           # 15% circuit breaker
    'portfolio_heat_limit': 0.10,   # 10% max total risk
    'stop_loss_method': StopLossMethod.PERCENTAGE,
    'stop_loss_pct': 0.035,         # 3.5% stops
    'atr_multiplier': 1.0,          # Not used
}
```

#### Buy & Hold (Moderate)
```python
{
    'risk_per_trade': 0.020,        # 2.0% risk per trade
    'max_position_pct': 0.30,       # 30% max position
    'max_positions': 2,             # 2 large positions
    'max_drawdown': 0.18,           # 18% drawdown tolerance
    'portfolio_heat_limit': 0.10,   # 10% max total risk
    'stop_loss_method': StopLossMethod.PERCENTAGE,
    'stop_loss_pct': 0.10,          # 10% wide stops
    'atr_multiplier': 1.0,          # Not used
}
```

### AGGRESSIVE Risk Level

#### Trend Following (Aggressive)
```python
{
    'risk_per_trade': 0.025,        # 2.5% risk per trade
    'max_position_pct': 0.20,       # 20% max position size
    'max_positions': 4,             # 4 concurrent positions
    'max_drawdown': 0.18,           # 18% circuit breaker
    'portfolio_heat_limit': 0.12,   # 12% max total risk
    'stop_loss_method': StopLossMethod.ATR,
    'stop_loss_pct': 0.05,          # 5% default stop
    'atr_multiplier': 2.5,          # Aggressive ATR
}
```

#### Mean Reversion (Aggressive)
```python
{
    'risk_per_trade': 0.025,        # 2.5% risk per trade
    'max_position_pct': 0.15,       # 15% max position
    'max_positions': 4,             # 4 concurrent positions
    'max_drawdown': 0.18,           # 18% circuit breaker
    'portfolio_heat_limit': 0.12,   # 12% max total risk
    'stop_loss_method': StopLossMethod.PERCENTAGE,
    'stop_loss_pct': 0.04,          # 4% stops
    'atr_multiplier': 1.0,          # Not used
}
```

#### Buy & Hold (Aggressive)
```python
{
    'risk_per_trade': 0.025,        # 2.5% risk per trade
    'max_position_pct': 0.35,       # 35% max position (very large)
    'max_positions': 3,             # 3 large positions
    'max_drawdown': 0.20,           # 20% drawdown tolerance
    'portfolio_heat_limit': 0.12,   # 12% max total risk
    'stop_loss_method': StopLossMethod.PERCENTAGE,
    'stop_loss_pct': 0.12,          # 12% very wide stops
    'atr_multiplier': 1.0,          # Not used
}
```

## 🎪 Strategy-Specific Reasoning

### Why Trend Following Uses ATR Stops
```python
# Trend following strategies need to adapt to market volatility
# ATR stops automatically widen in volatile markets
# This prevents getting stopped out of good trends by noise

if strategy_type == StrategyType.TREND_FOLLOWING:
    # Use ATR-based stops for volatility adaptation
    stop_method = StopLossMethod.ATR
    atr_multiplier = 2.0  # 2x ATR is standard
```

### Why Mean Reversion Uses Percentage Stops
```python
# Mean reversion strategies expect quick moves back to mean
# Fixed percentage stops work well for this predictable behavior
# Tighter stops are appropriate since moves should be quick

if strategy_type == StrategyType.MEAN_REVERSION:
    # Use tight percentage stops for quick reversions
    stop_method = StopLossMethod.PERCENTAGE
    stop_pct = 0.035  # 3.5% - tighter than trend following
```

### Why Buy & Hold Uses Large Positions
```python
# Buy & hold strategies hold for years, not days
# Can handle larger positions since they're long-term bets
# Wide stops accommodate major market corrections

if strategy_type == StrategyType.BUY_HOLD:
    # Allow larger positions for long-term holds
    max_position_pct = 0.30  # 30% vs 15% for other strategies
    stop_loss_pct = 0.10     # 10% wide stops for long-term noise
```

## 📈 Strategy Performance Expectations

### Trend Following Strategies
- **Expected Win Rate:** 45-55%
- **Average Win/Loss Ratio:** 2:1 to 3:1
- **Typical Holding Period:** 2-8 weeks
- **Best Markets:** Strongly trending markets
- **Worst Markets:** Choppy, sideways markets

### Mean Reversion Strategies
- **Expected Win Rate:** 60-75%
- **Average Win/Loss Ratio:** 1:1 to 1.5:1
- **Typical Holding Period:** 1-5 days
- **Best Markets:** Range-bound, stable markets
- **Worst Markets:** Strong trending markets

### Momentum Strategies
- **Expected Win Rate:** 40-50%
- **Average Win/Loss Ratio:** 3:1 to 5:1
- **Typical Holding Period:** Hours to days
- **Best Markets:** Breakout, high volatility
- **Worst Markets:** Low volatility, range-bound

### Buy & Hold Strategies
- **Expected Win Rate:** 70-80% (over years)
- **Average Win/Loss Ratio:** 10:1+ (long-term)
- **Typical Holding Period:** Years
- **Best Markets:** Long-term bull markets
- **Worst Markets:** Multi-year bear markets

## 🔧 Implementation: Strategy Detection

### Automatic Strategy Type Detection
```python
def detect_strategy_type(strategy_name: str) -> StrategyType:
    """Auto-detect strategy type from strategy name/class"""
    strategy_name = strategy_name.lower()

    if any(trend_word in strategy_name for trend_word in
           ['sma', 'ema', 'macd', 'trend', 'crossover']):
        return StrategyType.TREND_FOLLOWING

    elif any(mean_word in strategy_name for mean_word in
             ['rsi', 'bollinger', 'mean', 'reversion', 'contrarian']):
        return StrategyType.MEAN_REVERSION

    elif any(momentum_word in strategy_name for momentum_word in
             ['momentum', 'breakout', 'volume']):
        return StrategyType.MOMENTUM

    elif any(buy_hold_word in strategy_name for buy_hold_word in
             ['buy_hold', 'buyhold', 'dca', 'hold']):
        return StrategyType.BUY_HOLD

    else:
        return StrategyType.TREND_FOLLOWING  # Default
```

### Risk Config Selection
```python
def get_strategy_config(strategy_type: StrategyType,
                       risk_level: RiskLevel) -> Dict[str, Any]:
    """Get configuration for specific strategy type and risk level"""

    # Base configuration matrix
    configs = {
        (StrategyType.TREND_FOLLOWING, RiskLevel.CONSERVATIVE): {
            'risk_per_trade': 0.015,
            'max_position_pct': 0.12,
            'stop_loss_method': StopLossMethod.ATR,
            # ... complete config
        },
        # ... all 12 combinations
    }

    return configs.get((strategy_type, risk_level), default_config)
```

## 📊 Strategy Comparison Dashboard

### Multi-Strategy Risk Comparison
```python
def print_strategy_comparison():
    """Compare risk settings across strategy types"""

    print("📊 STRATEGY RISK COMPARISON (MODERATE Profile)")
    print("=" * 70)

    strategies = [
        ("Trend Following", StrategyType.TREND_FOLLOWING),
        ("Mean Reversion", StrategyType.MEAN_REVERSION),
        ("Momentum", StrategyType.MOMENTUM),
        ("Buy & Hold", StrategyType.BUY_HOLD)
    ]

    for name, strategy_type in strategies:
        config = RiskConfig.get_strategy_config(strategy_type, RiskLevel.MODERATE)
        print(f"{name:15} | Risk: {config['risk_per_trade']*100:.1f}% | "
              f"Max Pos: {config['max_position_pct']*100:.0f}% | "
              f"Stop: {config['stop_loss_pct']*100:.1f}% | "
              f"Method: {config['stop_loss_method'].name}")
```

**Output:**
```
📊 STRATEGY RISK COMPARISON (MODERATE Profile)
======================================================================
Trend Following | Risk: 2.0% | Max Pos: 15% | Stop: 4.0% | Method: ATR
Mean Reversion  | Risk: 2.0% | Max Pos: 12% | Stop: 3.5% | Method: PERCENTAGE
Momentum        | Risk: 2.0% | Max Pos: 15% | Stop: 5.0% | Method: ATR
Buy & Hold      | Risk: 2.0% | Max Pos: 30% | Stop: 10.0% | Method: PERCENTAGE
```

## 🚀 Best Practices by Strategy Type

### Trend Following Strategies ✅
- Use ATR-based stops for volatility adaptation
- Allow larger positions (markets trend for weeks)
- Be patient - trends take time to develop
- Expect lower win rates but larger wins
- Monitor for trend exhaustion signals

### Mean Reversion Strategies ✅
- Use tight percentage stops for quick exits
- Take profits quickly when mean is reached
- Avoid during strong trends
- Expect higher win rates but smaller wins
- Watch for breakdown of trading ranges

### Momentum Strategies ✅
- Use wide ATR stops for volatility spikes
- Enter quickly when momentum confirmed
- Exit quickly if momentum fades
- Size positions smaller due to volatility
- Watch for momentum divergences

### Buy & Hold Strategies ✅
- Use wide percentage stops for major corrections
- Size positions larger (long-term conviction)
- Ignore short-term market noise
- Focus on fundamental strength
- Rebalance periodically, not frequently

## 🔬 Testing Strategy-Specific Configs

```python
def test_strategy_configs():
    """Test that strategy configurations are appropriate"""

    # Test that mean reversion has tighter stops than trend following
    mean_rev_config = RiskConfig.get_strategy_config(
        StrategyType.MEAN_REVERSION, RiskLevel.MODERATE)
    trend_config = RiskConfig.get_strategy_config(
        StrategyType.TREND_FOLLOWING, RiskLevel.MODERATE)

    assert mean_rev_config['stop_loss_pct'] < trend_config['stop_loss_pct']

    # Test that buy & hold allows larger positions
    buy_hold_config = RiskConfig.get_strategy_config(
        StrategyType.BUY_HOLD, RiskLevel.MODERATE)

    assert buy_hold_config['max_position_pct'] > trend_config['max_position_pct']

    # Test that aggressive profiles have higher risk
    aggressive_config = RiskConfig.get_strategy_config(
        StrategyType.TREND_FOLLOWING, RiskLevel.AGGRESSIVE)
    conservative_config = RiskConfig.get_strategy_config(
        StrategyType.TREND_FOLLOWING, RiskLevel.CONSERVATIVE)

    assert aggressive_config['risk_per_trade'] > conservative_config['risk_per_trade']
```

**Bottom Line: One size does NOT fit all in risk management. Each strategy type has unique characteristics that require tailored risk settings. Using the right profile for your strategy dramatically improves risk-adjusted returns.** 🎯
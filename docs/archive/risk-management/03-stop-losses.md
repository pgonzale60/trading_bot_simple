# Stop Loss Management System

## 🛑 Core Principle: Every Trade Must Have a Stop Loss

**BEFORE (Catastrophic):**
```python
# No stop losses - unlimited downside risk!
self.buy(size=massive_size)  # Pray it goes up
```

**AFTER (Protected):**
```python
# Automatic stop loss on every trade
self.enter_long(reason="Golden Cross")
# Automatically sets 4% stop loss below entry
```

## 🎯 Stop Loss Methods Available

### 1. PERCENTAGE Stops (Default)
Fixed percentage below/above entry price:
```python
# Long position: 4% below entry
# Short position: 4% above entry
entry_price = 100.00
long_stop = entry_price * (1 - 0.04) = 96.00
short_stop = entry_price * (1 + 0.04) = 104.00
```

### 2. ATR Stops (Volatility-Based)
Based on Average True Range (market volatility):
```python
# Adapts to market conditions
# High volatility = wider stops
# Low volatility = tighter stops
atr_value = calculate_atr(20_periods)
long_stop = entry_price - (atr_value * 2.0)
short_stop = entry_price + (atr_value * 2.0)
```

### 3. SUPPORT_RESISTANCE Stops (Technical)
Based on chart levels:
```python
# Stop just below support (long) or above resistance (short)
support_level = find_nearest_support(entry_price)
long_stop = support_level - 0.01  # Penny below support
```

## ⚙️ Stop Loss Configuration by Risk Profile

### CONSERVATIVE Profile
- **Default Method:** PERCENTAGE
- **Stop Distance:** 3% (tight stops)
- **ATR Multiplier:** 1.5x (conservative)
- **Philosophy:** Preserve capital, limit losses

### MODERATE Profile
- **Default Method:** PERCENTAGE
- **Stop Distance:** 4% (balanced stops)
- **ATR Multiplier:** 2.0x (standard)
- **Philosophy:** Balance risk and reward

### AGGRESSIVE Profile
- **Default Method:** ATR
- **Stop Distance:** 5% (wider stops)
- **ATR Multiplier:** 2.5x (give room to breathe)
- **Philosophy:** Let winners run, accept volatility

## 📊 Strategy-Specific Stop Methods

### Trend Following Strategies
```python
# Use ATR stops - adapt to volatility
# Trending markets need room to breathe
stop_method = StopLossMethod.ATR
atr_multiplier = 2.5
```

### Mean Reversion Strategies
```python
# Use tight percentage stops - quick moves expected
# Mean reversion happens fast
stop_method = StopLossMethod.PERCENTAGE
stop_pct = 0.03  # 3% stops
```

### Momentum Strategies
```python
# Use ATR stops - ride the momentum
# Volatile breakouts need wider stops
stop_method = StopLossMethod.ATR
atr_multiplier = 3.0  # Extra room
```

### Buy & Hold Strategies
```python
# Use wide percentage stops - long-term focus
# Ignore short-term noise
stop_method = StopLossMethod.PERCENTAGE
stop_pct = 0.08  # 8% stops
```

## 🔧 Implementation Details

### Automatic Stop Loss Placement
```python
def _setup_stop_loss(self, entry_order, order_info):
    """Automatically place stop loss after entry fills"""
    if order_info['is_long']:
        # Long position - stop below entry
        stop_order = self.sell(
            exectype=bt.Order.Stop,
            price=order_info['stop_price'],
            size=entry_order.executed.size
        )
    else:
        # Short position - stop above entry
        stop_order = self.buy(
            exectype=bt.Order.Stop,
            price=order_info['stop_price'],
            size=entry_order.executed.size
        )
```

### Stop Loss Calculation
```python
def get_stop_loss_price(self, entry_price: float, is_long: bool,
                       method: StopLossMethod = None, atr_value: float = None) -> float:
    """Calculate stop loss price using specified method"""

    method = method or self.config['stop_loss_method']

    if method == StopLossMethod.PERCENTAGE:
        stop_pct = self.config['stop_loss_pct']
        if is_long:
            return entry_price * (1 - stop_pct)
        else:
            return entry_price * (1 + stop_pct)

    elif method == StopLossMethod.ATR:
        if atr_value is None:
            return self.get_stop_loss_price(entry_price, is_long,
                                          StopLossMethod.PERCENTAGE)

        atr_multiplier = self.config.get('atr_multiplier', 2.0)
        if is_long:
            return entry_price - (atr_value * atr_multiplier)
        else:
            return entry_price + (atr_value * atr_multiplier)
```

## 📈 Stop Loss Examples

### AAPL Stock - Different Methods
**Entry Price:** $150.00
**Current ATR:** $3.50

#### Percentage Stop (4%)
- **Long Stop:** $150 × 0.96 = $144.00
- **Risk per share:** $6.00
- **Simple and predictable**

#### ATR Stop (2x multiplier)
- **Long Stop:** $150 - ($3.50 × 2) = $143.00
- **Risk per share:** $7.00
- **Adapts to volatility**

#### Support Stop (Technical)
- **Support Level:** $146.50
- **Long Stop:** $146.49
- **Risk per share:** $3.51
- **Based on chart structure**

### TSLA Stock - High Volatility
**Entry Price:** $200.00
**Current ATR:** $12.00

#### Conservative (3% + low ATR)
- **Percentage Stop:** $200 × 0.97 = $194.00
- **ATR Stop:** $200 - ($12 × 1.5) = $182.00
- **Uses ATR (wider) for high volatility stock**

#### Aggressive (5% + high ATR)
- **Percentage Stop:** $200 × 0.95 = $190.00
- **ATR Stop:** $200 - ($12 × 2.5) = $170.00
- **Uses ATR (much wider) for swing room**

## ⚠️ Stop Loss Challenges

### Slippage
- **Market gaps** can cause stops to fill below stop price
- **Low liquidity** can worsen slippage
- **Solution:** Use stop-limit orders for better control

### Whipsaws
- **Tight stops** get hit by normal volatility
- **Creates frequent small losses**
- **Solution:** Use ATR stops in volatile markets

### Weekend Gaps
- **Stocks can gap** past stop levels
- **Crypto trades 24/7** - less gapping
- **Solution:** Reduce position sizes before weekends

## 🎪 Advanced Stop Management

### Trailing Stops
```python
# Move stop up as price moves favorably
def update_trailing_stop(self, current_price):
    if self.position.size > 0:  # Long position
        new_stop = current_price * 0.96  # 4% trailing
        if new_stop > self.current_stop:
            self.current_stop = new_stop
```

### Time-Based Stops
```python
# Exit if trade hasn't worked after X bars
def check_time_stop(self):
    if self.bars_in_trade > self.max_bars_in_trade:
        self.exit_position(reason="Time stop")
```

### Volatility Adjustments
```python
# Widen stops in high volatility
def adjust_stop_for_volatility(self, base_stop):
    current_vix = get_vix_level()
    if current_vix > 30:  # High volatility
        return base_stop * 1.5  # 50% wider stops
    return base_stop
```

## 📊 Stop Loss Metrics

### Key Metrics to Track
- **Average Stop Distance:** Mean % risk per trade
- **Stop Hit Rate:** % of trades stopped out
- **Average Stop Loss:** Mean $ loss when stopped
- **Slippage Rate:** Actual vs intended stop fills
- **Whipsaw Rate:** Stops hit then price reverses

### Monitoring Dashboard
```python
metrics = strategy.get_risk_metrics()
print(f"Stop Hit Rate: {metrics['stop_hit_rate']*100:.1f}%")
print(f"Average Stop Loss: ${metrics['avg_stop_loss']:.2f}")
print(f"Slippage Rate: {metrics['slippage_rate']*100:.2f}%")
```

## 🚀 Best Practices

### DO ✅
- **ALWAYS use stop losses** - no exceptions
- Match stop method to strategy type
- Adjust stops for volatility
- Monitor slippage and adjust
- Test different stop methods
- Use position sizing with stops

### DON'T ❌
- Trade without stops (EVER!)
- Use mental stops (place actual orders)
- Set stops too tight (whipsaws)
- Set stops too wide (large losses)
- Ignore slippage costs
- Move stops against you

## 🔬 Testing Stop Losses

```python
def test_stop_loss_calculation():
    """Test stop loss calculations"""
    risk_manager = RiskManager(mock_strategy, RiskLevel.MODERATE)

    # Test percentage stops
    long_stop = risk_manager.get_stop_loss_price(100, is_long=True)
    assert long_stop == 96.0  # 4% below for moderate

    short_stop = risk_manager.get_stop_loss_price(100, is_long=False)
    assert short_stop == 104.0  # 4% above for moderate

    # Test ATR stops
    atr_stop = risk_manager.get_stop_loss_price(
        100, is_long=True,
        method=StopLossMethod.ATR,
        atr_value=2.0
    )
    assert atr_stop == 96.0  # 100 - (2.0 * 2.0) = 96
```

## 📈 Stop Loss Performance Impact

### Proper Stops vs No Stops (TSLA 2020-2024)
- **With Stops:** Max loss per trade = 4% of position
- **Without Stops:** Max loss per trade = 100% of position
- **Result:** Stops prevent account destruction

### Tight vs Wide Stops (Backtest Results)
- **3% Stops:** Higher win rate, more trades, lower profits
- **6% Stops:** Lower win rate, fewer trades, higher profits
- **Sweet Spot:** 4% stops balance frequency and profit

**Bottom Line: Stop losses are your insurance policy. Every professional trader uses them. Every account without them eventually blows up.** 🛑
# Portfolio Heat Management

## 🌡️ Core Principle: Monitor Total Risk Exposure

**Portfolio Heat** = Total amount of capital at risk across all open positions

**BEFORE (Unlimited Risk):**
```python
# Could have 10 positions each risking 95% = 950% portfolio risk!
# Recipe for account destruction
```

**AFTER (Controlled Risk):**
```python
# Maximum 10% portfolio heat across ALL positions
# Professional risk management
```

## 📊 Portfolio Heat Formula

### Basic Calculation
```
Portfolio Heat = Σ (Position Size × Risk Per Share) / Account Value

For each position:
Risk Per Share = |Entry Price - Stop Loss Price|
Position Risk = Position Size × Risk Per Share
Total Heat = Sum of all Position Risks / Account Value
```

### Example Portfolio
**Account Value:** $100,000

| Symbol | Position Size | Entry | Stop | Risk/Share | Position Risk |
|--------|---------------|-------|------|------------|---------------|
| AAPL   | 100 shares   | $150  | $144 | $6         | $600         |
| TSLA   | 50 shares    | $200  | $190 | $10        | $500         |
| GOOGL  | 20 shares    | $2500 | $2400| $100       | $2000        |

**Total Portfolio Risk:** $600 + $500 + $2000 = $3,100
**Portfolio Heat:** $3,100 / $100,000 = 3.1% ✅

## 🎯 Heat Limits by Risk Profile

### CONSERVATIVE Profile
- **Maximum Portfolio Heat:** 8%
- **Target Heat:** 4-6%
- **Max Positions:** 2
- **Philosophy:** Extreme safety first

### MODERATE Profile
- **Maximum Portfolio Heat:** 10%
- **Target Heat:** 6-8%
- **Max Positions:** 3
- **Philosophy:** Balanced approach

### AGGRESSIVE Profile
- **Maximum Portfolio Heat:** 12%
- **Target Heat:** 8-10%
- **Max Positions:** 4
- **Philosophy:** Higher returns, accept more risk

## ⚙️ Heat Monitoring Implementation

### Real-Time Heat Calculation
```python
class PortfolioHeatMonitor:
    def __init__(self, max_heat: float):
        self.max_heat = max_heat
        self.position_risks = {}  # position_id -> risk_amount

    def calculate_current_heat(self, account_value: float) -> float:
        """Calculate current portfolio heat percentage"""
        total_risk = sum(self.position_risks.values())
        return total_risk / account_value if account_value > 0 else 0

    def can_add_position(self, new_position_risk: float,
                        account_value: float) -> bool:
        """Check if adding new position would exceed heat limit"""
        current_heat = self.calculate_current_heat(account_value)
        new_risk_pct = new_position_risk / account_value
        return (current_heat + new_risk_pct) <= self.max_heat
```

### Pre-Trade Heat Check
```python
def should_enter_trade(self) -> bool:
    """Check all risk controls before entering trade"""
    # Calculate what the new position risk would be
    entry_price = self.data.close[0]
    stop_price = self.get_stop_loss_price(entry_price, is_long=True)
    position_size = self.calculate_position_size(entry_price, stop_price)

    if position_size <= 0:
        return False

    # Check portfolio heat limit
    new_position_risk = position_size * abs(entry_price - stop_price)
    account_value = self.strategy.broker.getvalue()

    if not self.heat_monitor.can_add_position(new_position_risk, account_value):
        self.log("TRADE REJECTED - Would exceed portfolio heat limit")
        return False

    return True
```

## 🔥 Heat Level Warnings and Actions

### Heat Level Thresholds
```python
def check_heat_warnings(self, current_heat: float):
    """Issue warnings and take action based on heat level"""

    if current_heat > self.max_heat * 0.9:  # 90% of limit
        self.log("⚠️  WARNING: Portfolio heat at 90% of maximum!")

    if current_heat > self.max_heat * 0.95:  # 95% of limit
        self.log("🚨 CRITICAL: Portfolio heat at 95% of maximum!")
        # Start reducing positions

    if current_heat > self.max_heat:  # Over limit
        self.log("🛑 EMERGENCY: Portfolio heat exceeded maximum!")
        # Force position reduction
```

### Automatic Heat Reduction
```python
def reduce_portfolio_heat(self):
    """Automatically reduce heat when over limits"""
    current_heat = self.calculate_current_heat()

    if current_heat > self.max_heat:
        # Close most risky position first
        highest_risk_position = self.find_highest_risk_position()
        self.close_position(highest_risk_position,
                           reason="Portfolio heat reduction")
```

## 📈 Heat Management Strategies

### Strategy 1: Equal Heat Distribution
```python
# Distribute risk equally across positions
target_heat_per_position = max_heat / max_positions
# Conservative: 8% / 2 = 4% per position
# Moderate: 10% / 3 = 3.3% per position
# Aggressive: 12% / 4 = 3% per position
```

### Strategy 2: Conviction-Based Heat
```python
# Allocate more heat to high-conviction trades
high_conviction_trade = 4% heat  # Double normal
medium_conviction_trade = 2% heat  # Normal
low_conviction_trade = 1% heat  # Half normal
```

### Strategy 3: Volatility-Adjusted Heat
```python
# Reduce heat for volatile assets
def adjust_heat_for_volatility(base_heat, volatility):
    if volatility > 0.30:  # High volatility (30%+ annual)
        return base_heat * 0.5  # Halve the heat
    elif volatility > 0.20:  # Medium volatility
        return base_heat * 0.75  # Reduce by 25%
    return base_heat  # Normal heat for stable assets
```

## 🎪 Portfolio Heat Examples

### Conservative Portfolio ($50K Account)
**Heat Limit:** 8% = $4,000 maximum risk

| Position | Size | Entry | Stop | Risk | Heat |
|----------|------|-------|------|------|------|
| SPY ETF  | 100  | $400  | $384 | $1,600| 3.2% |
| AAPL     | 50   | $150  | $144 | $300  | 0.6% |
| **Total**|      |       |      |$1,900 |3.8% ✅|

**Result:** Well within 8% limit, room for one more position.

### Aggressive Portfolio ($100K Account)
**Heat Limit:** 12% = $12,000 maximum risk

| Position | Size | Entry | Stop | Risk  | Heat |
|----------|------|-------|------|-------|------|
| QQQ      | 200  | $350  | $332 | $3,600| 3.6% |
| TSLA     | 100  | $200  | $180 | $2,000| 2.0% |
| NVDA     | 50   | $800  | $760 | $2,000| 2.0% |
| AMZN     | 30   | $3000 | $2850| $4,500| 4.5% |
| **Total**|      |       |      |$12,100|12.1%❌|

**Result:** Slightly over limit! Need to reduce smallest position.

## 🚨 Heat Emergency Procedures

### Level 1: 90% of Heat Limit
- **Action:** Warning message only
- **Impact:** No trading restrictions
- **Response:** Monitor closely, be selective

### Level 2: 95% of Heat Limit
- **Action:** No new positions allowed
- **Impact:** Entry signals rejected
- **Response:** Wait for position to close

### Level 3: 100%+ of Heat Limit
- **Action:** Force close highest risk position
- **Impact:** Automatic risk reduction
- **Response:** Emergency position management

## 📊 Heat Monitoring Dashboard

### Key Heat Metrics
```python
def get_heat_metrics(self) -> Dict[str, float]:
    """Get comprehensive heat monitoring metrics"""
    account_value = self.strategy.broker.getvalue()
    current_heat = self.calculate_current_heat(account_value)

    return {
        'current_heat': current_heat,
        'heat_utilization': current_heat / self.max_heat,
        'remaining_heat': self.max_heat - current_heat,
        'positions_count': len(self.position_risks),
        'max_positions': self.max_positions,
        'average_position_heat': current_heat / len(self.position_risks) if self.position_risks else 0,
        'largest_position_heat': max(self.position_risks.values()) / account_value if self.position_risks else 0
    }
```

### Heat Dashboard Output
```
📊 PORTFOLIO HEAT DASHBOARD
==============================
Current Heat: 7.8% / 10.0% (78% utilized)
Remaining Heat: 2.2%
Active Positions: 3 / 3 maximum
Average Position Heat: 2.6%
Largest Position Heat: 4.1%
Heat Status: NORMAL ✅
```

## 🔧 Integration with Position Sizing

### Heat-Aware Position Sizing
```python
def calculate_heat_adjusted_size(self, entry_price: float,
                                stop_price: float) -> int:
    """Calculate position size considering heat limits"""
    # Normal risk-based calculation
    normal_size = self.calculate_position_size(entry_price, stop_price)
    normal_risk = normal_size * abs(entry_price - stop_price)

    # Check heat constraints
    account_value = self.strategy.broker.getvalue()
    current_heat = self.heat_monitor.calculate_current_heat(account_value)
    remaining_heat = self.max_heat - current_heat
    max_risk_allowed = remaining_heat * account_value

    # Use smaller of normal size or heat-limited size
    if normal_risk <= max_risk_allowed:
        return normal_size
    else:
        heat_limited_size = int(max_risk_allowed / abs(entry_price - stop_price))
        return heat_limited_size
```

## 🚀 Best Practices

### DO ✅
- Monitor heat in real-time
- Set appropriate heat limits for your risk profile
- Reserve heat capacity for high-conviction trades
- Automatically reduce heat when over limits
- Track heat metrics and trends
- Adjust heat for market volatility

### DON'T ❌
- Ignore portfolio heat (focus only on individual positions)
- Set heat limits too high (>15%)
- Add positions when near heat limit
- Forget to update heat when positions close
- Use fixed position sizes regardless of heat
- Override heat limits for "sure thing" trades

## 🔬 Testing Heat Management

```python
def test_heat_monitoring():
    """Test portfolio heat calculations"""
    monitor = PortfolioHeatMonitor(max_heat=0.10)  # 10%
    account_value = 10000

    # Add first position: $200 risk
    monitor.position_risks['pos1'] = 200
    heat1 = monitor.calculate_current_heat(account_value)
    assert heat1 == 0.02  # 2%

    # Add second position: $300 risk
    monitor.position_risks['pos2'] = 300
    heat2 = monitor.calculate_current_heat(account_value)
    assert heat2 == 0.05  # 5%

    # Check if can add $600 risk position
    can_add = monitor.can_add_position(600, account_value)
    assert can_add == False  # 5% + 6% = 11% > 10% limit
```

## 📈 Heat Performance Impact

### Controlled Heat vs Unlimited Risk
- **With Heat Control:** Maximum portfolio loss = 12%
- **Without Heat Control:** Maximum portfolio loss = 100%
- **Result:** Heat management prevents account destruction

### Different Heat Limits (Backtest Results)
- **8% Heat Limit:** Lower returns, much safer
- **10% Heat Limit:** Balanced returns and safety
- **12% Heat Limit:** Higher returns, more volatility
- **15%+ Heat Limit:** Dangerous territory

**Bottom Line: Portfolio heat management is your safety net. It prevents you from having too much risk in the market at once, ensuring you can survive bad periods and trade another day.** 🌡️
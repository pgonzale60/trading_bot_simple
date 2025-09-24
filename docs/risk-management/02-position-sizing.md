# Position Sizing Framework

## 🎯 Core Principle: Risk-Based Position Sizing

**OLD APPROACH (Dangerous):**
```python
# Risked 95% of account on every trade!
cash = self.broker.getcash() * 0.95
size = int(cash / self.data.close[0])
```

**NEW APPROACH (Professional):**
```python
# Risk only 2% of account per trade
Position Size = Risk Amount ÷ (Entry Price - Stop Price)
```

## 📊 Position Sizing Formula

### Basic Formula
```
Position Size = (Account Value × Risk %) ÷ (Entry Price - Stop Loss Price)
```

### Example Calculation
- **Account Value:** $10,000
- **Risk Per Trade:** 2% = $200
- **Entry Price:** $100
- **Stop Loss:** $96 (4% stop)
- **Position Size:** $200 ÷ ($100 - $96) = 50 shares
- **Position Value:** 50 × $100 = $5,000 (50% of account)
- **Maximum Loss:** 50 × $4 = $200 (2% of account) ✅

## 🛡️ Risk Profile Limits

### CONSERVATIVE Profile
- **Risk Per Trade:** 1.5%
- **Max Position Size:** 12% of account
- **Max Positions:** 2
- **Portfolio Heat Limit:** 8%

### MODERATE Profile
- **Risk Per Trade:** 2.0%
- **Max Position Size:** 15% of account
- **Max Positions:** 3
- **Portfolio Heat Limit:** 10%

### AGGRESSIVE Profile
- **Risk Per Trade:** 2.5%
- **Max Position Size:** 20% of account
- **Max Positions:** 4
- **Portfolio Heat Limit:** 12%

## ⚙️ Implementation Details

### RiskManager.calculate_position_size()
```python
def calculate_position_size(self, entry_price: float, stop_price: float) -> int:
    """Calculate position size based on risk management rules"""
    account_value = self.strategy.broker.getvalue()
    risk_amount = account_value * self.config['risk_per_trade']

    # Calculate risk per share
    risk_per_share = abs(entry_price - stop_price)
    if risk_per_share == 0:
        return 0

    # Calculate ideal position size
    ideal_size = int(risk_amount / risk_per_share)

    # Apply position size limits
    max_position_value = account_value * self.config['max_position_pct']
    max_size_allowed = int(max_position_value / entry_price)

    # Return the smaller of ideal size or maximum allowed
    return min(ideal_size, max_size_allowed)
```

## 🔍 Position Size Validation

### Size Checks Applied
1. **Risk Check:** Position must not risk more than configured %
2. **Size Check:** Position must not exceed max position %
3. **Heat Check:** Must not exceed portfolio heat limit
4. **Capital Check:** Must have sufficient buying power
5. **Minimum Check:** Position must be at least 1 share

### Rejection Reasons
- `"Position size too small"` - Less than 1 share
- `"Exceeds position limit"` - Violates max position %
- `"Exceeds portfolio heat"` - Total risk too high
- `"Insufficient capital"` - Not enough buying power

## 📈 Strategy-Specific Adjustments

### Trend Following Strategies
- **Larger positions** allowed (volatility expected)
- **ATR-based stops** result in dynamic sizing
- **Multiple positions** common

### Mean Reversion Strategies
- **Smaller positions** preferred (quick moves)
- **Tight percentage stops** result in larger sizes
- **Fewer concurrent positions**

### Buy & Hold Strategies
- **Largest positions** allowed (long-term hold)
- **Wide stops** result in smaller sizes
- **Single large position** typical

## 🎪 Position Size Examples

### Small Cap Stock (High Volatility)
- **Entry:** $50
- **ATR Stop:** $47 (6% stop due to volatility)
- **2% Risk:** $200 on $10K account
- **Position Size:** $200 ÷ $3 = 66 shares
- **Position Value:** $3,300 (33% of account)

### Large Cap Stock (Low Volatility)
- **Entry:** $150
- **Percentage Stop:** $144 (4% stop)
- **2% Risk:** $200 on $10K account
- **Position Size:** $200 ÷ $6 = 33 shares
- **Position Value:** $4,950 (49% of account)

### High Price Stock
- **Entry:** $3,000 (like BRK.A)
- **Percentage Stop:** $2,880 (4% stop)
- **2% Risk:** $200 on $10K account
- **Position Size:** $200 ÷ $120 = 1.6 → 1 share
- **Position Value:** $3,000 (30% of account)

## ⚠️ Special Cases

### Insufficient Capital
When ideal position size exceeds account value:
```python
if position_value > account_value * 0.95:
    # Reduce to maximum affordable size
    size = int((account_value * max_position_pct) / entry_price)
```

### Crypto/High Volatility Assets
- **Wider stops** required (10-15% typical)
- **Smaller positions** result from large stops
- **Higher minimum volatility** assumptions

### Fractional Shares
- **Traditional Stocks:** Round down to whole shares
- **Crypto:** Can use fractional positions
- **ETFs:** Usually whole shares only

## 📊 Position Sizing Metrics

### Key Metrics Tracked
- **Average Position Size:** Mean % of account per position
- **Position Size Range:** Min/max position sizes
- **Risk Utilization:** Actual risk vs maximum allowed
- **Position Concentration:** Largest single position
- **Size Distribution:** Histogram of position sizes

### Monitoring Dashboard
```python
metrics = strategy.get_risk_metrics()
print(f"Average Position: {metrics['avg_position_pct']*100:.1f}%")
print(f"Largest Position: {metrics['max_position_pct']*100:.1f}%")
print(f"Risk Utilization: {metrics['risk_utilization']*100:.1f}%")
```

## 🚀 Best Practices

### DO ✅
- Always use the risk-based formula
- Respect maximum position limits
- Monitor portfolio heat continuously
- Adjust for strategy type and volatility
- Test position sizing thoroughly

### DON'T ❌
- Use fixed dollar amounts
- Ignore position size limits
- Risk more than configured %
- Size positions on "gut feel"
- Forget to validate calculations

## 🔬 Testing Position Sizing

```python
# Test position sizing logic
def test_position_sizing():
    risk_manager = RiskManager(strategy, RiskLevel.MODERATE)

    # Test normal case
    size = risk_manager.calculate_position_size(100, 96)  # 4% stop
    expected = 50  # $200 risk / $4 stop = 50 shares
    assert size == expected

    # Test size limit case
    size = risk_manager.calculate_position_size(10, 9.6)  # Small price, tight stop
    # Should be limited by max_position_pct, not ideal risk size
```

**Bottom Line: Proper position sizing is the foundation of risk management. Get this right and everything else follows.** 🎯
# Professional Risk-Managed Trading Bot

[![codecov](https://codecov.io/github/pgonzale60/trading_bot_simple/graph/badge.svg)](https://codecov.io/github/pgonzale60/trading_bot_simple)
[![Tests](https://github.com/pgonzale60/trading_bot_simple/workflows/Trading%20Bot%20Tests/badge.svg)](https://github.com/pgonzale60/trading_bot_simple/actions/workflows/tests.yml)

A **professional algorithmic trading system** with comprehensive risk management, transforming dangerous gambling strategies into systematic, capital-preserving trading approaches.

## 🎯 **[VIEW PERFORMANCE REPORT →](PERFORMANCE_REPORT.md)**

**Key Results:** 76.4% strategy success rate across 250 tests, 97% risk reduction vs gambling approaches, professional risk management with 2% max risk per trade.

## 🛡️ **Risk Management Revolution**

This system **prevents account destruction** through professional risk controls:
- **97% safer** risk per trade (2% vs 95% account risk)
- **84% safer** position sizes (20% vs 95% of account max)
- **Circuit breakers** halt trading at 15-18% drawdown
- **Stop losses** on every single trade
- **Portfolio heat monitoring** limits total exposure

## 🚀 Quick Setup

### Option 1: GitHub Codespaces (Recommended)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/pgonzale60/trading_bot_simple)

Click the badge above to open in Codespaces. Environment will be automatically configured with micromamba.

### Option 2: Local Setup (macOS/Linux)
```bash
# Create and activate environment
micromamba env create -f environment-simple.yml -y
micromamba activate trading-bot-simple

# Test everything works
python test_bot.py

# Run the bot
python main.py
```

## 🎯 What This System Does
- **Risk-managed trading** across stocks, ETFs, and cryptocurrencies
- **Multiple professional strategies** (SMA, RSI, MACD, Buy & Hold, etc.)
- **Automatic position sizing** based on 2% risk per trade
- **Complete portfolio protection** with stop losses and circuit breakers
- **Professional performance tracking** and comprehensive reporting

## 📈 Available Risk-Managed Strategies
- **SMA (Simple Moving Average)**: Trend following with volatility-adjusted stops
- **RSI (Relative Strength Index)**: Mean reversion with tight risk control
- **MACD**: Momentum trading with professional position sizing
- **Buy & Hold**: Long-term investing with drawdown protection
- **All strategies**: Automatic risk management, stop losses, and position sizing

## 🧪 Advanced Testing Modes

### 1. Single Strategy Test (Original)
```bash
# Test SMA strategy on Apple
python main.py --mode single --symbol AAPL --strategy sma --short 10 --long 30

# Test RSI strategy on Bitcoin
python main.py --mode single --symbol BTC-USD --strategy rsi --rsi-period 14

# Test different strategies
python main.py --mode single --strategy macd --symbol TSLA
python main.py --mode single --strategy bollinger --symbol SPY
```

### 2. Multi-Asset Risk-Managed Testing ⭐
```bash
# Quick test across stocks and crypto (RECOMMENDED - see performance report!)
python main.py --mode multi --test-mode quick

# Test all risk-managed strategies on stocks only
python main.py --mode multi --test-mode stocks

# Test all risk-managed strategies on cryptocurrencies only
python main.py --mode multi --test-mode crypto

# Full comprehensive test with risk management (may take 30+ minutes)
python main.py --mode multi --test-mode full
```

**All tests now use AGGRESSIVE risk profile (2.5% risk per trade) by default for maximum growth potential with professional protection.**

### 3. Parameter Optimization
```bash
# Find best SMA parameters for Apple
python main.py --mode optimize --symbol AAPL

# Optimize for different assets
python main.py --mode optimize --symbol BTC-USD
python main.py --mode optimize --symbol SPY
```

### 4. Results Visualization
```bash
# Generate charts and analysis from cached results
python main.py --mode visualize
```

## 🧪 Testing

### Run All Tests
```bash
# Run comprehensive unit test suite
python run_tests.py

# Run with pytest (alternative)
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Test Modules
```bash
# Test trading strategies
python run_tests.py --module test_strategies

# Test data fetching
python run_tests.py --module test_data

# Test multi-asset functionality
python run_tests.py --module test_multi_asset_tester

# Test parameter optimization
python run_tests.py --module test_optimizer
```

## 📊 What You'll Discover

**[See the complete PERFORMANCE REPORT for detailed results →](PERFORMANCE_REPORT.md)**

The risk-managed multi-asset testing reveals:
- **76.4% strategy success rate** across 250 strategy-asset combinations
- **Professional risk control** prevents account destruction (2% max risk per trade)
- **5 different strategies tested** across 41 assets (23 stocks + 18 cryptos)
- **RSI strategy shows highest returns** but with significant volatility
- **SMA and MACD provide consistent performance** with good risk control

**Key Finding:** Risk management transforms dangerous gambling (95% account risk) into professional trading with systematic position sizing and stop losses!

## 📁 Project Structure
```
trading_bot/
├── PERFORMANCE_REPORT.md     # 🎯 COMPREHENSIVE PERFORMANCE ANALYSIS
├── main.py                   # Advanced trading bot with multiple modes
├── risk_managed_strategies.py # 🛡️ Professional risk-managed strategies
├── risk_management.py        # 🛡️ Core risk management engine
├── risk_managed_strategy.py  # 🛡️ Base class for all strategies
├── risk_config.py           # 🛡️ Risk configuration system
├── test_risk_management.py  # 🛡️ Risk management validation tests
├── multi_asset_tester.py    # Test strategies across stocks and crypto
├── strategies.py            # Legacy strategies (now risk-managed)
├── data.py                  # Yahoo Finance data fetching
├── docs/risk-management/    # 📚 Complete risk management documentation
│   ├── README.md           # Quick start guide
│   ├── 01-overview.md      # Risk philosophy and transformation
│   ├── 02-position-sizing.md # Professional position sizing
│   ├── 03-stop-losses.md   # Stop loss management
│   ├── 04-portfolio-heat.md # Portfolio risk monitoring
│   ├── 05-drawdown-protection.md # Circuit breaker systems
│   ├── 06-strategy-profiles.md # Strategy-specific risk settings
│   ├── 07-configuration.md # Configuration guide
│   ├── 08-examples.md      # Complete working examples
│   └── 09-testing.md       # Comprehensive testing framework
├── cache/                  # JSON cache files for test results
├── data_cache/            # Yahoo Finance data cache
└── tests/                 # Unit test suite
```

## 🛡️ **Professional Risk Management**

This system now includes **enterprise-grade risk management** that:
- **Prevents account destruction** through systematic risk controls
- **Transforms gambling** into professional algorithmic trading
- **Provides complete documentation** for implementation and operation
- **Includes comprehensive testing** to validate all safety systems
- **Offers multiple risk profiles** from conservative to aggressive

**[Read the complete risk management documentation →](docs/risk-management/README.md)**
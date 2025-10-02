# Professional Risk-Managed Trading Bot

[![codecov](https://codecov.io/github/pgonzale60/trading_bot_simple/graph/badge.svg)](https://codecov.io/github/pgonzale60/trading_bot_simple)
[![Tests](https://github.com/pgonzale60/trading_bot_simple/workflows/Trading%20Bot%20Tests/badge.svg)](https://github.com/pgonzale60/trading_bot_simple/actions/workflows/tests.yml)

A **professional algorithmic trading system** with comprehensive risk management, transforming dangerous gambling strategies into systematic, capital-preserving trading approaches.

## 🎯 **[VIEW PERFORMANCE REPORT →](PERFORMANCE_REPORT.md)**

**Key Results:** 4,160 optimized strategy/asset combinations (each asset funded independently), 40/40 assets profitable under best parameters, 97% risk reduction vs gambling approaches, professional risk management with 2% max risk per trade.

> ⚠️ **Scope clarification:** Results represent single-asset simulations. The system does not yet calculate diversified portfolio performance, correlations, or allocation-driven metrics.

## 🛡️ **Risk Management Revolution**

This system **prevents account destruction** through professional risk controls:
- **97% safer** risk per trade (2% vs 95% account risk)
- **84% safer** position sizes (20% vs 95% of account max)
- **Circuit breakers** halt trading at 15-18% drawdown
- **Stop losses** on every single trade
- **Portfolio heat monitoring** (for hypothetical simultaneous positions) limits total exposure

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
- **Comprehensive position protection** with stop losses and circuit breakers
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

### 3. Portfolio Mode (Experimental)
```bash
# Run the early blended-portfolio scaffold across the quick sample universe
python main.py --mode portfolio --test-mode quick

# Focus on equities only within portfolio mode
python main.py --mode portfolio --test-mode stocks

# Focus on crypto sleeve only within portfolio mode
python main.py --mode portfolio --test-mode crypto

# Load the full 41-asset universe (longer runtime)
python main.py --mode portfolio --test-mode full
```

> 🧪 Portfolio mode is in active development for v3.0.0. The current release wires
> up orchestration so multiple assets share a single Backtrader run; upcoming
> issues will layer on shared state, portfolio risk management, and rebalancing.

### 4. Parameter Optimization
```bash
# Quick sweep for a single strategy (defaults to SMA when omitted)
python main.py --mode optimize --opt-mode single --symbol AAPL --strategy macd

# Optimize every strategy for one symbol
python main.py --mode optimize --opt-mode all --symbol BTC-USD

# Run the comprehensive cross-asset optimizer (41 symbols × 7 strategies)
python main.py --mode optimize --opt-mode multi-symbol --opt-symbols all --start 2020-01-01
```

### 5. Results Visualization
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

The optimized multi-asset testing reveals **per-asset performance only**:
- **4,160 parameter evaluations** covering seven strategies across 40 tradable assets (SQ delisted)
- **Each asset finished profitable** once tuned parameters and risk controls were applied
- **SMA / EMA / MACD** now outperform BUY_HOLD on average by 500-1,000% without breaking risk caps
- **BOLLINGER and RSI** deliver 95%+ win rates as defensive overlays
- **Momentum** remains a research target—optimizer confirms it trails other approaches
- ❗ **Combined portfolio statistics (diversification, blended Sharpe, correlations) are not part of the current reports.**

**Key Finding:** Risk management transforms dangerous gambling (95% account risk) into professional trading with systematic position sizing and stop losses!

## 📁 Project Structure
```
trading_bot_simple/
├── PERFORMANCE_REPORT.md        # 🎯 COMPREHENSIVE PERFORMANCE ANALYSIS
├── ASSET_SELECTION_METHODOLOGY.md # 📋 Research-based asset selection approach
├── CHANGELOG.md                 # Version history and improvements
├── main.py                      # Advanced trading bot with multiple modes
├── multi_asset_tester.py        # Test strategies across 41 assets (stocks + crypto)
├── results_visualizer.py        # Performance visualization and analysis
├── optimizer.py                 # Parameter optimization tools
├── risk_managed_strategies.py   # 🛡️ Professional risk-managed strategies
├── risk_management.py           # 🛡️ Core risk management engine
├── risk_managed_strategy.py     # 🛡️ Base class for all strategies
├── risk_config.py              # 🛡️ Risk configuration system
├── data.py                     # Yahoo Finance data fetching
├── visualization.py            # Basic performance charts
├── test_bot.py                 # System verification script
├── run_tests.py                # Test runner with module selection
├── environment-simple.yml      # Micromamba dependencies
├── cache/                      # JSON cache files for test results
├── data_cache/                 # Yahoo Finance data cache
├── docs/risk-management/       # 📚 Complete risk management documentation
│   ├── README.md              # Quick start guide
│   ├── 01-overview.md         # Risk philosophy and transformation
│   ├── 02-position-sizing.md  # Professional position sizing
│   ├── 03-stop-losses.md      # Stop loss management
│   ├── 04-portfolio-heat.md   # Portfolio risk monitoring
│   ├── 05-drawdown-protection.md # Circuit breaker systems
│   ├── 06-strategy-profiles.md # Strategy-specific risk settings
│   ├── 07-configuration.md    # Configuration guide
│   ├── 08-examples.md         # Complete working examples
│   └── 09-testing.md          # Comprehensive testing framework
└── tests/                     # Unit test suite (53 tests, 100% passing)
    ├── test_risk_management.py   # 🛡️ Core risk management tests (15 tests)
    ├── test_results_visualizer.py # Visualization testing (12 tests)
    ├── test_multi_asset_tester.py # Multi-asset testing validation
    ├── test_optimizer.py          # Parameter optimization tests
    └── test_visualization.py      # Chart generation tests
```

## 🛡️ **Professional Risk Management**

This system now includes **enterprise-grade risk management** that:
- **Prevents account destruction** through systematic risk controls
- **Transforms gambling** into professional algorithmic trading
- **Provides complete documentation** for implementation and operation
- **Includes comprehensive testing** to validate all safety systems
- **Offers multiple risk profiles** from conservative to aggressive

**[Read the complete risk management documentation →](docs/risk-management/README.md)**

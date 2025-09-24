# Simple Trading Bot - Learning Project

[![codecov](https://codecov.io/github/pgonzale60/trading_bot_simple/graph/badge.svg)](https://codecov.io/github/pgonzale60/trading_bot_simple)
[![Tests](https://github.com/pgonzale60/trading_bot_simple/workflows/Trading%20Bot%20Tests/badge.svg)](https://github.com/pgonzale60/trading_bot_simple/actions/workflows/tests.yml)

A minimal trading bot to learn algorithmic trading basics with Python.

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

## 🎯 What This Does
- Fetches 2 years of stock data (default: AAPL)
- Runs a Moving Average Crossover strategy
- Shows buy/sell signals and performance stats
- Creates charts of results

## 📈 The Strategy
**Simple Moving Average Crossover:**
- **Buy**: When 10-day SMA crosses above 30-day SMA
- **Sell**: When 10-day SMA crosses below 30-day SMA

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

### 2. Multi-Asset Comparison (NEW!)
```bash
# Quick test across stocks and crypto
python main.py --mode multi --test-mode quick

# Test all strategies on stocks only
python main.py --mode multi --test-mode stocks

# Test all strategies on cryptocurrencies only
python main.py --mode multi --test-mode crypto

# Full comprehensive test (may take 30+ minutes)
python main.py --mode multi --test-mode full
```

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

The multi-asset testing will show you:
- **Which strategies work best on different asset types**
- **Whether strategies that work on stocks also work on crypto**
- **Consistency across different market conditions**
- **Risk-adjusted performance comparisons**

Available strategies: SMA, RSI, MACD, Bollinger Bands, EMA, Momentum, Buy & Hold

## 📁 Project Structure
```
trading_bot/
├── main.py                   # Advanced trading bot with multiple modes
├── strategies.py             # Multiple trading strategies (SMA, RSI, MACD, etc.)
├── multi_asset_tester.py     # Test strategies across stocks and crypto
├── optimizer.py              # Parameter optimization framework
├── results_visualizer.py     # Generate charts and analysis reports
├── data.py                   # Yahoo Finance data fetching
├── visualization.py          # Performance summaries
├── test_bot.py              # Basic system verification
├── run_tests.py             # Comprehensive unit test runner
├── tests/                   # Unit test suite
│   ├── test_strategies.py   # Strategy testing
│   ├── test_data.py         # Data fetching tests
│   ├── test_multi_asset_tester.py  # Multi-asset tests
│   └── test_optimizer.py    # Optimization tests
├── cache/                   # JSON cache files for test results
├── environment-simple.yml   # micromamba dependencies with testing tools
└── enterprise-version/      # Archived enterprise-grade specifications
```

## 🏗️ Enterprise Version Available

If you're interested in building a production-ready trading system, check the `enterprise-version/` directory which contains comprehensive specifications for:
- Security and encryption frameworks
- Regulatory compliance systems
- Risk management controls
- 6-phase development plan
- Production deployment guides
# Simple Trading Bot - Learning Project

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

## 🧪 Try Different Things
```bash
# Different stock
python main.py --symbol GOOGL

# Different moving average periods
python main.py --short 5 --long 20

# Different date range
python main.py --start 2020-01-01

# Different starting capital
python main.py --cash 50000
```

## 📁 Project Structure
```
trading_bot/
├── main.py                  # Main trading bot
├── strategy.py              # SMA crossover strategy
├── data.py                  # Yahoo Finance data fetching
├── visualization.py         # Performance charts and summaries
├── test_bot.py             # System verification
├── environment-simple.yml  # micromamba dependencies
├── .env.example            # Environment variables template
└── enterprise-version/     # Archived enterprise-grade specifications
```

## 🏗️ Enterprise Version Available

If you're interested in building a production-ready trading system, check the `enterprise-version/` directory which contains comprehensive specifications for:
- Security and encryption frameworks
- Regulatory compliance systems
- Risk management controls
- 6-phase development plan
- Production deployment guides
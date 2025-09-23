# Changelog

## v2.0.0 - Advanced Multi-Asset Testing Framework

### 🚀 Major Features Added
- **Multi-Asset Testing**: Test strategies across 15 stocks and 10 cryptocurrencies
- **Multiple Strategies**: Added RSI, MACD, Bollinger Bands, EMA, Momentum strategies
- **Parameter Optimization**: Systematic testing of different parameter combinations
- **Smart Caching**: JSON-based caching system for faster re-runs
- **Advanced Analytics**: Sharpe ratios, win rates, drawdowns, consistency analysis
- **Results Visualization**: Generate charts and comprehensive reports

### 🔧 Technical Improvements
- **Modular Architecture**: Separated concerns into focused modules
- **Performance Metrics**: Added comprehensive backtesting analytics
- **Error Handling**: Robust error handling for data fetching and analysis
- **Cross-Market Analysis**: Compare strategy effectiveness across asset types

### 📁 New Files
- `strategies.py` - Multiple trading strategy implementations
- `multi_asset_tester.py` - Cross-asset strategy testing framework
- `optimizer.py` - Parameter optimization tools
- `results_visualizer.py` - Chart generation and analysis reporting

### 🗑️ Removed Files
- `strategy.py` - Replaced by comprehensive `strategies.py`

### 🎯 New Usage Modes
```bash
# Single strategy test
python main.py --mode single --strategy rsi --symbol BTC-USD

# Multi-asset comparison
python main.py --mode multi --test-mode quick

# Parameter optimization
python main.py --mode optimize --symbol AAPL

# Generate analysis reports
python main.py --mode visualize
```

### 📊 Assets Tested
**Stocks**: AAPL, MSFT, GOOGL, AMZN, TSLA, SPY, QQQ, VTI, JPM, JNJ, PG, KO, WMT, XOM, GLD
**Crypto**: BTC-USD, ETH-USD, BNB-USD, ADA-USD, SOL-USD, DOT-USD, AVAX-USD, MATIC-USD, LINK-USD, UNI-USD

---

## v1.0.0 - Simple Trading Bot

### Features
- Basic SMA crossover strategy
- Single asset backtesting
- Yahoo Finance data integration
- Simple performance metrics
- Basic visualization
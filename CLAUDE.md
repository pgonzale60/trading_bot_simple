# Simple Trading Bot - Claude Configuration

## Project Overview
A minimal educational trading bot for learning algorithmic trading concepts with Python. Uses Backtrader framework with Yahoo Finance data for backtesting simple strategies.

## Quick Start Commands
```bash
# Environment setup
micromamba env create -f environment-simple.yml -y
micromamba activate trading-bot-simple

# Test system
python test_bot.py

# Run trading bot
python main.py
python main.py --symbol GOOGL --short 5 --long 20
python main.py --start 2020-01-01 --cash 50000

# Debug data issues
python -c "import yfinance as yf; print(yf.download('AAPL', period='5d'))"
```

## Project Structure
```
├── main.py              # Entry point with CLI arguments
├── strategy.py          # SMA crossover strategy (Backtrader)
├── data.py             # Yahoo Finance data fetching
├── visualization.py    # Performance summaries and charts
├── test_bot.py         # System verification script
└── environment-simple.yml  # Dependencies
```

## Core Dependencies
- **backtrader**: Trading strategy framework
- **yfinance**: Free market data from Yahoo Finance
- **pandas**: Data manipulation
- **matplotlib**: Chart visualization
- **numpy**: Numerical calculations

## Code Guidelines
- Keep it simple - this is for learning, not production
- Use descriptive variable names for financial concepts
- Add comments explaining trading logic
- Handle data fetch errors gracefully
- Print clear messages for buy/sell signals

## Common Issues & Solutions

### Data Problems
```bash
# Yahoo Finance rate limiting
# Solution: Add delays between requests or use smaller date ranges

# Missing data for symbol
# Solution: Try different symbols (AAPL, GOOGL, SPY work well)

# Network/SSL issues
# Solution: Try from different network environment

# Charts not showing
# Solution: Charts may not work in SSH/headless environments
```

### Strategy Development
```python
# Current strategy: SMA Crossover
# Buy: 10-day SMA > 30-day SMA
# Sell: 10-day SMA < 30-day SMA

# Experiment ideas:
# - Different periods (5/20, 15/50)
# - Add RSI indicator
# - Include stop-loss rules
# - Try different stocks
```

## Testing Approach
- `test_bot.py` verifies all imports and basic functionality
- Test with known stable stocks (AAPL, SPY) first
- Use recent date ranges (last 1-2 years) for reliability
- Compare results across different parameter combinations

## Development Workflow
1. Test changes with `python test_bot.py`
2. Run quick backtest: `python main.py --start 2023-01-01`
3. Try different parameters to understand strategy behavior
4. Experiment with new stocks and time periods

## File Purposes
- **main.py**: CLI interface, orchestrates everything
- **strategy.py**: Contains the SMA crossover logic in Backtrader format
- **data.py**: Handles Yahoo Finance API calls and data formatting
- **visualization.py**: Creates performance summaries and handles chart display
- **test_bot.py**: Verifies environment setup and basic functionality

## Learning Goals
- Understand how algorithmic trading strategies work
- Learn backtesting concepts and limitations
- Experiment with technical indicators
- See how parameter changes affect performance
- Understand buy/sell signal generation

## Next Steps for Learning
- Try different moving average periods
- Test on various stocks and time periods
- Add transaction costs to backtesting
- Implement other indicators (RSI, MACD)
- Study why some periods/stocks work better than others

## Enterprise Version
Complex production-ready specifications are archived in `enterprise-version/` directory for future reference.
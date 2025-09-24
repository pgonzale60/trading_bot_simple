# Trading Bot Project - Claude Configuration

## Project Overview
This is a Python-based trading bot for programmatically testing and implementing investment strategies. The project uses modern Python tooling and popular trading frameworks for backtesting, risk management, and modular strategy development.

## Tech Stack Decisions
- **Environment Management**: micromamba (lightweight, fast, perfect for conda-forge packages)
- **Trading Framework**: Backtrader (simple, flexible, great for strategy development)
- **Alternative Option**: Freqtrade (if focusing on crypto) or QuantConnect (for cloud-based infrastructure)
- **Linting/Formatting**: ruff (extremely fast Python linter and formatter written in Rust)
- **Type Checking**: mypy
- **Testing**: pytest

## Common Commands

### Environment Management (micromamba)
```bash
# Create environment
micromamba create -n trading-bot python=3.11 -c conda-forge -y
micromamba activate trading-bot

# Install dependencies
micromamba install -n trading-bot -c conda-forge pandas numpy matplotlib pytest mypy -y
pip install backtrader yfinance

# Alternative: Install from environment file
micromamba env create -f environment.yml
```

### Code Quality (ruff + mypy)
```bash
# Linting and formatting with ruff
ruff check .                    # Check for linting issues
ruff check . --fix              # Auto-fix issues
ruff format .                   # Format code

# Type checking
mypy trading_bot/

# Combined quality check
ruff check . --fix && ruff format . && mypy trading_bot/
```

### Testing
```bash
# Run all tests
pytest

# Verbose testing
pytest -v

# Test specific modules
pytest tests/strategies/
pytest tests/backtesting/

# Test with coverage
pytest --cov=trading_bot tests/
```

### Strategy Development
```bash
# Run backtest
python -m trading_bot.strategies.ma_crossover
python -m trading_bot.backtesting.runner --strategy=sma_strategy --symbol=AAPL

# Download data
python -m trading_bot.data.downloader --symbol=SPY --period=2y

# Strategy optimization
python -m trading_bot.optimization.optimizer --strategy=rsi_strategy
```

## Project Structure
```
trading_bot/
├── strategies/          # Trading strategy implementations (Backtrader strategies)
├── data/               # Market data storage and yfinance integration
├── backtesting/        # Backtrader engine and performance analysis
├── utils/              # Shared utilities and indicators
├── models/             # Data models and portfolio schemas
├── optimization/       # Strategy parameter optimization
tests/                  # Comprehensive test suite
config/                 # Configuration files and parameters
docs/                   # Documentation and notebooks
logs/                   # Application and trading logs
environment.yml         # micromamba environment specification
```

## Core Dependencies & Frameworks

### Primary Trading Framework: Backtrader
- **Why**: Simple, flexible, Pythonic, excellent documentation
- **Strengths**: Smooth transition from backtesting to live trading
- **Use cases**: Strategy development, indicator creation, portfolio analysis
- **Files**: All strategies inherit from `backtrader.Strategy`

### Data Sources
- **yfinance**: Free market data for development/testing
- **Alpha Vantage**: Professional API for production
- **Interactive Brokers**: Live trading integration via Backtrader

### Key Libraries
```python
import backtrader as bt           # Trading framework
import pandas as pd              # Data manipulation
import numpy as np               # Numerical computation
import yfinance as yf            # Market data
from decimal import Decimal      # Precise financial calculations
```

## Code Style Guidelines

### ruff Configuration (pyproject.toml)
```toml
[tool.ruff]
line-length = 88
target-version = "py311"
exclude = ["venv", ".git", "__pycache__", "*.egg-info"]

[tool.ruff.lint]
select = ["E", "F", "B", "I", "UP", "C4"]
ignore = ["E501"]  # Line length handled by formatter
fixable = ["ALL"]

[tool.ruff.format]
quote-style = "double"
docstring-code-format = true
```

### Python Standards
- Use type hints for all functions: `def calculate_sma(prices: pd.Series, window: int) -> pd.Series:`
- Google-style docstrings for all classes and public methods
- Use `Decimal` for financial calculations to avoid floating-point errors
- Descriptive variable names: `closing_prices`, `position_size`, `risk_per_trade`
- Keep strategy logic functions under 50 lines

## Backtrader Strategy Structure
```python
import backtrader as bt

class BaseStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('risk_percent', 0.02),
    )

    def __init__(self):
        # Initialize indicators
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.period
        )

    def next(self):
        # Strategy logic here
        pass

    def log(self, txt, dt=None):
        """Logging function for strategy events"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')
```

## Testing Guidelines
- Mock external data sources for consistent testing
- Test strategies with known datasets and expected outcomes
- Include edge cases: market gaps, holidays, extreme volatility
- Performance tests for strategy execution speed
- Integration tests with small, real market data samples

## Development Rules
- **NEVER** commit API keys or secrets
- Use environment variables for all sensitive configuration
- **ALWAYS** validate input data before backtesting
- Include comprehensive error handling for data fetching
- Log all trading decisions with timestamps and reasoning
- Use `Decimal` for all monetary calculations
- Handle missing data appropriately (forward fill vs skip)

## Financial Data Best Practices
- Validate data integrity before every backtest
- Account for stock splits and dividend adjustments
- Consider transaction costs and slippage in all backtests
- Implement proper position sizing and risk management
- Handle market holidays and data gaps gracefully
- Cache historical data to avoid repeated API calls

## Environment Setup
```bash
# 1. Install micromamba
curl -L micro.mamba.pm/install.sh | bash

# 2. Create environment
micromamba create -n trading-bot python=3.11 -c conda-forge -y

# 3. Activate and install packages
micromamba activate trading-bot
micromamba install -c conda-forge pandas numpy matplotlib jupyter pytest mypy -y
pip install backtrader yfinance python-dotenv

# 4. Set up environment variables
cp .env.example .env  # Add your API keys
```

## Configuration Management
- Create `.env` file for API keys and secrets
- Use `.env.example` as template (commit this)
- Load config via `python-dotenv`
- Never commit the actual `.env` file

## Performance Optimization
- Use vectorized pandas operations for data processing
- Cache market data locally to reduce API calls
- Profile strategy performance before live testing
- Implement data pagination for large historical datasets
- Monitor memory usage with multi-year backtests

## Risk Management Standards
- Always implement position sizing based on account risk
- Set stop-loss levels for all positions
- Limit maximum portfolio allocation per trade
- Monitor correlation between positions
- Include transaction costs in all backtesting

## Live Trading Considerations (Future)
- Paper trading integration via Backtrader
- Interactive Brokers API connection
- Real-time data feed integration
- Order management and execution monitoring
- Position and PnL tracking
# Trading Bot Simple - Claude Project Context

## What This Project Is
Professional algorithmic trading system with **risk-first approach**. Key principle: Transform dangerous gambling strategies (95% portfolio risk) into systematic capital-preserving approaches (2% max risk per trade). Tests 7 strategies across 41 assets with comprehensive backtesting and optimization.

> ⚠️ The current analytics remain **per-asset**. There is no blended portfolio return, correlation, or allocation engine yet—each run assumes the entire cash balance is deployed into one asset at a time.

## Essential Commands
```bash
# Environment (ALWAYS use micromamba)
micromamba run -n trading-bot-simple python <command>

# Testing (run before changes)
python run_tests.py                                          # All 53 tests
python -m pytest tests/test_risk_management.py              # Individual test file

# Main execution modes (main.py orchestrates everything)
python main.py --mode single --symbol AAPL --strategy sma    # Single backtest
python main.py --mode multi --test-mode full                 # 250 combinations test
python main.py --mode optimize --opt-mode multi-symbol       # Cross-asset optimization
python main.py --mode visualize                              # Generate charts
```

## Core Files & What They Do
- **main.py**: CLI orchestrator - all modes route through here
- **optimizer.py**: Parameter optimization (single + multi-symbol comprehensive)
- **multi_asset_tester.py**: Tests strategies across 41 assets (23 stocks + 18 crypto)
- **strategies.py**: 7 strategies (SMA, RSI, MACD, Bollinger, EMA, Momentum, BuyHold)
- **risk_management.py**: Core 2% risk engine - NEVER bypass this
- **data.py**: Yahoo Finance fetching with caching
- **results_visualizer.py**: Charts and analysis

## Key Architecture Principles
- **Risk-first**: Every strategy MUST include 2% max risk per trade
- **Professional standards**: No gambling, systematic position sizing only
- **Comprehensive testing**: 53 unit tests must pass, backtests across multiple assets
- **Attribution honesty**: Returns come from asset selection, not strategy timing
- **Caching**: Data and results cached to avoid re-downloading

## Output Files to Expect
```
# Multi-symbol optimization (comprehensive)
multi_symbol_optimization_all_20250925_143022.json      # All 41 assets
multi_symbol_optimization_stocks_20250925_143022.json   # 23 stocks only
multi_symbol_optimization_crypto_20250925_143022.json   # 18 crypto only

# Single-symbol optimization
optimization_rsi_AAPL_20200101.csv                      # Single strategy
optimization_all_strategies_BTC-USD_20200101.csv        # All strategies
optimization_quick_TSLA_20200101.csv                    # Quick test
```

## Development Guidelines
- **Test first**: Run `python run_tests.py` before suggesting changes
- **Risk management**: Never modify risk_management.py without deep understanding
- **Code style**: Follow existing patterns, especially in strategies.py
- **Symbol handling**: Some symbols may fail (SQ delisted) - system handles gracefully
- **Performance**: Multi-symbol optimization takes significant time (1000+ backtests)

## Common Issues Claude Should Know
- **Data issues**: Yahoo Finance can be flaky, system has retry logic and caching
- **Missing symbols**: SQ is delisted, system gracefully skips failed symbols
- **Long runtimes**: Multi-symbol optimization across 41 assets takes 10+ minutes
- **Memory usage**: Large backtests can consume significant memory
- **Commission model**: All backtests include 0.1% commission (realistic)

## What Success Looks Like
- All 53 tests passing
- Risk management preventing account destruction (no >2% position sizes)
- Comprehensive cross-asset analysis showing which strategies work for which symbols
- Buy & Hold baseline comparisons (most strategies DON'T beat it)
- Professional attribution analysis (asset selection > strategy timing)

## Important Warnings
- **NEVER** suggest bypassing risk management for "better returns"
- **NEVER** assume strategies will work without testing across multiple assets
- **NEVER** ignore the 2% risk limit - it's the core principle
- **ALWAYS** run tests before code changes
- **REMEMBER** past performance ≠ future results (backtesting limitations)

# Risk-Managed Strategy Lab

Compact research environment for exploring **risk-managed trading strategies** across equities and crypto. The focus is on answering three questions:

1. **Which strategy + parameters perform best per asset when risk controls are enforced?**
2. **How do those results behave when visualised at scale (outliers, distributions, summary stats)?**
3. **What actually happened inside a run (entries, exits, portfolio heat) for the top performers?**

Everything in the repo exists to serve those flows and provides a clean base for the future portfolio engine.

## 3 Core Workflows

| Workflow | Entry point | What it does |
| --- | --- | --- |
| Multi-asset optimiser | `python -m trading_bot.optimizer` or `main.py --mode optimize` | Sweeps the registered strategies for each symbol, writing a summary JSON (e.g. `multi_symbol_optimization_all_*.json`). |
| Result dashboards | `python main.py --mode visualize` | Aggregates optimiser output, plots distributions/boxplots, and handles extreme outliers separately. |
| Trade inspector | `python -m trading_bot.top_performer_visualization --report <file> --top-k 3` | Replays selected runs, capturing trades and risk telemetry for charting. |

The scripts write to `cache/`, `visualizations/`, and the repo root as needed. Everything is single-asset today; the `PortfolioEngine` stub anchors future blended portfolio work.

## Quick Start

```bash
micromamba env create -f environment-simple.yml -y
micromamba run -n trading-bot-simple python main.py --mode optimize --opt-mode multi-symbol --opt-symbols crypto
micromamba run -n trading-bot-simple python main.py --mode visualize
micromamba run -n trading-bot-simple python -m trading_bot.top_performer_visualization --report multi_symbol_optimization_all_20251002_194419.json --top-k 3
micromamba run -n trading-bot-simple python main.py --mode report --opt-symbols all --report-top-k 3
```

- Cached market data lives in `data_cache/`. Clear it with `python main.py --clear-data-cache`.
- Optimiser and tester caches live under `cache/` with per-symbol JSON dumps.
- Charts drop into `visualizations/` (ignored by git).
- End-to-end lab reports land in `reports/<timestamp>/` with JSON, Markdown, and charts.

## Project Layout

```
.
├── main.py                     # Thin CLI wrapper (optimize / visualize / inspect / portfolio)
├── src/trading_bot/            # Core package
│   ├── data.py                 # Yahoo Finance ingestion + caching
│   ├── multi_asset_tester.py   # Strategy sweeps per symbol (uses risk-managed strategies)
│   ├── optimizer.py            # Parameter optimiser built on the tester
│   ├── results_visualizer.py   # Summary charts (boxplots, outlier handling)
│   ├── top_performer_visualization.py  # Trade + risk timeline plots
│   ├── risk_management.py      # Risk manager, heat/drawdown monitors
│   ├── risk_managed_strategy.py / risk_managed_strategies.py
│   ├── portfolio_engine.py     # Portfolio scaffold for future work
│   └── ...
├── tests/                      # Pytest suite (invoked via `pytest` or `run_tests.py`)
├── docs/                       # Focused notes tied to the new layout (see below)
└── scripts                     # Utility entry points (generate fixtures, legacy smoke tests)
```

### Documentation

The old long-form guides have been retired. The remaining references are:

- `docs/overview.md` – high-level architecture diagram + quick reminders
- `docs/portfolio-roadmap.md` – notes for the upcoming blended portfolio engine
- `CHANGELOG.md` – user-facing changes

## Testing

```bash
micromamba run -n trading-bot-simple pytest -q              # full suite
micromamba run -n trading-bot-simple pytest tests/test_optimizer.py -q
python run_tests.py --module test_risk_management
```

Pytest is configured with `pythonpath = src`, so package imports (`trading_bot.*`) work from anywhere.

## Roadmap

- Flesh out `PortfolioEngine` with cross-asset allocation, shared risk budgets, and rebalancing logic.
- Promote optimiser outputs into a simple API (e.g. `trading_bot.optimize.run(...)`) for notebooks.
- Persist analytics (summary tables, charts) to a structured `reports/` directory with timestamps.
- Add PostgreSQL or DuckDB sinks for long-term result analysis.

Feel free to keep the repo lean—any file that doesn’t serve the three workflows gets pruned.

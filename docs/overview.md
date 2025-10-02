# Trading Bot Overview

- **Package**: `trading_bot` (under `src/`)
- **Strategies**: risk-managed implementations only (no legacy strategies remain)
- **Optimiser pipeline**: `MultiAssetTester` -> `ParameterOptimizer` -> JSON summary
- **Visual analytics**: `ResultsVisualizer` for portfolio-wide plots, `top_performer_visualization` for trade-by-trade charts
- **Data**: Yahoo Finance with JSON caching (`data_cache/`)
- **Persistence**: Optimiser exports live in repo root (`multi_symbol_optimization_*.json`), charts in `visualizations/`

The entire codebase aims to answer “which strategy works best per asset with risk constraints?” and to set the stage for a future portfolio engine.

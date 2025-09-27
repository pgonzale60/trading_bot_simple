# Repository Guidelines

## Project Structure & Module Organization
Core trading flows live at the repository root: `main.py` orchestrates execution modes, while `strategies.py`, `risk_managed_strategies.py`, and `risk_management.py` hold portfolio logic and controls. Optimizers and analysis tooling reside in `optimizer.py`, `results_visualizer.py`, and `multi_asset_tester.py`. Cached market data is stored under `data_cache/`, and generated performance artefacts land in CSV/PNG files in the root. Documentation expands on risk processes inside `docs/risk-management/`. Tests sit in `tests/`, with fixtures in `tests/fixtures.json` and suite entry points such as `tests/test_risk_management.py`.

## Build, Test, and Development Commands
- `micromamba env create -f environment-simple.yml -y` creates the trading environment locally.
- `micromamba run -n trading-bot-simple python main.py --mode multi --test-mode quick` exercises the default multi-asset flow.
- `python run_tests.py` runs the curated unittest wrapper; `pytest tests/ -v` runs the same set via pytest.
- `pytest tests/ --cov=. --cov-report=html` generates coverage for deeper reviews.

## Coding Style & Naming Conventions
Write Python with four-space indentation, module-level constants in `UPPER_SNAKE_CASE`, functions and files in `snake_case`, and classes in `PascalCase`. Match the repository’s use of f-strings and descriptive docstrings for public entry points. Prefer explicit imports over star imports, keep functions under ~40 lines where practical, and group risk configuration helpers beside their strategy counterparts. When changing signatures, add type hints consistent with existing annotations.

## Testing Guidelines
Pytest discovery follows `pytest.ini`: place new suites under `tests/` as `test_<topic>.py`, classes prefixed `Test`, and functions `test_*`. Critical risk protection should extend `tests/test_risk_management.py`; multi-asset behaviour belongs in `tests/test_multi_asset_tester.py`. Add fixtures to `tests/fixtures.json` when sharing test data. Always run `pytest` (or `python run_tests.py --module <name>`) before submitting and include new markers (`unit`, `integration`, etc.) when scope warrants. Aim to keep new functionality covered and update coverage expectations if behaviour shifts.

## Commit & Pull Request Guidelines
Use concise, imperative commit subjects (e.g., `tighten position sizing checks`) and append issue references in parentheses when closing work (`(#12)`). Each PR should link to its tracking issue, summarise scenario-level changes, and note test commands executed. Attach relevant artefacts (logs, performance charts) when behavioural results matter, and call out any modules needing follow-up so reviewers can plan validation.

## Configuration & Caching Notes
The bot reads cached Yahoo Finance data from `data_cache/`; clear it with `python main.py --clear-data-cache` when datasets go stale. Avoid committing generated CSV/PNG outputs or `cache/` contents. Environment definition lives in `environment-simple.yml`; update it alongside dependency bumps and verify micromamba syncs cleanly.

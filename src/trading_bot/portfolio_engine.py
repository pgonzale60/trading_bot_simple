"""Portfolio engine scaffold for v3.0.0.

The engine currently focuses on orchestration: it spins up a single
Backtrader `Cerebro` instance, loads the selected asset universe, and
runs a placeholder strategy. Later issues will inject portfolio-aware
risk management, state tracking, and rebalancing logic on top of this
foundation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

import backtrader as bt

from .asset_universe import (
    ALL_ASSETS_2019,
    CRYPTO_UNIVERSE_2019,
    QUICK_SAMPLE_ALL,
    QUICK_SAMPLE_CRYPTO,
    QUICK_SAMPLE_STOCKS,
    STOCK_UNIVERSE_2019,
)
from .data import get_stock_data
from .portfolio_config import DEFAULT_PORTFOLIO_CONFIG, PortfolioConfig

logger = logging.getLogger(__name__)


@dataclass
class PortfolioRunResult:
    """Lightweight container for portfolio run metadata."""

    symbols: Sequence[str]
    starting_cash: float
    final_value: float


class PortfolioEngine:
    """Scaffold for running blended equity/crypto portfolios in Backtrader."""

    def __init__(
        self,
        start_date: str = "2020-01-01",
        cash: float = 10000.0,
        test_mode: str = "quick",
        use_cache: bool = True,
        config: Optional[PortfolioConfig] = None,
    ) -> None:
        self.start_date = start_date
        self.cash = cash
        self.test_mode = test_mode
        self.use_cache = use_cache
        self.config = config or DEFAULT_PORTFOLIO_CONFIG

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self, symbols: Optional[Sequence[str]] = None) -> PortfolioRunResult:
        """Execute a portfolio backtest using the configured universe."""

        resolved_symbols = self._resolve_symbols(symbols)
        if not resolved_symbols:
            raise ValueError("PortfolioEngine requires at least one symbol to run")

        logger.info(
            "Starting portfolio run | mode=%s | symbols=%s", self.test_mode, ",".join(resolved_symbols)
        )

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(self.cash)
        cerebro.broker.setcommission(commission=0.001)

        for symbol in resolved_symbols:
            data_feed = get_stock_data(
                symbol=symbol,
                start_date=self.start_date,
                use_cache=self.use_cache,
            )
            data_feed._name = symbol  # annotate feed for logging
            cerebro.adddata(data_feed, name=symbol)

        cerebro.addstrategy(PortfolioBuyHoldStrategy)

        cerebro.run()
        final_value = cerebro.broker.getvalue()

        logger.info(
            "Portfolio run complete | start_cash=%.2f | final_value=%.2f",
            self.cash,
            final_value,
        )

        return PortfolioRunResult(
            symbols=resolved_symbols,
            starting_cash=self.cash,
            final_value=final_value,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve_symbols(self, symbols: Optional[Sequence[str]]) -> List[str]:
        if symbols:
            return list(dict.fromkeys(symbols))  # preserve order, drop duplicates

        mode = (self.test_mode or "quick").lower()
        if mode == "stocks":
            return STOCK_UNIVERSE_2019.copy()
        if mode == "crypto":
            return CRYPTO_UNIVERSE_2019.copy()
        if mode == "full":
            return ALL_ASSETS_2019.copy()
        # Default to quick sample for smoke-speed runs
        return QUICK_SAMPLE_ALL.copy()


class PortfolioBuyHoldStrategy(bt.Strategy):
    """Placeholder strategy used during the portfolio scaffolding phase.

    The strategy does not place trades yet; it simply logs the combined
    NAV trajectory to prove that the engine can host multiple data feeds
    within a single Cerebro run. Later stages will replace this with
    portfolio-aware strategy logic.
    """

    params = (("log_frequency", 20),)  # log every N bars to avoid excessive noise

    def __init__(self) -> None:
        self.bar_counter = 0

    def next(self) -> None:
        self.bar_counter += 1
        if self.bar_counter % self.params.log_frequency == 0:
            dt = self.datas[0].datetime.date(0)
            value = self.broker.getvalue()
            cash = self.broker.getcash()
            logger.info("[PortfolioStub] %s | NAV=%.2f | Cash=%.2f", dt.isoformat(), value, cash)


__all__ = [
    "PortfolioBuyHoldStrategy",
    "PortfolioEngine",
    "PortfolioRunResult",
]

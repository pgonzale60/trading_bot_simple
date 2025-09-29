"""Configuration primitives for portfolio mode.

Keeping the configuration in a dedicated module ensures that upcoming
features (risk limits, rebalancing cadence, sleeve caps) have a single
source of truth that can be imported by both runtime code and tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(frozen=True)
class SleeveLimit:
    """Represents a portfolio sleeve and its maximum capital allocation."""

    name: str
    max_allocation: float  # expressed as fraction of total NAV (0-1)


@dataclass
class PortfolioConfig:
    """Top-level configuration for the blended portfolio mode."""

    name: str = "blended"
    rebalance_frequency: str = "monthly"  # placeholder for future scheduling logic
    risk_profile: str = "moderate"
    equity_sleeve: SleeveLimit = field(
        default_factory=lambda: SleeveLimit(name="equities", max_allocation=1.0)
    )
    crypto_sleeve: SleeveLimit = field(
        default_factory=lambda: SleeveLimit(name="crypto", max_allocation=0.5)
    )
    metadata: Optional[Dict[str, str]] = None

    @property
    def sleeve_limits(self) -> Dict[str, SleeveLimit]:
        """Convenience accessor for iterating over sleeve limits."""

        return {
            self.equity_sleeve.name: self.equity_sleeve,
            self.crypto_sleeve.name: self.crypto_sleeve,
        }


DEFAULT_PORTFOLIO_CONFIG = PortfolioConfig()

__all__ = [
    "DEFAULT_PORTFOLIO_CONFIG",
    "PortfolioConfig",
    "SleeveLimit",
]

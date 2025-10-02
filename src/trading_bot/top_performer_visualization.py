#!/usr/bin/env python3
"""Visualize top-performing strategy runs with risk overlays.

This script rebuilds the best strategy/asset combinations from the
multi-asset optimization report and renders price, capital usage,
and risk telemetry so the charts mirror the performance narrative.
"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import backtrader as bt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from .data import get_stock_data
from .risk_managed_strategies import RISK_MANAGED_STRATEGIES
from .risk_management import RiskLevel, StopLossMethod


@dataclass
class TradeEvent:
    """Structured record for plotting executed trades."""

    timestamp: pd.Timestamp
    price: float
    size: float
    action: str  # "buy" or "sell"


class RecordingStrategyMixin:
    """Mixin that captures bar-by-bar account metrics and trade events."""

    def __init__(self, *args, **kwargs):
        self.metrics_history: List[Dict[str, float]] = []
        self.trade_events: List[TradeEvent] = []
        super().__init__(*args, **kwargs)

    def next(self):  # type: ignore[override]
        super().next()

        dt = pd.Timestamp(self.datas[0].datetime.datetime(0))
        account_value = float(self.broker.getvalue())
        cash = float(self.broker.getcash())
        risk_metrics = self.get_risk_metrics()

        self.metrics_history.append(
            {
                "timestamp": dt,
                "close": float(self.data.close[0]),
                "portfolio_value": account_value,
                "cash": cash,
                "invested_value": account_value - cash,
                "portfolio_heat": float(risk_metrics.get("portfolio_heat", 0.0)),
                "drawdown": float(risk_metrics.get("current_drawdown", 0.0)),
            }
        )

    def notify_order(self, order):  # type: ignore[override]
        super().notify_order(order)

        if order.status != order.Completed:
            return

        action = "buy" if order.isbuy() else "sell"
        dt = pd.Timestamp(self.datas[0].datetime.datetime(0))
        event = TradeEvent(
            timestamp=dt,
            price=float(order.executed.price),
            size=float(abs(order.executed.size)),
            action=action,
        )
        self.trade_events.append(event)


def build_tracking_strategy(strategy_name: str):
    """Return a strategy class that records telemetry for plotting."""
    base_cls = RISK_MANAGED_STRATEGIES[strategy_name]

    class TrackingStrategy(RecordingStrategyMixin, base_cls):
        pass

    TrackingStrategy.__name__ = f"Recording{base_cls.__name__}"
    return TrackingStrategy


def parse_param_string(param_str: str) -> Dict[str, object]:
    """Convert the optimizer's param string into kwargs."""
    if not param_str or param_str.lower().endswith("default)"):
        return {}

    start = param_str.find("{")
    end = param_str.rfind("}")
    if start == -1 or end == -1:
        return {}

    try:
        parsed = ast.literal_eval(param_str[start : end + 1])
    except (SyntaxError, ValueError):
        return {}

    return parsed if isinstance(parsed, dict) else {}


def load_top_performers(
    report_path: Path, top_k: int, min_return_pct: Optional[float]
) -> List[Dict[str, object]]:
    """Extract the strongest strategy/asset pairs from the optimization report."""
    with report_path.open("r") as handle:
        data = json.load(handle)

    entries: List[Dict[str, object]] = []
    for symbol, payload in data.get("results_by_symbol", {}).items():
        best = payload.get("best_strategy")
        if not best:
            continue

        entry = {
            "symbol": symbol,
            "asset_type": payload.get("symbol_type", "unknown"),
            "strategy": best.get("strategy", "").lower(),
            "params": best.get("params", ""),
            "return_pct": best.get("return_pct", 0.0),
        }
        entries.append(entry)

    if min_return_pct is not None:
        entries = [e for e in entries if e["return_pct"] >= min_return_pct]

    entries.sort(key=lambda e: e["return_pct"], reverse=True)
    return entries[:top_k]


def _coerce_risk_level(label: str) -> RiskLevel:
    normalized = label.replace("RiskLevel.", "").replace("risklevel.", "")
    try:
        return RiskLevel[normalized.upper()]
    except KeyError as exc:
        valid = ", ".join(level.name.lower() for level in RiskLevel)
        raise ValueError(f"Unknown risk profile '{label}'. Expected one of: {valid}") from exc


def _coerce_stop_method(label: str) -> StopLossMethod:
    normalized = label.replace("StopLossMethod.", "").replace("stoplossmethod.", "")
    try:
        return StopLossMethod[normalized.upper()]
    except KeyError as exc:
        valid = ", ".join(method.name.lower() for method in StopLossMethod)
        raise ValueError(f"Unknown stop loss method '{label}'. Expected one of: {valid}") from exc


def _build_history_dataframe(strategy) -> pd.DataFrame:
    history = pd.DataFrame(strategy.metrics_history)
    if history.empty:
        raise RuntimeError("Strategy run produced no telemetry to plot.")

    history = history.drop_duplicates(subset="timestamp").sort_values("timestamp")
    history["exposure_pct"] = (history["invested_value"] / history["portfolio_value"]).fillna(0.0)
    history["portfolio_heat_pct"] = history["portfolio_heat"] * 100.0
    history["drawdown_pct"] = history["drawdown"] * 100.0
    return history


def _format_title(symbol: str, strategy: str, achieved: float, reported: float) -> str:
    delta = achieved - reported
    delta_text = f"Δ {delta:+.1f}% vs report" if abs(delta) > 0.5 else "matches report"
    return (
        f"{symbol} · {strategy.upper()} | Actual {achieved:.1f}% · Reported {reported:.1f}% ({delta_text})"
    )


def plot_top_performer(
    history: pd.DataFrame,
    trades: Iterable[TradeEvent],
    output_path: Path,
    *,
    symbol: str,
    strategy: str,
    reported_return: float,
    risk_params: Dict[str, float],
):
    plt.style.use("seaborn-v0_8-darkgrid")

    achieved_return = ((history["portfolio_value"].iloc[-1] / history["portfolio_value"].iloc[0]) - 1) * 100
    title = _format_title(symbol, strategy, achieved_return, reported_return)

    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    fig.suptitle(title, fontsize=16, fontweight="bold")

    # --- Panel 1: Price & trade markers ---
    price_ax = axes[0]
    price_ax.plot(history["timestamp"], history["close"], label="Close", color="#1f77b4", linewidth=1.2)

    buy_label_used = False
    sell_label_used = False
    for trade in trades:
        marker = "^" if trade.action == "buy" else "v"
        color = "#2ca02c" if trade.action == "buy" else "#d62728"
        label = None
        if trade.action == "buy" and not buy_label_used:
            label = "Buy"
            buy_label_used = True
        elif trade.action == "sell" and not sell_label_used:
            label = "Sell"
            sell_label_used = True

        price_ax.scatter(trade.timestamp, trade.price, marker=marker, color=color, s=70, label=label, zorder=5)

    price_ax.set_ylabel("Price (USD)")
    price_ax.legend(loc="upper left", frameon=False)

    # --- Panel 2: Account value vs cash ---
    value_ax = axes[1]
    value_ax.plot(
        history["timestamp"], history["portfolio_value"], label="Account Value", color="#1f77b4", linewidth=1.4
    )
    value_ax.plot(history["timestamp"], history["cash"], label="Cash", color="#9467bd", linestyle="--", linewidth=1.2)
    value_ax.fill_between(
        history["timestamp"],
        history["cash"],
        history["portfolio_value"],
        where=history["portfolio_value"] >= history["cash"],
        color="#1f77b4",
        alpha=0.2,
        label="Capital Deployed",
    )
    value_ax.set_ylabel("USD")
    value_ax.legend(loc="upper left", frameon=False)

    max_value = history["portfolio_value"].max()
    max_ts = history.loc[history["portfolio_value"].idxmax(), "timestamp"]
    value_ax.annotate(
        f"Peak Value ${max_value:,.0f}",
        xy=(max_ts, max_value),
        xytext=(10, 18),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#1f77b4"},
        fontsize=9,
        color="#1f77b4",
    )

    # --- Panel 3: Risk telemetry ---
    risk_ax = axes[2]
    risk_ax.plot(
        history["timestamp"], history["portfolio_heat_pct"], label="Portfolio Heat (%)", color="#d62728", linewidth=1.2
    )
    risk_ax.plot(
        history["timestamp"], history["drawdown_pct"], label="Drawdown (%)", color="#ff9896", linewidth=1.2
    )
    risk_ax.plot(
        history["timestamp"], history["exposure_pct"] * 100,
        label="Exposure (%)",
        color="#17becf",
        linewidth=1.1,
    )

    max_heat = risk_params.get("max_portfolio_heat")
    if max_heat is not None:
        risk_ax.axhline(max_heat * 100, color="#d62728", linestyle=":", linewidth=1.0, label="Heat Limit")

    max_dd = risk_params.get("max_drawdown")
    if max_dd is not None:
        risk_ax.axhline(max_dd * 100, color="#ff9896", linestyle=":", linewidth=1.0, label="Drawdown Limit")
        risk_ax.text(
            history["timestamp"].iloc[0],
            max_dd * 100,
            "Max Drawdown",
            va="bottom",
            ha="left",
            fontsize=8,
            color="#ff9896",
        )

    risk_ax.set_ylabel("% of equity")
    risk_ax.set_xlabel("Date")
    risk_ax.legend(loc="upper left", frameon=False)

    axes[-1].xaxis.set_major_locator(mdates.AutoDateLocator())
    axes[-1].xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
    fig.autofmt_xdate()
    fig.tight_layout(rect=[0, 0.01, 1, 0.97])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"📈 Saved: {output_path}")


def visualize_top_performers(
    report_path: Path,
    output_dir: Path,
    top_k: int,
    risk_profile: RiskLevel,
    min_return_pct: Optional[float],
):
    if not report_path.exists():
        raise FileNotFoundError(f"Optimization report not found: {report_path}")

    performers = load_top_performers(report_path, top_k, min_return_pct)
    if not performers:
        print("No performers matched the criteria.")
        return

    with report_path.open("r") as handle:
        data = json.load(handle)
    metadata = data.get("optimization_metadata", {})
    start_date = metadata.get("start_date", "2020-01-01")
    initial_cash = float(metadata.get("cash", 10000))

    for rank, performer in enumerate(performers, start=1):
        symbol = performer["symbol"]
        strategy_name = performer["strategy"]
        reported_return = float(performer["return_pct"])

        if strategy_name not in RISK_MANAGED_STRATEGIES:
            print(f"Skipping {symbol} ({strategy_name}) – strategy not registered.")
            continue

        params = parse_param_string(performer["params"])
        strategy_kwargs = dict(params)

        if "risk_profile" in strategy_kwargs:
            profile_value = strategy_kwargs["risk_profile"]
            if isinstance(profile_value, str):
                strategy_kwargs["risk_profile"] = _coerce_risk_level(profile_value)
        else:
            strategy_kwargs["risk_profile"] = risk_profile

        if "stop_loss_method" in strategy_kwargs and isinstance(strategy_kwargs["stop_loss_method"], str):
            strategy_kwargs["stop_loss_method"] = _coerce_stop_method(strategy_kwargs["stop_loss_method"])

        strategy_kwargs.setdefault("enable_risk_logging", False)
        strategy_kwargs.setdefault("log_all_signals", False)

        tracking_cls = build_tracking_strategy(strategy_name)

        cerebro = bt.Cerebro()
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=0.001)

        try:
            data_feed = get_stock_data(symbol, start_date)
        except Exception as exc:
            print(f"⚠️  Failed to load data for {symbol}: {exc}")
            continue

        cerebro.adddata(data_feed)
        cerebro.addstrategy(tracking_cls, **strategy_kwargs)

        try:
            results = cerebro.run()
        except Exception as exc:
            print(f"⚠️  Backtest failed for {symbol} ({strategy_name}): {exc}")
            continue

        strategy = results[0]
        history = _build_history_dataframe(strategy)
        history.attrs["risk_params"] = strategy.risk_manager.risk_params

        filename = f"{rank:02d}_{symbol.replace('-', '_')}_{strategy_name}.png"
        output_path = output_dir / filename
        plot_top_performer(
            history,
            strategy.trade_events,
            output_path,
            symbol=symbol,
            strategy=strategy_name,
            reported_return=reported_return,
            risk_params=strategy.risk_manager.risk_params,
        )


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize top-performing optimization results.")
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("multi_symbol_optimization_all_20250926_075253.json"),
        help="Path to the optimization summary JSON.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("visualizations/top_performers"),
        help="Directory where charts will be written.",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Number of performers to visualize.")
    parser.add_argument(
        "--risk-profile",
        type=str,
        default="aggressive",
        help="Risk profile to apply when rerunning strategies (conservative/moderate/aggressive).",
    )
    parser.add_argument(
        "--min-return",
        type=float,
        default=None,
        help="Optional minimum return percentage filter before ranking.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    risk_profile = _coerce_risk_level(args.risk_profile)
    visualize_top_performers(args.report, args.output_dir, args.top_k, risk_profile, args.min_return)


if __name__ == "__main__":
    main()

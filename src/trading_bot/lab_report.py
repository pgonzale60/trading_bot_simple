"""Automated lab report generation for the trading bot."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .optimizer import ParameterOptimizer
from .results_visualizer import ResultsVisualizer
from .risk_management import RiskLevel
from .top_performer_visualization import visualize_top_performers


def _load_results(json_path: Path) -> Dict[str, object]:
    with json_path.open("r") as handle:
        return json.load(handle)


def _select_top_performers(results: Dict[str, object], top_k: int) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    for symbol, payload in results.get("results_by_symbol", {}).items():
        best = payload.get("best_strategy")
        if not best:
            continue
        entry = {
            "symbol": symbol,
            "asset_type": payload.get("symbol_type", "unknown"),
            "strategy": best.get("strategy", "").upper(),
            "params": best.get("params", ""),
            "return_pct": float(best.get("return_pct", 0.0)),
        }
        entries.append(entry)

    entries.sort(key=lambda item: item["return_pct"], reverse=True)
    return entries[:top_k]


def _format_percent(value: float) -> str:
    return f"{value:,.1f}%"


def _render_markdown(
    results: Dict[str, object],
    metadata: Dict[str, object],
    top_performers: List[Dict[str, object]],
    viz_paths: Dict[str, Path],
    performer_charts: List[Path],
    optimizer_args: Dict[str, object],
) -> str:
    lines: List[str] = []
    timestamp = metadata.get("timestamp", datetime.utcnow().isoformat())
    lines.append(f"# Performance Report ({timestamp})")
    lines.append("")

    lines.append("## Optimizer Run")
    lines.append("")
    lines.append(f"- Symbols analysed: {metadata.get('total_symbols', 'N/A')} ({metadata.get('symbols_type')})")
    lines.append(f"- Strategies tested: {metadata.get('total_strategies', 'N/A')}")
    lines.append(f"- Start date: {metadata.get('start_date')} | Cash per run: ${metadata.get('cash', 'N/A'):,.0f}")
    lines.append(f"- Parameter combinations: {metadata.get('total_combinations', 'N/A')}")
    lines.append(f"- Completed symbols: {metadata.get('completed_symbols', 'N/A')}")
    failed = metadata.get('failed_symbols', [])
    if failed:
        lines.append(f"- Failed symbols: {', '.join(failed)}")
    lines.append("- Command parameters: " + ", ".join(f"{k}={v}" for k, v in optimizer_args.items()))
    lines.append("")

    if top_performers:
        lines.append(f"## Top Assets (Top {len(top_performers)})")
        lines.append("")
        lines.append("| Rank | Symbol | Strategy | Return | Parameters |")
        lines.append("| --- | --- | --- | --- | --- |")
        for idx, item in enumerate(top_performers, start=1):
            lines.append(
                f"| {idx} | {item['symbol']} | {item['strategy']} | "
                f"{_format_percent(item['return_pct'])} | {item['params']} |"
            )
        lines.append("")

    strategy_rankings = results.get("overall_insights", {}).get("strategy_rankings", [])
    if strategy_rankings:
        lines.append("## Strategy Rankings")
        lines.append("")
        lines.append("| Strategy | Avg Return | Best Symbol | Best Return |")
        lines.append("| --- | --- | --- | --- |")
        for entry in strategy_rankings:
            lines.append(
                f"| {entry['strategy'].upper()} | {_format_percent(entry['avg_return'])} | "
                f"{entry['best_symbol']} | {_format_percent(entry['best_return'])} |"
            )
        lines.append("")

    buy_hold = results.get("overall_insights", {}).get("buy_hold_analysis", {})
    if buy_hold:
        lines.append("## Buy & Hold Comparison")
        lines.append("")
        lines.append(f"- Buy & Hold average return: {_format_percent(buy_hold.get('avg_return', 0.0))}")
        outperformers = buy_hold.get('strategies_beating_buy_hold', [])
        if outperformers:
            lines.append("- Strategies beating buy & hold:")
            for entry in outperformers:
                lines.append(
                    f"  - {entry['strategy'].upper()} (avg return {_format_percent(entry['avg_return'])})"
                )
        lines.append("")

    lines.append("## Visualisations")
    lines.append("")
    if viz_paths:
        if viz_paths.get('strategy_plot'):
            lines.append(f"![Strategy Performance]({viz_paths['strategy_plot'].name})")
        if viz_paths.get('asset_plot'):
            lines.append(f"![Asset Performance]({viz_paths['asset_plot'].name})")
        if viz_paths.get('extreme_plot'):
            lines.append(f"![Extreme Outliers]({viz_paths['extreme_plot'].name})")
    lines.append("")

    if performer_charts:
        lines.append("## Top Performer Timelines")
        lines.append("")
        for chart in sorted(performer_charts):
            rel_path = Path("top_performers") / chart.name
            lines.append(f"![{chart.stem}]({rel_path.as_posix()})")
        lines.append("")

    lines.append("## Source Data")
    lines.append("")
    lines.append(f"- Optimisation JSON: {Path(results.get('output_file', 'N/A')).name}")
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def _generate_report_from_json_file(
    *,
    json_source: Path,
    risk_profile: RiskLevel,
    top_k: int,
    min_return: Optional[float],
    reports_root: Path,
    optimizer_args: Dict[str, object],
) -> Path:
    """Internal helper to generate report from a JSON file."""
    timestamp = json_source.stem.split("_")[-1]
    report_dir = reports_root / timestamp
    report_dir.mkdir(parents=True, exist_ok=True)

    json_target = report_dir / json_source.name
    if json_source != json_target:
        import shutil
        if json_target.exists():
            json_target.unlink()
        shutil.copy2(json_source, json_target)

    visualizer = ResultsVisualizer(report_dir=report_dir)
    viz_outputs = visualizer.generate_full_report(output_dir=report_dir, show=False)

    top_dir = report_dir / "top_performers"
    visualize_top_performers(
        json_target,
        top_dir,
        top_k,
        risk_profile,
        min_return,
    )
    top_charts = sorted(top_dir.glob("*.png"))

    results_dict = _load_results(json_target)
    results_dict["output_file"] = json_target.name
    metadata = results_dict.get("optimization_metadata", {})
    top_performers = _select_top_performers(results_dict, top_k)

    markdown = _render_markdown(
        results_dict,
        metadata,
        top_performers,
        viz_outputs,
        top_charts,
        optimizer_args,
    )

    report_path = report_dir / "performance_report.md"
    report_path.write_text(markdown)

    return report_dir


def generate_report_from_json(
    *,
    json_path: Path,
    risk_profile: RiskLevel,
    top_k: int,
    min_return: Optional[float],
    reports_root: Path,
) -> Path:
    """Generate a report from an existing optimization JSON file without re-running the optimizer."""
    reports_root.mkdir(parents=True, exist_ok=True)

    if not json_path.exists():
        raise FileNotFoundError(f"Optimization JSON not found: {json_path}")

    json_source = json_path if json_path.is_absolute() else Path.cwd() / json_path

    # Extract optimizer args from metadata
    results_dict = _load_results(json_source)
    metadata = results_dict.get("optimization_metadata", {})

    optimizer_args = {
        "start_date": metadata.get("start_date", "N/A"),
        "cash": metadata.get("cash", "N/A"),
        "symbols_type": metadata.get("symbols_type", "N/A"),
        "risk_profile": risk_profile.name.lower(),
        "top_k": top_k,
        "min_return": min_return if min_return is not None else "None",
    }

    report_dir = _generate_report_from_json_file(
        json_source=json_source,
        risk_profile=risk_profile,
        top_k=top_k,
        min_return=min_return,
        reports_root=reports_root,
        optimizer_args=optimizer_args,
    )

    print(f"\n📄 Report generated in {report_dir}")
    return report_dir


def generate_lab_report(
    *,
    start_date: str,
    cash: float,
    symbols_type: str,
    risk_profile: RiskLevel,
    top_k: int,
    min_return: Optional[float],
    reports_root: Path,
) -> Path:
    reports_root.mkdir(parents=True, exist_ok=True)

    optimizer = ParameterOptimizer(start_date=start_date, cash=cash)
    results = optimizer.optimize_all_symbols(symbols_type=symbols_type)

    output_file = Path(results["output_file"])
    json_source = output_file if output_file.is_absolute() else Path.cwd() / output_file

    optimizer_args = {
        "start_date": start_date,
        "cash": cash,
        "symbols_type": symbols_type,
        "risk_profile": risk_profile.name.lower(),
        "top_k": top_k,
        "min_return": min_return if min_return is not None else "None",
    }

    report_dir = _generate_report_from_json_file(
        json_source=json_source,
        risk_profile=risk_profile,
        top_k=top_k,
        min_return=min_return,
        reports_root=reports_root,
        optimizer_args=optimizer_args,
    )

    print(f"\n📄 Report generated in {report_dir}")
    return report_dir


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a lab performance report")
    parser.add_argument("--start", default="2020-01-01", help="Backtest start date (YYYY-MM-DD)")
    parser.add_argument("--cash", type=float, default=10000, help="Initial cash per run")
    parser.add_argument(
        "--symbols",
        choices=["all", "stocks", "crypto"],
        default="all",
        help="Symbol universe to optimise",
    )
    parser.add_argument(
        "--risk-profile",
        choices=[level.name.lower() for level in RiskLevel],
        default="aggressive",
        help="Risk profile for top performer replays",
    )
    parser.add_argument("--top-k", type=int, default=3, help="Number of top performers to visualise")
    parser.add_argument(
        "--min-return",
        type=float,
        default=None,
        help="Optional minimum return percentage filter for top performer charts",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="Destination directory for generated reports",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> Path:
    args = parse_args(argv)
    risk_profile = RiskLevel[args.risk_profile.upper()]
    report_dir = generate_lab_report(
        start_date=args.start,
        cash=args.cash,
        symbols_type=args.symbols,
        risk_profile=risk_profile,
        top_k=args.top_k,
        min_return=args.min_return,
        reports_root=args.reports_dir,
    )
    print(f"\n📄 Report generated in {report_dir}")
    return report_dir


if __name__ == "__main__":
    main()

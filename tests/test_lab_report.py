from pathlib import Path

from trading_bot.lab_report import _render_markdown, _select_top_performers


def test_select_top_performers_sorts_and_limits():
    sample = {
        'results_by_symbol': {
            'AAA': {'symbol_type': 'stock', 'best_strategy': {'strategy': 'sma', 'params': 'x', 'return_pct': 10}},
            'BBB': {'symbol_type': 'crypto', 'best_strategy': {'strategy': 'macd', 'params': 'y', 'return_pct': 25}},
            'CCC': {'symbol_type': 'stock', 'best_strategy': {'strategy': 'ema', 'params': 'z', 'return_pct': 5}},
        }
    }
    top = _select_top_performers(sample, top_k=2)
    assert [entry['symbol'] for entry in top] == ['BBB', 'AAA']


def test_render_markdown_includes_sections(tmp_path):
    results = {
        'output_file': 'multi_symbol_optimization_all_20250101_120000.json',
        'results_by_symbol': {},
        'overall_insights': {
            'strategy_rankings': [
                {'strategy': 'sma', 'avg_return': 12.5, 'best_symbol': 'AAA', 'best_return': 20.0},
            ],
            'buy_hold_analysis': {
                'avg_return': 0.0,
                'strategies_beating_buy_hold': [
                    {'strategy': 'sma', 'avg_return': 12.5},
                ],
            },
        },
    }
    metadata = {
        'timestamp': '2025-01-01T12:00:00',
        'total_symbols': 3,
        'total_strategies': 2,
        'symbols_type': 'all',
        'start_date': '2020-01-01',
        'cash': 10000,
        'total_combinations': 6,
        'completed_symbols': 3,
    }
    viz_paths = {
        'strategy_plot': Path('strategy_performance.png'),
        'asset_plot': Path('asset_performance.png'),
        'extreme_plot': Path('extreme_outliers.png'),
    }
    performer_dir = tmp_path / 'top_performers'
    performer_dir.mkdir()
    chart_path = performer_dir / '01_sample.png'
    chart_path.write_bytes(b'')

    markdown = _render_markdown(
        results,
        metadata,
        top_performers=[],
        viz_paths=viz_paths,
        performer_charts=[chart_path],
        optimizer_args={'start_date': '2020-01-01', 'cash': 10000, 'symbols_type': 'all', 'risk_profile': 'aggressive', 'top_k': 3, 'min_return': 'None'},
    )

    assert 'Performance Report' in markdown
    assert 'Strategy Rankings' in markdown
    assert 'Visualisations' in markdown
    assert 'top_performers/01_sample.png' in markdown

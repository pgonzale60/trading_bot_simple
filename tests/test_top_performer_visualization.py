import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from trading_bot import top_performer_visualization as tpv
from trading_bot.risk_management import RiskLevel


def test_parse_param_string_handles_dictionary():
    params = tpv.parse_param_string("SMA({'short_period': 5, 'long_period': 50})")
    assert params == {'short_period': 5, 'long_period': 50}


def test_parse_param_string_handles_default_marker():
    assert tpv.parse_param_string('SMA(default)') == {}


def test_coerce_helpers_accept_strings():
    aggressive = tpv._coerce_risk_level('aggressive')
    assert aggressive is RiskLevel.AGGRESSIVE

    with pytest.raises(ValueError):
        tpv._coerce_risk_level('unknown')

    assert tpv._coerce_stop_method('percentage').name == 'PERCENTAGE'


@pytest.mark.parametrize(
    'heat,drawdown',
    [
        (0.05, 0.01),
        (0.0, 0.0),
    ],
)
def test_build_history_dataframe_computes_percentages(heat, drawdown):
    strategy = SimpleNamespace(
        metrics_history=[
            {
                'timestamp': pd.Timestamp('2020-01-01'),
                'close': 10.0,
                'portfolio_value': 100.0,
                'cash': 60.0,
                'invested_value': 40.0,
                'portfolio_heat': heat,
                'drawdown': drawdown,
            },
            {
                'timestamp': pd.Timestamp('2020-01-02'),
                'close': 11.0,
                'portfolio_value': 105.0,
                'cash': 55.0,
                'invested_value': 50.0,
                'portfolio_heat': heat,
                'drawdown': drawdown,
            },
        ]
    )

    enriched = tpv._build_history_dataframe(strategy)

    assert 'exposure_pct' in enriched
    assert 'portfolio_heat_pct' in enriched
    assert 'drawdown_pct' in enriched
    assert enriched['exposure_pct'].iloc[0] == pytest.approx(0.4)
    assert enriched['portfolio_heat_pct'].iloc[0] == pytest.approx(heat * 100)


def test_visualize_top_performers_generates_output(tmp_path, monkeypatch):
    report_payload = {
        'optimization_metadata': {
            'start_date': '2020-01-01',
            'cash': 10000,
        },
        'results_by_symbol': {
            'DOGE-USD': {
                'symbol_type': 'crypto',
                'best_strategy': {
                    'strategy': 'sma',
                    'params': "SMA({'short_period': 5, 'long_period': 50, 'risk_profile': 'moderate'})",
                    'return_pct': 100.0,
                },
            },
            'ADA-USD': {
                'symbol_type': 'crypto',
                'best_strategy': {
                    'strategy': 'macd',
                    'params': "MACD({'fast_ema': 12, 'slow_ema': 26, 'signal_ema': 9})",
                    'return_pct': 80.0,
                },
            },
        },
    }

    report_path = tmp_path / 'report.json'
    report_path.write_text(json.dumps(report_payload))

    captured_plot_calls = []

    def fake_plot(history, trades, output_path, **kwargs):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text('ok')
        captured_plot_calls.append((history, trades, kwargs))

    class DummyCerebro:
        def __init__(self):
            self.broker = SimpleNamespace(
                setcash=lambda *_: None,
                setcommission=lambda **__: None,
                getvalue=lambda: 10000,
                getcash=lambda: 5000,
            )
            self.kwargs = None

        def addstrategy(self, strategy_cls, **kwargs):
            self.kwargs = kwargs

        def adddata(self, data):
            # Data is unused in the dummy implementation
            self.data = data

        def run(self):
            strategy = SimpleNamespace(
                metrics_history=[
                    {
                        'timestamp': pd.Timestamp('2020-01-01'),
                        'close': 1.0,
                        'portfolio_value': 10000.0,
                        'cash': 5000.0,
                        'invested_value': 5000.0,
                        'portfolio_heat': 0.05,
                        'drawdown': 0.02,
                    },
                    {
                        'timestamp': pd.Timestamp('2020-01-02'),
                        'close': 1.1,
                        'portfolio_value': 10400.0,
                        'cash': 4800.0,
                        'invested_value': 5600.0,
                        'portfolio_heat': 0.04,
                        'drawdown': 0.01,
                    },
                ],
                trade_events=[
                    tpv.TradeEvent(
                        timestamp=pd.Timestamp('2020-01-01'),
                        price=1.0,
                        size=100.0,
                        action='buy',
                    )
                ],
                risk_manager=SimpleNamespace(
                    risk_params={'max_portfolio_heat': 0.2, 'max_drawdown': 0.25}
                ),
            )
            return [strategy]

        def plot(self, *args, **kwargs):
            return []

    monkeypatch.setattr(tpv, 'plot_top_performer', fake_plot)
    monkeypatch.setattr(tpv.bt, 'Cerebro', DummyCerebro)
    monkeypatch.setattr(tpv, 'get_stock_data', lambda *_, **__: object())
    monkeypatch.setattr(tpv, 'build_tracking_strategy', lambda name: object)

    output_dir = tmp_path / 'charts'
    tpv.visualize_top_performers(report_path, output_dir, top_k=1, risk_profile=RiskLevel.AGGRESSIVE, min_return_pct=None)

    assert captured_plot_calls, 'expected plot_top_performer to be invoked'
    out_file = output_dir / '01_DOGE_USD_sma.png'
    assert out_file.exists()

    # Ensure risk profile coercion defaults apply when not specified in params
    plotted_kwargs = captured_plot_calls[0][2]
    assert plotted_kwargs['symbol'] == 'DOGE-USD'

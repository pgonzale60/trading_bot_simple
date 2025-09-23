"""
Multiple Trading Strategies for Systematic Testing

This module contains various trading strategies that can be compared
and optimized to find what actually works.
"""

import backtrader as bt


class SMAStrategy(bt.Strategy):
    """Simple Moving Average Crossover Strategy."""
    params = (
        ('short_period', 10),
        ('long_period', 30),
    )

    def __init__(self):
        self.short_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.short_period
        )
        self.long_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.long_period
        )
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        else:
            if self.crossover < 0:
                self.sell()


class RSIStrategy(bt.Strategy):
    """RSI (Relative Strength Index) Strategy."""
    params = (
        ('rsi_period', 14),
        ('rsi_low', 30),
        ('rsi_high', 70),
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(
            self.data.close,
            period=self.params.rsi_period
        )

    def next(self):
        if not self.position:
            # Buy when RSI is oversold
            if self.rsi < self.params.rsi_low:
                self.buy()
        else:
            # Sell when RSI is overbought
            if self.rsi > self.params.rsi_high:
                self.sell()


class MACDStrategy(bt.Strategy):
    """MACD (Moving Average Convergence Divergence) Strategy."""
    params = (
        ('fast_ema', 12),
        ('slow_ema', 26),
        ('signal_ema', 9),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.fast_ema,
            period_me2=self.params.slow_ema,
            period_signal=self.params.signal_ema
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if not self.position:
            if self.crossover > 0:  # MACD crosses above signal
                self.buy()
        else:
            if self.crossover < 0:  # MACD crosses below signal
                self.sell()


class BollingerBandsStrategy(bt.Strategy):
    """Bollinger Bands Mean Reversion Strategy."""
    params = (
        ('period', 20),
        ('devfactor', 2.0),
    )

    def __init__(self):
        self.bollinger = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.period,
            devfactor=self.params.devfactor
        )

    def next(self):
        if not self.position:
            # Buy when price touches lower band
            if self.data.close <= self.bollinger.lines.bot:
                self.buy()
        else:
            # Sell when price touches upper band
            if self.data.close >= self.bollinger.lines.top:
                self.sell()


class EMAStrategy(bt.Strategy):
    """Exponential Moving Average Crossover Strategy."""
    params = (
        ('short_period', 10),
        ('long_period', 30),
    )

    def __init__(self):
        self.short_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.short_period
        )
        self.long_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.long_period
        )
        self.crossover = bt.indicators.CrossOver(self.short_ema, self.long_ema)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        else:
            if self.crossover < 0:
                self.sell()


class MomentumStrategy(bt.Strategy):
    """Simple Momentum Strategy."""
    params = (
        ('period', 10),
        ('threshold', 0.02),  # 2% momentum threshold
    )

    def __init__(self):
        self.momentum = bt.indicators.Momentum(
            self.data.close,
            period=self.params.period
        )

    def next(self):
        momentum_pct = (self.momentum[0] / self.data.close[-self.params.period]) - 1

        if not self.position:
            # Buy on positive momentum
            if momentum_pct > self.params.threshold:
                self.buy()
        else:
            # Sell on negative momentum
            if momentum_pct < -self.params.threshold:
                self.sell()


class BuyAndHoldStrategy(bt.Strategy):
    """Buy and Hold Benchmark Strategy."""

    def __init__(self):
        self.bought = False

    def next(self):
        if not self.bought:
            self.buy()
            self.bought = True


# Strategy registry for easy access
STRATEGIES = {
    'sma': SMAStrategy,
    'rsi': RSIStrategy,
    'macd': MACDStrategy,
    'bollinger': BollingerBandsStrategy,
    'ema': EMAStrategy,
    'momentum': MomentumStrategy,
    'buy_hold': BuyAndHoldStrategy,
}


def get_strategy_params(strategy_name):
    """Get default parameter ranges for optimization."""
    param_ranges = {
        'sma': {
            'short_period': [5, 10, 15, 20],
            'long_period': [30, 50, 100]
        },
        'rsi': {
            'rsi_period': [10, 14, 20],
            'rsi_low': [20, 25, 30],
            'rsi_high': [70, 75, 80]
        },
        'macd': {
            'fast_ema': [8, 12, 16],
            'slow_ema': [21, 26, 30],
            'signal_ema': [6, 9, 12]
        },
        'bollinger': {
            'period': [15, 20, 25],
            'devfactor': [1.5, 2.0, 2.5]
        },
        'ema': {
            'short_period': [5, 10, 15, 20],
            'long_period': [30, 50, 100]
        },
        'momentum': {
            'period': [5, 10, 15, 20],
            'threshold': [0.01, 0.02, 0.03, 0.05]
        }
    }

    return param_ranges.get(strategy_name, {})
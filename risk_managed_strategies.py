#!/usr/bin/env python3
"""
Risk-Managed Trading Strategies

All strategies have been converted to use the comprehensive risk management framework.
These strategies replace the old high-risk implementations with proper:
- Position sizing based on risk percentage
- Stop loss management
- Portfolio heat monitoring
- Drawdown protection
- Professional trade tracking
"""

import backtrader as bt
from risk_managed_strategy import RiskManagedStrategy
from risk_management import RiskLevel, StopLossMethod
from risk_config import StrategyType


class RiskManagedSMAStrategy(RiskManagedStrategy):
    """Risk-Managed Simple Moving Average Crossover Strategy"""

    params = (
        ('short_period', 10),
        ('long_period', 30),
        ('risk_profile', RiskLevel.MODERATE),
        ('stop_loss_method', StopLossMethod.ATR),
    )

    def __init__(self):
        # Set strategy type for proper risk configuration
        self.strategy_type = StrategyType.TREND_FOLLOWING

        # Initialize parent class (includes risk management)
        super().__init__()

        # Strategy-specific indicators
        self.short_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.short_period
        )
        self.long_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.long_period
        )
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)

    def next(self):
        # Golden Cross - buy signal
        if not self.position and self.crossover > 0:
            self.enter_long(
                reason=f"Golden Cross - SMA{self.params.short_period} > SMA{self.params.long_period}",
                stop_method=self.params.stop_loss_method
            )

        # Death Cross - sell signal
        elif self.position and self.crossover < 0:
            self.exit_position(
                reason=f"Death Cross - SMA{self.params.short_period} < SMA{self.params.long_period}"
            )


class RiskManagedEMAStrategy(RiskManagedStrategy):
    """Risk-Managed Exponential Moving Average Crossover Strategy"""

    params = (
        ('short_period', 10),
        ('long_period', 30),
        ('risk_profile', RiskLevel.MODERATE),
        ('stop_loss_method', StopLossMethod.ATR),
    )

    def __init__(self):
        self.strategy_type = StrategyType.TREND_FOLLOWING
        super().__init__()

        self.short_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.short_period
        )
        self.long_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.long_period
        )
        self.crossover = bt.indicators.CrossOver(self.short_ema, self.long_ema)

    def next(self):
        if not self.position and self.crossover > 0:
            self.enter_long(
                reason=f"EMA Golden Cross - EMA{self.params.short_period} > EMA{self.params.long_period}",
                stop_method=self.params.stop_loss_method
            )

        elif self.position and self.crossover < 0:
            self.exit_position(
                reason=f"EMA Death Cross - EMA{self.params.short_period} < EMA{self.params.long_period}"
            )


class RiskManagedMACDStrategy(RiskManagedStrategy):
    """Risk-Managed MACD Strategy"""

    params = (
        ('fast_ema', 12),
        ('slow_ema', 26),
        ('signal_ema', 9),
        ('risk_profile', RiskLevel.MODERATE),
        ('stop_loss_method', StopLossMethod.ATR),
    )

    def __init__(self):
        self.strategy_type = StrategyType.TREND_FOLLOWING
        super().__init__()

        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.fast_ema,
            period_me2=self.params.slow_ema,
            period_signal=self.params.signal_ema
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if not self.position and self.crossover > 0:
            self.enter_long(
                reason="MACD Bullish Cross - MACD > Signal",
                stop_method=self.params.stop_loss_method
            )

        elif self.position and self.crossover < 0:
            self.exit_position(
                reason="MACD Bearish Cross - MACD < Signal"
            )


class RiskManagedRSIStrategy(RiskManagedStrategy):
    """Risk-Managed RSI Mean Reversion Strategy"""

    params = (
        ('rsi_period', 14),
        ('rsi_low', 30),
        ('rsi_high', 70),
        ('rsi_neutral', 50),
        ('risk_profile', RiskLevel.MODERATE),
        ('stop_loss_method', StopLossMethod.PERCENTAGE),
    )

    def __init__(self):
        self.strategy_type = StrategyType.MEAN_REVERSION
        super().__init__()

        self.rsi = bt.indicators.RSI(
            self.data.close,
            period=self.params.rsi_period
        )

    def next(self):
        # Buy on oversold condition
        if not self.position and self.rsi < self.params.rsi_low:
            self.enter_long(
                reason=f"RSI Oversold - RSI: {self.rsi[0]:.1f} < {self.params.rsi_low}",
                stop_method=self.params.stop_loss_method
            )

        # Sell on overbought or return to neutral
        elif self.position and (self.rsi > self.params.rsi_high or
                               self.rsi > self.params.rsi_neutral):
            exit_reason = "RSI Overbought" if self.rsi > self.params.rsi_high else "RSI Neutral"
            self.exit_position(
                reason=f"{exit_reason} - RSI: {self.rsi[0]:.1f}"
            )


class RiskManagedBollingerBandsStrategy(RiskManagedStrategy):
    """Risk-Managed Bollinger Bands Mean Reversion Strategy"""

    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('risk_profile', RiskLevel.CONSERVATIVE),  # More conservative for mean reversion
        ('stop_loss_method', StopLossMethod.PERCENTAGE),
    )

    def __init__(self):
        self.strategy_type = StrategyType.MEAN_REVERSION
        super().__init__()

        self.bollinger = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.period,
            devfactor=self.params.devfactor
        )

    def next(self):
        # Buy when price touches lower band (oversold)
        if not self.position and self.data.close[0] <= self.bollinger.lines.bot[0]:
            self.enter_long(
                reason=f"Bollinger Lower Band Touch - Price: ${self.data.close[0]:.2f}",
                stop_method=self.params.stop_loss_method
            )

        # Sell when price reaches upper band or middle line
        elif self.position and (self.data.close[0] >= self.bollinger.lines.top[0] or
                               self.data.close[0] >= self.bollinger.lines.mid[0]):
            exit_reason = "Upper Band" if self.data.close[0] >= self.bollinger.lines.top[0] else "Middle Band"
            self.exit_position(
                reason=f"Bollinger {exit_reason} - Price: ${self.data.close[0]:.2f}"
            )


class RiskManagedMomentumStrategy(RiskManagedStrategy):
    """Risk-Managed Momentum Strategy"""

    params = (
        ('period', 10),
        ('threshold', 0.02),  # 2% momentum threshold
        ('profit_target', 0.05),  # 5% profit target
        ('risk_profile', RiskLevel.AGGRESSIVE),  # Momentum can be more aggressive
        ('stop_loss_method', StopLossMethod.PERCENTAGE),
    )

    def __init__(self):
        self.strategy_type = StrategyType.MOMENTUM
        super().__init__()

        self.momentum = bt.indicators.Momentum(
            self.data.close,
            period=self.params.period
        )

    def next(self):
        if len(self) < self.params.period:
            return

        # Calculate momentum percentage
        momentum_pct = (self.momentum[0] / self.data.close[-self.params.period]) - 1

        # Buy on strong positive momentum
        if not self.position and momentum_pct > self.params.threshold:
            self.enter_long(
                reason=f"Strong Momentum - {momentum_pct*100:.1f}% > {self.params.threshold*100:.1f}%",
                stop_method=self.params.stop_loss_method
            )

        # Exit on negative momentum or profit target
        elif self.position:
            # Check profit target
            if (hasattr(self.position, 'price') and self.position.price and
                (self.data.close[0] / self.position.price - 1) > self.params.profit_target):
                self.exit_position(
                    reason=f"Profit Target Reached - {((self.data.close[0]/self.position.price-1)*100):.1f}%"
                )
            # Check momentum reversal
            elif momentum_pct < -self.params.threshold:
                self.exit_position(
                    reason=f"Momentum Reversal - {momentum_pct*100:.1f}% < -{self.params.threshold*100:.1f}%"
                )


class RiskManagedBuyAndHoldStrategy(RiskManagedStrategy):
    """Risk-Managed Buy and Hold Strategy"""

    params = (
        ('risk_profile', RiskLevel.CONSERVATIVE),  # Very conservative for buy & hold
        ('stop_loss_method', StopLossMethod.PERCENTAGE),
    )

    def __init__(self):
        self.strategy_type = StrategyType.BUY_HOLD
        super().__init__()

        self.bought = False

    def next(self):
        # Buy once at the beginning if we haven't bought yet
        if not self.bought and not self.position:
            self.enter_long(
                reason="Buy and Hold Initial Purchase",
                stop_method=self.params.stop_loss_method
            )
            self.bought = True


# Strategy registry for risk-managed strategies
RISK_MANAGED_STRATEGIES = {
    'sma': RiskManagedSMAStrategy,
    'ema': RiskManagedEMAStrategy,
    'macd': RiskManagedMACDStrategy,
    'rsi': RiskManagedRSIStrategy,
    'bollinger': RiskManagedBollingerBandsStrategy,
    'momentum': RiskManagedMomentumStrategy,
    'buy_hold': RiskManagedBuyAndHoldStrategy,
}


def get_risk_managed_strategy_params(strategy_name):
    """Get default parameter ranges for optimization of risk-managed strategies"""
    param_ranges = {
        'sma': {
            'short_period': [5, 10, 15, 20],
            'long_period': [30, 50, 100],
            'risk_profile': [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]
        },
        'ema': {
            'short_period': [5, 10, 15, 20],
            'long_period': [30, 50, 100],
            'risk_profile': [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]
        },
        'rsi': {
            'rsi_period': [10, 14, 20],
            'rsi_low': [20, 25, 30],
            'rsi_high': [70, 75, 80],
            'risk_profile': [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE]
        },
        'macd': {
            'fast_ema': [8, 12, 16],
            'slow_ema': [21, 26, 30],
            'signal_ema': [6, 9, 12],
            'risk_profile': [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]
        },
        'bollinger': {
            'period': [15, 20, 25],
            'devfactor': [1.5, 2.0, 2.5],
            'risk_profile': [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE]
        },
        'momentum': {
            'period': [5, 10, 15, 20],
            'threshold': [0.01, 0.02, 0.03, 0.05],
            'risk_profile': [RiskLevel.MODERATE, RiskLevel.AGGRESSIVE]
        },
        'buy_hold': {
            'risk_profile': [RiskLevel.CONSERVATIVE, RiskLevel.MODERATE]
        }
    }

    return param_ranges.get(strategy_name, {})
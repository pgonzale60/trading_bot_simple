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
        ('portfolio_pct', 0.95),  # Use 95% of available cash
    )

    def __init__(self):
        self.short_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.short_period
        )
        self.long_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.long_period
        )
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)
        self.order = None

    def next(self):
        if self.order:  # Skip if order is pending
            return

        if not self.position:
            if self.crossover > 0:  # Golden cross - buy signal
                cash = self.broker.getcash() * self.params.portfolio_pct
                size = int(cash / self.data.close[0])
                if size > 0:
                    self.order = self.buy(size=size)
                    self.log(f'BUY SIGNAL - Size: {size}, Price: {self.data.close[0]:.2f}')
        else:
            if self.crossover < 0:  # Death cross - sell signal
                self.order = self.sell(size=self.position.size)
                self.log(f'SELL SIGNAL - Size: {self.position.size}, Price: {self.data.close[0]:.2f}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'TRADE CLOSED - P&L: ${trade.pnl:.2f}, P&L Net: ${trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')


class RSIStrategy(bt.Strategy):
    """RSI (Relative Strength Index) Strategy."""
    params = (
        ('rsi_period', 14),
        ('rsi_low', 30),
        ('rsi_high', 70),
        ('portfolio_pct', 0.95),
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(
            self.data.close,
            period=self.params.rsi_period
        )
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy when RSI is oversold (potential bounce)
            if self.rsi < self.params.rsi_low:
                cash = self.broker.getcash() * self.params.portfolio_pct
                size = int(cash / self.data.close[0])
                if size > 0:
                    self.order = self.buy(size=size)
                    self.log(f'BUY SIGNAL (RSI: {self.rsi[0]:.1f}) - Size: {size}, Price: {self.data.close[0]:.2f}')
        else:
            # Sell when RSI is overbought OR returns to neutral (take profits)
            if self.rsi > self.params.rsi_high or self.rsi > 50:
                self.order = self.sell(size=self.position.size)
                self.log(f'SELL SIGNAL (RSI: {self.rsi[0]:.1f}) - Size: {self.position.size}, Price: {self.data.close[0]:.2f}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'TRADE CLOSED - P&L: ${trade.pnl:.2f}, P&L Net: ${trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')


class MACDStrategy(bt.Strategy):
    """MACD (Moving Average Convergence Divergence) Strategy."""
    params = (
        ('fast_ema', 12),
        ('slow_ema', 26),
        ('signal_ema', 9),
        ('portfolio_pct', 0.95),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.fast_ema,
            period_me2=self.params.slow_ema,
            period_signal=self.params.signal_ema
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:  # MACD crosses above signal - bullish
                cash = self.broker.getcash() * self.params.portfolio_pct
                size = int(cash / self.data.close[0])
                if size > 0:
                    self.order = self.buy(size=size)
                    self.log(f'BUY SIGNAL (MACD Cross) - Size: {size}, Price: {self.data.close[0]:.2f}')
        else:
            if self.crossover < 0:  # MACD crosses below signal - bearish
                self.order = self.sell(size=self.position.size)
                self.log(f'SELL SIGNAL (MACD Cross) - Size: {self.position.size}, Price: {self.data.close[0]:.2f}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'TRADE CLOSED - P&L: ${trade.pnl:.2f}, P&L Net: ${trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')


class BollingerBandsStrategy(bt.Strategy):
    """Bollinger Bands Mean Reversion Strategy."""
    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('portfolio_pct', 0.95),
    )

    def __init__(self):
        self.bollinger = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.period,
            devfactor=self.params.devfactor
        )
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy when price touches lower band (oversold)
            if self.data.close[0] <= self.bollinger.lines.bot[0]:
                cash = self.broker.getcash() * self.params.portfolio_pct
                size = int(cash / self.data.close[0])
                if size > 0:
                    self.order = self.buy(size=size)
                    self.log(f'BUY SIGNAL (Lower Band) - Size: {size}, Price: {self.data.close[0]:.2f}')
        else:
            # Sell when price touches upper band (overbought) or returns to middle
            if (self.data.close[0] >= self.bollinger.lines.top[0] or
                self.data.close[0] >= self.bollinger.lines.mid[0]):
                self.order = self.sell(size=self.position.size)
                self.log(f'SELL SIGNAL (Upper/Mid Band) - Size: {self.position.size}, Price: {self.data.close[0]:.2f}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'TRADE CLOSED - P&L: ${trade.pnl:.2f}, P&L Net: ${trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')


class EMAStrategy(bt.Strategy):
    """Exponential Moving Average Crossover Strategy."""
    params = (
        ('short_period', 10),
        ('long_period', 30),
        ('portfolio_pct', 0.95),
    )

    def __init__(self):
        self.short_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.short_period
        )
        self.long_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.long_period
        )
        self.crossover = bt.indicators.CrossOver(self.short_ema, self.long_ema)
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:  # Short EMA crosses above Long EMA - bullish
                cash = self.broker.getcash() * self.params.portfolio_pct
                size = int(cash / self.data.close[0])
                if size > 0:
                    self.order = self.buy(size=size)
                    self.log(f'BUY SIGNAL (EMA Cross) - Size: {size}, Price: {self.data.close[0]:.2f}')
        else:
            if self.crossover < 0:  # Short EMA crosses below Long EMA - bearish
                self.order = self.sell(size=self.position.size)
                self.log(f'SELL SIGNAL (EMA Cross) - Size: {self.position.size}, Price: {self.data.close[0]:.2f}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'TRADE CLOSED - P&L: ${trade.pnl:.2f}, P&L Net: ${trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')


class MomentumStrategy(bt.Strategy):
    """Simple Momentum Strategy."""
    params = (
        ('period', 10),
        ('threshold', 0.02),  # 2% momentum threshold
        ('portfolio_pct', 0.95),
    )

    def __init__(self):
        self.momentum = bt.indicators.Momentum(
            self.data.close,
            period=self.params.period
        )
        self.order = None

    def next(self):
        if self.order or len(self) < self.params.period:
            return

        # Calculate momentum as percentage change
        momentum_pct = (self.momentum[0] / self.data.close[-self.params.period]) - 1

        if not self.position:
            # Buy on positive momentum
            if momentum_pct > self.params.threshold:
                cash = self.broker.getcash() * self.params.portfolio_pct
                size = int(cash / self.data.close[0])
                if size > 0:
                    self.order = self.buy(size=size)
                    self.log(f'BUY SIGNAL (Momentum: {momentum_pct*100:.1f}%) - Size: {size}, Price: {self.data.close[0]:.2f}')
        else:
            # Sell on negative momentum or take profits at 5%+ gain
            if (momentum_pct < -self.params.threshold or
                (self.position.price and (self.data.close[0] / self.position.price - 1) > 0.05)):
                self.order = self.sell(size=self.position.size)
                self.log(f'SELL SIGNAL (Momentum: {momentum_pct*100:.1f}%) - Size: {self.position.size}, Price: {self.data.close[0]:.2f}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'TRADE CLOSED - P&L: ${trade.pnl:.2f}, P&L Net: ${trade.pnlcomm:.2f}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')


class BuyAndHoldStrategy(bt.Strategy):
    """Buy and Hold Benchmark Strategy."""

    def __init__(self):
        self.order = None
        self.bought = False

    def start(self):
        self.val_start = self.broker.getcash()

    def next(self):
        # Only buy once at the beginning if we haven't bought yet
        if not self.bought and not self.order:
            # Calculate how many shares we can buy with all our cash
            available_cash = self.broker.getcash()
            current_price = self.data.close[0]
            shares_to_buy = int(available_cash / current_price)

            if shares_to_buy > 0:
                self.order = self.buy(size=shares_to_buy)
                self.log(f'BUY ORDER SUBMITTED - Shares: {shares_to_buy}, Price: {current_price:.2f}, Total: ${shares_to_buy * current_price:.2f}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.bought = True
                self.log(f'BUY EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED - Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, Commission: ${order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def log(self, txt, dt=None):
        """Logging function for this strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')


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
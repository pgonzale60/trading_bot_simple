import backtrader as bt


class SMAStrategy(bt.Strategy):
    params = (
        ('short_period', 10),
        ('long_period', 30),
    )

    def __init__(self):
        # Create moving averages
        self.short_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.short_period
        )
        self.long_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.long_period
        )

        # Create crossover signal
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)

    def next(self):
        # If we don't have a position, look for buy signal
        if not self.position:
            if self.crossover > 0:  # Short MA crosses above Long MA
                self.buy()
                print(f"BUY signal at {self.data.datetime.date(0)} - Price: ${self.data.close[0]:.2f}")

        # If we have a position, look for sell signal
        else:
            if self.crossover < 0:  # Short MA crosses below Long MA
                self.sell()
                print(f"SELL signal at {self.data.datetime.date(0)} - Price: ${self.data.close[0]:.2f}")

    def notify_trade(self, trade):
        if trade.isclosed:
            print(f"Trade closed: PnL = ${trade.pnl:.2f}")
#!/usr/bin/env python3
"""
Risk-Managed Strategy Base Class

Provides a base class for all trading strategies with integrated risk management.
All strategies should inherit from RiskManagedStrategy instead of bt.Strategy.
"""

import backtrader as bt
import uuid
from typing import Dict, Optional, Any
from risk_management import RiskManager, RiskLevel, StopLossMethod


class RiskManagedStrategy(bt.Strategy):
    """
    Base strategy class with integrated risk management

    All trading strategies should inherit from this class to get:
    - Automatic position sizing based on risk
    - Stop loss management
    - Portfolio heat monitoring
    - Drawdown protection
    - Trade tracking and metrics
    """

    params = (
        # Risk Management Parameters
        ('risk_profile', RiskLevel.MODERATE),  # CONSERVATIVE, MODERATE, AGGRESSIVE
        ('stop_loss_method', StopLossMethod.PERCENTAGE),  # PERCENTAGE, ATR, etc.
        ('enable_risk_logging', True),  # Log risk metrics
        ('log_all_signals', False),  # Log all buy/sell signals (including rejected)

        # Strategy-specific parameters (can be overridden)
        ('portfolio_pct', 0.95),  # Deprecated - now handled by risk manager
    )

    def __init__(self):
        # Initialize risk management
        self.risk_manager = RiskManager(self, self.params.risk_profile)

        # Position and order tracking
        self.active_orders = {}  # order_id -> position info
        self.active_positions = {}  # position_id -> position info
        self.order_counter = 0

        # Technical indicators commonly used for risk management
        self.atr = bt.indicators.ATR(self.data, period=20)

        # Trade tracking
        self.trade_count = 0
        self.last_trade_profitable = None

        # Call parent init for any strategy-specific indicators
        super().__init__()

    def enter_long(self, reason: str = "", stop_method: Optional[StopLossMethod] = None) -> Optional[bt.Order]:
        """
        Enter a long position with integrated risk management

        Args:
            reason: Reason for entering trade (for logging)
            stop_method: Override default stop loss method

        Returns:
            Order object if trade was entered, None if rejected
        """
        if not self.risk_manager.should_enter_trade():
            if self.params.log_all_signals:
                self.log(f"LONG SIGNAL REJECTED - Risk controls prevented entry: {reason}")
            return None

        # Get entry price and calculate stop
        entry_price = self.data.close[0]
        stop_method = stop_method or self.params.stop_loss_method
        atr_value = self.atr[0] if len(self.atr) > 0 else None

        stop_price = self.risk_manager.get_stop_loss_price(
            entry_price, is_long=True, method=stop_method, atr_value=atr_value
        )

        # Calculate position size
        size = self.risk_manager.calculate_position_size(entry_price, stop_price)

        if size <= 0:
            if self.params.log_all_signals:
                self.log(f"LONG SIGNAL REJECTED - Position size too small: {reason}")
            return None

        # Place the order
        order = self.buy(size=size)
        if order:
            order_id = str(uuid.uuid4())
            self.active_orders[id(order)] = {
                'order': order,
                'order_id': order_id,
                'entry_price': entry_price,
                'stop_price': stop_price,
                'size': size,
                'is_long': True,
                'reason': reason,
                'stop_method': stop_method,
                'stop_order': None  # Will be set when entry is filled
            }

            self.log(f"LONG ENTRY SUBMITTED - Size: {size}, Entry: ${entry_price:.2f}, "
                    f"Stop: ${stop_price:.2f}, Risk: ${abs(entry_price-stop_price)*size:.2f}, "
                    f"Reason: {reason}")

        return order

    def enter_short(self, reason: str = "", stop_method: Optional[StopLossMethod] = None) -> Optional[bt.Order]:
        """
        Enter a short position with integrated risk management

        Args:
            reason: Reason for entering trade (for logging)
            stop_method: Override default stop loss method

        Returns:
            Order object if trade was entered, None if rejected
        """
        if not self.risk_manager.should_enter_trade():
            if self.params.log_all_signals:
                self.log(f"SHORT SIGNAL REJECTED - Risk controls prevented entry: {reason}")
            return None

        # Get entry price and calculate stop
        entry_price = self.data.close[0]
        stop_method = stop_method or self.params.stop_loss_method
        atr_value = self.atr[0] if len(self.atr) > 0 else None

        stop_price = self.risk_manager.get_stop_loss_price(
            entry_price, is_long=False, method=stop_method, atr_value=atr_value
        )

        # Calculate position size
        size = self.risk_manager.calculate_position_size(entry_price, stop_price)

        if size <= 0:
            if self.params.log_all_signals:
                self.log(f"SHORT SIGNAL REJECTED - Position size too small: {reason}")
            return None

        # Place the order
        order = self.sell(size=size)
        if order:
            order_id = str(uuid.uuid4())
            self.active_orders[id(order)] = {
                'order': order,
                'order_id': order_id,
                'entry_price': entry_price,
                'stop_price': stop_price,
                'size': size,
                'is_long': False,
                'reason': reason,
                'stop_method': stop_method,
                'stop_order': None  # Will be set when entry is filled
            }

            self.log(f"SHORT ENTRY SUBMITTED - Size: {size}, Entry: ${entry_price:.2f}, "
                    f"Stop: ${stop_price:.2f}, Risk: ${abs(entry_price-stop_price)*size:.2f}, "
                    f"Reason: {reason}")

        return order

    def exit_position(self, reason: str = "Manual Exit") -> Optional[bt.Order]:
        """
        Exit current position manually

        Args:
            reason: Reason for exit

        Returns:
            Order object if exit was placed
        """
        if not self.position:
            return None

        if self.position.size > 0:
            order = self.sell(size=abs(self.position.size))
            self.log(f"LONG EXIT SUBMITTED - Size: {abs(self.position.size)}, "
                    f"Price: ${self.data.close[0]:.2f}, Reason: {reason}")
        else:
            order = self.buy(size=abs(self.position.size))
            self.log(f"SHORT EXIT SUBMITTED - Size: {abs(self.position.size)}, "
                    f"Price: ${self.data.close[0]:.2f}, Reason: {reason}")

        return order

    def notify_order(self, order):
        """Enhanced order notification with risk management"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        # Get order info if it exists
        order_info = self.active_orders.get(id(order))

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED - Price: ${order.executed.price:.2f}, "
                        f"Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, "
                        f"Commission: ${order.executed.comm:.2f}")

                # Set up stop loss for new long position
                if order_info and order_info['is_long']:
                    self._setup_stop_loss(order, order_info)

            elif order.issell():
                self.log(f"SELL EXECUTED - Price: ${order.executed.price:.2f}, "
                        f"Size: {order.executed.size}, Cost: ${order.executed.value:.2f}, "
                        f"Commission: ${order.executed.comm:.2f}")

                # Set up stop loss for new short position
                if order_info and not order_info['is_long']:
                    self._setup_stop_loss(order, order_info)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f"ORDER REJECTED - Status: {order.getstatusname()}")

            # Clean up rejected order
            if id(order) in self.active_orders:
                del self.active_orders[id(order)]

        # Clean up completed orders
        if id(order) in self.active_orders and order.status in [order.Completed]:
            order_info = self.active_orders[id(order)]
            # Update risk manager
            self.risk_manager.update_position_risk(
                order_info['order_id'],
                order.executed.price,
                order_info['stop_price'],
                order.executed.size
            )
            del self.active_orders[id(order)]

    def notify_trade(self, trade):
        """Enhanced trade notification with risk management"""
        if not trade.isclosed:
            return

        # Track trade statistics
        self.trade_count += 1
        self.last_trade_profitable = trade.pnl > 0

        # Update risk manager
        self.risk_manager.total_trades += 1
        if trade.pnl > 0:
            self.risk_manager.winning_trades += 1

        # Log trade results
        self.log(f"TRADE #{self.trade_count} CLOSED - "
                f"P&L: ${trade.pnl:.2f}, P&L Net: ${trade.pnlcomm:.2f}, "
                f"Size: {trade.size}, Bars: {trade.barlen}")

        # Remove from risk tracking
        # Note: In a more sophisticated system, we'd track this properly
        # For now, we'll clean up based on trade completion

        # Log risk status periodically
        if self.params.enable_risk_logging and self.trade_count % 5 == 0:
            self.risk_manager.log_risk_status()

    def _setup_stop_loss(self, entry_order, order_info):
        """Set up stop loss order after entry is filled"""
        try:
            if order_info['is_long']:
                # Long position - stop loss below entry
                stop_order = self.sell(
                    exectype=bt.Order.Stop,
                    price=order_info['stop_price'],
                    size=entry_order.executed.size
                )
            else:
                # Short position - stop loss above entry
                stop_order = self.buy(
                    exectype=bt.Order.Stop,
                    price=order_info['stop_price'],
                    size=entry_order.executed.size
                )

            if stop_order:
                order_info['stop_order'] = stop_order
                self.log(f"STOP LOSS SET - Price: ${order_info['stop_price']:.2f}")

        except Exception as e:
            self.log(f"STOP LOSS SETUP FAILED: {e}")

    def next(self):
        """
        Main strategy logic - must be implemented by child classes

        Child classes should implement their trading logic here and use:
        - self.enter_long(reason="Signal description")
        - self.enter_short(reason="Signal description")
        - self.exit_position(reason="Exit description")

        Instead of directly calling self.buy() or self.sell()
        """
        raise NotImplementedError("Child strategies must implement next() method")

    def log(self, txt, dt=None):
        """Enhanced logging with timestamp"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

    def get_risk_metrics(self) -> Dict[str, Any]:
        """Get comprehensive risk metrics for the strategy"""
        metrics = self.risk_manager.get_risk_metrics()

        # Add strategy-specific metrics
        win_rate = 0
        if self.risk_manager.total_trades > 0:
            win_rate = (self.risk_manager.winning_trades / self.risk_manager.total_trades) * 100

        metrics.update({
            'total_trades': self.trade_count,
            'win_rate': win_rate,
            'active_orders': len(self.active_orders),
            'has_position': bool(self.position.size if self.position else False),
            'current_price': float(self.data.close[0]) if len(self.data.close) > 0 else 0
        })

        return metrics

    def print_risk_summary(self):
        """Print a comprehensive risk summary"""
        metrics = self.get_risk_metrics()

        print("\n" + "="*60)
        print("RISK MANAGEMENT SUMMARY")
        print("="*60)
        print(f"Risk Profile: {metrics['risk_profile'].upper()}")
        print(f"Account Value: ${metrics['account_value']:,.2f}")
        print(f"Peak Equity: ${metrics['peak_equity']:,.2f}")
        print(f"Current Drawdown: {metrics['current_drawdown']*100:.1f}%")
        print(f"Portfolio Heat: {metrics['portfolio_heat']*100:.1f}%")
        print(f"Active Positions: {metrics['active_positions']}/{metrics['max_positions']}")
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.1f}%")
        print(f"Trading Status: {'HALTED' if metrics['trading_halted'] else 'ACTIVE'}")
        print(f"Drawdown Protection: {'ACTIVE' if metrics['in_drawdown_protection'] else 'NORMAL'}")
        print("="*60)
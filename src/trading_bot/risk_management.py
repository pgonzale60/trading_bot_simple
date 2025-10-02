#!/usr/bin/env python3
"""
Comprehensive Risk Management Framework for Trading Strategies

This module provides centralized risk management capabilities including:
- Position sizing based on risk percentage
- Stop loss management with multiple methods
- Portfolio heat monitoring
- Drawdown protection with circuit breakers
- Volatility-based adjustments
"""

import backtrader as bt
import numpy as np
from enum import Enum
from typing import Dict, Optional, Tuple, List
import warnings


class StopLossMethod(Enum):
    """Available stop loss calculation methods"""
    PERCENTAGE = "percentage"
    ATR = "atr"
    SUPPORT_RESISTANCE = "support_resistance"
    TRAILING = "trailing"


class RiskLevel(Enum):
    """Risk profile levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class RiskManager:
    """Centralized risk management for trading strategies"""

    def __init__(self, strategy, risk_profile: RiskLevel = RiskLevel.MODERATE):
        self.strategy = strategy
        self.risk_profile = risk_profile

        # Risk parameters based on profile
        self.risk_params = self._get_risk_parameters(risk_profile)

        # State tracking
        self.peak_equity = 0
        self.positions_risk = {}  # Track risk per position
        self.total_trades = 0
        self.winning_trades = 0

        # Risk controls
        self.in_drawdown_protection = False
        self.trading_halted = False

    def _get_risk_parameters(self, risk_profile: RiskLevel) -> Dict:
        """Get risk parameters based on profile"""
        profiles = {
            RiskLevel.CONSERVATIVE: {
                'risk_per_trade': 0.015,      # 1.5% risk per trade
                'max_position_pct': 0.12,     # Max 12% of portfolio per position
                'max_portfolio_heat': 0.08,   # Max 8% total portfolio at risk
                'max_drawdown': 0.12,         # Stop at 12% drawdown
                'max_positions': 2,           # Max 2 concurrent positions
                'stop_loss_pct': 0.03,        # 3% stop loss
                'atr_multiplier': 1.5,        # 1.5x ATR for stops
                'drawdown_reduction_threshold': 0.08,  # Reduce risk at 8% drawdown
            },
            RiskLevel.MODERATE: {
                'risk_per_trade': 0.02,       # 2% risk per trade
                'max_position_pct': 0.15,     # Max 15% of portfolio per position
                'max_portfolio_heat': 0.10,   # Max 10% total portfolio at risk
                'max_drawdown': 0.15,         # Stop at 15% drawdown
                'max_positions': 3,           # Max 3 concurrent positions
                'stop_loss_pct': 0.04,        # 4% stop loss
                'atr_multiplier': 2.0,        # 2x ATR for stops
                'drawdown_reduction_threshold': 0.10,  # Reduce risk at 10% drawdown
            },
            RiskLevel.AGGRESSIVE: {
                'risk_per_trade': 0.025,      # 2.5% risk per trade
                'max_position_pct': 0.20,     # Max 20% of portfolio per position
                'max_portfolio_heat': 0.12,   # Max 12% total portfolio at risk
                'max_drawdown': 0.18,         # Stop at 18% drawdown
                'max_positions': 4,           # Max 4 concurrent positions
                'stop_loss_pct': 0.05,        # 5% stop loss
                'atr_multiplier': 2.5,        # 2.5x ATR for stops
                'drawdown_reduction_threshold': 0.12,  # Reduce risk at 12% drawdown
            }
        }
        return profiles[risk_profile]

    def calculate_position_size(self, entry_price: float, stop_price: float,
                              volatility: Optional[float] = None,
                              allow_fractional: bool = None) -> float:
        """
        Calculate position size based on risk parameters

        Args:
            entry_price: Intended entry price
            stop_price: Stop loss price
            volatility: Optional volatility adjustment (0-1 scale)
            allow_fractional: Auto-detect fractional capability (crypto vs stocks)

        Returns:
            Position size in shares (or fractional shares for crypto)
        """
        if self.trading_halted:
            return 0

        # Get current account value
        account_value = self.strategy.broker.getvalue()

        # Calculate risk amount (reduced if in drawdown protection)
        base_risk_pct = self.risk_params['risk_per_trade']
        if self.in_drawdown_protection:
            base_risk_pct *= 0.5  # Halve risk during drawdown

        risk_amount = account_value * base_risk_pct

        # Calculate price risk per share
        price_risk = abs(entry_price - stop_price)
        if price_risk == 0:
            return 0

        # Auto-detect if fractional shares are supported (crypto symbols contain '-USD')
        if allow_fractional is None:
            # Check if this looks like a crypto symbol
            symbol_name = getattr(self.strategy.data, '_name', '') or str(self.strategy.data)
            allow_fractional = '-USD' in symbol_name or 'USD' in symbol_name

        # Calculate ideal position value in dollars first
        ideal_position_value = min(risk_amount / (price_risk / entry_price),
                                 account_value * self.risk_params['max_position_pct'])

        if allow_fractional:
            # For crypto: use dollar-based sizing, convert to fractional shares
            position_size_float = ideal_position_value / entry_price
            if position_size_float >= 0.001:  # Minimum meaningful crypto position
                position_size = round(position_size_float, 6)  # 6 decimal places for crypto
            else:
                position_size = 0
        else:
            # For stocks: traditional whole share logic with minimum 1 share for expensive assets
            ideal_position_size = risk_amount / price_risk
            if ideal_position_size >= 0.5:  # Can afford at least half a share
                position_size = max(1, int(ideal_position_size))
            else:
                position_size = 0

        # Apply volatility adjustment if provided
        if volatility is not None:
            # Reduce size during high volatility
            volatility_factor = max(0.5, 1.0 - (volatility - 1.0))
            position_size = position_size * volatility_factor

        # Check portfolio heat constraint
        if not self._can_add_position_heat(position_size, entry_price, stop_price):
            return 0

        return max(0, position_size)

    def get_stop_loss_price(self, entry_price: float, is_long: bool,
                           method: StopLossMethod = StopLossMethod.PERCENTAGE,
                           atr_value: Optional[float] = None) -> float:
        """
        Calculate stop loss price based on method

        Args:
            entry_price: Entry price
            is_long: True for long positions, False for short
            method: Stop loss calculation method
            atr_value: ATR value for ATR-based stops

        Returns:
            Stop loss price
        """
        if method == StopLossMethod.PERCENTAGE:
            stop_pct = self.risk_params['stop_loss_pct']
            if is_long:
                return entry_price * (1 - stop_pct)
            else:
                return entry_price * (1 + stop_pct)

        elif method == StopLossMethod.ATR:
            if atr_value is None:
                # Fallback to percentage if no ATR provided
                return self.get_stop_loss_price(entry_price, is_long, StopLossMethod.PERCENTAGE)

            atr_distance = atr_value * self.risk_params['atr_multiplier']
            if is_long:
                return entry_price - atr_distance
            else:
                return entry_price + atr_distance

        else:
            # Default to percentage method
            return self.get_stop_loss_price(entry_price, is_long, StopLossMethod.PERCENTAGE)

    def should_enter_trade(self) -> bool:
        """
        Check if new trade should be entered based on risk controls

        Returns:
            True if trade can be entered, False otherwise
        """
        if self.trading_halted:
            return False

        # Check maximum positions limit
        current_positions = len([pos for pos in self.strategy.getpositions() if pos.size != 0])
        if current_positions >= self.risk_params['max_positions']:
            return False

        # Check drawdown protection
        self._update_drawdown_status()

        return True

    def update_position_risk(self, order_id: str, entry_price: float,
                           stop_price: float, size: int):
        """Update position risk tracking"""
        risk_amount = abs(entry_price - stop_price) * size
        self.positions_risk[order_id] = {
            'entry_price': entry_price,
            'stop_price': stop_price,
            'size': size,
            'risk_amount': risk_amount
        }

    def remove_position_risk(self, order_id: str):
        """Remove position from risk tracking"""
        if order_id in self.positions_risk:
            del self.positions_risk[order_id]

    def get_portfolio_heat(self) -> float:
        """
        Calculate current portfolio heat (total risk exposure)

        Returns:
            Portfolio heat as percentage of account value
        """
        total_risk = sum([pos['risk_amount'] for pos in self.positions_risk.values()])
        account_value = self.strategy.broker.getvalue()
        return total_risk / account_value if account_value > 0 else 0

    def _can_add_position_heat(self, size: int, entry_price: float, stop_price: float) -> bool:
        """Check if adding position would exceed heat limit"""
        new_risk = abs(entry_price - stop_price) * size
        current_heat = self.get_portfolio_heat()
        account_value = self.strategy.broker.getvalue()

        new_heat = (new_risk / account_value) if account_value > 0 else 1
        total_heat = current_heat + new_heat

        return total_heat <= self.risk_params['max_portfolio_heat']

    def _update_drawdown_status(self):
        """Update drawdown protection status"""
        current_value = self.strategy.broker.getvalue()
        self.peak_equity = max(self.peak_equity, current_value)

        if self.peak_equity > 0:
            drawdown = (self.peak_equity - current_value) / self.peak_equity

            # Circuit breaker - halt trading on max drawdown
            if drawdown >= self.risk_params['max_drawdown']:
                self.trading_halted = True
                return

            # Reduce risk on drawdown threshold
            if drawdown >= self.risk_params['drawdown_reduction_threshold']:
                self.in_drawdown_protection = True
            else:
                self.in_drawdown_protection = False

    def get_risk_metrics(self) -> Dict:
        """Get current risk metrics for monitoring"""
        current_value = self.strategy.broker.getvalue()
        drawdown = 0
        if self.peak_equity > 0:
            drawdown = (self.peak_equity - current_value) / self.peak_equity

        return {
            'account_value': current_value,
            'peak_equity': self.peak_equity,
            'current_drawdown': drawdown,
            'portfolio_heat': self.get_portfolio_heat(),
            'active_positions': len(self.positions_risk),
            'max_positions': self.risk_params['max_positions'],
            'in_drawdown_protection': self.in_drawdown_protection,
            'trading_halted': self.trading_halted,
            'risk_profile': self.risk_profile.value
        }

    def log_risk_status(self):
        """Log current risk status for monitoring"""
        metrics = self.get_risk_metrics()
        print(f"RISK STATUS - Value: ${metrics['account_value']:.2f}, "
              f"Heat: {metrics['portfolio_heat']*100:.1f}%, "
              f"DD: {metrics['current_drawdown']*100:.1f}%, "
              f"Positions: {metrics['active_positions']}/{metrics['max_positions']}")


class PortfolioHeatMonitor:
    """Advanced portfolio heat monitoring and management"""

    def __init__(self, max_heat: float = 0.10, warning_threshold: float = 0.08):
        self.max_heat = max_heat
        self.warning_threshold = warning_threshold
        self.position_risks = {}

    def add_position(self, position_id: str, entry_price: float,
                    stop_price: float, size: int):
        """Add position to heat monitoring"""
        risk_amount = abs(entry_price - stop_price) * size
        self.position_risks[position_id] = {
            'entry_price': entry_price,
            'stop_price': stop_price,
            'size': size,
            'risk_amount': risk_amount
        }

    def remove_position(self, position_id: str):
        """Remove position from heat monitoring"""
        if position_id in self.position_risks:
            del self.position_risks[position_id]

    def calculate_current_heat(self, account_value: float) -> float:
        """Calculate current portfolio heat percentage"""
        total_risk = sum([pos['risk_amount'] for pos in self.position_risks.values()])
        return total_risk / account_value if account_value > 0 else 0

    def can_add_position(self, new_risk_amount: float, account_value: float) -> bool:
        """Check if new position can be added without exceeding heat limit"""
        current_heat = self.calculate_current_heat(account_value)
        new_heat = new_risk_amount / account_value if account_value > 0 else 1
        return (current_heat + new_heat) <= self.max_heat

    def get_heat_status(self, account_value: float) -> str:
        """Get current heat status"""
        heat = self.calculate_current_heat(account_value)
        if heat >= self.max_heat:
            return "CRITICAL"
        elif heat >= self.warning_threshold:
            return "WARNING"
        else:
            return "NORMAL"


class DrawdownProtector:
    """Advanced drawdown protection with multiple levels"""

    def __init__(self, max_drawdown: float = 0.15,
                 reduction_threshold: float = 0.10,
                 warning_threshold: float = 0.05):
        self.max_drawdown = max_drawdown
        self.reduction_threshold = reduction_threshold
        self.warning_threshold = warning_threshold
        self.peak_value = 0
        self.consecutive_losses = 0
        self.protection_level = 0  # 0=Normal, 1=Warning, 2=Reduction, 3=Halt

    def update(self, current_value: float, last_trade_profitable: Optional[bool] = None):
        """
        Update drawdown status

        Args:
            current_value: Current account value
            last_trade_profitable: Whether last trade was profitable

        Returns:
            Protection status: NORMAL, WARNING, REDUCE_RISK, STOP_TRADING
        """
        # Update peak value
        if current_value > self.peak_value:
            self.peak_value = current_value
            self.consecutive_losses = 0  # Reset loss counter on new peak

        # Track consecutive losses
        if last_trade_profitable is not None:
            if last_trade_profitable:
                self.consecutive_losses = 0
            else:
                self.consecutive_losses += 1

        # Calculate drawdown
        drawdown = 0
        if self.peak_value > 0:
            drawdown = (self.peak_value - current_value) / self.peak_value

        # Determine protection level
        if drawdown >= self.max_drawdown or self.consecutive_losses >= 5:
            self.protection_level = 3
            return "STOP_TRADING"
        elif drawdown >= self.reduction_threshold or self.consecutive_losses >= 3:
            self.protection_level = 2
            return "REDUCE_RISK"
        elif drawdown >= self.warning_threshold:
            self.protection_level = 1
            return "WARNING"
        else:
            self.protection_level = 0
            return "NORMAL"

    def get_risk_multiplier(self) -> float:
        """Get risk multiplier based on protection level"""
        multipliers = {0: 1.0, 1: 0.8, 2: 0.5, 3: 0.0}
        return multipliers.get(self.protection_level, 1.0)

    def should_trade(self) -> bool:
        """Check if trading should continue"""
        return self.protection_level < 3

    def get_status_info(self) -> Dict:
        """Get detailed status information"""
        current_value = self.peak_value  # This should be passed in
        drawdown = (self.peak_value - current_value) / self.peak_value if self.peak_value > 0 else 0

        return {
            'peak_value': self.peak_value,
            'current_drawdown': drawdown,
            'consecutive_losses': self.consecutive_losses,
            'protection_level': self.protection_level,
            'risk_multiplier': self.get_risk_multiplier(),
            'should_trade': self.should_trade()
        }
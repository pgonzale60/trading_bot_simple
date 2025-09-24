#!/usr/bin/env python3
"""
Risk Management Configuration System

Centralized configuration for risk management parameters across all strategies.
Provides pre-defined risk profiles and strategy-specific adjustments.
"""

from enum import Enum
from typing import Dict, Any
from risk_management import RiskLevel, StopLossMethod


class StrategyType(Enum):
    """Strategy types with different risk characteristics"""
    TREND_FOLLOWING = "trend_following"  # SMA, EMA, MACD
    MEAN_REVERSION = "mean_reversion"    # RSI, Bollinger Bands
    MOMENTUM = "momentum"                # Momentum strategy
    BUY_HOLD = "buy_hold"               # Buy and hold


class RiskConfig:
    """Centralized risk configuration management"""

    # Base risk profiles (from risk_management.py)
    BASE_RISK_PROFILES = {
        RiskLevel.CONSERVATIVE: {
            'risk_per_trade': 0.015,
            'max_position_pct': 0.12,
            'max_portfolio_heat': 0.08,
            'max_drawdown': 0.12,
            'max_positions': 2,
            'stop_loss_pct': 0.03,
            'atr_multiplier': 1.5,
            'drawdown_reduction_threshold': 0.08,
        },
        RiskLevel.MODERATE: {
            'risk_per_trade': 0.02,
            'max_position_pct': 0.15,
            'max_portfolio_heat': 0.10,
            'max_drawdown': 0.15,
            'max_positions': 3,
            'stop_loss_pct': 0.04,
            'atr_multiplier': 2.0,
            'drawdown_reduction_threshold': 0.10,
        },
        RiskLevel.AGGRESSIVE: {
            'risk_per_trade': 0.025,
            'max_position_pct': 0.20,
            'max_portfolio_heat': 0.12,
            'max_drawdown': 0.18,
            'max_positions': 4,
            'stop_loss_pct': 0.05,
            'atr_multiplier': 2.5,
            'drawdown_reduction_threshold': 0.12,
        }
    }

    # Strategy-specific risk adjustments
    STRATEGY_RISK_ADJUSTMENTS = {
        StrategyType.TREND_FOLLOWING: {
            'description': 'Trend following strategies (SMA, EMA, MACD)',
            'adjustments': {
                RiskLevel.CONSERVATIVE: {
                    'stop_loss_method': StopLossMethod.ATR,
                    'atr_multiplier': 1.5,
                    'risk_per_trade': 0.015,
                },
                RiskLevel.MODERATE: {
                    'stop_loss_method': StopLossMethod.ATR,
                    'atr_multiplier': 2.0,
                    'risk_per_trade': 0.018,
                },
                RiskLevel.AGGRESSIVE: {
                    'stop_loss_method': StopLossMethod.ATR,
                    'atr_multiplier': 2.5,
                    'risk_per_trade': 0.022,
                }
            }
        },

        StrategyType.MEAN_REVERSION: {
            'description': 'Mean reversion strategies (RSI, Bollinger Bands)',
            'adjustments': {
                RiskLevel.CONSERVATIVE: {
                    'stop_loss_method': StopLossMethod.PERCENTAGE,
                    'stop_loss_pct': 0.025,  # Tighter stops for mean reversion
                    'risk_per_trade': 0.012,  # Lower risk due to tighter stops
                },
                RiskLevel.MODERATE: {
                    'stop_loss_method': StopLossMethod.PERCENTAGE,
                    'stop_loss_pct': 0.03,
                    'risk_per_trade': 0.015,
                },
                RiskLevel.AGGRESSIVE: {
                    'stop_loss_method': StopLossMethod.PERCENTAGE,
                    'stop_loss_pct': 0.04,
                    'risk_per_trade': 0.02,
                }
            }
        },

        StrategyType.MOMENTUM: {
            'description': 'Momentum-based strategies',
            'adjustments': {
                RiskLevel.CONSERVATIVE: {
                    'stop_loss_method': StopLossMethod.PERCENTAGE,
                    'stop_loss_pct': 0.04,
                    'risk_per_trade': 0.018,  # Higher risk for momentum
                    'max_positions': 2,
                },
                RiskLevel.MODERATE: {
                    'stop_loss_method': StopLossMethod.PERCENTAGE,
                    'stop_loss_pct': 0.05,
                    'risk_per_trade': 0.022,
                    'max_positions': 3,
                },
                RiskLevel.AGGRESSIVE: {
                    'stop_loss_method': StopLossMethod.PERCENTAGE,
                    'stop_loss_pct': 0.06,
                    'risk_per_trade': 0.028,
                    'max_positions': 4,
                }
            }
        },

        StrategyType.BUY_HOLD: {
            'description': 'Buy and hold strategy',
            'adjustments': {
                RiskLevel.CONSERVATIVE: {
                    'stop_loss_method': StopLossMethod.PERCENTAGE,
                    'stop_loss_pct': 0.15,  # Wide stops for buy & hold
                    'risk_per_trade': 0.05,  # Can risk more with wide stops
                    'max_positions': 1,
                    'max_position_pct': 0.95,  # Nearly full position
                },
                RiskLevel.MODERATE: {
                    'stop_loss_method': StopLossMethod.PERCENTAGE,
                    'stop_loss_pct': 0.20,
                    'risk_per_trade': 0.08,
                    'max_positions': 1,
                    'max_position_pct': 0.95,
                },
                RiskLevel.AGGRESSIVE: {
                    'stop_loss_method': StopLossMethod.PERCENTAGE,
                    'stop_loss_pct': 0.25,
                    'risk_per_trade': 0.10,
                    'max_positions': 1,
                    'max_position_pct': 0.95,
                }
            }
        }
    }

    @classmethod
    def get_strategy_config(cls, strategy_type: StrategyType,
                          risk_level: RiskLevel) -> Dict[str, Any]:
        """
        Get complete risk configuration for a specific strategy and risk level

        Args:
            strategy_type: Type of strategy
            risk_level: Risk level (CONSERVATIVE, MODERATE, AGGRESSIVE)

        Returns:
            Complete risk configuration dictionary
        """
        # Start with base profile
        config = cls.BASE_RISK_PROFILES[risk_level].copy()

        # Apply strategy-specific adjustments
        if strategy_type in cls.STRATEGY_RISK_ADJUSTMENTS:
            adjustments = cls.STRATEGY_RISK_ADJUSTMENTS[strategy_type]['adjustments']
            if risk_level in adjustments:
                config.update(adjustments[risk_level])

        # Add metadata
        config['strategy_type'] = strategy_type.value
        config['risk_level'] = risk_level.value

        return config

    @classmethod
    def get_all_configurations(cls) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get all possible risk configurations"""
        all_configs = {}

        for strategy_type in StrategyType:
            all_configs[strategy_type.value] = {}
            for risk_level in RiskLevel:
                all_configs[strategy_type.value][risk_level.value] = \
                    cls.get_strategy_config(strategy_type, risk_level)

        return all_configs

    @classmethod
    def print_configuration(cls, strategy_type: StrategyType, risk_level: RiskLevel):
        """Print a human-readable configuration"""
        config = cls.get_strategy_config(strategy_type, risk_level)

        print(f"\n{'='*60}")
        print(f"RISK CONFIGURATION")
        print(f"{'='*60}")
        print(f"Strategy Type: {strategy_type.value.replace('_', ' ').title()}")
        print(f"Risk Level: {risk_level.value.upper()}")
        print(f"{'='*60}")

        print(f"Risk per Trade: {config['risk_per_trade']*100:.1f}%")
        print(f"Max Position Size: {config['max_position_pct']*100:.1f}% of portfolio")
        print(f"Max Portfolio Heat: {config['max_portfolio_heat']*100:.1f}%")
        print(f"Max Drawdown: {config['max_drawdown']*100:.1f}%")
        print(f"Max Positions: {config['max_positions']}")
        print(f"Stop Loss: {config['stop_loss_pct']*100:.1f}%")

        if 'stop_loss_method' in config:
            print(f"Stop Loss Method: {config['stop_loss_method'].value}")

        if 'atr_multiplier' in config:
            print(f"ATR Multiplier: {config['atr_multiplier']}")

        print(f"Drawdown Reduction Threshold: {config['drawdown_reduction_threshold']*100:.1f}%")
        print(f"{'='*60}")

    @classmethod
    def create_custom_config(cls, base_risk_level: RiskLevel, **overrides) -> Dict[str, Any]:
        """
        Create a custom risk configuration based on a base level

        Args:
            base_risk_level: Base risk level to start from
            **overrides: Parameters to override

        Returns:
            Custom risk configuration
        """
        config = cls.BASE_RISK_PROFILES[base_risk_level].copy()
        config.update(overrides)
        config['custom'] = True
        return config


# Predefined configurations for easy access
CONSERVATIVE_TREND = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, RiskLevel.CONSERVATIVE)
MODERATE_TREND = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, RiskLevel.MODERATE)
AGGRESSIVE_TREND = RiskConfig.get_strategy_config(StrategyType.TREND_FOLLOWING, RiskLevel.AGGRESSIVE)

CONSERVATIVE_MEAN_REVERSION = RiskConfig.get_strategy_config(StrategyType.MEAN_REVERSION, RiskLevel.CONSERVATIVE)
MODERATE_MEAN_REVERSION = RiskConfig.get_strategy_config(StrategyType.MEAN_REVERSION, RiskLevel.MODERATE)
AGGRESSIVE_MEAN_REVERSION = RiskConfig.get_strategy_config(StrategyType.MEAN_REVERSION, RiskLevel.AGGRESSIVE)

CONSERVATIVE_MOMENTUM = RiskConfig.get_strategy_config(StrategyType.MOMENTUM, RiskLevel.CONSERVATIVE)
MODERATE_MOMENTUM = RiskConfig.get_strategy_config(StrategyType.MOMENTUM, RiskLevel.MODERATE)
AGGRESSIVE_MOMENTUM = RiskConfig.get_strategy_config(StrategyType.MOMENTUM, RiskLevel.AGGRESSIVE)

CONSERVATIVE_BUY_HOLD = RiskConfig.get_strategy_config(StrategyType.BUY_HOLD, RiskLevel.CONSERVATIVE)
MODERATE_BUY_HOLD = RiskConfig.get_strategy_config(StrategyType.BUY_HOLD, RiskLevel.MODERATE)
AGGRESSIVE_BUY_HOLD = RiskConfig.get_strategy_config(StrategyType.BUY_HOLD, RiskLevel.AGGRESSIVE)


if __name__ == "__main__":
    # Demo of configuration system
    print("RISK MANAGEMENT CONFIGURATION SYSTEM")
    print("="*50)

    # Show all strategy types and their configurations
    for strategy_type in StrategyType:
        for risk_level in RiskLevel:
            RiskConfig.print_configuration(strategy_type, risk_level)
            print()

    # Show custom configuration example
    print("\nCUSTOM CONFIGURATION EXAMPLE:")
    custom = RiskConfig.create_custom_config(
        RiskLevel.MODERATE,
        risk_per_trade=0.015,  # Lower risk
        max_positions=2,       # Fewer positions
        stop_loss_pct=0.03     # Tighter stops
    )
    print(custom)
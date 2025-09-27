#!/usr/bin/env python3
"""
Trading Strategy Optimizer - Systematic Parameter Testing

This module allows you to test different strategies and parameters
to find what actually works vs what doesn't.
"""

import backtrader as bt
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from itertools import product
from data import get_stock_data
from strategies import STRATEGIES, get_strategy_params
from multi_asset_tester import MultiAssetTester
import warnings
warnings.filterwarnings('ignore')


class ParameterOptimizer:
    """Systematically test different parameters for trading strategies."""

    def __init__(self, symbol='AAPL', start_date='2020-01-01', cash=10000):
        self.symbol = symbol
        self.start_date = start_date
        self.cash = cash
        self.results = []
        self.data = None

    def load_data(self):
        """Load stock data for backtesting."""
        print(f"Loading data for {self.symbol} from {self.start_date}...")
        try:
            self.data = get_stock_data(self.symbol, self.start_date)
            print("✓ Data loaded successfully")
        except Exception as e:
            print(f"✗ Data loading failed: {e}")
            return False
        return True

    def test_strategy_parameters(self, strategy_name, custom_params=None):
        """Test different parameters for a specific strategy."""
        if strategy_name not in STRATEGIES:
            print(f"Unknown strategy: {strategy_name}")
            print(f"Available strategies: {list(STRATEGIES.keys())}")
            return []

        strategy_class = STRATEGIES[strategy_name]
        param_ranges = custom_params if custom_params else get_strategy_params(strategy_name)

        if not param_ranges:
            # Test strategy with default parameters if no ranges available
            print(f"\nTesting {strategy_name.upper()} with default parameters...")
            try:
                result = self._run_backtest(strategy_class)
                result['strategy'] = strategy_name.upper()
                result['params'] = f"{strategy_name.upper()}(default)"
                return [result]
            except Exception as e:
                print(f" → ERROR: {e}")
                return []

        print(f"\nTesting {strategy_name.upper()} combinations...")
        print(f"Parameter ranges: {param_ranges}")

        results = []
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())

        # Generate all parameter combinations
        combinations = list(product(*param_values))
        total_tests = len(combinations)

        for i, combination in enumerate(combinations, 1):
            params_dict = dict(zip(param_names, combination))

            # Skip invalid combinations for crossover strategies
            if strategy_name in ['sma', 'ema'] and 'short_period' in params_dict and 'long_period' in params_dict:
                if params_dict['short_period'] >= params_dict['long_period']:
                    continue

            print(f"Testing {i}/{total_tests}: {strategy_name.upper()}({params_dict})", end="")

            try:
                result = self._run_backtest(strategy_class, **params_dict)
                result['strategy'] = strategy_name.upper()
                result.update(params_dict)
                result['params'] = f"{strategy_name.upper()}({params_dict})"
                results.append(result)
                print(f" → Return: {result['return_pct']:.2f}%")
            except Exception as e:
                print(f" → ERROR: {e}")

        return results

    def test_sma_parameters(self, short_periods=None, long_periods=None):
        """Backward-compatible SMA optimization wrapper for legacy tests."""
        if short_periods is None:
            short_periods = [5, 10, 15, 20]
        if long_periods is None:
            long_periods = [20, 30, 50, 100]

        param_ranges = {
            'short_period': short_periods,
            'long_period': long_periods
        }

        return self.test_strategy_parameters('sma', custom_params=param_ranges)

    def _run_backtest(self, strategy_class, **kwargs):
        """Run a single backtest with given parameters."""
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class, **kwargs)
        cerebro.adddata(self.data)
        cerebro.broker.setcash(self.cash)
        cerebro.broker.setcommission(commission=0.001)  # 0.1% commission

        # Add analyzers for detailed metrics
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

        results = cerebro.run()
        final_value = cerebro.broker.getvalue()

        # Extract metrics
        strategy_result = results[0]
        trades = strategy_result.analyzers.trades.get_analysis()
        sharpe = strategy_result.analyzers.sharpe.get_analysis()
        drawdown = strategy_result.analyzers.drawdown.get_analysis()

        return {
            'initial_value': self.cash,
            'final_value': final_value,
            'profit': final_value - self.cash,
            'return_pct': ((final_value - self.cash) / self.cash) * 100,
            'total_trades': trades.get('total', {}).get('closed', 0) if isinstance(trades, dict) else (trades.total.closed if hasattr(trades, 'total') and hasattr(trades.total, 'closed') else 0),
            'winning_trades': trades.get('won', {}).get('total', 0) if isinstance(trades, dict) else (trades.won.total if hasattr(trades, 'won') and hasattr(trades.won, 'total') else 0),
            'losing_trades': trades.get('lost', {}).get('total', 0) if isinstance(trades, dict) else (trades.lost.total if hasattr(trades, 'lost') and hasattr(trades.lost, 'total') else 0),
            'win_rate': (trades.get('won', {}).get('total', 0) / trades.get('total', {}).get('closed', 1) * 100) if trades.get('total', {}).get('closed', 0) > 0 else 0,
            'sharpe_ratio': sharpe.get('sharperatio', 0) or 0,
            'max_drawdown': drawdown.get('max', {}).get('drawdown', 0) if isinstance(drawdown, dict) else (drawdown.max.drawdown if hasattr(drawdown, 'max') and hasattr(drawdown.max, 'drawdown') else 0),
            'avg_trade': trades.get('won', {}).get('pnl', {}).get('average', 0) if isinstance(trades, dict) else (trades.won.pnl.average if hasattr(trades, 'won') and hasattr(trades.won, 'pnl') and hasattr(trades.won.pnl, 'average') else 0)
        }

    def analyze_results(self, results):
        """Analyze and rank the results."""
        if not results:
            print("No results to analyze!")
            return None

        df = pd.DataFrame(results)

        # Sort by return percentage (descending)
        df_sorted = df.sort_values('return_pct', ascending=False)

        print(f"\n{'='*80}")
        print(f"{'OPTIMIZATION RESULTS':^80}")
        print(f"{'='*80}")
        print(f"Symbol: {self.symbol} | Period: {self.start_date} to present")
        print(f"Total combinations tested: {len(df)}")
        print(f"{'='*80}")

        # Top 10 performers
        print(f"\n🏆 TOP 10 BEST PERFORMING STRATEGIES:")
        print(f"{'Rank':<4} {'Strategy':<15} {'Return%':<8} {'Trades':<7} {'Win%':<6} {'Sharpe':<7} {'Max DD%':<8}")
        print("-" * 70)

        for i, (_, row) in enumerate(df_sorted.head(10).iterrows(), 1):
            print(f"{i:<4} {row['params']:<15} {row['return_pct']:>7.1f}% "
                  f"{row['total_trades']:>6.0f} {row['win_rate']:>5.1f}% "
                  f"{row['sharpe_ratio']:>6.2f} {row['max_drawdown']:>7.1f}%")

        # Bottom 5 performers
        print(f"\n💀 WORST 5 PERFORMING STRATEGIES:")
        for i, (_, row) in enumerate(df_sorted.tail(5).iterrows(), 1):
            print(f"{i:<4} {row['params']:<15} {row['return_pct']:>7.1f}% "
                  f"{row['total_trades']:>6.0f} {row['win_rate']:>5.1f}% "
                  f"{row['sharpe_ratio']:>6.2f} {row['max_drawdown']:>7.1f}%")

        # Statistics
        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"Average Return: {df['return_pct'].mean():.2f}%")
        print(f"Best Return: {df['return_pct'].max():.2f}%")
        print(f"Worst Return: {df['return_pct'].min():.2f}%")
        print(f"Profitable strategies: {len(df[df['return_pct'] > 0])}/{len(df)} ({len(df[df['return_pct'] > 0])/len(df)*100:.1f}%)")

        return df_sorted

    def test_all_strategies(self):
        """Test all available strategies with their parameter ranges."""
        if not self.load_data():
            return

        all_results = []

        print(f"\n🔬 Testing all strategies on {self.symbol}")
        print(f"Available strategies: {list(STRATEGIES.keys())}")
        print("=" * 60)

        for strategy_name in STRATEGIES.keys():
            print(f"\n📊 Testing {strategy_name.upper()} strategy...")
            strategy_results = self.test_strategy_parameters(strategy_name)
            all_results.extend(strategy_results)

        # Analyze all results
        best_results = self.analyze_results(all_results)

        # Save results to CSV
        if best_results is not None:
            filename = f"optimization_all_strategies_{self.symbol}_{self.start_date.replace('-', '')}.csv"
            best_results.to_csv(filename, index=False)
            print(f"\n💾 Results saved to: {filename}")

        return best_results

    def test_single_strategy(self, strategy_name, custom_params=None):
        """Test a single strategy with parameter optimization."""
        if not self.load_data():
            return

        print(f"\n🎯 Optimizing {strategy_name.upper()} strategy on {self.symbol}")
        print("=" * 60)

        # Test strategy parameters
        strategy_results = self.test_strategy_parameters(strategy_name, custom_params)

        # Analyze results
        best_results = self.analyze_results(strategy_results)

        # Save results to CSV
        if best_results is not None:
            filename = f"optimization_{strategy_name}_{self.symbol}_{self.start_date.replace('-', '')}.csv"
            best_results.to_csv(filename, index=False)
            print(f"\n💾 Results saved to: {filename}")

        return best_results

    def quick_test(self, strategy_name=None):
        """Run a quick test with common parameter ranges."""
        if strategy_name:
            return self.test_single_strategy(strategy_name)
        else:
            # Test a subset of strategies for quick results
            if not self.load_data():
                return

            quick_strategies = ['sma', 'rsi', 'buy_hold']  # Most reliable strategies
            all_results = []

            print(f"\n⚡ Quick optimization test on {self.symbol}")
            print(f"Testing strategies: {quick_strategies}")
            print("=" * 60)

            for strategy_name in quick_strategies:
                if strategy_name in STRATEGIES:
                    print(f"\n📊 Testing {strategy_name.upper()} strategy...")
                    if strategy_name == 'sma':
                        strategy_results = self.test_sma_parameters()
                    else:
                        strategy_results = self.test_strategy_parameters(strategy_name)
                    all_results.extend(strategy_results)

            # Analyze all results
            best_results = self.analyze_results(all_results)

            # Save results to CSV
            if best_results is not None:
                filename = f"optimization_quick_{self.symbol}_{self.start_date.replace('-', '')}.csv"
                best_results.to_csv(filename, index=False)
                print(f"\n💾 Results saved to: {filename}")

            return best_results

    def optimize_all_symbols(self, symbols_type='all'):
        """
        Comprehensive optimization across all symbols and strategies.

        Args:
            symbols_type: 'all', 'stocks', 'crypto' - which symbols to include

        Returns:
            dict: Comprehensive results with symbol-strategy performance matrix
        """
        # Get symbol lists from MultiAssetTester
        mat = MultiAssetTester(start_date=self.start_date, cash=self.cash)

        if symbols_type == 'stocks':
            symbols = mat.stock_symbols
        elif symbols_type == 'crypto':
            symbols = mat.crypto_symbols
        else:
            symbols = mat.all_symbols

        print(f"\n🌐 COMPREHENSIVE MULTI-SYMBOL OPTIMIZATION")
        print(f"Testing {len(STRATEGIES)} strategies across {len(symbols)} symbols")
        print(f"Total tests: {len(STRATEGIES) * len(symbols)} combinations")
        print(f"Symbols type: {symbols_type.upper()}")
        print("=" * 80)

        # Initialize comprehensive results structure
        comprehensive_results = {
            "optimization_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_symbols": len(symbols),
                "total_strategies": len(STRATEGIES),
                "symbols_type": symbols_type,
                "start_date": self.start_date,
                "cash": self.cash,
                "total_combinations": 0
            },
            "results_by_symbol": {},
            "results_by_strategy": {},
            "overall_insights": {}
        }

        # Track overall progress
        total_tests = 0
        completed_tests = 0
        failed_symbols = []

        # Process each symbol
        for i, symbol in enumerate(symbols, 1):
            print(f"\n📊 Processing Symbol {i}/{len(symbols)}: {symbol}")
            print("-" * 50)

            symbol_results = {
                "symbol": symbol,
                "symbol_type": "stock" if symbol in mat.stock_symbols else "crypto",
                "strategy_results": {},
                "best_strategy": None,
                "data_loaded": False,
                "total_combinations": 0
            }

            try:
                # Load data for this symbol
                temp_optimizer = ParameterOptimizer(symbol, self.start_date, self.cash)
                if not temp_optimizer.load_data():
                    print(f"❌ Failed to load data for {symbol}")
                    failed_symbols.append(symbol)
                    continue

                symbol_results["data_loaded"] = True

                # Test each strategy for this symbol
                best_return = float('-inf')
                best_strategy_info = None

                for strategy_name in STRATEGIES.keys():
                    print(f"  🔍 Testing {strategy_name.upper()} on {symbol}...", end=" ")

                    try:
                        # Get parameter optimization results for this strategy
                        strategy_results = temp_optimizer.test_strategy_parameters(strategy_name)

                        if strategy_results:
                            # Find best result for this strategy
                            best_result = max(strategy_results, key=lambda x: x['return_pct'])
                            print(f"✓ Best: {best_result['return_pct']:.1f}%")

                            symbol_results["strategy_results"][strategy_name] = {
                                "all_results": strategy_results,
                                "best_result": best_result,
                                "total_tests": len(strategy_results)
                            }

                            # Track overall best for this symbol
                            if best_result['return_pct'] > best_return:
                                best_return = best_result['return_pct']
                                best_strategy_info = {
                                    "strategy": strategy_name,
                                    "params": best_result.get('params', 'default'),
                                    "return_pct": best_result['return_pct'],
                                    "sharpe_ratio": best_result.get('sharpe_ratio', 0),
                                    "max_drawdown": best_result.get('max_drawdown', 0),
                                    "total_trades": best_result.get('total_trades', 0)
                                }

                            total_tests += len(strategy_results)
                            symbol_results["total_combinations"] += len(strategy_results)
                        else:
                            print("❌ No results")
                            symbol_results["strategy_results"][strategy_name] = {
                                "all_results": [],
                                "best_result": None,
                                "total_tests": 0
                            }

                    except Exception as e:
                        print(f"❌ Error: {str(e)[:50]}...")
                        symbol_results["strategy_results"][strategy_name] = {
                            "all_results": [],
                            "best_result": None,
                            "total_tests": 0,
                            "error": str(e)
                        }

                # Set best strategy for this symbol
                symbol_results["best_strategy"] = best_strategy_info
                comprehensive_results["results_by_symbol"][symbol] = symbol_results
                completed_tests += 1

            except Exception as e:
                print(f"❌ Failed to process {symbol}: {e}")
                failed_symbols.append(symbol)
                symbol_results["error"] = str(e)
                comprehensive_results["results_by_symbol"][symbol] = symbol_results

        # Update metadata
        comprehensive_results["optimization_metadata"]["total_combinations"] = total_tests
        comprehensive_results["optimization_metadata"]["completed_symbols"] = completed_tests
        comprehensive_results["optimization_metadata"]["failed_symbols"] = failed_symbols

        # Generate strategy-centric analysis
        print(f"\n📈 GENERATING STRATEGY ANALYSIS...")
        comprehensive_results["results_by_strategy"] = self._analyze_by_strategy(comprehensive_results)

        # Generate overall insights
        print(f"🎯 GENERATING OVERALL INSIGHTS...")
        comprehensive_results["overall_insights"] = self._generate_overall_insights(comprehensive_results)

        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"multi_symbol_optimization_{symbols_type}_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(comprehensive_results, f, indent=2)

        print(f"\n💾 COMPREHENSIVE RESULTS SAVED TO: {filename}")

        # Display summary
        self._display_multi_symbol_summary(comprehensive_results)

        return comprehensive_results

    def _analyze_by_strategy(self, comprehensive_results):
        """Analyze results from strategy perspective."""
        strategy_analysis = {}

        for strategy_name in STRATEGIES.keys():
            strategy_analysis[strategy_name] = {
                "symbol_performance": {},
                "overall_stats": {
                    "total_symbols_tested": 0,
                    "successful_symbols": 0,
                    "avg_return": 0,
                    "best_symbol": None,
                    "worst_symbol": None,
                    "best_return": float('-inf'),
                    "worst_return": float('inf'),
                    "returns": []
                }
            }

            returns = []
            best_symbol = None
            worst_symbol = None
            best_return = float('-inf')
            worst_return = float('inf')

            # Collect data for this strategy across all symbols
            for symbol, symbol_data in comprehensive_results["results_by_symbol"].items():
                if strategy_name in symbol_data["strategy_results"]:
                    strategy_results = symbol_data["strategy_results"][strategy_name]
                    best_result = strategy_results.get("best_result")

                    strategy_analysis[strategy_name]["symbol_performance"][symbol] = {
                        "best_result": best_result,
                        "total_tests": strategy_results.get("total_tests", 0),
                        "symbol_type": symbol_data["symbol_type"]
                    }

                    if best_result:
                        return_pct = best_result["return_pct"]
                        returns.append(return_pct)

                        if return_pct > best_return:
                            best_return = return_pct
                            best_symbol = symbol

                        if return_pct < worst_return:
                            worst_return = return_pct
                            worst_symbol = symbol

            # Calculate overall stats
            stats = strategy_analysis[strategy_name]["overall_stats"]
            stats["total_symbols_tested"] = len(strategy_analysis[strategy_name]["symbol_performance"])
            stats["successful_symbols"] = len([r for r in returns if r is not None])
            stats["avg_return"] = np.mean(returns) if returns else 0
            stats["best_symbol"] = best_symbol
            stats["worst_symbol"] = worst_symbol
            stats["best_return"] = best_return if best_return != float('-inf') else 0
            stats["worst_return"] = worst_return if worst_return != float('inf') else 0
            stats["returns"] = returns
            stats["median_return"] = np.median(returns) if returns else 0
            stats["std_return"] = np.std(returns) if returns else 0

        return strategy_analysis

    def _generate_overall_insights(self, comprehensive_results):
        """Generate high-level insights across all symbols and strategies."""
        insights = {
            "best_strategy_overall": None,
            "best_symbol_overall": None,
            "strategy_rankings": [],
            "symbol_rankings": [],
            "buy_hold_analysis": {},
            "symbol_type_analysis": {
                "stocks": {"avg_return": 0, "best_symbol": None, "count": 0},
                "crypto": {"avg_return": 0, "best_symbol": None, "count": 0}
            }
        }

        # Strategy rankings by average performance
        strategy_performance = []
        for strategy, data in comprehensive_results["results_by_strategy"].items():
            avg_return = data["overall_stats"]["avg_return"]
            successful_symbols = data["overall_stats"]["successful_symbols"]
            strategy_performance.append({
                "strategy": strategy,
                "avg_return": avg_return,
                "successful_symbols": successful_symbols,
                "best_symbol": data["overall_stats"]["best_symbol"],
                "best_return": data["overall_stats"]["best_return"]
            })

        insights["strategy_rankings"] = sorted(strategy_performance, key=lambda x: x["avg_return"], reverse=True)
        insights["best_strategy_overall"] = insights["strategy_rankings"][0]["strategy"] if insights["strategy_rankings"] else None

        # Symbol rankings by best strategy performance
        symbol_performance = []
        stock_returns = []
        crypto_returns = []

        for symbol, data in comprehensive_results["results_by_symbol"].items():
            best_strategy = data.get("best_strategy")
            if best_strategy:
                symbol_performance.append({
                    "symbol": symbol,
                    "symbol_type": data["symbol_type"],
                    "best_strategy": best_strategy["strategy"],
                    "best_return": best_strategy["return_pct"],
                    "best_params": best_strategy["params"]
                })

                # Track by symbol type
                if data["symbol_type"] == "stock":
                    stock_returns.append(best_strategy["return_pct"])
                else:
                    crypto_returns.append(best_strategy["return_pct"])

        insights["symbol_rankings"] = sorted(symbol_performance, key=lambda x: x["best_return"], reverse=True)
        insights["best_symbol_overall"] = insights["symbol_rankings"][0]["symbol"] if insights["symbol_rankings"] else None

        # Symbol type analysis
        if stock_returns:
            insights["symbol_type_analysis"]["stocks"]["avg_return"] = np.mean(stock_returns)
            insights["symbol_type_analysis"]["stocks"]["count"] = len(stock_returns)
            best_stock = max(symbol_performance, key=lambda x: x["best_return"] if x["symbol_type"] == "stock" else -float('inf'))
            insights["symbol_type_analysis"]["stocks"]["best_symbol"] = best_stock["symbol"]

        if crypto_returns:
            insights["symbol_type_analysis"]["crypto"]["avg_return"] = np.mean(crypto_returns)
            insights["symbol_type_analysis"]["crypto"]["count"] = len(crypto_returns)
            best_crypto = max(symbol_performance, key=lambda x: x["best_return"] if x["symbol_type"] == "crypto" else -float('inf'))
            insights["symbol_type_analysis"]["crypto"]["best_symbol"] = best_crypto["symbol"]

        # Buy & Hold baseline analysis
        buy_hold_results = comprehensive_results["results_by_strategy"].get("buy_hold", {})
        if buy_hold_results:
            insights["buy_hold_analysis"] = {
                "avg_return": buy_hold_results["overall_stats"]["avg_return"],
                "best_symbol": buy_hold_results["overall_stats"]["best_symbol"],
                "best_return": buy_hold_results["overall_stats"]["best_return"],
                "strategies_beating_buy_hold": []
            }

            # Find strategies that beat buy & hold on average
            buy_hold_avg = buy_hold_results["overall_stats"]["avg_return"]
            for strategy_data in insights["strategy_rankings"]:
                if strategy_data["strategy"] != "buy_hold" and strategy_data["avg_return"] > buy_hold_avg:
                    insights["buy_hold_analysis"]["strategies_beating_buy_hold"].append({
                        "strategy": strategy_data["strategy"],
                        "avg_return": strategy_data["avg_return"],
                        "outperformance": strategy_data["avg_return"] - buy_hold_avg
                    })

        return insights

    def _display_multi_symbol_summary(self, comprehensive_results):
        """Display a comprehensive summary of multi-symbol optimization results."""
        print(f"\n{'='*80}")
        print(f"{'MULTI-SYMBOL OPTIMIZATION SUMMARY':^80}")
        print(f"{'='*80}")

        metadata = comprehensive_results["optimization_metadata"]
        insights = comprehensive_results["overall_insights"]

        print(f"📊 SCOPE: {metadata['total_strategies']} strategies × {metadata['total_symbols']} symbols = {metadata['total_combinations']} total tests")
        print(f"⏱️  COMPLETED: {metadata['completed_symbols']}/{metadata['total_symbols']} symbols")
        if metadata.get('failed_symbols'):
            print(f"❌ FAILED: {len(metadata['failed_symbols'])} symbols: {', '.join(metadata['failed_symbols'][:5])}")

        print(f"\n🏆 TOP 5 STRATEGIES (by avg return):")
        print(f"{'Rank':<4} {'Strategy':<12} {'Avg Return':<12} {'Best Symbol':<12} {'Best Return':<12}")
        print("-" * 60)
        for i, strategy in enumerate(insights["strategy_rankings"][:5], 1):
            print(f"{i:<4} {strategy['strategy'].upper():<12} {strategy['avg_return']:>10.1f}% {strategy['best_symbol']:<12} {strategy['best_return']:>10.1f}%")

        print(f"\n🎯 TOP 5 SYMBOLS (by best strategy return):")
        print(f"{'Rank':<4} {'Symbol':<10} {'Type':<6} {'Best Strategy':<12} {'Return':<10}")
        print("-" * 50)
        for i, symbol in enumerate(insights["symbol_rankings"][:5], 1):
            print(f"{i:<4} {symbol['symbol']:<10} {symbol['symbol_type']:<6} {symbol['best_strategy'].upper():<12} {symbol['best_return']:>8.1f}%")

        # Buy & Hold Analysis
        if insights.get("buy_hold_analysis"):
            bh_analysis = insights["buy_hold_analysis"]
            print(f"\n📈 BUY & HOLD BASELINE:")
            print(f"   Average Return: {bh_analysis['avg_return']:.1f}%")
            print(f"   Best Symbol: {bh_analysis['best_symbol']} ({bh_analysis['best_return']:.1f}%)")

            if bh_analysis["strategies_beating_buy_hold"]:
                print(f"   Strategies beating Buy & Hold: {len(bh_analysis['strategies_beating_buy_hold'])}")
                for strat in bh_analysis["strategies_beating_buy_hold"][:3]:
                    print(f"     • {strat['strategy'].upper()}: +{strat['outperformance']:.1f}% outperformance")
            else:
                print(f"   ⚠️  NO strategies beat Buy & Hold on average!")

        # Symbol Type Analysis
        type_analysis = insights["symbol_type_analysis"]
        print(f"\n📋 BY ASSET TYPE:")
        if type_analysis["stocks"]["count"] > 0:
            print(f"   Stocks ({type_analysis['stocks']['count']}): Avg {type_analysis['stocks']['avg_return']:.1f}% | Best: {type_analysis['stocks']['best_symbol']}")
        if type_analysis["crypto"]["count"] > 0:
            print(f"   Crypto ({type_analysis['crypto']['count']}): Avg {type_analysis['crypto']['avg_return']:.1f}% | Best: {type_analysis['crypto']['best_symbol']}")


def main():
    """Run optimization example."""
    import argparse

    parser = argparse.ArgumentParser(description='Trading Strategy Optimizer')
    parser.add_argument('--symbol', default='AAPL', help='Stock symbol')
    parser.add_argument('--start', default='2020-01-01', help='Start date YYYY-MM-DD')
    parser.add_argument('--cash', type=float, default=10000, help='Starting cash')
    parser.add_argument('--strategy', default=None, help='Single strategy to optimize (default: test all)')
    parser.add_argument('--mode', choices=['single', 'all', 'quick', 'multi-symbol'], default='quick',
                       help='Optimization mode: single strategy, all strategies, quick test, or multi-symbol comprehensive')
    parser.add_argument('--symbols', choices=['all', 'stocks', 'crypto'], default='all',
                       help='For multi-symbol mode: which symbols to include')

    args = parser.parse_args()

    optimizer = ParameterOptimizer(
        symbol=args.symbol,
        start_date=args.start,
        cash=args.cash
    )

    print("🔬 TRADING STRATEGY OPTIMIZER")
    print("Finding the best parameters for your strategies...")

    if args.mode == 'single' and args.strategy:
        optimizer.test_single_strategy(args.strategy)
    elif args.mode == 'all':
        optimizer.test_all_strategies()
    elif args.mode == 'multi-symbol':
        optimizer.optimize_all_symbols(symbols_type=args.symbols)
    else:  # quick mode
        optimizer.quick_test(args.strategy)


if __name__ == '__main__':
    main()

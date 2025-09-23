#!/usr/bin/env python3
"""
Trading Strategy Optimizer - Systematic Parameter Testing

This module allows you to test different strategies and parameters
to find what actually works vs what doesn't.
"""

import backtrader as bt
import pandas as pd
import numpy as np
from itertools import product
from data import get_stock_data
from strategy import SMAStrategy
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

    def test_sma_parameters(self, short_periods=None, long_periods=None):
        """Test different SMA crossover parameters."""
        if short_periods is None:
            short_periods = [5, 10, 15, 20]
        if long_periods is None:
            long_periods = [20, 30, 50, 100]

        print(f"\nTesting SMA combinations...")
        print(f"Short periods: {short_periods}")
        print(f"Long periods: {long_periods}")

        results = []
        total_tests = len(short_periods) * len(long_periods)
        test_count = 0

        for short, long in product(short_periods, long_periods):
            if short >= long:  # Skip invalid combinations
                continue

            test_count += 1
            print(f"Testing {test_count}/{total_tests}: SMA({short},{long})", end="")

            try:
                result = self._run_backtest(SMAStrategy, short_period=short, long_period=long)
                result['strategy'] = 'SMA'
                result['short_period'] = short
                result['long_period'] = long
                result['params'] = f"SMA({short},{long})"
                results.append(result)
                print(f" → Return: {result['return_pct']:.2f}%")
            except Exception as e:
                print(f" → ERROR: {e}")

        return results

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
            'total_trades': trades.total.closed if 'total' in trades else 0,
            'winning_trades': trades.won.total if 'won' in trades else 0,
            'losing_trades': trades.lost.total if 'lost' in trades else 0,
            'win_rate': (trades.won.total / trades.total.closed * 100) if trades.get('total', {}).get('closed', 0) > 0 else 0,
            'sharpe_ratio': sharpe.get('sharperatio', 0) or 0,
            'max_drawdown': drawdown.max.drawdown if 'max' in drawdown else 0,
            'avg_trade': trades.won.pnl.average if trades.get('won', {}).get('pnl', {}).get('average') else 0
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

    def quick_test(self):
        """Run a quick test with common parameter ranges."""
        if not self.load_data():
            return

        # Test SMA strategies
        sma_results = self.test_sma_parameters(
            short_periods=[5, 10, 15, 20],
            long_periods=[30, 50, 100]
        )

        # Analyze results
        best_results = self.analyze_results(sma_results)

        # Save results to CSV
        if best_results is not None:
            filename = f"optimization_results_{self.symbol}_{self.start_date.replace('-', '')}.csv"
            best_results.to_csv(filename, index=False)
            print(f"\n💾 Results saved to: {filename}")

        return best_results


def main():
    """Run optimization example."""
    import argparse

    parser = argparse.ArgumentParser(description='Trading Strategy Optimizer')
    parser.add_argument('--symbol', default='AAPL', help='Stock symbol')
    parser.add_argument('--start', default='2020-01-01', help='Start date YYYY-MM-DD')
    parser.add_argument('--cash', type=float, default=10000, help='Starting cash')

    args = parser.parse_args()

    optimizer = ParameterOptimizer(
        symbol=args.symbol,
        start_date=args.start,
        cash=args.cash
    )

    print("🔬 TRADING STRATEGY OPTIMIZER")
    print("Finding the best parameters for your strategies...")

    optimizer.quick_test()


if __name__ == '__main__':
    main()
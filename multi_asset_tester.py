#!/usr/bin/env python3
"""
Multi-Asset Strategy Testing Framework with Caching

Test strategies across multiple stocks and cryptocurrencies to find
what works consistently across different markets.
"""

import backtrader as bt
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from itertools import product
from data import get_stock_data
from risk_managed_strategies import RISK_MANAGED_STRATEGIES, get_risk_managed_strategy_params
from risk_management import RiskLevel
import warnings
warnings.filterwarnings('ignore')


class MultiAssetTester:
    """Test strategies across multiple assets with caching."""

    def __init__(self, start_date='2020-01-01', cash=10000, cache_dir='cache'):
        self.start_date = start_date
        self.cash = cash
        self.cache_dir = cache_dir
        self.results = []

        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)

        # Define asset lists
        self.stock_symbols = [
            'AAPL',  # Apple - tech
            'MSFT',  # Microsoft - tech
            'GOOGL', # Google - tech
            'AMZN',  # Amazon - tech/retail
            'TSLA',  # Tesla - EV/tech
            'SPY',   # S&P 500 ETF
            'QQQ',   # Nasdaq ETF
            'VTI',   # Total Stock Market ETF
            'JPM',   # JPMorgan - finance
            'JNJ',   # Johnson & Johnson - healthcare
            'PG',    # Procter & Gamble - consumer goods
            'KO',    # Coca-Cola - consumer goods
            'WMT',   # Walmart - retail
            'XOM',   # ExxonMobil - energy
            'GLD',   # Gold ETF
        ]

        self.crypto_symbols = [
            'BTC-USD',   # Bitcoin
            'ETH-USD',   # Ethereum
            'BNB-USD',   # Binance Coin
            'ADA-USD',   # Cardano
            'SOL-USD',   # Solana
            'DOT-USD',   # Polkadot
            'AVAX-USD',  # Avalanche
            'MATIC-USD', # Polygon
            'LINK-USD',  # Chainlink
            'UNI-USD',   # Uniswap
        ]

        self.all_symbols = self.stock_symbols + self.crypto_symbols

    def get_cache_file(self, symbol):
        """Get cache filename for a specific symbol."""
        return os.path.join(
            self.cache_dir,
            f"results_{symbol.replace('-', '_')}_{self.start_date.replace('-', '')}_{self.cash}.json"
        )

    def load_cache(self, symbol):
        """Load cached results for a specific symbol."""
        cache_file = self.get_cache_file(symbol)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    return cached_data.get('results', [])
            except Exception as e:
                print(f"⚠ Failed to load cache for {symbol}: {e}")
        return []

    def save_cache(self, symbol, results):
        """Save results to cache for a specific symbol."""
        cache_file = self.get_cache_file(symbol)
        try:
            cache_data = {
                'symbol': symbol,
                'start_date': self.start_date,
                'cash': self.cash,
                'generated_at': datetime.now().isoformat(),
                'total_results': len(results),
                'results': results
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"⚠ Failed to save cache for {symbol}: {e}")

    def get_cache_key(self, strategy_name, params):
        """Generate a unique key for caching a specific test."""
        sorted_params = sorted(params.items()) if params else []
        return f"{strategy_name}_{sorted_params}"

    def find_cached_result(self, cached_results, strategy_name, params):
        """Find a specific result in cached data."""
        cache_key = self.get_cache_key(strategy_name, params)

        for result in cached_results:
            result_key = self.get_cache_key(result['strategy'].lower(),
                                          self._parse_params(result.get('params', '')))
            if result_key == cache_key:
                return result
        return None

    def _parse_params(self, param_string):
        """Parse parameter string back to dict for cache comparison."""
        if not param_string:
            return {}

        params = {}
        try:
            for pair in param_string.split(', '):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    try:
                        if '.' in value:
                            params[key] = float(value)
                        else:
                            params[key] = int(value)
                    except ValueError:
                        params[key] = value
        except Exception:
            pass

        return params

    def test_strategy_on_symbol(self, symbol, strategy_name, cached_results=None, **params):
        """Test a single strategy on a single symbol."""
        # Check cache first
        if cached_results:
            cached = self.find_cached_result(cached_results, strategy_name, params)
            if cached:
                return cached

        # Load data for this symbol
        try:
            data = get_stock_data(symbol, self.start_date)
        except Exception as e:
            print(f"  ✗ Failed to load data for {symbol}: {e}")
            return None

        # Run backtest
        if strategy_name not in RISK_MANAGED_STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        strategy_class = RISK_MANAGED_STRATEGIES[strategy_name]

        cerebro = bt.Cerebro()
        # Add strategy with AGGRESSIVE risk profile by default for multi-asset testing
        cerebro.addstrategy(strategy_class, risk_profile=RiskLevel.AGGRESSIVE, **params)
        cerebro.adddata(data)
        cerebro.broker.setcash(self.cash)
        cerebro.broker.setcommission(commission=0.001)

        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')

        results = cerebro.run()
        final_value = cerebro.broker.getvalue()

        # Extract metrics
        strategy_result = results[0]
        trades = strategy_result.analyzers.trades.get_analysis()
        sharpe = strategy_result.analyzers.sharpe.get_analysis()
        drawdown = strategy_result.analyzers.drawdown.get_analysis()
        sqn = strategy_result.analyzers.sqn.get_analysis()

        param_str = ', '.join([f"{k}={v}" for k, v in params.items()]) if params else ''

        return {
            'symbol': symbol,
            'asset_type': 'crypto' if '-USD' in symbol else 'stock',
            'strategy': strategy_name.upper(),
            'params': param_str,
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
            'sqn': sqn.get('sqn', 0) or 0,
            'avg_trade': trades.get('won', {}).get('pnl', {}).get('average', 0) if isinstance(trades, dict) else (trades.won.pnl.average if hasattr(trades, 'won') and hasattr(trades.won, 'pnl') and hasattr(trades.won.pnl, 'average') else 0),
            'tested_at': datetime.now().isoformat()
        }

    def test_strategy_across_assets(self, strategy_name, symbols=None, use_cache=True, **params):
        """Test a single strategy configuration across multiple assets."""
        if symbols is None:
            symbols = self.all_symbols

        results = []
        successful_tests = 0
        cache_hits = 0

        print(f"\nTesting {strategy_name.upper()} across {len(symbols)} assets...")

        for i, symbol in enumerate(symbols):
            print(f"  {i+1:2d}/{len(symbols)} {symbol:<8} ", end="")

            try:
                # Load cache for this symbol
                cached_results = self.load_cache(symbol) if use_cache else []

                # Test strategy
                result = self.test_strategy_on_symbol(
                    symbol, strategy_name, cached_results, **params
                )

                if result:
                    results.append(result)
                    successful_tests += 1

                    # Check if result was cached
                    was_cached = self.find_cached_result(cached_results, strategy_name, params) is not None
                    if was_cached:
                        cache_hits += 1
                        print(f"→ {result['return_pct']:6.1f}% (cached)")
                    else:
                        print(f"→ {result['return_pct']:6.1f}% (tested)")

                        # Update cache
                        if use_cache:
                            cached_results.append(result)
                            self.save_cache(symbol, cached_results)
                else:
                    print("→ FAILED")

            except Exception as e:
                print(f"→ ERROR: {e}")

        print(f"  ✓ Completed {successful_tests}/{len(symbols)} tests")
        if cache_hits > 0:
            print(f"  💡 Used cache for {cache_hits}/{successful_tests} tests")

        return results

    def compare_strategies_across_assets(self, strategies=None, symbols=None, use_cache=True):
        """Compare multiple strategies across multiple assets."""
        if strategies is None:
            strategies = ['buy_hold', 'sma', 'rsi', 'macd', 'bollinger']

        if symbols is None:
            symbols = self.all_symbols

        print(f"🔬 MULTI-ASSET STRATEGY COMPARISON")
        print(f"Testing {len(strategies)} strategies across {len(symbols)} assets")
        print(f"Assets: {len(self.stock_symbols)} stocks, {len(self.crypto_symbols)} cryptocurrencies")

        all_results = []

        # Test each strategy with default parameters
        strategy_configs = {
            'buy_hold': {},
            'sma': {'short_period': 10, 'long_period': 30},
            'rsi': {'rsi_period': 14, 'rsi_low': 30, 'rsi_high': 70},
            'macd': {'fast_ema': 12, 'slow_ema': 26, 'signal_ema': 9},
            'bollinger': {'period': 20, 'devfactor': 2.0},
            'ema': {'short_period': 10, 'long_period': 30},
            'momentum': {'period': 10, 'threshold': 0.02}
        }

        for strategy_name in strategies:
            if strategy_name in strategy_configs:
                params = strategy_configs[strategy_name]
                results = self.test_strategy_across_assets(
                    strategy_name, symbols, use_cache, **params
                )
                all_results.extend(results)

        return self.analyze_multi_asset_results(all_results)

    def analyze_multi_asset_results(self, results):
        """Analyze results across multiple assets and strategies."""
        if not results:
            print("No results to analyze!")
            return None

        df = pd.DataFrame(results)

        print(f"\n{'='*120}")
        print(f"{'MULTI-ASSET STRATEGY ANALYSIS':^120}")
        print(f"{'='*120}")

        # Overall best performers
        df_sorted = df.sort_values('return_pct', ascending=False)
        print(f"\n🏆 TOP 20 BEST PERFORMING STRATEGY-ASSET COMBINATIONS:")
        print(f"{'Rank':<4} {'Symbol':<10} {'Type':<6} {'Strategy':<12} {'Return%':<8} {'Sharpe':<7} {'MaxDD%':<8} {'Trades':<7}")
        print("-" * 120)

        for i, (_, row) in enumerate(df_sorted.head(20).iterrows(), 1):
            print(f"{i:<4} {row['symbol']:<10} {row['asset_type']:<6} {row['strategy']:<12} "
                  f"{row['return_pct']:>7.1f}% {row['sharpe_ratio']:>6.2f} {row['max_drawdown']:>7.1f}% "
                  f"{row['total_trades']:>6.0f}")

        # Strategy performance across all assets
        print(f"\n📊 STRATEGY PERFORMANCE SUMMARY (across all assets):")
        strategy_summary = df.groupby('strategy').agg({
            'return_pct': ['count', 'mean', 'std', 'min', 'max'],
            'sharpe_ratio': 'mean',
            'win_rate': 'mean',
            'max_drawdown': 'mean'
        }).round(2)

        print(strategy_summary)

        # Asset type performance
        print(f"\n🏦 PERFORMANCE BY ASSET TYPE:")
        asset_summary = df.groupby('asset_type').agg({
            'return_pct': ['count', 'mean', 'std'],
            'sharpe_ratio': 'mean',
            'win_rate': 'mean'
        }).round(2)

        print(asset_summary)

        # Best strategy for each asset
        print(f"\n🎯 BEST STRATEGY FOR EACH ASSET:")
        best_per_asset = df.loc[df.groupby('symbol')['return_pct'].idxmax()]
        for _, row in best_per_asset.sort_values('return_pct', ascending=False).iterrows():
            print(f"{row['symbol']:<8} → {row['strategy']:<12} {row['return_pct']:>7.1f}%")

        # Consistency analysis
        print(f"\n📈 STRATEGY CONSISTENCY (% of profitable tests):")
        consistency = df.groupby('strategy').apply(
            lambda x: (x['return_pct'] > 0).mean() * 100
        ).sort_values(ascending=False)

        for strategy, pct in consistency.items():
            total_tests = len(df[df['strategy'] == strategy])
            print(f"{strategy:<12} {pct:>5.1f}% profitable ({total_tests} tests)")

        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"multi_asset_results_{timestamp}.csv"
        df_sorted.to_csv(filename, index=False)
        print(f"\n💾 Complete results saved to: {filename}")

        return df_sorted

    def quick_multi_asset_test(self, sample_assets=True):
        """Run a quick test across a sample of assets."""
        if sample_assets:
            # Test on a sample of assets for speed
            sample_stocks = ['AAPL', 'SPY', 'TSLA', 'WMT', 'GLD']
            sample_crypto = ['BTC-USD', 'ETH-USD', 'ADA-USD']
            symbols = sample_stocks + sample_crypto
        else:
            symbols = self.all_symbols

        strategies = ['buy_hold', 'sma', 'rsi', 'macd']

        return self.compare_strategies_across_assets(strategies, symbols)

    def clear_all_caches(self):
        """Clear all cache files."""
        cache_files = [f for f in os.listdir(self.cache_dir) if f.startswith('results_') and f.endswith('.json')]
        for cache_file in cache_files:
            os.remove(os.path.join(self.cache_dir, cache_file))
        print(f"🗑️ Cleared {len(cache_files)} cache files")


def main():
    """Run multi-asset strategy comparison."""
    import argparse

    parser = argparse.ArgumentParser(description='Multi-Asset Strategy Comparison')
    parser.add_argument('--start', default='2020-01-01', help='Start date YYYY-MM-DD')
    parser.add_argument('--cash', type=float, default=10000, help='Starting cash')
    parser.add_argument('--mode', choices=['quick', 'full', 'stocks', 'crypto'], default='quick',
                       help='Test mode')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    parser.add_argument('--clear-cache', action='store_true', help='Clear all caches and exit')

    args = parser.parse_args()

    tester = MultiAssetTester(
        start_date=args.start,
        cash=args.cash
    )

    if args.clear_cache:
        tester.clear_all_caches()
        return

    use_cache = not args.no_cache

    if args.mode == 'quick':
        tester.quick_multi_asset_test(sample_assets=True)
    elif args.mode == 'full':
        tester.compare_strategies_across_assets(use_cache=use_cache)
    elif args.mode == 'stocks':
        tester.compare_strategies_across_assets(symbols=tester.stock_symbols, use_cache=use_cache)
    elif args.mode == 'crypto':
        tester.compare_strategies_across_assets(symbols=tester.crypto_symbols, use_cache=use_cache)


if __name__ == '__main__':
    main()
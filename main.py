import argparse
import sys
import os
import glob
from multi_asset_tester import MultiAssetTester
from results_visualizer import ResultsVisualizer


def clear_data_cache(cache_dir='data_cache'):
    """Clear all cached stock data files."""
    if os.path.exists(cache_dir):
        cache_files = glob.glob(os.path.join(cache_dir, '*.json'))
        for cache_file in cache_files:
            os.remove(cache_file)
        print(f"🗑️ Cleared {len(cache_files)} data cache files from {cache_dir}/")
        if len(cache_files) == 0:
            print(f"📁 Data cache directory {cache_dir}/ was already empty")
    else:
        print(f"📁 Data cache directory {cache_dir}/ does not exist")


def run_single_test(symbol, strategy, start_date, cash, use_cache=True, **params):
    """Run a single strategy test (legacy mode)."""
    import backtrader as bt
    from strategies import STRATEGIES
    from data import get_stock_data
    from visualization import print_performance_summary

    if strategy not in STRATEGIES:
        print(f"Unknown strategy: {strategy}")
        print(f"Available strategies: {list(STRATEGIES.keys())}")
        return

    print(f"\nTesting {strategy.upper()} strategy on {symbol}")
    print(f"Parameters: {params}")
    print("-" * 50)

    try:
        # Load data with caching
        data = get_stock_data(symbol, start_date, use_cache=use_cache)

        # Set up backtest
        cerebro = bt.Cerebro()
        cerebro.addstrategy(STRATEGIES[strategy], **params)
        cerebro.adddata(data)
        cerebro.broker.setcash(cash)
        cerebro.broker.setcommission(commission=0.001)

        print(f"Starting Portfolio Value: ${cerebro.broker.getvalue():.2f}")

        # Run backtest
        cerebro.run()
        final_value = cerebro.broker.getvalue()

        # Print results
        print_performance_summary(cash, final_value)

        # Try to plot
        try:
            cerebro.plot(style='candlestick', barup='green', bardown='red')
        except Exception as e:
            print(f"Chart generation failed: {e}")

    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description='Advanced Trading Bot with Multi-Asset Testing')

    # Mode selection
    parser.add_argument('--mode', choices=['single', 'multi', 'optimize', 'visualize'],
                       default='single', help='Operation mode')

    # Single test parameters
    parser.add_argument('--symbol', default='AAPL', help='Stock symbol')
    parser.add_argument('--strategy', default=None, help='Strategy name (defaults to SMA when omitted)')
    parser.add_argument('--start', default='2020-01-01', help='Start date YYYY-MM-DD')
    parser.add_argument('--cash', type=float, default=10000, help='Starting cash')

    # Strategy parameters
    parser.add_argument('--short', type=int, default=10, help='Short period (SMA/EMA)')
    parser.add_argument('--long', type=int, default=30, help='Long period (SMA/EMA)')
    parser.add_argument('--rsi-period', type=int, default=14, help='RSI period')
    parser.add_argument('--rsi-low', type=int, default=30, help='RSI oversold level')
    parser.add_argument('--rsi-high', type=int, default=70, help='RSI overbought level')

    # Multi-asset testing
    parser.add_argument('--test-mode', choices=['quick', 'full', 'stocks', 'crypto'],
                       default='quick', help='Multi-asset test mode')

    # Optimization parameters
    parser.add_argument('--opt-mode', choices=['single', 'all', 'quick', 'multi-symbol'], default='quick',
                       help='Optimization mode: single strategy, all strategies, quick test, or multi-symbol comprehensive')
    parser.add_argument('--opt-symbols', choices=['all', 'stocks', 'crypto'], default='all',
                       help='For multi-symbol optimization: which symbols to include')

    # Caching
    parser.add_argument('--no-cache', action='store_true', help='Disable data and results caching')
    parser.add_argument('--clear-cache', action='store_true', help='Clear all cache files')
    parser.add_argument('--clear-data-cache', action='store_true', help='Clear data cache only')

    args = parser.parse_args()

    # Handle cache clearing options
    if args.clear_cache or args.clear_data_cache:
        clear_data_cache()
        if args.clear_cache:
            # Also clear MultiAssetTester cache
            tester = MultiAssetTester()
            tester.clear_all_caches()
        return

    use_cache = not args.no_cache

    if args.mode == 'single':
        # Single strategy test (legacy mode)
        strategy_params = {}
        strategy_name = args.strategy or 'sma'

        if strategy_name in ['sma', 'ema']:
            strategy_params = {'short_period': args.short, 'long_period': args.long}
        elif strategy_name == 'rsi':
            strategy_params = {'rsi_period': args.rsi_period, 'rsi_low': args.rsi_low, 'rsi_high': args.rsi_high}

        run_single_test(args.symbol, strategy_name, args.start, args.cash, use_cache, **strategy_params)

    elif args.mode == 'multi':
        # Multi-asset strategy comparison
        tester = MultiAssetTester(start_date=args.start, cash=args.cash)

        if args.clear_cache:
            tester.clear_all_caches()
            return

        use_cache = not args.no_cache

        if args.test_mode == 'quick':
            tester.quick_multi_asset_test()
        elif args.test_mode == 'full':
            tester.compare_strategies_across_assets(use_cache=use_cache)
        elif args.test_mode == 'stocks':
            tester.compare_strategies_across_assets(symbols=tester.stock_symbols, use_cache=use_cache)
        elif args.test_mode == 'crypto':
            tester.compare_strategies_across_assets(symbols=tester.crypto_symbols, use_cache=use_cache)

    elif args.mode == 'optimize':
        # Parameter optimization
        from optimizer import ParameterOptimizer

        optimizer = ParameterOptimizer(
            symbol=args.symbol,
            start_date=args.start,
            cash=args.cash
        )

        print("🔬 TRADING STRATEGY OPTIMIZER")
        print("Finding the best parameters for your strategies...")

        selected_strategy = args.strategy

        if args.opt_mode == 'single':
            optimizer.test_single_strategy(selected_strategy or 'sma')
        elif args.opt_mode == 'all':
            optimizer.test_all_strategies()
        elif args.opt_mode == 'multi-symbol':
            optimizer.optimize_all_symbols(symbols_type=args.opt_symbols)
        else:  # quick mode
            optimizer.quick_test(selected_strategy)

    elif args.mode == 'visualize':
        # Generate visualization report
        visualizer = ResultsVisualizer()
        visualizer.generate_full_report()

    else:
        print("Unknown mode. Use --help for options.")


if __name__ == '__main__':
    main()

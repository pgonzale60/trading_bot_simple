import argparse
import backtrader as bt
from strategy import SMAStrategy
from data import get_stock_data
from visualization import print_performance_summary


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simple Trading Bot')
    parser.add_argument('--symbol', default='AAPL', help='Stock symbol (default: AAPL)')
    parser.add_argument('--short', type=int, default=10, help='Short MA period (default: 10)')
    parser.add_argument('--long', type=int, default=30, help='Long MA period (default: 30)')
    parser.add_argument('--start', help='Start date YYYY-MM-DD')
    parser.add_argument('--cash', type=float, default=10000, help='Starting cash (default: 10000)')

    args = parser.parse_args()

    # Create Cerebro engine
    cerebro = bt.Cerebro()

    # Add strategy
    cerebro.addstrategy(SMAStrategy, short_period=args.short, long_period=args.long)

    # Get data
    try:
        data = get_stock_data(symbol=args.symbol, start_date=args.start)
        cerebro.adddata(data)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    # Set starting cash
    cerebro.broker.setcash(args.cash)

    # Set commission (0.1% per trade)
    cerebro.broker.setcommission(commission=0.001)

    # Print starting conditions
    print(f"\nStarting Portfolio Value: ${cerebro.broker.getvalue():.2f}")
    print(f"Strategy: {args.short}-day SMA vs {args.long}-day SMA crossover")
    print(f"Symbol: {args.symbol}")
    print("-" * 50)

    # Run backtest
    cerebro.run()

    # Print final results
    final_value = cerebro.broker.getvalue()

    # Use our custom performance summary
    print_performance_summary(args.cash, final_value)

    # Plot results
    print("\nGenerating chart...")
    try:
        cerebro.plot(style='candlestick', barup='green', bardown='red')
    except Exception as e:
        print(f"Chart generation failed: {e}")
        print("Note: Charts may not work in some environments. Data analysis completed successfully.")


if __name__ == '__main__':
    main()
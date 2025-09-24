#!/usr/bin/env python3
"""
Test all fixed strategies with TSLA data to verify they work correctly.
"""

import backtrader as bt
import yfinance as yf
import pandas as pd
from strategies import STRATEGIES

def test_strategy(strategy_class, strategy_name, data, cash=10000):
    """Test a single strategy with given data."""
    print(f"\n{'='*60}")
    print(f"TESTING: {strategy_name.upper()} STRATEGY")
    print(f"{'='*60}")

    # Create a fresh Cerebro instance
    cerebro = bt.Cerebro()

    # Set up the broker
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)  # 0.1% commission

    # Add our data and strategy
    cerebro.adddata(data)
    cerebro.addstrategy(strategy_class)

    # Record starting values
    starting_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: ${starting_value:.2f}')
    print(f'Starting Cash: ${cerebro.broker.getcash():.2f}')
    print()

    # Run the backtest
    results = cerebro.run()

    # Calculate results
    final_value = cerebro.broker.getvalue()
    total_return = ((final_value / starting_value) - 1) * 100

    print(f'\nFinal Portfolio Value: ${final_value:.2f}')
    print(f'Total Return: {total_return:.1f}%')
    print(f'Final Cash: ${cerebro.broker.getcash():.2f}')

    return {
        'strategy': strategy_name,
        'starting_value': starting_value,
        'final_value': final_value,
        'total_return': total_return,
        'final_cash': cerebro.broker.getcash()
    }

def main():
    """Test all strategies with TSLA data."""
    print("Downloading TSLA data from 2020-01-01 to 2024-09-24...")

    # Download TSLA data
    tsla_data = yf.download('TSLA', start='2020-01-01', end='2024-09-24')

    if tsla_data.empty:
        print("ERROR: No data downloaded!")
        return

    # Prepare data for backtrader
    tsla_data.columns = tsla_data.columns.droplevel(1)  # Remove ticker level from MultiIndex
    tsla_data.reset_index(inplace=True)

    # Create backtrader data feed
    data = bt.feeds.PandasData(
        dataname=tsla_data,
        datetime='Date',
        open='Open',
        high='High',
        low='Low',
        close='Close',
        volume='Volume'
    )

    print(f"Downloaded {len(tsla_data)} days of TSLA data")
    first_close = tsla_data['Close'].iloc[0]
    last_close = tsla_data['Close'].iloc[-1]
    print(f"TSLA Price Range: ${first_close:.2f} to ${last_close:.2f}")
    print(f"Buy & Hold Return: {((last_close / first_close) - 1) * 100:.1f}%")

    # Test all strategies
    results = []
    strategies_to_test = [
        'sma', 'rsi', 'macd', 'bollinger', 'ema', 'momentum', 'buy_hold'
    ]

    for strategy_name in strategies_to_test:
        if strategy_name in STRATEGIES:
            try:
                result = test_strategy(
                    STRATEGIES[strategy_name],
                    strategy_name,
                    data
                )
                results.append(result)
            except Exception as e:
                print(f"ERROR testing {strategy_name}: {e}")
                results.append({
                    'strategy': strategy_name,
                    'error': str(e)
                })
        else:
            print(f"Strategy {strategy_name} not found!")

    # Summary of all results
    print(f"\n{'='*80}")
    print("STRATEGY PERFORMANCE SUMMARY")
    print(f"{'='*80}")
    print(f"{'Strategy':<15} {'Start Value':<12} {'Final Value':<12} {'Return %':<10} {'Status'}")
    print("-" * 80)

    for result in results:
        if 'error' in result:
            print(f"{result['strategy']:<15} {'N/A':<12} {'N/A':<12} {'ERROR':<10} {result['error']}")
        else:
            print(f"{result['strategy']:<15} ${result['starting_value']:<11.2f} ${result['final_value']:<11.2f} {result['total_return']:<9.1f}% {'OK'}")

    print("-" * 80)

    # Find best and worst performers
    successful_results = [r for r in results if 'error' not in r]
    if successful_results:
        best_strategy = max(successful_results, key=lambda x: x['total_return'])
        worst_strategy = min(successful_results, key=lambda x: x['total_return'])

        print(f"\nBest Performer: {best_strategy['strategy'].upper()} with {best_strategy['total_return']:.1f}% return")
        print(f"Worst Performer: {worst_strategy['strategy'].upper()} with {worst_strategy['total_return']:.1f}% return")

if __name__ == '__main__':
    main()
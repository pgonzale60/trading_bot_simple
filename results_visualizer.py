#!/usr/bin/env python3
"""
Trading Results Visualizer

Create charts and visualizations from strategy test results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json
import os


class ResultsVisualizer:
    """Visualize trading strategy results."""

    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        plt.style.use('default')
        sns.set_palette("husl")

    def load_all_cached_results(self):
        """Load all cached results into a single DataFrame."""
        all_results = []

        if not os.path.exists(self.cache_dir):
            print(f"Cache directory {self.cache_dir} doesn't exist!")
            return pd.DataFrame()

        cache_files = [f for f in os.listdir(self.cache_dir)
                      if f.startswith('results_') and f.endswith('.json')]

        for cache_file in cache_files:
            try:
                with open(os.path.join(self.cache_dir, cache_file), 'r') as f:
                    data = json.load(f)
                    results = data.get('results', [])
                    all_results.extend(results)
            except Exception as e:
                print(f"Warning: Failed to load {cache_file}: {e}")

        if not all_results:
            print("No cached results found!")
            return pd.DataFrame()

        df = pd.DataFrame(all_results)
        print(f"Loaded {len(df)} results from {len(cache_files)} cache files")
        return df

    def plot_strategy_performance(self, df, save_path=None):
        """Create a comprehensive strategy performance visualization."""
        if df.empty:
            return

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Trading Strategy Performance Analysis', fontsize=16, fontweight='bold')

        # 1. Return distribution by strategy
        ax1 = axes[0, 0]
        strategy_returns = df.groupby('strategy')['return_pct'].apply(list)
        strategies = list(strategy_returns.keys())
        returns_data = [strategy_returns[s] for s in strategies]

        bp1 = ax1.boxplot(returns_data, labels=strategies, patch_artist=True)
        ax1.set_title('Return Distribution by Strategy')
        ax1.set_ylabel('Return (%)')
        ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7)
        ax1.tick_params(axis='x', rotation=45)

        # Color boxes
        colors = sns.color_palette("husl", len(strategies))
        for patch, color in zip(bp1['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        # 2. Average return by strategy
        ax2 = axes[0, 1]
        avg_returns = df.groupby('strategy')['return_pct'].mean().sort_values(ascending=True)
        bars = ax2.barh(range(len(avg_returns)), avg_returns.values)
        ax2.set_yticks(range(len(avg_returns)))
        ax2.set_yticklabels(avg_returns.index)
        ax2.set_xlabel('Average Return (%)')
        ax2.set_title('Average Return by Strategy')
        ax2.axvline(x=0, color='red', linestyle='--', alpha=0.7)

        # Color bars based on positive/negative
        for i, (bar, value) in enumerate(zip(bars, avg_returns.values)):
            bar.set_color('green' if value > 0 else 'red')
            bar.set_alpha(0.7)

        # 3. Win rate vs Return scatter
        ax3 = axes[1, 0]
        if 'asset_type' in df.columns:
            for asset_type in df['asset_type'].unique():
                subset = df[df['asset_type'] == asset_type]
                ax3.scatter(subset['win_rate'], subset['return_pct'],
                          label=asset_type.title(), alpha=0.6, s=50)
        else:
            ax3.scatter(df['win_rate'], df['return_pct'], alpha=0.6, s=50)

        ax3.set_xlabel('Win Rate (%)')
        ax3.set_ylabel('Return (%)')
        ax3.set_title('Win Rate vs Return')
        ax3.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax3.axvline(x=50, color='gray', linestyle='--', alpha=0.5)
        if 'asset_type' in df.columns:
            ax3.legend()

        # 4. Sharpe ratio comparison
        ax4 = axes[1, 1]
        if 'sharpe_ratio' in df.columns:
            sharpe_by_strategy = df.groupby('strategy')['sharpe_ratio'].mean().sort_values(ascending=True)
            bars = ax4.barh(range(len(sharpe_by_strategy)), sharpe_by_strategy.values)
            ax4.set_yticks(range(len(sharpe_by_strategy)))
            ax4.set_yticklabels(sharpe_by_strategy.index)
            ax4.set_xlabel('Average Sharpe Ratio')
            ax4.set_title('Risk-Adjusted Returns (Sharpe Ratio)')
            ax4.axvline(x=0, color='red', linestyle='--', alpha=0.7)

            # Color bars
            for bar, value in zip(bars, sharpe_by_strategy.values):
                bar.set_color('green' if value > 0 else 'red')
                bar.set_alpha(0.7)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")

        plt.show()

    def plot_asset_performance(self, df, save_path=None):
        """Create asset-specific performance visualization."""
        if df.empty or 'symbol' not in df.columns:
            return

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Asset Performance Analysis', fontsize=16, fontweight='bold')

        # 1. Best performing assets
        ax1 = axes[0, 0]
        best_per_asset = df.loc[df.groupby('symbol')['return_pct'].idxmax()]
        best_sorted = best_per_asset.sort_values('return_pct', ascending=True).tail(15)

        bars = ax1.barh(range(len(best_sorted)), best_sorted['return_pct'])
        ax1.set_yticks(range(len(best_sorted)))
        ax1.set_yticklabels(best_sorted['symbol'])
        ax1.set_xlabel('Best Return (%)')
        ax1.set_title('Top 15 Assets (Best Strategy Performance)')

        for bar, value in zip(bars, best_sorted['return_pct']):
            bar.set_color('green' if value > 0 else 'red')
            bar.set_alpha(0.7)

        # 2. Asset type comparison
        ax2 = axes[0, 1]
        if 'asset_type' in df.columns:
            asset_returns = df.groupby('asset_type')['return_pct'].mean()
            bars = ax2.bar(asset_returns.index, asset_returns.values)
            ax2.set_ylabel('Average Return (%)')
            ax2.set_title('Performance by Asset Type')
            ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)

            for bar, value in zip(bars, asset_returns.values):
                bar.set_color('green' if value > 0 else 'red')
                bar.set_alpha(0.7)

        # 3. Strategy effectiveness by asset type
        ax3 = axes[1, 0]
        if 'asset_type' in df.columns:
            pivot_data = df.pivot_table(values='return_pct', index='strategy',
                                      columns='asset_type', aggfunc='mean')
            im = ax3.imshow(pivot_data.values, cmap='RdYlGn', aspect='auto')
            ax3.set_xticks(range(len(pivot_data.columns)))
            ax3.set_xticklabels(pivot_data.columns)
            ax3.set_yticks(range(len(pivot_data.index)))
            ax3.set_yticklabels(pivot_data.index)
            ax3.set_title('Strategy Performance Heatmap')

            # Add colorbar
            cbar = plt.colorbar(im, ax=ax3)
            cbar.set_label('Average Return (%)')

            # Add text annotations
            for i in range(len(pivot_data.index)):
                for j in range(len(pivot_data.columns)):
                    text = ax3.text(j, i, f'{pivot_data.iloc[i, j]:.1f}%',
                                  ha="center", va="center", color="black", fontweight='bold')

        # 4. Volatility analysis
        ax4 = axes[1, 1]
        if 'max_drawdown' in df.columns:
            scatter = ax4.scatter(df['max_drawdown'], df['return_pct'],
                                c=df['total_trades'], cmap='viridis', alpha=0.6, s=50)
            ax4.set_xlabel('Max Drawdown (%)')
            ax4.set_ylabel('Return (%)')
            ax4.set_title('Return vs Risk (Drawdown)')
            ax4.axhline(y=0, color='red', linestyle='--', alpha=0.5)

            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax4)
            cbar.set_label('Number of Trades')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Asset analysis plot saved to: {save_path}")

        plt.show()

    def create_summary_report(self, df):
        """Create a text summary report."""
        if df.empty:
            return

        print(f"\n{'='*80}")
        print(f"{'TRADING STRATEGY ANALYSIS SUMMARY':^80}")
        print(f"{'='*80}")

        # Overall statistics
        total_tests = len(df)
        profitable_tests = len(df[df['return_pct'] > 0])
        avg_return = df['return_pct'].mean()
        best_return = df['return_pct'].max()
        worst_return = df['return_pct'].min()

        print(f"\n📊 OVERALL STATISTICS:")
        print(f"Total tests: {total_tests}")
        print(f"Profitable tests: {profitable_tests} ({profitable_tests/total_tests*100:.1f}%)")
        print(f"Average return: {avg_return:.2f}%")
        print(f"Best return: {best_return:.2f}%")
        print(f"Worst return: {worst_return:.2f}%")

        # Strategy rankings
        print(f"\n🏆 STRATEGY RANKINGS (by average return):")
        strategy_avg = df.groupby('strategy')['return_pct'].agg(['mean', 'count', 'std']).round(2)
        strategy_avg['profitable_pct'] = df.groupby('strategy').apply(
            lambda x: (x['return_pct'] > 0).mean() * 100
        ).round(1)

        strategy_avg = strategy_avg.sort_values('mean', ascending=False)

        print(f"{'Strategy':<12} {'Avg Return':<10} {'Tests':<6} {'Std Dev':<8} {'Profitable%':<12}")
        print("-" * 60)
        for strategy, row in strategy_avg.iterrows():
            print(f"{strategy:<12} {row['mean']:>8.1f}% {row['count']:>5.0f} {row['std']:>7.1f}% {row['profitable_pct']:>10.1f}%")

        # Asset analysis (if available)
        if 'symbol' in df.columns:
            print(f"\n🎯 TOP 10 BEST ASSETS:")
            best_per_asset = df.loc[df.groupby('symbol')['return_pct'].idxmax()]
            top_assets = best_per_asset.nlargest(10, 'return_pct')

            print(f"{'Asset':<10} {'Best Return':<12} {'Strategy':<12}")
            print("-" * 40)
            for _, row in top_assets.iterrows():
                print(f"{row['symbol']:<10} {row['return_pct']:>10.1f}% {row['strategy']:<12}")

    def generate_full_report(self):
        """Generate a complete analysis report with visualizations."""
        df = self.load_all_cached_results()

        if df.empty:
            print("No data available for visualization!")
            return

        print(f"Generating comprehensive analysis report...")

        # Create text summary
        self.create_summary_report(df)

        # Create visualizations
        self.plot_strategy_performance(df, 'strategy_performance.png')
        self.plot_asset_performance(df, 'asset_performance.png')

        print(f"\n✅ Analysis complete! Check the generated PNG files for detailed charts.")


def main():
    """Generate visualization report."""
    import argparse

    parser = argparse.ArgumentParser(description='Trading Results Visualizer')
    parser.add_argument('--cache-dir', default='cache', help='Cache directory path')

    args = parser.parse_args()

    visualizer = ResultsVisualizer(cache_dir=args.cache_dir)
    visualizer.generate_full_report()


if __name__ == '__main__':
    main()
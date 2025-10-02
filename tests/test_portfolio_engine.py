import unittest
from unittest import mock

from trading_bot import asset_universe
from trading_bot.portfolio_config import DEFAULT_PORTFOLIO_CONFIG, PortfolioConfig, SleeveLimit
from trading_bot.portfolio_engine import PortfolioBuyHoldStrategy, PortfolioEngine, PortfolioRunResult


class TestPortfolioEngineRun(unittest.TestCase):
    @mock.patch('trading_bot.portfolio_engine.bt')
    @mock.patch('trading_bot.portfolio_engine.get_stock_data')
    def test_run_deduplicates_symbols_and_returns_result(self, mock_get_stock_data, mock_bt):
        engine = PortfolioEngine(start_date='2020-01-01', cash=5000.0, test_mode='quick', use_cache=False)

        first_feed = mock.Mock()
        second_feed = mock.Mock()
        mock_get_stock_data.side_effect = [first_feed, second_feed]

        cerebro = mock.Mock()
        cerebro.broker.getvalue.return_value = 12345.0
        mock_bt.Cerebro.return_value = cerebro

        result = engine.run(symbols=['AAPL', 'AAPL', 'MSFT'])

        mock_bt.Cerebro.assert_called_once()
        cerebro.broker.setcash.assert_called_once_with(5000.0)
        cerebro.broker.setcommission.assert_called_once()
        self.assertEqual(mock_get_stock_data.call_count, 2)
        mock_get_stock_data.assert_has_calls([
            mock.call(symbol='AAPL', start_date='2020-01-01', use_cache=False),
            mock.call(symbol='MSFT', start_date='2020-01-01', use_cache=False),
        ])

        self.assertEqual(first_feed._name, 'AAPL')
        self.assertEqual(second_feed._name, 'MSFT')
        cerebro.adddata.assert_has_calls([
            mock.call(first_feed, name='AAPL'),
            mock.call(second_feed, name='MSFT'),
        ])
        cerebro.addstrategy.assert_called_once_with(PortfolioBuyHoldStrategy)
        cerebro.run.assert_called_once()

        self.assertIsInstance(result, PortfolioRunResult)
        self.assertEqual(list(result.symbols), ['AAPL', 'MSFT'])
        self.assertEqual(result.starting_cash, 5000.0)
        self.assertEqual(result.final_value, 12345.0)

    def test_run_raises_when_no_symbols_resolved(self):
        engine = PortfolioEngine()
        with mock.patch.object(engine, '_resolve_symbols', return_value=[]):
            with self.assertRaises(ValueError):
                engine.run()

    def test_resolve_symbols_by_mode(self):
        engine = PortfolioEngine(test_mode='stocks')
        stocks = engine._resolve_symbols(symbols=None)
        self.assertEqual(stocks, asset_universe.STOCK_UNIVERSE_2019)
        self.assertIsNot(stocks, asset_universe.STOCK_UNIVERSE_2019)

        engine.test_mode = 'crypto'
        crypto = engine._resolve_symbols(symbols=None)
        self.assertEqual(crypto, asset_universe.CRYPTO_UNIVERSE_2019)

        engine.test_mode = 'full'
        all_assets = engine._resolve_symbols(symbols=None)
        self.assertEqual(all_assets, asset_universe.ALL_ASSETS_2019)

        engine.test_mode = 'quick'
        quick = engine._resolve_symbols(symbols=None)
        self.assertEqual(quick, asset_universe.QUICK_SAMPLE_ALL)


class TestPortfolioConfig(unittest.TestCase):
    def test_default_sleeve_limits(self):
        config = DEFAULT_PORTFOLIO_CONFIG
        self.assertEqual(config.name, 'blended')
        self.assertEqual(config.rebalance_frequency, 'monthly')
        self.assertEqual(config.risk_profile, 'moderate')
        self.assertEqual(config.crypto_sleeve.max_allocation, 0.5)
        self.assertEqual(config.equity_sleeve.max_allocation, 1.0)

        limits = config.sleeve_limits
        self.assertIn('equities', limits)
        self.assertIn('crypto', limits)
        self.assertIs(limits['equities'], config.equity_sleeve)
        self.assertIs(limits['crypto'], config.crypto_sleeve)

    def test_custom_portfolio_config(self):
        alt = PortfolioConfig(
            name='custom',
            rebalance_frequency='weekly',
            risk_profile='aggressive',
            equity_sleeve=SleeveLimit(name='equities', max_allocation=0.8),
            crypto_sleeve=SleeveLimit(name='crypto', max_allocation=0.2),
            metadata={'notes': 'test'},
        )
        self.assertEqual(alt.sleeve_limits['crypto'].max_allocation, 0.2)
        self.assertEqual(alt.metadata['notes'], 'test')


class TestAssetUniverse(unittest.TestCase):
    def test_asset_universe_composition(self):
        stocks = set(asset_universe.STOCK_UNIVERSE_2019)
        crypto = set(asset_universe.CRYPTO_UNIVERSE_2019)
        self.assertTrue(stocks)
        self.assertTrue(crypto)
        self.assertFalse(stocks.intersection(crypto))

        combined = asset_universe.ALL_ASSETS_2019
        self.assertEqual(len(combined), len(stocks) + len(crypto))
        self.assertEqual(combined[:len(asset_universe.STOCK_UNIVERSE_2019)], asset_universe.STOCK_UNIVERSE_2019)
        self.assertEqual(combined[len(asset_universe.STOCK_UNIVERSE_2019):], asset_universe.CRYPTO_UNIVERSE_2019)

    def test_quick_samples_are_subsets(self):
        expected = asset_universe.QUICK_SAMPLE_STOCKS + asset_universe.QUICK_SAMPLE_CRYPTO
        self.assertEqual(asset_universe.QUICK_SAMPLE_ALL, expected)
        self.assertEqual(len(expected), len(set(expected)), "Quick sample should not contain duplicates")


if __name__ == '__main__':
    unittest.main()

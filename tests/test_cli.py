import argparse
import sys
import types
import unittest
from types import SimpleNamespace
from unittest import mock

import main


class TestPortfolioModeFlag(unittest.TestCase):
    def _get_mode_choices(self):
        parser = main.build_arg_parser()
        mode_action = next(action for action in parser._actions if action.dest == 'mode')
        return mode_action.choices

    def test_portfolio_mode_added_to_parser_choices(self):
        choices = self._get_mode_choices()
        self.assertIn('portfolio', choices)

    @mock.patch('trading_bot.portfolio_engine.PortfolioEngine.run')
    @mock.patch('trading_bot.portfolio_engine.PortfolioEngine.__init__', return_value=None)
    def test_execute_invokes_portfolio_engine(self, mock_init, mock_run):
        parser = main.build_arg_parser()
        args = parser.parse_args(['--mode', 'portfolio', '--test-mode', 'quick'])

        sentinel = object()
        mock_run.return_value = sentinel

        result = main.execute(args)

        mock_init.assert_called_once()
        mock_run.assert_called_once()
        self.assertIs(result, sentinel)

    @mock.patch('main.run_single_test')
    @mock.patch('trading_bot.portfolio_engine.PortfolioEngine')
    def test_single_mode_does_not_trigger_portfolio_engine(self, mock_engine, mock_run_single):
        parser = main.build_arg_parser()
        args = parser.parse_args(['--mode', 'single'])

        main.execute(args)

        mock_engine.assert_not_called()
        mock_run_single.assert_called_once()

    def test_run_single_test_uses_risk_managed_strategy(self):
        # Stub external modules imported inside run_single_test
        fake_module_bt = types.SimpleNamespace()

        class FakeBroker:
            def __init__(self):
                self.value = 10000
                self.cash = 6000

            def setcash(self, amount):
                self.value = amount

            def setcommission(self, **kwargs):
                self.commission = kwargs

            def getvalue(self):
                return self.value

            def getcash(self):
                return self.cash

        class FakeCerebro:
            instances = []

            def __init__(self):
                self.broker = FakeBroker()
                self.strategy_kwargs = None
                self.plotted = False
                FakeCerebro.instances.append(self)

            def addstrategy(self, cls, **kwargs):
                self.strategy_kwargs = kwargs

            def adddata(self, data):
                self.data = data

            def run(self):
                # Simulate portfolio growth and return strategy list
                self.broker.value = 12000
                return []

            def plot(self, *args, **kwargs):
                self.plotted = True

        fake_module_bt.Cerebro = FakeCerebro

        def fake_get_stock_data(*args, **kwargs):
            return SimpleNamespace()

        printed = {}

        def fake_print_summary(cash, final_value):
            printed['cash'] = cash
            printed['final'] = final_value

        fake_data_module = types.SimpleNamespace(get_stock_data=fake_get_stock_data)
        fake_vis_module = types.SimpleNamespace(print_performance_summary=fake_print_summary)

        with mock.patch.dict(sys.modules, {
            'backtrader': fake_module_bt,
            'trading_bot.data': fake_data_module,
            'trading_bot.visualization': fake_vis_module,
        }):
            from trading_bot.risk_managed_strategies import RISK_MANAGED_STRATEGIES

            class DummyStrategy:
                pass

            RISK_MANAGED_STRATEGIES['dummy'] = DummyStrategy

            try:
                main.run_single_test('SYM', 'dummy', '2020-01-01', 10000, use_cache=False)
            finally:
                del RISK_MANAGED_STRATEGIES['dummy']

        # Verify summary output and default kwargs were applied
        self.assertEqual(printed['cash'], 10000)
        self.assertEqual(printed['final'], 12000)
        self.assertIsNotNone(FakeCerebro.instances[-1].strategy_kwargs)
        self.assertFalse(FakeCerebro.instances[-1].strategy_kwargs['enable_risk_logging'])


if __name__ == '__main__':
    unittest.main()

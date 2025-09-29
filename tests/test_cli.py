import argparse
import unittest
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

    @mock.patch('portfolio_engine.PortfolioEngine.run')
    @mock.patch('portfolio_engine.PortfolioEngine.__init__', return_value=None)
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
    @mock.patch('portfolio_engine.PortfolioEngine')
    def test_single_mode_does_not_trigger_portfolio_engine(self, mock_engine, mock_run_single):
        parser = main.build_arg_parser()
        args = parser.parse_args(['--mode', 'single'])

        main.execute(args)

        mock_engine.assert_not_called()
        mock_run_single.assert_called_once()


if __name__ == '__main__':
    unittest.main()

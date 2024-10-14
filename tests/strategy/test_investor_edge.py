import unittest
from unittest.mock import Mock
from datetime import datetime
import pandas as pd
from copy import deepcopy
from pandas.tseries.offsets import DateOffset

from src.strategy.investor import Investor
from utils.portfolio_type import PortfolioType
from utils.portfolio import Portfolio


class TestInvestorEdgeCases(unittest.TestCase):

    def setUp(self):
        """ Setup for edge cases tests """
        self.starting_cash = 10000
        self.investment_ratio = 0.5
        self.investor = Investor(self.starting_cash, self.investment_ratio)

        # Mock Stock objects
        self.winner_stock = Mock()
        self.loser_stock = Mock()
        self.winner_stock.get_ticker_code.return_value = 'WIN'
        self.winner_stock.get_price.return_value = 100
        self.loser_stock.get_ticker_code.return_value = 'LOS'
        self.loser_stock.get_price.return_value = 50

    def test_create_position_empty_collections(self):
        """ Test create_position with empty winners and losers collections """
        winners = []
        losers = []
        date = datetime.now()

        # Should handle gracefully without error
        self.investor.create_position(winners, losers, date)

        # No portfolios should be created
        self.assertEqual(len(self.investor.get_long_portfolios()), 0)
        self.assertEqual(len(self.investor.get_short_portfolios()), 0)

    def test_negative_cash_values(self):
        """ Test behavior when cash goes negative """
        self.investor._Investor__cash = -100  # Force negative cash

        # Should still be able to create positions but reflect in cash balance
        winners = [self.winner_stock]
        losers = [self.loser_stock]
        date = datetime.now()

        self.investor.create_position(winners, losers, date)
        self.assertTrue(self.investor.get_cash() < 0)

    def test_zero_or_negative_stock_price(self):
        """ Test adding stocks with zero or negative price """
        self.winner_stock.get_price.return_value = 0
        self.loser_stock.get_price.return_value = -50

        # Portfolio creation should handle these cases properly
        portfolio_long = Portfolio(datetime.now(), PortfolioType.LONG)
        portfolio_short = Portfolio(datetime.now(), PortfolioType.SHORT)

        # Handle zero price
        with self.assertRaises(ZeroDivisionError):
            self.investor.add_to_portfolio(self.winner_stock, 1000, portfolio_long)

        # Handle negative price
        with self.assertRaises(ValueError):
            self.investor.add_to_portfolio(self.loser_stock, 1000, portfolio_short)

    def test_zero_investment_ratio(self):
        """ Test with zero investment ratio """
        investor_zero_ratio = Investor(self.starting_cash, 0)
        winners = [self.winner_stock]
        losers = [self.loser_stock]
        date = datetime.now()

        investor_zero_ratio.create_position(winners, losers, date)

        # Should not invest any cash
        self.assertEqual(investor_zero_ratio.get_cash(), self.starting_cash)

    def test_empty_portfolios_on_settle(self):
        """ Test settlement with empty portfolios """
        current_stocks = pd.Series({'WIN': 120, 'LOS': 40})

        # No portfolios created, but settle_position is called
        with self.assertRaises(KeyError):
            self.investor.settle_position(datetime.now(), current_stocks, K=1)

    def test_date_mismatch_on_settle(self):
        """ Test settling position with a date mismatch """
        winners = [self.winner_stock]
        losers = [self.loser_stock]
        date = datetime.now()

        # Create a position today
        self.investor.create_position(winners, losers, date)

        current_stocks = pd.Series({'WIN': 120, 'LOS': 40})
        future_date = date + DateOffset(months=2)

        # Attempt to settle a position from 2 months in the future
        with self.assertRaises(KeyError):
            self.investor.settle_position(future_date, current_stocks, 1)

    def test_non_numeric_cash_values(self):
        """ Test with non-numeric cash values """
        # Manually setting non-numeric cash value
        self.investor._Investor__cash = "invalid_cash_value"

        # Check if cash tracker raises error for non-numeric cash
        with self.assertRaises(TypeError):
            self.investor.update_cash_tracker()

    def test_future_date_for_position(self):
        """ Test creating a position with a future date """
        winners = [self.winner_stock]
        losers = [self.loser_stock]
        future_date = datetime.now() + DateOffset(months=1)

        # Should handle future dates, but portfolios will be created for that date
        self.investor.create_position(winners, losers, future_date)

        # Ensure future portfolio is created
        self.assertIn(future_date, self.investor.get_long_portfolios())
        self.assertIn(future_date, self.investor.get_short_portfolios())
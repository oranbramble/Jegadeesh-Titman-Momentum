import unittest
from unittest.mock import Mock
from datetime import datetime
import pandas as pd
from pandas.tseries.offsets import DateOffset
from src.strategy.investor import Investor
from utils.portfolio_type import PortfolioType


class TestInvestor(unittest.TestCase):

    def setUp(self):
        """ Setup for all tests """
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

        # Mock Portfolio object
        self.portfolio_mock = Mock()

    def test_initial_cash(self):
        """ Test initial cash after initialization """
        self.assertEqual(self.investor.get_cash(), self.starting_cash)

    def test_investment_ratio(self):
        """ Test initial investment ratio """
        self.assertEqual(self.investor.get_investment_ratio(), self.investment_ratio)

    def test_create_position(self):
        """ Test creating long and short positions """
        winners = [self.winner_stock]
        losers = [self.loser_stock]
        date = datetime.now()

        self.investor.create_position(winners, losers, date)
        self.assertIn(date, self.investor.get_long_portfolios())
        self.assertIn(date, self.investor.get_short_portfolios())

        long_portfolio = self.investor.get_long_portfolios()[date].get_stocks()
        short_portfolio = self.investor.get_short_portfolios()[date].get_stocks()

        self.assertIn('WIN', long_portfolio)
        self.assertIn('LOS', short_portfolio)

    def test_add_to_portfolio_long(self):
        """ Test adding stock to long portfolio """
        portfolio = {}
        self.investor.add_to_portfolio(self.winner_stock, 1000, PortfolioType.LONG, portfolio)
        self.assertIn('WIN', portfolio)

    def test_add_to_portfolio_short(self):
        """ Test adding stock to short portfolio """
        portfolio = {}
        self.investor.add_to_portfolio(self.loser_stock, 500, PortfolioType.SHORT, portfolio)
        self.assertIn('LOS', portfolio)

    def test_settle_long_and_short(self):
        """ Test settling long and short positions """
        portfolio_l = Mock()
        portfolio_s = Mock()
        portfolio_l.get_stocks.return_value = {'WIN': 10}
        portfolio_s.get_stocks.return_value = {'LOS': 20}
        current_stocks = pd.Series({'WIN': 120, 'LOS': 40})

        initial_cash = self.investor.get_cash()
        self.investor.settle_long_and_short(portfolio_l, portfolio_s, current_stocks)

        # Expect 10 shares of WIN to increase by 20 (120 - 100), total gain = 200
        # Expect 20 shares of LOS to decrease by 10 (50 - 40), total gain = 200
        expected_cash = initial_cash + (10 * 120) - (20 * 40)
        self.assertEqual(self.investor.get_cash(), expected_cash)

    def test_settle_position(self):
        """ Test settling position after K months """
        print("BEGIN")
        winners = [self.winner_stock]
        losers = [self.loser_stock]
        date = datetime.now()

        # Create a position K months ago
        self.investor.create_position(winners, losers, date - DateOffset(months=1))

        current_stocks = pd.Series({'WIN': 120, 'LOS': 40})
        current_date = date

        initial_cash = self.investor.get_cash()
        self.investor.settle_position(current_date, current_stocks, 1)

        # Ensure portfolio is settled and cash is updated correctly
        expected_cash = initial_cash + (25 * 120) - (50 * 40)
        self.assertEqual(self.investor.get_cash(), expected_cash)

    def test_get_stock_amount(self):
        """ Test stock amount calculation """
        stock_amount, cash_left_over = self.investor.get_stock_amount(1000, 100)
        self.assertEqual(stock_amount, 10)
        self.assertAlmostEqual(cash_left_over, 0)

    def test_fill_cash_tracker(self):
        """ Test cash tracker filling """
        self.investor.fill_cash_tracker(5)
        self.assertEqual(len(self.investor.get_cash_tally()), 5)
        self.assertTrue(all(cash == self.starting_cash for cash in self.investor.get_cash_tally()))

    def test_update_cash_tracker(self):
        """ Test updating cash tracker """
        self.investor.update_cash_tracker()
        self.assertEqual(len(self.investor.get_cash_tally()), 1)
        self.assertEqual(self.investor.get_cash_tally()[0], self.starting_cash)

    def test_update_cash_tracker_invalid(self):
        """ Test update cash tracker with invalid cash value """
        self.investor._Investor__cash = 'invalid'
        with self.assertRaises(TypeError):
            self.investor.update_cash_tracker()


if __name__ == '__main__':
    unittest.main()
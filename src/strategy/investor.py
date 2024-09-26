from enum import Enum
from typing import Collection, Tuple
from datetime import datetime
import pandas as pd
from pandas.tseries.offsets import DateOffset

from utils.stock import Stock
from utils.portfolio import Portfolio
from utils.portfolio_type import PortfolioType

class Investor:

    def __init__(self, starting_cash, investment_ratio):
        self.__cash = starting_cash
        self.__investment_ratio = investment_ratio
        self.__cash_tracker = []
        self.__portfolios_short = {}
        self.__portfolios_long = {}


    """ CREATING POSITION """


    def create_position(self, winners: Collection[Stock], losers: Collection[Stock], date: datetime):
        # Cash to invest per stock, assuming equally weighted portfolios
        cash_per_stock = (self.__cash * self.__investment_ratio) / (len(winners) + len(losers))
        # Portfolio for long and short stocks
        portfolio_l = {}
        portfolio_s = {}
        for short_stock, long_stock in zip(losers, winners):
            # Add stock to long portfolio
            self.add_to_portfolio(long_stock, cash_per_stock, PortfolioType.LONG, portfolio_l)
            # Add stock to short portfolio
            self.add_to_portfolio(short_stock, cash_per_stock, PortfolioType.SHORT, portfolio_s)
        # Saves portfolios for when we settle the position in K months
        self.__portfolios_short[date] = Portfolio(portfolio_s, date)
        self.__portfolios_long[date] = Portfolio(portfolio_l, date)

    def add_to_portfolio(self, stock: Stock, cash_per_stock: float, portfolio_type: PortfolioType, portfolio: dict):
        ticker_code = stock.get_ticker_code()
        price = stock.get_price()
        stock_amount, cash_left_over = self.get_stock_amount(cash_per_stock, price)

        if portfolio_type == PortfolioType.LONG:
            self.__cash = self.__cash - (cash_per_stock - cash_left_over)
        else:
            self.__cash = self.__cash + (cash_per_stock - cash_left_over)

        portfolio[ticker_code] = stock_amount
        return portfolio


    """ SETTLING POSITION """


    def settle_long_and_short(self, portfolio_l: Portfolio, portfolio_s: Portfolio, current_stocks: pd.Series):
        """
        Method to settle the long and shorted positions from K months ago
        :param portfolio_l:
        :param portfolio_s:
        :param current_stocks:
        :return:
        """
        stocks_s, stocks_l = portfolio_s.get_stocks(), portfolio_l.get_stocks()
        for stock_s, stock_l in zip(stocks_s.keys(), stocks_l.keys()):
            current_price_s = current_stocks[stock_s]
            current_price_l = current_stocks[stock_l]
            self.__cash += current_price_l * stocks_l[stock_l]
            self.__cash -= current_price_s * stocks_s[stock_s]

    def settle_position(self, current_date: datetime, current_stocks: pd.Series, K: int):
        """
        Method to settle the position from K months ago
        :param current_date:
        :param current_stocks:
        :param K:
        :return:
        """
        K_date = current_date - DateOffset(months=K)
        try:
            portfolio_longed = self.__portfolios_long[K_date]
            portfolio_shorted = self.__portfolios_short[K_date]

            self.settle_long_and_short(portfolio_longed, portfolio_shorted, current_stocks)
        except KeyError:
            print("WARNING: Date not found in portfolios")
            self.__cash_tracker.append(self.__cash)

    def fill_cash_tracker(self, end_index):
        """
        Method for when bankrupt. Fills the rest of the cash tracker with final cash value
        :param end_index: End index we want to fill to
        """
        size_to_fill = end_index - len(self.__cash_tracker)
        self.__cash_tracker += [self.__cash for x in range(size_to_fill)]

    def update_cash_tracker(self):
        self.__cash_tracker.append(self.__cash)

    def get_cash_tally(self) -> Collection[float]:
        return self.__cash_tracker

    def get_cash(self) -> float:
        return self.__cash

    def get_plotting_data(self) -> Tuple[float, Collection[pd.Timestamp]]:
        return self.__cash, self.__cash_tracker

    def get_investment_ratio(self) -> float:
        return self.__investment_ratio

    @staticmethod
    def get_stock_amount(cash_per_stock: float, price: float) -> Tuple[float, float]:
        """
        Method
        :param cash_per_stock:
        :param price:
        :return:
        """
        amount_of_stock = cash_per_stock // price
        cash_left_over = ((cash_per_stock / price) - amount_of_stock) * price
        return amount_of_stock, cash_left_over


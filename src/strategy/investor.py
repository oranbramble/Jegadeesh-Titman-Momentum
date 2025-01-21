from enum import Enum
from typing import Collection, Tuple
from copy import deepcopy
from datetime import datetime
import pandas as pd
from pandas.tseries.offsets import DateOffset

from utils.stock import Stock
from utils.portfolio import Portfolio
from utils.portfolio_type import PortfolioType

class Investor:
    """
    Class to manage cash and positions created from Strategy. Handles creation of winner and loser portfolios, as well
    as settling of long and short portfolios (after K months). Tracks the cash to assess profitability of strategy.
    """

    def __init__(self, starting_cash: float, investment_ratio: float):
        self.__cash = starting_cash
        self.__investment_ratio = investment_ratio
        self.__cash_tracker = []
        self.__position_tracker = []
        self.__portfolios_short = {}
        self.__portfolios_long = {}


    """ CREATING POSITION """


    def create_position(self, winners: Collection[Stock], losers: Collection[Stock], date: datetime):
        """
        Creates long and short portfolios out of winner and loser stocks respectively. Assumes equal weight for
        each security across both portfolios. Includes updating of cash to simulate longing and shorting of stock

        Parameters:
            - winners (list[Stock]): List of Stock objects to create winner portfolio from
            - losers (list[Stock]): List of Stock objects to create loser portfolio from
        """
        # Check we have portfolios to create a position with
        if len(winners) + len(losers) > 0:
            # Make list of stocks same length so that 'zip' works correctly later
            losers, winners = self.correct_portfolio_length(losers, winners)
            # Cash to invest per stock, assuming equally weighted portfolios
            cash_per_stock = (self.__cash * self.__investment_ratio) / (len(winners) + len(losers))
            # Creates portfolios for long and short stocks
            portfolio_l = Portfolio(date, PortfolioType.LONG)
            portfolio_s = Portfolio(date, PortfolioType.SHORT)

            for short_stock, long_stock in zip(losers, winners):
                # Add stock to long portfolio
                self.add_to_portfolio(long_stock, cash_per_stock, portfolio_l)
                # Add stock to short portfolio
                self.add_to_portfolio(short_stock, cash_per_stock, portfolio_s)
            # Saves portfolios for when we settle the position in K months
            self.__portfolios_short[date] = portfolio_s
            self.__portfolios_long[date] = portfolio_l

    def add_to_portfolio(self, stock: Stock, cash_per_stock: float, portfolio: Portfolio):
        """
        Adds a stock to portfolio. Works out how much stock to short/long and updates cash amount to simulate
        longing/shorting. Adds stock and amount of stock to portfolio.

        Parameters:
            - stock (Stock): Stock object to add to portfolio
            - cash_per_stock (float): Cash available to buy/long stock with
            - portfolio (Portfolio): Portfolio to add stock to

        Returns:
            - Portfolio: The updated portfolio object with the new stock added.

        """
        if isinstance(stock, Stock) and isinstance(portfolio, Portfolio) and cash_per_stock > 0:
            # Stock works out how much of stock is shorted/longed, and returns total cash spent
            cash_spent = stock.calculate_amount(cash_per_stock)
            if portfolio.get_type() == PortfolioType.LONG:
                # If longing, subtract cash spent because we buy security
                self.__cash = self.__cash - cash_spent
            else:
                # If shorting, add cash spent because we borrow security and sell immediately
                self.__cash = self.__cash + cash_spent
            portfolio.add_stock(stock)



    """ SETTLING POSITION """


    def settle_long_and_short(self, portfolio_l: Portfolio, portfolio_s: Portfolio, current_stocks: pd.Series):
        """
        Method to settle the longed and shorted portfolios

        Parameters:
            - portfolio_l (Portfolio): The longed portfolio to settle
            - portfolio_s (Portfolio): The shorted portfolio to settle
            - current_stocks (pd.Series): Series object containing current price of the stocks
        """
        # Gets the long and short portfolio's stocks and makes the lists equal length so that 'zip' works correctly
        stocks_s, stocks_l = portfolio_s.get_stocks(), portfolio_l.get_stocks()
        stocks_s, stocks_l = self.correct_portfolio_length(stocks_s, stocks_l)
        for s, l in zip(stocks_s, stocks_l):
            # Gets the price of the stocks in the current month
            current_price_s = current_stocks[str(s)]
            current_price_l = current_stocks[str(l)]
            prev_cash1 = deepcopy(self.__cash)
            # Buys back shorted stock
            # TODO: Implement transaction costs
            self.__cash -= current_price_s * s.get_amount()
            jump1 = ((self.__cash - prev_cash1) / prev_cash1)
            prev_cash2 = deepcopy(self.__cash)
            # Sells longed stock
            self.__cash += current_price_l * l.get_amount()
            jump2 = ((self.__cash - prev_cash2) / prev_cash2)

            if abs(jump1) > 0.15:
                print("JUMPED")
                print(f"Cash: {prev_cash1}, {self.__cash}")
                print(f"Short {str(s)}: {s.get_price()}, {current_price_s}, {s.get_amount()}")
            if abs(jump2) > 0.15:
                print("JUMPED")
                print(f"Cash: {prev_cash2}, {self.__cash}")
                print(f"Long {str(l)}: {l.get_price()}, {current_price_l} {l.get_amount()}")




    def settle_position(self, current_date: datetime, current_stocks: pd.Series, K: int):
        """
        Method to settle the position from K months ago

        Parameters:
            - current_data (datetime): Current date
            - current_stocks (pd.Series): Series containing the current price of the stocks
            - K (int): Look-back period, used to retrieve portfolios from K months ago to settle them
        """
        # Date from K months ago
        K_date = current_date - DateOffset(months=K)
        try:
            # Gets long and short portfolios from K months ago
            portfolio_longed = self.__portfolios_long[K_date]
            portfolio_shorted = self.__portfolios_short[K_date]
            # Settles portfolios
            self.settle_long_and_short(portfolio_longed, portfolio_shorted, current_stocks)
        except KeyError:
            raise KeyError(f"No portfolio's found for date {K_date} with current date {current_date}")



    """ UPDATING CASH TRACKER """



    def fill_cash_tracker(self, end_index):
        """
        Method for when bankrupt. Fills the rest of the cash tracker with final cash value
        :param end_index: End index we want to fill to
        """
        size_to_fill = end_index - len(self.__cash_tracker)
        self.__cash_tracker += [self.__cash for x in range(size_to_fill)]

    def update_trackers(self, current_stocks: pd.Series):
        if isinstance(self.__cash, float) or isinstance(self.__cash, int):
            self.__cash_tracker.append(self.__cash)
        else:
            raise TypeError("Unexpected type in cash")

        portfolios_position = 0
        for portfolio in self.__portfolios_long.values():
            portfolios_position += portfolio.get_value(current_stocks)
        for portfolio in self.__portfolios_short.values():
            portfolios_position -= portfolio.get_value(current_stocks)
        self.__position_tracker.append(portfolios_position)



    """ GETTERS """



    def get_cash_tally(self) -> Collection[float]:
        return self.__cash_tracker

    def get_cash(self) -> float:
        return self.__cash

    def get_cash_data(self) -> Tuple[float, Collection[pd.Timestamp]]:
        return self.__cash, self.__cash_tracker

    def get_position_tally(self) -> Collection[float]:
        return self.__position_tracker

    def get_investment_ratio(self) -> float:
        return self.__investment_ratio

    def get_long_portfolios(self) -> dict:
        return self.__portfolios_long

    def get_short_portfolios(self) -> dict:
        return self.__portfolios_short



    """ STATIC HELPERS """


    @staticmethod
    def correct_portfolio_length( p1: Collection[Stock], p2: Collection[Stock]) -> Collection[Stock]:
        if len(p1) < len(p2):
            p1 = p1 + [None for x in range(len(p2) - len(p1))]
        elif len(p1) > len(p2):
            p2 = p2 + [None for x in range(len(p1) - len(p2))]
        return p1, p2




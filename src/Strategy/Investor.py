from typing import Collection, Tuple
from datetime import datetime
import pandas as pd
from pandas.tseries.offsets import DateOffset
from Strategy.Stock import Stock
from Strategy.Portfolio import Portfolio

class Investor:

    def __init__(self, starting_cash, investment_ratio):
        self.__cash = starting_cash
        self.__investment_ratio = investment_ratio
        self.__cash_tracker = []
        self.__date_tracker = []
        self.__portfolios_short = {}
        self.__portfolios_long = {}


    def get_stock_amount(self, cash_per_stock: float, price: float) -> Tuple[float, float]:
        """
        Method
        :param cash_per_stock:
        :param price:
        :return:
        """
        amount_of_stock = cash_per_stock // price
        cash_left_over = ((cash_per_stock / price) - amount_of_stock) * price

        return amount_of_stock, cash_left_over


    def long_and_short(self, winners: Collection[Stock], losers: Collection[Stock], date: datetime):
        """
        Method to long and short the stocks in the winner and loser portfolios
        :param winners:
        :param losers:
        :param date:
        :return:
        """
        # Cash to invest per stock, assuming equally weighted portfolios
        cash_per_stock = (self.__cash * self.__investment_ratio) / (len(winners) + len(losers))
        # Portfolio for long and short stocks
        portfolio_l = {}
        portfolio_s = {}
        for short_stock, long_stock in zip(losers, winners):
            ticker_code_s, ticker_code_l = short_stock.get_ticker_code(), long_stock.get_ticker_code()
            price_s, price_l = short_stock.get_price(), long_stock.get_price()

            amount_of_stock_s, cash_left_over_s = self.get_stock_amount(cash_per_stock, price_s)
            # Adjust cash, adding amount gained from shorting stock
            self.__cash = self.__cash + (cash_per_stock - cash_left_over_s)

            amount_of_stock_l, cash_left_over_l = self.get_stock_amount(cash_per_stock, price_l)
            # Adjust cash, removing amount spent on longing stock
            self.__cash = self.__cash - (cash_per_stock - cash_left_over_l)

            # Add long and short stocks to portfolio
            portfolio_s[ticker_code_s] = amount_of_stock_s
            portfolio_l[ticker_code_l] = amount_of_stock_l
        # Saves portfolios for when we settle the position in K months
        self.__portfolios_short[date] = Portfolio(portfolio_s, date)
        self.__portfolios_long[date] = Portfolio(portfolio_l, date)


    def settle_short_and_long(self, portfolio_l: Portfolio, portfolio_s: Portfolio, current_stocks: pd.Series):
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
        Method to settle the postion from K months ago
        :param current_date:
        :param current_stocks:
        :param K:
        :return:
        """
        K_date = current_date - DateOffset(months=K)
        try:
            portfolio_longed = self.__portfolios_long[K_date]
            portfolio_shorted = self.__portfolios_short[K_date]

            self.settle_short_and_long(portfolio_longed, portfolio_shorted, current_stocks)
            self.__cash_tracker.append(self.__cash)
        except KeyError:
            print("WARNING: Date not found in portfolios")
            self.__cash_tracker.append(self.__cash)

        self.__date_tracker.append(current_date.strftime("%m/%Y"))

    def update_trackers(self, date):
        self.__cash_tracker.append(self.__cash)
        self.__date_tracker.append(str(date))

    def output_state(self):
        print(f"Current Cash : {self.__cash_tracker[-1]}")
        print(f"Current Date : {self.__date_tracker[-1]}")

    def get_cash(self):
        return self.__cash

    def get_plotting_data(self):
        return self.__cash, self.__cash_tracker, self.__date_tracker
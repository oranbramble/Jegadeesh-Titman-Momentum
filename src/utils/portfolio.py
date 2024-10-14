from typing import Collection
from datetime import datetime
import logging

from utils.portfolio_type import PortfolioType
from utils.stock import Stock

class Portfolio:
    """
    Portfolio class to hold Stock objects and a date of when it is formed

    A new Portfolio is created when stocks are longed/shorted at the start of each month. They are then settled
    after K months.

    Parameters:
        - stocks (list[Stock]): List of Stock objects forming the Portfolio
        - date (datetime): Date when Portfolio is created
    """

    def __init__(self, date: datetime, type: PortfolioType):
        self.__stocks = []
        self.__date_created = date
        self.__type = type

    def __len__(self) -> int:
        return len(self.__stocks)

    def get_value(self, current_stock_prices):
        value = 0
        original_value = 0
        for stock in self.__stocks:
            value += current_stock_prices[stock.get_ticker_code()] * stock.get_amount()
            original_value += stock.get_price() * stock.get_amount()
        if self.__type == PortfolioType.LONG:
            return value
        else:
            difference = original_value - value
            return difference

    def add_stock(self, stock: Stock):
        self.__stocks.append(stock)

    def get_stocks(self) -> Collection[Stock]:
        return self.__stocks

    def get_date(self) -> datetime:
        return self.__date_created

    def get_type(self) -> PortfolioType:
        return self.__type

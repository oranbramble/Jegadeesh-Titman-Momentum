from typing import Collection
from datetime import datetime

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

    def __init__(self, stocks: Collection[Stock], date: datetime):
        self.__stocks = stocks
        self.__date_created = date

    def get_stocks(self):
        return self.__stocks

    def get_date(self):
        return self.__date_created
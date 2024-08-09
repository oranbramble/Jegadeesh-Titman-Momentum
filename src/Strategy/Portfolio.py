from datetime import datetime

class Portfolio:

    def __init__(self, stocks, date):
        self.__stocks = stocks
        self.__date_created = date

    def get_stocks(self):
        return self.__stocks

    def get_date(self):
        return self.__date_created
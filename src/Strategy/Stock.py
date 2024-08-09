class Stock:

    def __init__(self, ticker_code: str, average_J_returns: float,  price: float):
        self.__ticker_code = ticker_code
        self.__J_returns = average_J_returns
        self.__price = price

    def __lt__(self, obj):
        return self.__J_returns < obj.get_J_returns()

    def __gt__(self, obj):
        return self.__J_returns > obj.get_J_returns()

    def __le__(self, obj):
        return self.__J_returns <= obj.get_J_returns()

    def __ge__(self, obj):
        return self.__J_returns >= obj.get_J_returns()

    def __eq__(self, obj):
        return self.__J_returns == obj.get_J_returns()

    def __str__(self):
        return self.__ticker_code

    def get_ticker_code(self):
        return self.__ticker_code

    def get_price(self):
        return self.__price

    def get_J_returns(self):
        return self.__J_returns


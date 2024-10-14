class Stock:
    """
    Stock class which enables easy comparison of average stock returns over last J months for strategy
    It is also used to hold stock price of when stock is longed/shorted

    Parameters:
        - ticker_code (str): Ticker code for the stock
        - average_J_returns (float): Average returns over the last J months
        - price (float): Current price of stock when objet is created
    """

    def __init__(self, ticker_code: str, average_J_returns: float,  price: float):
        self.__ticker_code = ticker_code
        self.__J_returns = average_J_returns
        if price > 0:
            self.__price = price
        else:
            raise ValueError(f"Price less than 0 for Stock {ticker_code}")
        self.__amount = 0

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

    def set_amount(self, amount):
        self.__amount = amount

    def calculate_amount(self, cash_per_stock: float) -> float:
        """
        Method
        :param cash_per_stock:
        :param price:
        :return:
        """
        if cash_per_stock > 0:

            self.__amount = cash_per_stock // self.__price
            cash_left_over = ((cash_per_stock / self.__price) - self.__amount) * self.__price
            cash_spent = cash_per_stock - cash_left_over
          #  if (self.__amount > 100):
               # print(self.__amount, self.__price, cash_per_stock, cash_left_over, cash_spent)
            return cash_spent
        return 0

    def get_ticker_code(self):
        return self.__ticker_code

    def get_price(self):
        return self.__price

    def get_J_returns(self):
        return self.__J_returns

    def get_amount(self):
        return self.__amount


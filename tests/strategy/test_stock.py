from unittest import TestCase
from utils.stock import Stock

class StockTest(TestCase):

    def setUp(self):
        self.stock1 = Stock("high", 10, 10)
        self.stock2 = Stock("med", 5, 5)
        self.stock3 = Stock("low", 1, 1)
        self.stocks = [self.stock1, self.stock2, self.stock3]

        self.stock4 = Stock("equal1", 7, 7)
        self.stock5 = Stock("equal2", 7, 7)
        self.stock6 = Stock("equal3", 7, 7)
        self.stocks_equal = [self.stock4, self.stock5, self.stock6]

    def test_sorted(self):
        assert sorted(self.stocks) == [self.stock3, self.stock2, self.stock1]
        assert sorted(self.stocks, reverse=True) == [self.stock1, self.stock2, self.stock3]

    def test_sorted_edge(self):
        assert sorted(self.stocks_equal) == [self.stock4, self.stock5, self.stock6]
        assert sorted(self.stocks_equal, reverse=True) == [self.stock6, self.stock5, self.stock4]
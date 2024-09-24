from unittest import TestCase
import unittest
import pandas as pd
import json
from src.Strategy.JKStrategy import JKStrategy


class JKStrategyTest(TestCase):

    def setUp(self):
        self.df = pd.read_csv("Data/dummy_data.csv")
        self.df['Date'] = pd.to_datetime(self.df['Date'], format="%d/%m/%Y")

        with open("Data/code_to_currency_test.json", "r") as f:
            self.code_to_currency = json.load(f)



    """ TESTING `get_stock_data()` METHOD """



    def test_get_stock_data(self):
        returns_column = "AReturns"
        s = JKStrategy(J=1)
        
        # Test 1: Testing with NaN values in first and last row
        for i, row in self.df.iterrows():
            ticker_code, average_J_returns, adj_close = s.get_stock_data(returns_column, self.df, row)
            assert ticker_code == "A"
            # Returns over all the months are always 'None' because NaN values exist
            assert average_J_returns is None
            # Testing the adjusted close values are correct to what is in the data
            if i == 5:
                # Last row is NaN for adjusted close values, so verifying return is null
                assert pd.isnull(adj_close)
            else:
                expected_value = self.df.iloc[i][ticker_code]
                assert adj_close == expected_value

        # Test 2: Testing without NaN values in first and last row
        temp_df = self.df.iloc[1:5]
        for i, row in temp_df.iterrows():
            ticker_code, average_J_returns, adj_close = s.get_stock_data(returns_column, temp_df, row)
            assert ticker_code == "A"
            # Returns now 0.02 considering all months of dummy data without NaN values
            assert average_J_returns == 0.02
            # Testing the adjusted close values are correct to what is in the data
            if i == 5:
                # Last row is NaN for adjusted close values, so verifying return is null
                assert pd.isnull(adj_close)
            else:
                expected_value = self.df.iloc[i][ticker_code]
                assert adj_close == expected_value



    """ TESTING `rank_stocks()` METHOD """



    def test_rank_stocks_J_1(self):
        """
        Testing the rank_stocks method of JKStrategy using a J parameter of 1
        """
        J = 1
        s = JKStrategy(J=J)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            ranked_stocks = [str(s) for s in ranked_stocks]
            if i < J + 1:
                # While i less than J plus one, because we discount the first row as the first row has no returns,
                # there should be no stocks returned
                assert ranked_stocks == []
            elif i == 2:
                assert ranked_stocks == ['B', 'C', 'A', 'D', 'E']
            elif i == 3:
                assert ranked_stocks == ['B', 'C', 'E', 'A', 'D']
            elif i == 4:
                assert ranked_stocks == ['C', 'E', 'A', 'B', 'D']
            elif i == 5:
                # Last row there are no adjusted close values, only returns, so no stocks should be returned
                assert ranked_stocks == []


    def test_rank_stocks_J_3(self):
        """
        Testing the rank_stocks method of JKStrategy using a J parameter of 3, which should be the maximum J value
        where stocks are returned
        """
        J = 3
        s = JKStrategy(J=J)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            ranked_stocks = [str(s) for s in ranked_stocks]
            if i < J + 1:
                # While i less than J plus one, because we discount the first row as the first row has no returns,
                # there should be no stocks returned
                assert ranked_stocks == []
            elif i == 4:
                assert ranked_stocks == ['C', 'B', 'E', 'A', 'D']
            elif i == 5:
                # Last row there are no adjusted close values, only returns, so no stocks should be returned
                assert ranked_stocks == []

    def test_rank_stocks_J_4(self):
        """
        Testing the rank_stocks method of JKStrategy using a J parameter of 4, which is the number of months with
        returns data
        """
        J = 4
        s = JKStrategy(J=J)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            # Will never return stocks, as the last J months will always include a NaN value, or we get to the final
            # month which has NaN values in its adjusted returns column, so nothing is returned
            assert ranked_stocks == []


    def test_rank_stocks_J_10(self):
        """
        Testing the rank_stocks method of JKStrategy using a J parameter of 10, which is larger than the number of
        months, so no stocks should be returned
        """
        J = 10
        s = JKStrategy(J=J)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            assert ranked_stocks == []

    def test_rank_stocks_J_negative(self):
        """
        Testing the rank_stocks method of JKStrategy using a J parameter of -1
        """
        J = -1
        s = JKStrategy(J=J)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            assert ranked_stocks == []



    """ TESTING 'create_stock()' METHOD """



    def test_create_stock(self):
        """
        Testing the create_stock method of JKStrategy with normal data
        """
        stock = JKStrategy.create_stock("TEST", 0.01, 1.0)
        assert stock.get_ticker_code() == 'TEST'
        assert stock.get_J_returns() == 0.01
        assert stock.get_price() == 1.0

    def test_create_stock_incorrect_types(self):
        """
        Testing the create_stock method of JKStrategy with incorrect data types
        :return:
        """
        s1 = JKStrategy.create_stock(10, "t", True)
        s2 = JKStrategy.create_stock(True, 0, 0)
        s3 = JKStrategy.create_stock("TEST", "None", 0)
        s4 = JKStrategy.create_stock("TEST", 0, True)
        lst = [s1, s2, s3, s4]

        for s in lst:
            assert not s

    def test_create_stock_erroneous(self):
        """
        Testing the create_stock method of JKStrategy with missing data
        """
        s1 = JKStrategy.create_stock(None, None, None)
        s2 = JKStrategy.create_stock("TEST", 0, None)
        s3 = JKStrategy.create_stock("TEST", None, 0)
        s4 = JKStrategy.create_stock(None, 0, 0)
        s5 = JKStrategy.create_stock("TEST", 0, -1)
        lst = [s1, s2, s3, s4, s5]

        for s in lst:
            assert not s



    """ TESTING 'get_winners_and_losers()' METHOD """



    def test_get_winners_and_losers_J_1(self):
        J = 1
        s = JKStrategy(J)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            winners, losers = JKStrategy.get_winners_and_losers(ranked_stocks)
            winners = [str(w) for w in winners]
            losers = [str(l) for l in losers]

            if i < J + 1:
                # While i less than J plus one, because we discount the first row as the first row has no returns,
                # there should be no stocks returned
                assert not winners and not losers
            elif i == 2:
                # Ranked stocks = ['B', 'C', 'A', 'D', 'E']
                assert winners == ['E'] and losers == ['B']
            elif i == 3:
                # Ranked stocks = ['B', 'C', 'E', 'A', 'D']
                assert winners == ['D'] and losers == ['B']
            elif i == 4:
                # Ranked stocks = ['C', 'E', 'A', 'B', 'D']
                assert winners == ['D'] and losers == ['C']
            elif i == 5:
                assert not winners and not losers

    def test_get_winners_and_losers_J_2(self):
        J = 2
        s = JKStrategy(J)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            winners, losers = JKStrategy.get_winners_and_losers(ranked_stocks)
            winners = [str(w) for w in winners]
            losers = [str(l) for l in losers]
            if i < J + 1:
                # While i less than J plus one, because we discount the first row as the first row has no returns,
                # there should be no stocks returned
                assert not winners and not losers
            elif i == 3:
                # Ranked stocks = ['B', 'C', 'A', 'E', 'D']
                assert winners == ['D'] and losers == ['B']
            elif i == 4:
                # Ranked stocks = ['C', 'B', 'E', 'A', 'D']
                assert winners == ['D'] and losers == ['C']
            elif i == 5:
                assert not winners and not losers


    def test_winners_and_losers_J_10(self):
        J = 10
        s = JKStrategy(J=J)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            winners, losers = JKStrategy.get_winners_and_losers(ranked_stocks)
            assert not winners and not losers

    def test_winners_and_losers_J_negative(self):
        J = -1
        s = JKStrategy(J=J)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            winners, losers = JKStrategy.get_winners_and_losers(ranked_stocks)
            assert not winners and not losers



if __name__ == "__main__":
    unittest.main()

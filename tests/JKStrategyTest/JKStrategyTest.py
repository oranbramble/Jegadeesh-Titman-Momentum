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
        s = JKStrategy(J=1, K=1)
        
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
        # K parameter is unused for this method, so can be any value
        K = -1
        s = JKStrategy(J=J, K=K)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            if i < J + 1:
                # While i less than J plus one, because we discount the first row as the first row has no returns,
                # there should be no stocks returned
                assert ranked_stocks == []
            elif i == 2:
                assert [str(s) for s in ranked_stocks] == ['B', 'C', 'A', 'D', 'E']
            elif i == 3:
                assert [str(s) for s in ranked_stocks] == ['B', 'C', 'E', 'A', 'D']
            elif i == 4:
                assert [str(s) for s in ranked_stocks] == ['C', 'E', 'A', 'B', 'D']
            elif i == 5:
                # Last row there are no adjusted close values, only returns, so no stocks should be returned
                assert ranked_stocks == []


    def test_rank_stocks_J_3(self):
        """
        Testing the rank_stocks method of JKStrategy using a J parameter of 3, which should be the maximum J value
        where stocks are returned
        :return:
        """
        J = 3
        # K parameter is unused for this method, so can be any value
        K = -1
        s = JKStrategy(J=J, K=K)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            if i < J + 1:
                # While i less than J plus one, because we discount the first row as the first row has no returns,
                # there should be no stocks returned
                assert ranked_stocks == []
            elif i == 4:
                assert [str(s) for s in ranked_stocks] == ['C', 'B', 'E', 'A', 'D']
            elif i == 5:
                # Last row there are no adjusted close values, only returns, so no stocks should be returned
                assert ranked_stocks == []

    def test_rank_stocks_J_4(self):
        """
        Testing the rank_stocks method of JKStrategy using a J parameter of 4, which is the number of months with
        returns data
        :return:
        """
        J = 4
        # K parameter is unused for this method, so can be any value
        K = -1
        s = JKStrategy(J=J, K=K)

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
        :return:
        """
        J = 10
        # K parameter is unused for this method, so can be any value
        K = -1
        s = JKStrategy(J=J, K=K)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            assert ranked_stocks == []

    def test_rank_stocks_J_negative(self):
        """
        Testing the rank_stocks method of JKStrategy using a J parameter of -1
        :return:
        """
        J = -1
        # K parameter is unused for this method, so can be any value
        K = -1
        s = JKStrategy(J=J, K=K)

        for i, row in self.df.iterrows():
            t = row['Date']
            ranked_stocks = s.rank_stocks(self.df, t, row, self.code_to_currency)
            assert ranked_stocks == []



    """ TESTING """


if __name__ == "__main__":
    unittest.main()

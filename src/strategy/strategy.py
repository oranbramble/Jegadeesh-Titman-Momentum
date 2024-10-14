import pandas as pd
import logging
from datetime import datetime
from typing import Tuple
from pandas.tseries.offsets import DateOffset

from utils.stock import Stock


class JKStrategy:
    """
    Class to implement the J-month/K-month strategy, as described in Jegadeesh and Titman, 1993. The logic of this is
    summarized below.

    The strategy is focussed on selecting stocks based on their returns over the past J months, and holds them for
    K months before settling the position. At the beginning of a month, t, all stocks are ranked in ascending order of
    returns over the last J months, and split into 10 equal groups (deciles). A portfolio is then formed of each decile,
    with the top labelled as 'losers', and bottom labelled as 'winners'. In each month, t, the strategy longs the
    'winners' and  shorts the 'losers', and holds this for K months. It also closes the position started t-K months
    previously.

    Parameters:
        - J (int): J months (look-back period)
    """

    def __init__(self, J: int):
        # Look-back period
        self.__J = J

    def rank_stocks(self, df: pd.DataFrame, t: datetime, current_month: pd.Series, code_to_currency=None) -> list:
        """
        Ranks stocks in ascending order on returns over the last J months
        :param df: DataFrame containing stock average monthly returns and dates (MM/YYYY)
        :param t: Current month (MM/YYYY)
        :param current_month:
        :param code_to_currency:
        :return:
        """
        # Selects the last J months of returns
        split_df = df[(df['Date'] >= t - DateOffset(months=self.__J)) &
                      (df['Date'] < t)]
        # List of stocks containing data for current price and average returns over last J months
        stocks = []

        # Loops through each 'returns' column, gets the average of stocks returns over last J months, and appends
        # a tuple of the stock and its average J month returns to 'stock_and_returns'
        for col in df.columns:
            if not col == 'Date' and 'Returns' in col:
                # Gets the data required for the stock,
                ticker_code, average_J_returns, price = JKStrategy.get_stock_data(col, split_df, current_month)

                # If the there is a current price of the stock and average returns
                if not pd.isnull(price) and not pd.isnull(average_J_returns):
                    # Creates new Stock object containing data
                    stock = JKStrategy.create_stock(ticker_code, average_J_returns, price)
                    if stock:
                        stocks.append(stock)
                """
                else:
                    print("### FLAG ### NaN found")
                """

                # Flags for any currencies that are not USD
                # TODO: Add code to convert currency here or when reading file
                if code_to_currency:
                    if code_to_currency[ticker_code] != "USD":
                        logging.error("Non-USD Currency found")

        # Orders stocks by returns in ascending order
        ranked_stocks = sorted(stocks)
        return ranked_stocks

    @staticmethod
    def get_stock_data(returns_col: str, last_J_months_df: pd.DataFrame, current_month: pd.Series) -> \
            Tuple[str, float | str | None, float | str]:
        """
        Gets required data about stock to create stock object
        :param returns_col: Returns column name of stock (E.g., ABCReturns, AAPLReturns)
        :param last_J_months_df: DataFrame from the last J months
        :param current_month: Current row of dataframe, which represents the current month
        :return: ticker_code: Ticker code of stock,
                 average_J_returns: Average returns over last J months,
                 price: Current price
        """
        ticker_code = returns_col[:-7]
        adj_close = current_month[ticker_code]
        # Checks if any values in last J months a NaNs, and if they are, set average returns to None, so we can skip
        if pd.isna(last_J_months_df[returns_col]).sum():
            average_J_returns = None
        else:
            average_J_returns = last_J_months_df[returns_col].mean()
        return ticker_code, average_J_returns, adj_close

    @staticmethod
    def create_stock(ticker_code: str, average_J_returns: float, price: float) -> Stock | None:
        """
        Creates and returns a Stock object using arguments

        Parameters:
            - ticker_code (str): Stock ticker code
            - average_J_returns (float): Stock returns over the last J months
            - price (float): Current price of the stock

        Returns:
             - Stock | None: Returns Stock object created, or 'None' if any parameter was missing or invalid
        """
        if ticker_code is not None and average_J_returns is not None and price is not None:
            if isinstance(ticker_code, str) and isinstance(average_J_returns, float) and isinstance(price, float):
                if price >= 0.0:
                    return Stock(ticker_code, average_J_returns, price)
                else:
                    logging.error(f"Price of stock less than 0: {ticker_code} {price}")
            else:
                logging.error("Incorrect type when creating Stock")
        else:
            arg_names = ['ticker_code', 'average_J_returns', 'price']
            logging.error(f"Missing argument(s) when creating Stock: "
                          f"{[arg_names[i] for i,arg in enumerate([ticker_code, average_J_returns, price]) if not arg]}")
        return

    @staticmethod
    def get_winners_and_losers(ranked_stocks: list[Stock]) -> Tuple[list[Stock], list[Stock]]:
        """
        Gets the worst performing decile ('losers') and best performing decile ('winners')
        :param ranked_stocks: Stocks and their average J months of returns in ascending order by their J returns
        :return: 'winners' decile (top 10% performers), and 'losers' decile (bottom 10% decile)
        """
        if ranked_stocks:
            if len(ranked_stocks) < 10:
                return [ranked_stocks[-1]], [ranked_stocks[0]]

            decile_size = len(ranked_stocks) // 10
            losers = ranked_stocks[:decile_size]
            winners = ranked_stocks[-decile_size:]
            return winners, losers
        return [], []


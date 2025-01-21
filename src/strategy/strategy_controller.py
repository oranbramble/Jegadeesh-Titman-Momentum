import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Collection

from strategy import JKStrategy
from investor import Investor


class StrategyController:

    def __init__(self, J: int, K: int, ratio: float, cash, code_to_currency=None):
        self.__strategy = JKStrategy(J=J)
        self.__investor = Investor(starting_cash=cash, investment_ratio=ratio)
        self.__J = J
        self.__K = K
        self.__bankrupt = False

    def plot_cash(self, date_tally: Collection[pd.Timestamp], ax: plt.axes) -> plt.axes:
        cash_tally = self.__investor.get_cash_tally()
        ax.plot(date_tally, cash_tally, label=f"J: {self.__J}, K: {self.__K},"
                                              f" ratio: {self.__investor.get_investment_ratio()}")
        return ax

    def plot_position(self, date_tally: Collection[pd.Timestamp], ax: plt.axes) -> plt.axes:
        position_tally = self.__investor.get_position_tally()
        ax.plot(date_tally, position_tally, label=f"J: {self.__J}, K: {self.__K},"
                                              f" ratio: {self.__investor.get_investment_ratio()}")
        return ax

    def run_month(self, df: pd.DataFrame,  i: int,  t: datetime, row: pd.Series, code_to_currency=None):
        """
        Runs the strategy for one month

        Params:
        :param df:
        :param i:
        :param t:
        :param row:
        :param code_to_currency:
        :return:
        """
        ranked_stocks = self.__strategy.rank_stocks(df, t, row, code_to_currency)
        if ranked_stocks:
            winners, losers = self.__strategy.get_winners_and_losers(ranked_stocks)
            self.__investor.create_position(winners, losers, t)
        if i > self.__J + self.__K:
            self.__investor.settle_position(t, row, self.__K)

    def run(self, df: pd.DataFrame, code_to_currency=None):
        for i, row in df.iterrows():
            i = int(i)
            t = row['Date']
            if i >= self.__J:
                self.run_month(df, i, t, row, code_to_currency)
            self.__investor.update_trackers(row)

            if self.__investor.get_cash() < 0:
                print("#####   BANKRUPT   #####")
                self.__bankrupt = True
                self.__investor.fill_cash_tracker(len(df['Date']))
                break





    def get_bankrupt(self) -> bool:
        return self.__bankrupt

    def get_cash_tally(self) -> Collection[float]:
        return self.__investor.get_cash_tally()

    def get_position_tally(self) -> Collection[float]:
        return self.__investor.get_position_tally()

    def get_cash(self) -> float:
        return self.__investor.get_cash()


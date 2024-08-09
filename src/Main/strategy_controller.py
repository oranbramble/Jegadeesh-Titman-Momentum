import pandas as pd
import matplotlib.pyplot as plt


from Strategy.JKStrategy import JKStrategy
from Strategy.Investor import Investor
from datetime import datetime

class StrategyController:

    def __init__(self, J: int, K: int, df: pd.DataFrame, ratio: float, code_to_currency=None, cash=100000):
        self.__strategy = JKStrategy(J=J, K=K)
        self.__investor = Investor(starting_cash=cash, investment_ratio=ratio)
        self.__J = J
        self.__K = K
        self.__ratio = ratio
        self.__df = df
        self.__code_to_currency = code_to_currency
        self.__bankrupt = False

    def plot(self, ax):
        final_cash, cash_tally, date_tally = self.__investor.get_plotting_data()
        ax.plot(date_tally, cash_tally, label=f"J: {self.__J}, K: {self.__K}, ratio: {self.__ratio}")

        return ax

    def run_month(self, t: datetime, row: pd.Series):
        ranked_stocks = self.__strategy.rank_stocks(self.__df, t, row, self.__code_to_currency)
        if ranked_stocks:
            winners, losers = self.__strategy.get_winners_and_losers(ranked_stocks)
            self.__investor.long_and_short(winners, losers, t)
        self.__investor.settle_position(t, row, self.__K)

    def run(self, ax=None):
        for i, row in self.__df.iterrows():
            if i < self.__J:
                pass
            else:
                t = row['Date']
                self.run_month(t, row)
                self.__investor.update_trackers(t)
                if self.__investor.get_cash() < 0:
                    print("#####   BANKRUPT   #####")
                    self.__bankrupt = True
                    break

        if ax:
            return self.plot(ax)

    def get_bankrupt(self):
        return self.__bankrupt
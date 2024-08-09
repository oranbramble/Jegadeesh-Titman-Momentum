import pandas as pd
import json
import matplotlib.pyplot as plt
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple, Collection
import matplotlib.dates as mdates

from strategy_controller import StrategyController
from grid import Grid

def run(strategy_obj, params=None):
    strategy_obj.run(params)
    return strategy_obj


class Main:
    def __init__(self, data_filepath="../Data/stock_data.csv", currency_filepath="../Data/code_to_currency.json"):
        try:
            with open(currency_filepath, "r") as f:
                self.code_to_currency = json.load(f)
        except FileNotFoundError:
            logging.warning("No stock ticker currency file found, proceeding without")
            self.code_to_currency = {}
        try:
            self.df = pd.read_csv(data_filepath)
            self.df['Date'] = pd.to_datetime(self.df['Date'], format="%Y-%m-%d")
        except FileNotFoundError:
            raise FileNotFoundError("No historical data file found")

    @staticmethod
    def plot_result(strategy_controllers: Collection[StrategyController]):
        for s in strategy_controllers:
            s.plot(plt)

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # Set interval as needed
        plt.xticks(rotation=90)
        plt.legend()
        plt.show()

    @staticmethod
    def output_results(strategy_controllers: Collection[StrategyController]):
        number_of_bankrupt = 0
        for s in strategy_controllers:
            number_of_bankrupt += 1 if s.get_bankrupt() else 0
        bankrupt_percentage = (number_of_bankrupt / len(strategy_controllers)) * 100
        print(f"Percentage of bankrupt runs: {bankrupt_percentage:.2f}%")


    def run_grid_parameters(self, iterations, cash=100000):
        grid = Grid({
            "J": [x for x in range(1, 13)],
            "K": [x for x in range(1, 13)],
            "ratio": [x / 100 for x in range(100)]
        })

        strategy_controllers = []
        futures = []
        with ProcessPoolExecutor() as executor:
            for x in range(iterations):

                J = grid.get_J()
                K = grid.get_K()
                ratio = grid.get_ratio()

                print(f"Run {x + 1} begins!")
                print(f"J: {J}")
                print(f"K: {K}")
                print(f"Investment ratio: {ratio}")

                strategy_controller = StrategyController(J, K, self.df, ratio, self.code_to_currency, cash)
                futures.append(executor.submit(run, strategy_controller))

        for future in futures:
            strategy_controllers.append(future.result())

        Main.output_results(strategy_controllers)

        Main.plot_result(strategy_controllers)


if __name__ == '__main__':
    m = Main()
    m.run_grid_parameters(iterations=10, cash=1000)








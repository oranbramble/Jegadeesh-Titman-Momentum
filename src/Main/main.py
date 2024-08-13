import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple, Collection

from strategy_controller import StrategyController
from grid import Grid


def run(strategy_obj: StrategyController, df: pd.DataFrame, code_to_currency=None):
    strategy_obj.run(df, code_to_currency)
    return strategy_obj


class Main:
    def __init__(self, data_filepath="../Data/stock_data.csv", currency_filepath="../Data/code_to_currency.json"):
        """
        Constructor
        :param data_filepath:
        :param currency_filepath:
        """
        try:
            with open(currency_filepath, "r") as f:
                self.__code_to_currency = json.load(f)
        except FileNotFoundError:
            logging.warning("No stock ticker currency file found, proceeding without")
            self.__code_to_currency = {}
        try:
            self.__df = pd.read_csv(data_filepath)
            self.__df['Date'] = pd.to_datetime(self.__df['Date'], format="%Y-%m-%d")
            self.__dates = self.__df['Date']
        except FileNotFoundError:
            raise FileNotFoundError("No historical data file found")

    def plot_result(self, strategy_controllers: Collection[StrategyController]):
        """
        Plots the results on matplotlib graphs
        :param strategy_controllers: List of all strategy controllers from all runs
        """

        # Split into two graphs
        fig, axes = plt.subplots(nrows=1, ncols=2)
        cash_tallies = self.plot_per_run_graph(strategy_controllers, axes[0])
        self.plot_average_graph(cash_tallies, axes[1])
        plt.show()

    def plot_per_run_graph(self, strategy_controllers: Collection[StrategyController], axes: plt.axes) \
            -> Collection[Collection[float]]:
        # Saves all the cash tallies so they can be averaged
        cash_tallies = []
        for s in strategy_controllers:
            # Plots the cash tally and date tally for each run
            s.plot(self.__dates, axes)
            # Saves the cash tally for averaging
            cash_tallies.append(s.get_cash_tally())

        axes.legend()
        axes.set_title("Cash per run over time")
        axes.set_xlabel("Date")
        axes.set_ylabel("Cash")

        return cash_tallies

    def plot_average_graph(self, cash_tallies: Collection[Collection[float]], axes: plt.axes):
        average_cash_tally = np.average(np.array(cash_tallies), axis=0)
        axes.plot(self.__dates, average_cash_tally)
        axes.set_title("Average cash over time")
        axes.set_xlabel("Date")
        axes.set_ylabel("Cash")

    @staticmethod
    def output_results(strategy_controllers: Collection[StrategyController]):
        """
        Output statistical results to command line
        :param strategy_controllers:
        :return:
        """
        number_of_bankrupt = 0
        average_cash = 0
        for s in strategy_controllers:
            number_of_bankrupt += 1 if s.get_bankrupt() else 0
            average_cash += s.get_cash()
        average_cash /= len(strategy_controllers)
        bankrupt_percentage = (number_of_bankrupt / len(strategy_controllers)) * 100
        print(f"Percentage of bankrupt runs: {bankrupt_percentage:.2f}%")
        print(f"Average Final Cash {average_cash:.2f}")


    def run_grid_parameters(self, iterations, cash=100000):
        """
        Run the strategy using random grid search on parameters
        :param iterations: Number of iterations
        :param cash: Starting cash amount
        """
        # Sets grid of parameters
        grid = Grid({
            "J": [x for x in range(1, 13)],
            "K": [x for x in range(1, 13)],
            "ratio": [x / 100 for x in range(100)]
        })

        strategy_controllers = []
        futures = []
        with ProcessPoolExecutor() as executor:
            for x in range(iterations):

                # Gets parameters from grid
                J = grid.get_J()
                K = grid.get_K()
                ratio = grid.get_ratio()

                print(f"Run {x + 1} begins!")
                print(f"J: {J}")
                print(f"K: {K}")
                print(f"Investment ratio: {ratio}")

                # Runs the grid strategy using multiprocessing to improve efficiency
                strategy_controller = StrategyController(J, K, ratio, cash)
                futures.append(executor.submit(run, strategy_controller, self.__df, self.__code_to_currency))

        # Waits for each branch to execute before continuing
        for future in futures:
            strategy_controllers.append(future.result())

        # Output statistical results to command line
        Main.output_results(strategy_controllers)
        # Plots cash over time and average cash from all runs
        self.plot_result(strategy_controllers)


if __name__ == '__main__':
    m = Main()
    m.run_grid_parameters(iterations=1, cash=100000)








import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import Collection

from strategy_controller import StrategyController
from utils.grid import Grid
from utils.exceptions import InvalidTallyType


def run(strategy_obj: StrategyController, df: pd.DataFrame, code_to_currency=None):
    """
    Method to run strategy, needed for multiprocessing

        Parameters:
            strategy_obj: strategy object to run
            df: DataFrame containing stock data
    :param code_to_currency: Dictionary mapping from ticker code to currency (not necessary)
    :return:
    """
    strategy_obj.run(df, code_to_currency)
    return strategy_obj


class Main:
    """
    Main class that handles running grid search on parameters and threading the backtest

    Parameters:
        - data_filepath:
        - currency_filepath:
    """
    def __init__(self, data_filepath="../data/stock_data.csv", currency_filepath="../data/code_to_currency.json"):

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

    def plot_cash_graphs(self, strategy_controllers: Collection[StrategyController]):
        """
        Plots the cash tallies on matplotlib graphs.
        Shows how the cash level changes using strategy over historical data.
        :param strategy_controllers: List of all strategy controllers from all runs
        """

        # Split into two graphs
        fig, axes = plt.subplots(nrows=1, ncols=2)
        cash_tallies = self.plot_per_run_graph(strategy_controllers, axes[0], 'cash')
        self.plot_average_graph(cash_tallies, axes[1], 'cash')
        plt.show()

    def plot_position_graphs(self, strategy_controllers: Collection[StrategyController]):
        """
        Plots the position tallies on matplotlib graphs.
        Shows how the position value changes using strategy over historical data.
        :param strategy_controllers: List of all strategy controllers from all runs
        """
        # Split into two graphs
        fig, axes = plt.subplots(nrows=1, ncols=2)
        position_tallies = self.plot_per_run_graph(strategy_controllers, axes[0], 'position')
        self.plot_average_graph(position_tallies, axes[1], 'position')
        plt.show()

    def plot_per_run_graph(self, strategy_controllers: Collection[StrategyController], axes: plt.axes,
                           tally_type: str) -> Collection[Collection[float]]:
        """
        Plots lines for each run's cash or position value tally by time on the same graph

        Parameters:
            - strategy_controllers (Collection[StrategyController]): strategy Controllers used for runs
            - axes (plt.axes): Axes to plot on
            - tally_type (str): Either 'cash' or 'position' depending on what you want

        Returns:
            - Collection[Collection[float]]: list of lists, containing every tally from all runs

        Raises:
            - InvalidTallyType: If tally_type is not 'cash' or 'position'
        """

        # Saves all the tallies so they can be averaged
        tallies = []
        for s in strategy_controllers:
            if tally_type == 'cash':
                # Plots the cash tally and date tally for each run
                s.plot_cash(self.__dates, axes)
                # Saves the cash tally for averaging
                tallies.append(s.get_cash_tally())
            elif tally_type == 'position':
                # Plots the position tally and date tally for each run
                s.plot_position(self.__dates, axes)
                # Saves the position tally for averaging
                tallies.append(s.get_position_tally())
            else:
                raise InvalidTallyType(f"Tally type {tally_type} invalid. Must be 'cash' or 'position")

        axes.legend()
        axes.set_title(f"{tally_type} per run over time")
        axes.set_xlabel("Date")
        axes.set_ylabel(f"{tally_type}")

        return tallies

    def plot_average_graph(self, tallies: Collection[Collection[float]], axes: plt.axes, tally_type: str):
        """
        Plots average cash tally from all runs by time

        Parameters:
            - tallies (Collection[Collection[float]]): The tally (Collection[float]) for each run
            - axes (plt.axes): Axes to plot graph on
            - tally_type (str): The type of tally we are plotting ('cash' or 'position'). Only used for titles so
                                no exception thrown if invalid.
        """
        average_tally = np.average(np.array(tallies), axis=0)
        axes.plot(self.__dates, average_tally)
        axes.set_title(f"Average over {tally_type} time")
        axes.set_xlabel("Date")
        axes.set_ylabel(f"{tally_type}")

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
        print(f"Percentage of bankrupt runs: {bankrupt_percentage}%")
        print(f"Average Final Cash {average_cash}")


    def run_grid_parameters(self, iterations, cash):
        """
        Run the strategy using random grid search on parameters
        :param iterations: Number of iterations
        :param cash: Starting cash amount
        """
        # Sets grid of parameters
        grid = Grid({
            "J": [x for x in range(1, 13)],
            "K": [x for x in range(1, 13)],
            "ratio": [x / 100 for x in range(0,20,1)]
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
        self.plot_cash_graphs(strategy_controllers)
        self.plot_position_graphs(strategy_controllers)


if __name__ == '__main__':
    m = Main()
    m.run_grid_parameters(iterations=10, cash=1000)








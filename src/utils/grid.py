import random

class Grid:

    def __init__(self, grid: dict):
        self.__grid = grid

    def get_J(self) -> int:
        return self.__grid["J"][random.randint(0, len(self.__grid["J"]) - 1)]

    def get_K(self) -> int:
        return self.__grid["K"][random.randint(0, len(self.__grid["K"]) - 1)]

    def get_ratio(self) -> float:
        return self.__grid["ratio"][random.randint(0, len(self.__grid["ratio"]) - 1)]
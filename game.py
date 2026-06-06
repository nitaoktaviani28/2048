from __future__ import annotations
import logging
from typing import Literal, NewType, Callable, Dict
from logging import Logger
import textwrap
from enum import Enum
import numpy as np
import os
from board import Board2048, Direction
from engine import Engine2048
from time import sleep

# Ganti easy_logs dengan logging bawaan Python
def get_logger(lvl=10) -> Logger:
    logging.basicConfig(level=lvl)
    return logging.getLogger(__name__)

logger = get_logger(lvl=10)

class Game2048:
    CONTROL_KEYS: Dict[str, Direction] = {
        "w": Direction.UP,
        "s": Direction.DOWN,
        "a": Direction.LEFT,
        "d": Direction.RIGHT,
    }
    GET_MOVE_FUNCTION: Dict[str, Callable[[Game2048], Direction]] = {
        "human": lambda self: self.CONTROL_KEYS[input("Enter direction: ")],
        "ai": lambda self: self.engine.find_best_move(self.board, self.engine_depth),
        "random": lambda self: np.random.choice(
            [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
        ),
    }
    __instance = None

    def __new__(cls, *args, **kwargs):
        if Game2048.__instance is None:
            Game2048.__instance = object.__new__(cls)
        logger.warning("Game2048 is a singleton")
        return Game2048.__instance

    def __init__(self, logger: Logger = None, engine_depth=4) -> None:
        if logger is None:
            logger = get_logger(lvl=10)
        self.engine_depth = engine_depth
        self.board = Board2048(shape=(4, 4))
        self.game_over = False
        self.engine = Engine2048(logger)

    def ai_move(self) -> Board2048:
        direction = self.engine.find_best_move(self.board, self.engine_depth)
        self.board.move(direction)
        return self.board

    def move(self, direction: Direction | Literal["a", "s", "w", "d"]) -> Board2048:
        if isinstance(direction, str):
            direction = self.CONTROL_KEYS[direction]
        self.board.move(direction)
        return self.board

    def play_in_console(
        self,
        sleep_time=0.5,
        player: Literal["human", "ai", "random"] = "human",
    ):
        score = 0
        get_move = self.GET_MOVE_FUNCTION.get(player)
        while score < 2048 and not self.board.is_game_over:
            try:
                direction = get_move(self)
            except KeyError as e:
                logger.warning(f"Invalid direction: {e}")
                continue
            self.board.move(direction)
            os.system("cls")
            print(f"Score: {self.board.score} | Move: {direction}")
            print(self.board)
        score = self.board.score
        self.board.reset()
        sleep(sleep_time)
        print(f"Game over! Score: {score}")

    def __repr__(self) -> str:
        with open("readme.md", "r") as f:
            docstring = f.read()
        docstring = "\n".join(
            line.strip() for line in docstring.split("\n") if "![image]" not in line
        )
        return docstring

if __name__ == "__main__":
    game = Game2048()
    print(game)

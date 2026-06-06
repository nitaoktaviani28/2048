import numpy as np
from miskibin import get_logger
from logging import Logger
from enum import Enum
import os
from copy import deepcopy
from board import Board2048, Direction


class Engine2048:
    """
    Finds the best move for a given board. Follows rules of the game 2048.
    Supported algorithms:
        - minimax
    Future algorithms:
        - Reinforcement Learning
        - Monte Carlo Tree Search
        - Expectimax
    """

    def __init__(self, logger: Logger, board: Board2048 = Board2048()) -> None:
        self.logger = logger
        self.board = board

    def find_best_move(self, board: Board2048, depth=3) -> Direction:
        """
        This function uses the minimax algorithm to find the best move.
        """
        try:
            self.board._board = board._board
        except AttributeError:
            self.logger.error("Board is not a Board2048 object")
            raise AttributeError

        best_score = -1
        best_move = None
        for direction in (
            Direction.UP,
            Direction.DOWN,
            Direction.LEFT,
            Direction.RIGHT,
        ):
            if self.board.move(direction):
                self.board.generate_tile()
                score = self.get_best_score(depth=depth - 1)
                if score > best_score:
                    best_score = score
                    best_move = direction
            self.board._board = board._board
        return best_move

    def get_best_score(self, depth=2) -> int:
        if depth == 0:
            return len(self.board.empty_cells)
        best_score = 0
        for direction in (
            Direction.UP,
            Direction.DOWN,
            Direction.LEFT,
            Direction.RIGHT,
        ):
            old_board = self.board._board.copy()
            if self.board.move(direction):
                self.board.generate_tile()
                score = self.get_best_score(depth - 1)
                if score > best_score:
                    best_score = score
            self.board._board = old_board
        return best_score

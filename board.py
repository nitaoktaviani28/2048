import numpy as np
from easy_logs import get_logger
from logging import Logger
from enum import Enum
import os


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class Board2048:
    """
    ##### Rules
        - The board is a N x M grid (defined by `shape` argument)
        - The game starts with two tiles with values 2 or 4
        - The player can move the board in four directions: up, down, left, right
        - If two tiles with the same value collide while moving, they merge into a new tile
        - The value of the new tile is the sum of the two tiles that collided
        - After each move, a new tile with value 2 or 4 appears on the board
    ##### usage
        ```python
        board = Board2048()
        board.generate_tile()
        board.move(Direction.UP)
        print(board)
        ```
    """

    def __init__(
        self, logger: Logger = get_logger(lvl=10), shape: tuple = (4, 4)
    ) -> None:
        self.logger = logger
        self.shape = shape
        self._board = np.zeros(shape, dtype=np.int16)
        self.generate_tile()
        self.logger.debug(f"Board initialized with shape {shape}")

    @property
    def empty_cells(self) -> tuple:
        cells = np.where(self._board == 0)
        return tuple(zip(cells[0], cells[1]))

    @property
    def score(self) -> int:
        return np.sum(self._board)

    @property
    def is_game_over(self) -> bool:
        if len(self.empty_cells) > 0:
            return False
        old_board = self._board.copy()
        for direction in (Direction.UP, Direction.LEFT):
            if self.move(direction):
                self._board = old_board
                return False
        return True

    def generate_tile(self) -> None:
        if len(self.empty_cells) < 1:
            return False
        number = np.random.choice([2, 4], p=[0.8, 0.2])
        cells = self.empty_cells
        idx = np.random.randint(0, len(cells))
        x, y = cells[idx]
        self._board[x, y] = number

    def reset(self) -> np.ndarray:
        self._board = np.zeros(self.shape, dtype=np.int16)
        self.generate_tile()
        return self._board

    def move(self, direction: Direction, tf=False) -> bool:
        """
        Move the board in the given direction.
        return: True if the board changed, False otherwise
        """
        temp_board = self._board.copy()
        if isinstance(direction, int):
            direction = Direction(direction)
        match direction:
            case Direction.RIGHT:
                self._move(temp_board)
            case Direction.LEFT:
                np.flip(self._move(np.flip(temp_board, axis=1)), axis=1)
            case Direction.UP:
                self._move(temp_board[::-1].T).T[::-1]
            case Direction.DOWN:
                self._move(temp_board.T).T

        if np.array_equal(temp_board, self._board):
            if tf:
                return self._board, self.score, False
            return False
        self._board = temp_board
        self.generate_tile()
        if tf:
            return self._board, self.score, True
        return True

    def _move(self, board: np.ndarray) -> np.ndarray:
        """Always act like you moving up"""
        for row in range(board.shape[0]):
            board[row] = sorted(board[row], key=lambda x: x != 0)
            for col in range(1, board.shape[1]):
                if board[row, col] == board[row, col - 1]:
                    board[row, col - 1] *= 2
                    board[row, col] = 0
            board[row] = sorted(board[row], key=lambda x: x != 0)
        return board

    def __str__(self) -> str:
        data = ""
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if self._board[i, j]:
                    data += f"{str(self._board[i, j]):^4}"
                elif self._board[i, j] == 0:
                    data += f'{" ":^4}'
                if j < self.shape[1] - 1:
                    data += "|"
            if i < self.shape[0] - 1:
                data += f"\n{5*self.shape[0]*'-'}\n"
        return data

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Board2048):
            return np.array_equal(self._board, __o._board)
        return NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._board})"

    # list representation
    def __getitem__(self, key: int) -> list:
        return self._board[key].tolist()

    def aslist(self) -> list:
        return self._board.flatten().tolist()


if __name__ == "__main__":
    board = Board2048()
    # print(board.empty_cells)
    for i in range(4):
        board.generate_tile()
    print(board.aslist())
    # print(board)

    # input()
    # # os.system("cls")
    # board.move(Direction.UP)
    # print(board)

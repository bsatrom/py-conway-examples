"""Game module for py-conway.

This module contains the core functionality for running Conway's Game
of Life games, including the main Game class, GameState Enum, and
InitError exception object.
"""
from random import randint
from .helpers import PseudoEnum

"""Enum for managing the state of a game.

Uses a custom PseudoEnum class because Enum support is not available
on CircuitPython/MicroPython.

States:
    READY: The game is initialized and ready to start.
    RUNNING: The game is currently running.
    STASIS: The game has reached a point where the board is empty, or the
            only remaining cells are either still-life or oscillator objects.
            A game in stasis can still be run, but this state is indicated
            as a flag so the game consumer can catch stasis conditions
            and automatically restart or stop the game.
    FINISHED: The game has stopped and is ready for a new game to begin.
"""
GameState = PseudoEnum(["READY", "RUNNING", "STASIS", "FINISHED"])


class InitError(Exception):
    """Class for wrapping exceptions related to game initialization."""

    def __init__(self, init_message: str):
        """Initialize the exception class.

        Args:
            init_message (str): Message to include in the call to base
        """
        message = "Game Initialization failed: " + init_message
        super().__init__(message)


class Game:
    """Main module class.

    Class for running a game of Conway's Game of Life on a virtual
    two-dimensional board of any size.
    """

    generations = 0
    live_cells = 0

    def __init__(self, columns: int = 0, rows: int = 0,
                 seed: list = None, random: bool = False,
                 enforce_boundary: bool = True):
        """
        Intialize the game based on provided board size values and a seed.

        Args:
            columns (int): the number of columns in the game board
            rows (int): the number of rows in the game board
            seed (int): A two-dimensional list with 1 and 0 values that
                    should be set to the initial game state.
            random (bool): Boolean indicating whether a random seed should
                    be created. Ignored if a seed is provided.
            enforce_boundary (bool): Boolean indicating whether cells on
                    the edge of the board should wrap around to the other
                    side.
        """
        self.board_size = (columns, rows)
        self._enforce_boundary = enforce_boundary
        self._previous_board = None

        if seed is None:
            if columns == 0 or rows == 0:
                raise InitError("Please provide columns and rows values \
                                 geater than 0.")
            if random:
                self.seed = self._create_random_seed()
                self.live_cells = self._count_live_cells(self.seed)
            else:
                self.seed = self._create_zeros()
        else:
            if len(seed) != rows or len(seed[0]) != columns:
                self.board_size = (len(seed[0]), len(seed))

            self._scan_seed(seed)

            self.seed = seed
            self.live_cells = self._count_live_cells(self.seed)

        self.current_board = [row[:] for row in self.seed]
        self.state = GameState.READY

    def _count_live_cells(self, grid_state: list) -> int:
        """
        Count the number of live cells in a provided X by Y grid.

        Args:
            grid_state (list): An X by Y two-dimensional list
            with 1 and 0 values.

        Returns:
            int: the count of live cells on the board.
        """
        return len([col_val
                    for row in grid_state
                    for col_val in row if col_val == 1])

    def _create_zeros(self) -> list:
        """Initialize the board with all cells "dead" or off.

        Returns:
            list: Based on the provided board_size, returns a
            two-dimensional list of zeros.
        """
        cols, rows = self.board_size
        return [[0 for col in range(cols)] for row in range(rows)]

    def _create_random_seed(self) -> list:
        """Initialize the board with random alive (1) and dead (0) cells.

        Returns:
            list: Based on provided board_size, returns a two-dimensional
            list with random 0 and 1 values.
        """
        cols, rows = self.board_size
        return [[randint(0, 1) for col in range(cols)] for row in range(rows)]

    def _scan_seed(self, seed: list):
        """Scan each cell in a seed to ensure valid data (0, 1).

        Raises:
            InitError: if any value other than 0 or 1 is found.
        """
        for row in seed:
            for item in row:
                if item != 0 and item != 1:
                    raise InitError("Game seed can only contain 0s \
                                 and 1s.")

    def _num_neighbors(self, row: int, column: int) -> int:
        """Determine the number of live neighbors for a given cell.

        Args:
            row (int): The row of the current cell
            col (int): The column of the current cell

        Returns:
            int: Count of living neigbors adjecnt to the provided cell.
        """
        neighbors = 0
        num_cols, num_rows = self.board_size

        # Build up a set of possible coordinates to check
        # and then iterate over that set to get a count,
        # ignoring those values that exist outside of the grid
        neighbor_set = {(row - 1, column - 1),
                        (row - 1, column),
                        (row - 1, column + 1),
                        (row, column - 1),
                        (row, column + 1),
                        (row + 1, column - 1),
                        (row + 1, column),
                        (row + 1, column + 1)}
        for n_row, n_col in neighbor_set:
            # if row == 0, don't check the row above
            # if col == 0, don't check the column before
            # unless enforce_boundary is False, in which case
            # wrap around to the other side of the board.
            if n_row < 0 or n_col < 0:
                if self._enforce_boundary:
                    continue

                if n_row < 0:
                    n_row = num_rows - 1
                if n_col < 0:
                    n_col = num_cols - 1

            # if row + 1 == num_rows, don't check the row after
            # if col + 1 == num_cols, don't check the col after
            # unless enforce_boundary is False, in which case
            # wrap around to the other side of the board.
            if n_row == num_rows or n_col == num_cols:
                if self._enforce_boundary:
                    continue

                if n_row == num_rows:
                    n_row = 0
                if n_col == num_cols:
                    n_col = 0

            if self.current_board[n_row][n_col] == 1:
                neighbors += 1

        return neighbors

    def start(self):
        """Initialize important game properties."""
        self.current_board = [row[:] for row in self.seed]
        self.state = GameState.RUNNING
        self.generations = 0
        self.live_cells = self._count_live_cells(self.current_board)

    def stop(self):
        """Stop a running game."""
        if self.state == GameState.RUNNING:
            self.state = GameState.FINISHED
            self.live_cells = self._count_live_cells(self.current_board)

    def reseed(self):
        """Reseed the game board.

        Should only be called when the game is not started. Calling when a game
        is running will return silently.
        """
        if self.state != GameState.RUNNING:
            self.seed = self._create_random_seed()
            self.live_cells = self._count_live_cells(self.seed)
            self.current_board = [row[:] for row in self.seed]
            self.state = GameState.READY

    def run_generation(self):
        """Run a single generation across all cells.

        Enumerate over every element and determine its number of neighbors
        For each cell, check all eight neighbors and turn on or off.
        Once every cell has been checked against Conway's three rules,
        the entire state grid is updated at once.
        """
        if self.state != GameState.RUNNING and self.state != GameState.STASIS:
            return

        # Get a deep copy of the state to track cells that will need
        # to change without affecting the outcome for other cells
        # in-generation
        intermediate_state = [row[:] for row in self.current_board]
        upcoming_live_cells = self._count_live_cells(self.current_board)

        for row_index, row in enumerate(self.current_board):
            for col_index in range(len(row)):
                neighbors = self._num_neighbors(row_index, col_index)

                if (neighbors < 2 or neighbors > 3):
                    if (self.current_board[row_index][col_index] == 1):
                        upcoming_live_cells -= 1
                    intermediate_state[row_index][col_index] = 0
                elif (neighbors == 3):
                    if (self.current_board[row_index][col_index] == 0):
                        upcoming_live_cells += 1
                    intermediate_state[row_index][col_index] = 1

        self.generations += 1
        self.live_cells = upcoming_live_cells

        # When a board only contains still-live cells, there will
        # be no change in state
        if self.current_board == intermediate_state:
            self.state = GameState.STASIS
        # Alternatively, when the state is the same every other generation
        # we have an oscillator on our hands and should also change
        # the state to STASIS
        elif self._previous_board == intermediate_state:
            self.state = GameState.STASIS
        # Otherwise, the game is still running normally
        else:
            self._previous_board = self.current_board
            self.current_board = [row[:] for row in intermediate_state]

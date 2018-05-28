import string
import gomill.ascii_boards
import gomill.boards
from .gtp.entities import Move, StoneColor


class Board:
    """Display board using ascii letters

    """

    def __init__(self, size):
        self._board = gomill.boards.Board(size)

    def play(self, color, move):
        color = StoneColor(color)
        move = Move(move)
        row = self._get_move_row(move)
        col = self._get_move_col(move)
        self._board.play(row, col, color.value)

    def render(self):
        return gomill.ascii_boards.render_board(self._board)

    @staticmethod
    def _get_move_row(move):
        row_index = int(move.value[1]) - 1
        return row_index

    @staticmethod
    def _get_move_col(move):
        col_index = string.ascii_lowercase.index(move.value[0].lower())
        return col_index

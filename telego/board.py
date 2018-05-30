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
        self._board.play(move.row_index, move.col_index, color.value)

    def render(self):
        return gomill.ascii_boards.render_board(self._board)

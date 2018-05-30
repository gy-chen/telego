import string
from enum import Enum
from itertools import product

__ALL__ = ['StoneColor', 'Move']

board_columns = string.ascii_letters.replace('i', '')
moves = [(''.join(move), ''.join(move)) for move in
         product(board_columns, map(str, range(1, 20)))]
moves.extend([('resign', 'resign'), ('RESIGN', 'resign'), ('PASS', 'pass'), ('pass', 'pass')])
Move = Enum('Move', moves)


def is_valid(self, board_size):
    if self.value == 'resign' or self.value == 'pass':
        return True
    move_x = board_columns.index(self.value[0].lower()) + 1
    move_y = int(self.value[1:])
    if move_x > board_size or move_y > board_size:
        return False
    return True


@property
def row_index(self):
    return int(self.value[1]) - 1


@property
def col_index(self):
    return board_columns.index(self.value[0].lower())


Move.is_valid = is_valid
Move.row_index = row_index
Move.col_index = col_index


class StoneColor(Enum):
    B = 'b'
    BLACK = 'b'
    W = 'w'
    WHITE = 'w'

import string
from enum import Enum
from itertools import product

__ALL__ = ['StoneColor', 'Move']

moves = [(''.join(move), ''.join(move)) for move in product(string.ascii_letters, map(str, range(1, 20)))]
Move = Enum('Move', moves)


def is_valid(self, board_size):
    move_x = string.ascii_lowercase.index(self.value[0].lower()) + 1
    move_y = int(self.value[1:])
    if move_x > board_size or move_y > board_size:
        return False
    return True


Move.is_valid = is_valid


class StoneColor(Enum):
    B = 'b'
    BLACK = 'b'
    W = 'w'
    WHITE = 'w'

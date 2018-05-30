"""Go Text Protocol commands

This module provide GTP commands that can be used in GTP connection instance.
"""
from .base import Command
from .entities import StoneColor, Move


class Play(Command):
    """Command to place stone

    """

    def __init__(self, color, move):
        color = StoneColor(color)
        move = Move(move)
        self._command = "play {} {}".format(color.value, move.value)


class Genmove(Command):
    """Command GO engine to generate move of given color.

    """

    def __init__(self, color):
        color = StoneColor(color)
        self._command = "genmove {}".format(color.value)


class Boardsize(Command):
    """Command to setup board size

    """

    def __init__(self, size):
        size = int(size)
        self._command = "boardsize {}".format(size)


class Komi(Command):
    """Command to setup komi

    """

    def __init__(self, komi):
        komi = float(komi)
        self._command = "komi {}".format(komi)


class Finalscore(Command):
    """Command to get final score

    """

    def __init__(self):
        self._command = "final_score"

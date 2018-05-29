import contextlib
from enum import Enum, auto
from .gtp.base import ResponseType
from .gtp.commands import Genmove, Play
from .gtp.entities import Move, StoneColor
from .board import Board

__ALL__ = ['Game', 'GameState', 'GameTurn', 'GameTurnError', 'GameEngineError', 'GameMoveInvalidError']


# TODO deal with end of game
class Game(contextlib.AbstractContextManager):
    """Manage state of go game that play with computer

    """

    def __init__(self, player_color, gtp, board_size=9):
        self._player_color = StoneColor(player_color)
        self._gtp = gtp
        self._board_size = board_size
        self._context = None
        self._state = None

    def setup(self):
        self._gtp.open()
        self._context = self._startup_context()
        self._state = GameState.ACTIVE

    def close(self):
        self._gtp.close()
        self._state = None

    def _startup_context(self):
        if self.player_color == StoneColor.BLACK:
            turn = GameTurn.PLAYER
        else:
            turn = GameTurn.COMPUTER
        board = Board(self._board_size)
        context = {
            'turn': turn,
            'board': board
        }
        return context

    def is_computer_turn(self):
        return self._context['turn'] == GameTurn.COMPUTER

    def is_player_turn(self):
        return self._context['turn'] == GameTurn.PLAYER

    @property
    def game_state(self):
        return self._state

    @property
    def board(self):
        return self._context['board']

    @property
    def player_color(self):
        return self._player_color

    @property
    def computer_color(self):
        if self._player_color == StoneColor.BLACK:
            return StoneColor.WHITE
        elif self._player_color == StoneColor.WHITE:
            return StoneColor.BLACK

    def player_play(self, move):
        if not self.is_player_turn():
            raise GameTurnError()
        self._check_move(move)
        self._gtp.send_command(Play(self._player_color, move))
        response = self._gtp.recv_response()
        if response.type == ResponseType.ERROR:
            raise GameEngineError(response.content)
        self._place(self._player_color, move)
        self._end_turn()

    def computer_play(self):
        if not self.is_computer_turn():
            raise GameTurnError()
        self._gtp.send_command(Genmove(self.computer_color))
        response = self._gtp.recv_response()
        if response.type == ResponseType.ERROR:
            raise GameEngineError(response.content)
        move = Move(response.content)
        self._place(self.computer_color, move)
        self._end_turn()

    def _end_turn(self):
        if self.is_computer_turn():
            self._context['turn'] = GameTurn.PLAYER
        elif self.is_player_turn():
            self._context['turn'] = GameTurn.COMPUTER

    def _place(self, color, move):
        board = self._context['board']
        board.play(color, move)

    def _check_move(self, move):
        move = Move(move)
        if not move.is_valid(self._board_size):
            raise GameMoveInvalidError()

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class GameState(Enum):
    ACTIVE = auto()
    END = auto()


class GameTurn(Enum):
    COMPUTER = auto()
    PLAYER = auto()


class GameTurnError(Exception):
    pass


class GameEngineError(Exception):
    pass


class GameMoveInvalidError(Exception):
    pass


if __name__ == '__main__':
    from .gtp.base import GTP

    gtp = GTP('pachi')
    game = Game(StoneColor.BLACK, gtp)
    game.setup()

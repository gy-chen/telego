import contextlib
import logging
from enum import Enum, auto
from .gtp.base import ResponseType
from .gtp.commands import Genmove, Play, Finalscore, Komi
from .gtp.entities import Move, StoneColor
from .board import Board

__ALL__ = ['Game', 'GameState', 'GameTurn', 'GameTurnError', 'GameEngineError', 'GameMoveInvalidError']

logger = logging.getLogger(__name__)


class Game(contextlib.AbstractContextManager):
    """Manage state of go game that play with computer

    """

    def __init__(self, player_color, gtp, board_size=9, komi=5.5):
        self._player_color = StoneColor(player_color)
        self._gtp = gtp
        self._board_size = board_size
        self._komi = komi
        self._context = None
        self._state = None

    def setup(self):
        self._gtp.open()
        self._gtp.send_command(Komi(self._komi))
        response = self._gtp.recv_response()
        if response.type == ResponseType.ERROR:
            raise GameEngineError(response.content)
        self._context = self._startup_context()
        self._state = GameState.ACTIVE

    def close(self):
        self._gtp.close()

    def _startup_context(self):
        if self.player_color == StoneColor.BLACK:
            turn = GameTurn.PLAYER
        else:
            turn = GameTurn.COMPUTER
        board = Board(self._board_size)
        context = {
            'turn': turn,
            'board': board,
            'final_score': 0,
            'pass': {
                StoneColor.BLACK: False,
                StoneColor.WHITE: False
            }
        }
        return context

    def is_computer_turn(self):
        return self._context['turn'] == GameTurn.COMPUTER

    def is_player_turn(self):
        return self._context['turn'] == GameTurn.PLAYER

    @property
    def state(self):
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

    def final_score(self):
        return self._context['final_score']

    def player_play(self, move):
        if self.state == GameState.END:
            raise GameEndOfGameError()
        if not self.is_player_turn():
            raise GameTurnError()
        self._check_move(move)
        self._gtp.send_command(Play(self._player_color, move))
        response = self._gtp.recv_response()
        logger.info('player play response: {}'.format(response.content))
        if response.type == ResponseType.ERROR:
            raise GameEngineError(response.content)
        self._place(self._player_color, move)
        if self.player_color == StoneColor.BLACK:
            self._reset_pass()
        self._try_to_end_game(move)
        if self.state == GameState.ACTIVE:
            self._end_turn()

    def computer_play(self):
        """Make computer play

        :return: computer move
        """
        if self.state == GameState.END:
            raise GameEndOfGameError()
        if not self.is_computer_turn():
            raise GameTurnError()
        self._gtp.send_command(Genmove(self.computer_color))
        response = self._gtp.recv_response()
        logger.info('computer play response: {}'.format(response.content))
        if response.type == ResponseType.ERROR:
            raise GameEngineError(response.content)
        move = Move(response.content)
        self._place(self.computer_color, move)
        if self.computer_color == StoneColor.BLACK:
            self._reset_pass()
        self._try_to_end_game(move)
        if self.state == GameState.ACTIVE:
            self._end_turn()
        return move

    def _end_turn(self):
        if self.is_computer_turn():
            self._context['turn'] = GameTurn.PLAYER
        elif self.is_player_turn():
            self._context['turn'] = GameTurn.COMPUTER

    def _place(self, color, move):
        move = Move(move)
        if move == Move.RESIGN or move == Move.PASS:
            return
        board = self._context['board']
        board.play(color, move)

    def _check_move(self, move):
        move = Move(move)
        if not move.is_valid(self._board_size):
            raise GameMoveInvalidError()

    def _try_to_end_game(self, move):
        move = Move(move)
        if move == Move.PASS:
            self._set_pass(move)
            if self._is_both_pass():
                self._gtp.send_command(Finalscore())
                response = self._gtp.recv_response()
                logging.info('_try_to_end_game: game end: final_score: {}'.format(response.content))
                if response.type == ResponseType.ERROR:
                    raise GameEngineError(response.content)
                self._context['final_score'] = response.content
                self._state = GameState.END
        elif move == Move.RESIGN:
            if self.is_computer_turn():
                winner_color = self.player_color
            elif self.is_player_turn():
                winner_color = self.computer_color
            self._context['final_score'] = "{}+R".format(winner_color.value.upper())
            logging.info('_try_to_end_game: game end: final_score: {}'.format(self._context['final_score']))
            self._state = GameState.END

    def _reset_pass(self):
        self._context['pass'] = {
            StoneColor.BLACK: False,
            StoneColor.WHITE: False
        }

    def _set_pass(self, move):
        if move != Move.PASS:
            return
        if self.is_player_turn():
            self._context['pass'][self.player_color] = True
        elif self.is_computer_turn():
            self._context['pass'][self.computer_color] = True

    def _is_both_pass(self):
        return self._context['pass'][StoneColor.BLACK] and self._context['pass'][StoneColor.WHITE]

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


class GameEndOfGameError(Exception):
    pass


if __name__ == '__main__':
    from .gtp.base import GTP

    gtp = GTP('pachi')
    game = Game(StoneColor.BLACK, gtp)
    game.setup()

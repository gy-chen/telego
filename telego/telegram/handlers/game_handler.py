import logging
from telegram.ext import CommandHandler
from ...game import *
from ...gtp.base import GTP

logger = logging.getLogger(__name__)


class GameHandler:
    """Manage game states for every chats

    """

    def __init__(self):
        self._games = {}

    def start(self, bot, update, args):
        if self._is_game_started(update.message.chat_id):
            logger.info('game start: ignore command, game is already started')
            return
        logger.info('game start: receive args {}'.format(args))
        try:
            player_color = args[0]
        except IndexError:
            player_color = StoneColor.BLACK
        bot.send_message(chat_id=update.message.chat_id, text="Starting game...")
        # TODO catch color error
        self._initialize_game(update.message.chat_id, player_color)
        bot.send_message(chat_id=update.message.chat_id, text=self._get_game(update.message.chat_id).board.render())

    def play(self, bot, update, args):
        if not self._is_game_started(update.message.chat_id):
            logger.info('game play: ignore command, game is not started yet.')
            return
        game = self._get_game(update.message.chat_id)
        try:
            # TODO deal with end of game
            move = Move(args[0])
            game.player_play(move)
            bot.send_message(chat_id=update.message.chat_id, text="Waiting for computer...")
        except (ValueError, IndexError, GameEngineError, GameMoveInvalidError) as e:
            bot.send_message(chat_id=update.message.chat_id, text="Invalid move: {}".format(e))
            return
        game.computer_play()
        bot.send_message(chat_id=update.message.chat_id, text=game.board.render())

    def board(self, bot, update):
        if not self._is_game_started(update.message.chat_id):
            logger.info('game board: ignore command, game is not started yet.')
            return
        bot.send_message(chat_id=update.message.chat_id, text=game.board.render())

    def _initialize_game(self, chat_id, player_color):
        gtp = GTP('pachi')
        game = Game(player_color, gtp=gtp)
        game.setup()
        self._games[chat_id] = game
        if game.is_computer_turn():
            game.computer_play()

    def _get_game(self, chat_id):
        return self._games.get(chat_id, None)

    def _is_game_started(self, chat_id):
        # TODO check game state
        return bool(self._get_game(chat_id))


def register_handlers(dispatcher, game_handler=GameHandler()):
    """Register go game handlers

    Provide handlers:
      - /start
      - /play
      - /resign
      - /pass
      - /board

    :param dispatcher:
    :return:
    """
    start_handler = CommandHandler('start', game_handler.start, pass_args=True)
    play_handler = CommandHandler('play', game_handler.play, pass_args=True)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(play_handler)

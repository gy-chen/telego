import logging
from telegram.ext import CommandHandler
from .. import config
from ...game import *
from ...gtp.base import GTP

logger = logging.getLogger(__name__)


class GameHandler:
    """Manage game states for every chats

    """

    def __init__(self, gtp_command):
        self._games = {}
        self._gtp_command = gtp_command

    def start(self, bot, update, args):
        if self._is_game_active(update.message.chat_id):
            logger.info('game start: ignore command, game is already started')
            return
        logger.info('game start: receive args {}'.format(args))
        try:
            player_color = args[0]
            player_color = player_color.lower()
        except IndexError:
            player_color = StoneColor.BLACK
        bot.send_message(chat_id=update.message.chat_id, text="Starting game...")
        try:
            self._initialize_game(update.message.chat_id, player_color)
        except ValueError as e:
            bot.send_message(chat_id=update.message.chat_id, text="Invalid color: ".format(e))
            return
        game = self._get_game(update.message.chat_id)
        bot.send_message(chat_id=update.message.chat_id, text=self._render_board(game.board), parse_mode='Markdown')

    def play(self, bot, update, args):
        if not self._is_game_active(update.message.chat_id):
            logger.info('game play: ignore command, game is not started yet.')
            return
        game = self._get_game(update.message.chat_id)
        try:
            move = Move(args[0])
            game.player_play(move)
            bot.send_message(chat_id=update.message.chat_id, text=self._render_board(game.board), parse_mode='Markdown')
        except (ValueError, IndexError, GameEngineError, GameMoveInvalidError) as e:
            bot.send_message(chat_id=update.message.chat_id, text="Invalid move: {}".format(e))
            return
        if game.state == GameState.END:
            logger.info('play: game end')
            self.final_score(bot, update)
            return
        bot.send_message(chat_id=update.message.chat_id, text="Waiting for computer...")
        move = game.computer_play()
        bot.send_message(chat_id=update.message.chat_id, text="Computer: {}".format(move.value))
        bot.send_message(chat_id=update.message.chat_id, text=self._render_board(game.board), parse_mode='Markdown')
        if game.state == GameState.END:
            logger.info('play: game end')
            self.final_score(bot, update)

    def board(self, bot, update):
        if not self._is_game_active(update.message.chat_id):
            logger.info('game board: ignore command, game is not started yet.')
            return
        bot.send_message(chat_id=update.message.chat_id, text=self._render_board(game.board), parse_mode='Markdown')

    def final_score(self, bot, update):
        if self._is_game_active(update.message.chat_id):
            logger.info('game final_score: ignore command, game is not finish yet.')
            return
        game = self._get_game(update.message.chat_id)
        final_score = game.final_score()
        bot.send_message(chat_id=update.message.chat_id, text=final_score)

    def _initialize_game(self, chat_id, player_color):
        gtp = GTP(self._gtp_command)
        game = Game(player_color, gtp=gtp)
        game.setup()
        self._games[chat_id] = game
        if game.is_computer_turn():
            game.computer_play()

    @staticmethod
    def _render_board(board):
        return "```\n{}\n```".format(board.render())

    def _get_game(self, chat_id):
        return self._games.get(chat_id, None)

    def _is_game_active(self, chat_id):
        game = self._get_game(chat_id)
        return bool(game) and game.state == GameState.ACTIVE


def register_handlers(dispatcher):
    """Register go game handlers

    Provide handlers:
      - /start
      - /play
      - /board
      - /final_score

    :param dispatcher:
    :param game_handler:
    :return:
    """
    game_handler = GameHandler(gtp_command=config.GTP_COMMAND)

    start_handler = CommandHandler('start', game_handler.start, pass_args=True)
    play_handler = CommandHandler('play', game_handler.play, pass_args=True)
    board_handler = CommandHandler('board', game_handler.board)
    final_score_handler = CommandHandler('final_score', game_handler.final_score)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(play_handler)
    dispatcher.add_handler(board_handler)
    dispatcher.add_handler(final_score_handler)

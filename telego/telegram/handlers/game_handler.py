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
        """Start game

        If game is already start, this method will do nothing.

        :param bot:
        :param update:
        :param args: expect args[0] is player's stone color, can be W or B. Use B if not not provide this argument.
        :return:
        """
        logger.debug('game start: enter')
        if self._is_game_active(update.message.chat_id):
            logger.info('game start: ignore command, game is already started')
            logger.debug('game start: exit')
            return
        logger.info('game start: receive args {}'.format(args))
        try:
            player_color = args[0].lower()
        except IndexError:
            player_color = StoneColor.BLACK
        bot.send_message(chat_id=update.message.chat_id, text=_("Starting game..."))
        try:
            self._initialize_game(update.message.chat_id, player_color)
        except ValueError as e:
            logger.warning('game start: received ValueError: {}'.format(e))
            bot.send_message(chat_id=update.message.chat_id, text=_("Invalid color"))
            logger.debug('game start: exit')
            return
        game = self._get_game(update.message.chat_id)
        bot.send_message(chat_id=update.message.chat_id, text=self._render_board(game.board), parse_mode='Markdown')
        logger.debug('game start: exit')

    def play(self, bot, update, args):
        """Player  play

        If game is end, or game is not started yet, this method will do nothing.

        :param bot:
        :param update:
        :param args:  except args[0] is move, can be [A-J][1-9], e.g. C3, J7, ...etc.
        :return:
        """
        logger.debug('game play: enter')
        if not self._is_game_active(update.message.chat_id):
            logger.info('game play: ignore command, game is not started yet.')
            logger.debug('game play: exit')
            return
        game = self._get_game(update.message.chat_id)
        try:
            move = Move(args[0])
            logger.info('game play: player play: {}'.format(move))
            game.player_play(move)
            bot.send_message(chat_id=update.message.chat_id, text=self._render_board(game.board), parse_mode='Markdown')
        except (ValueError, IndexError, GameEngineError, GameMoveInvalidError) as e:
            logger.warning('game play: player move is rejected: {}'.format(e))
            bot.send_message(chat_id=update.message.chat_id, text=_("Invalid move"))
            logger.debug('game play: exit')
            return
        if game.state == GameState.END:
            logger.info('play: game end')
            self.final_score(bot, update)
            logger.debug('game play: exit')
            return
        bot.send_message(chat_id=update.message.chat_id, text=_("Waiting for computer..."))
        move = game.computer_play()
        logger.info('game play: computer play: {}'.format(move))
        bot.send_message(chat_id=update.message.chat_id, text=_("Computer: {}").format(move))
        bot.send_message(chat_id=update.message.chat_id, text=self._render_board(game.board), parse_mode='Markdown')
        if game.state == GameState.END:
            logger.info('play: game end')
            self.final_score(bot, update)
        logger.debug('game play: exit')

    def board(self, bot, update):
        """Display board

        If game is not started, this method will do nothing.

        :param bot:
        :param update:
        :return:
        """
        logger.debug('game board: enter')
        if not self._is_game_active(update.message.chat_id):
            logger.info('game board: ignore command, game is not started yet.')
            logger.debug('game board: exit')
            return
        game = self._get_game(update.message.chat_id)
        bot.send_message(chat_id=update.message.chat_id, text=self._render_board(game.board), parse_mode='Markdown')
        logger.debug('game board: exit')

    def final_score(self, bot, update):
        """Display final score

        If game is still playing, this method will do nothing.

        :param bot:
        :param update:
        :return:
        """
        logger.debug('game final_score: enter')
        if self._is_game_active(update.message.chat_id):
            logger.info('game final_score: ignore command, game is not finish yet.')
            logger.debug('game final_score: exit')
            return
        game = self._get_game(update.message.chat_id)
        final_score = game.final_score()
        bot.send_message(chat_id=update.message.chat_id, text=final_score)
        logger.debug('game final_score: exit')

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

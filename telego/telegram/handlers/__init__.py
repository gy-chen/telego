from . import game_handler


def register_handlers(dispatcher):
    """Register handlers of telego application

    :param dispatcher:
    :param game_handler:
    :return:
    """
    game_handler.register_handlers(dispatcher)
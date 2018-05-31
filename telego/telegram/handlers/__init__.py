def register_handlers(dispatcher):
    """Register handlers of telego application

    :param dispatcher:
    :param game_handler:
    :return:
    """
    from . import game_handler

    game_handler.register_handlers(dispatcher)

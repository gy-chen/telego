from telegram.ext import Updater
from . import config
from . import handlers


def create_app():
    updater = Updater(token=config.TOKEN)

    handlers.register_handlers(updater.dispatcher)

    return updater


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app = create_app()
    app.start_polling()
    app.idle()

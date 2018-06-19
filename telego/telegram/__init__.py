import gettext
import os
from telegram.ext import Updater
from . import config
from . import handlers

localedir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'translations'))
translation = gettext.translation(__name__, localedir=localedir, languages=[config.LANGUAGE])
translation.install()


def create_updater():
    updater = Updater(token=config.TOKEN)

    handlers.register_handlers(updater.dispatcher)

    return updater


def main():
    import logging

    logging.basicConfig(level=logging.DEBUG)

    updater = create_updater()
    if config.USE_WEBHOOK:
        logging.info('telego started using webhook')
        updater.start_webhook(
            listen="0.0.0.0",
            port=config.WEBHOOK_PORT,
            url_path=config.TOKEN)
        updater.bot.set_webhook(config.WEBHOOK_URL + TOKEN)
    else:
        logging.info('telego started using polling')
        updater.start_polling()
    updater.idle()

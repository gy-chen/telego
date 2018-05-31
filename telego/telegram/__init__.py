import gettext
import os
from telegram.ext import Updater
from . import config
from . import handlers

localedir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'translations'))
translation = gettext.translation(__name__, localedir=localedir, languages=[config.LANGUAGE])
translation.install()


def create_app():
    updater = Updater(token=config.TOKEN)

    handlers.register_handlers(updater.dispatcher)

    return updater

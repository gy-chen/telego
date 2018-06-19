import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TOKEN = os.getenv('TELEGO_TOKEN')
GTP_COMMAND = os.getenv('TELEGO_GTP_COMMAND', 'pachi')
LANGUAGE = os.getenv('TELEGO_LANGUAGE', 'zh_TW')
USE_WEBHOOK = bool(os.getenv('TELEGO_USE_WEBHOOK', False))
WEBHOOK_URL = os.getenv('TELEGO_WEBHOOK_URL', None)
WEBHOOK_PORT = int(os.getenv('PORT', 0) or os.getenv('TELEGO_WEBHOOK_PORT', 0)) or 80

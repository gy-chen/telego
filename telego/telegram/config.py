import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TOKEN = os.getenv('TELEGO_TOKEN')
GTP_COMMAND = os.getenv('TELEGO_GTP_COMMAND', 'pachi')
LANGUAGE = os.getenv('TELEGO_LANGUAGE', 'zh_TW')

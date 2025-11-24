import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

TOKEN = os.getenv('TOKEN')
if not TOKEN:
    logging.critical('❌ Критическая ошибка: Переменная BOT_TOKEN не найдена. Проверьте ваш файл .env!')
    raise ValueError("Bot token is missing!")

TOKEN = os.getenv('BOT_TOKEN')
DB_PATH = os.getenv('DB_PATH', 'bot.db')
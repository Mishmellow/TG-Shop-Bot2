import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    logger.critical("❌ Критическая ошибка: Токен бота не найден в переменных окружения.")
    logger.critical("Убедитесь что в .env файле есть строка: BOT_TOKEN=ваш_токен")
    raise ValueError('Bot token is missing! Add BOT_TOKEN to .env file')

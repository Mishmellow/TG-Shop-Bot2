import os
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    logging.critical('❌ Критическая ошибка: Переменная BOT_TOKEN не найдена. Проверьте Environment Variables в Railway!')
    raise ValueError('Bot token is missing!')

DB_PATH = os.getenv('DB_PATH', 'bot.db')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'default_secret')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

logging.info('✅ Конфигурация успешно загружена.')
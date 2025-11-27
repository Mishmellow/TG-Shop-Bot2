import asyncio
import logging
import os
import sys
from db_manager import DBManager
from aiogram.exceptions import TelegramAPIError

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.types import ErrorEvent, TelegramObject
from aiogram.client.session.aiohttp import AiohttpSession
from typing import Callable, Dict, Any, Awaitable

from config import TOKEN
from Handlers.start import router as start_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBMiddleware(BaseMiddleware):
    def __init__(self, db_manager):
        self.db = db_manager
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data['db'] = self.db
        return await handler(event, data)


try:
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

    env_port = os.environ.get("PORT")
    if not env_port:
        logger.warning(
            "⚠️ Переменная окружения PORT не установлена. Используется порт по умолчанию (8080) для Railway.")
        PORT = 8080
    else:
        PORT = int(env_port)

    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "final_secret_456")
    WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

    db_manager = DBManager(db_path='your_bot_shop.db')
    session = AiohttpSession(timeout=40)
    bot = Bot(token=TOKEN, session=session)
    dp = Dispatcher()

except Exception as e:
    logger.critical(f"❌ КРИТИЧЕСКИЙ СБОЙ В ГЛОБАЛЬНОЙ ИНИЦИАЛИЗАЦИИ: {type(e).__name__} - {e}", exc_info=True)
    sys.exit(1)


@dp.errors()
async def global_error_handler(event: ErrorEvent):
    logger.error(
        f'⚠️ Глобальная ошибка: {type(event.exception).__name__}: {event.exception}',
        exc_info=True
    )
    if event.update.message:
        try:
            await event.update.message.answer(
                'Произошла непредвиденная ошибка. Попробуйте позже.'
            )
        except TelegramAPIError:
            pass


async def on_startup(bot: Bot):
    logger.info("🔥 Очистка старого Webhook для запуска Polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("🟢 Webhook очищен.")


async def main():
    dp.message.middleware(DBMiddleware(db_manager))
    dp.callback_query.middleware(DBMiddleware(db_manager))

    dp.include_router(start_router)

    logger.info(f'🤖 Бот запущен в режиме Polling (локальный запуск)')

    await on_startup(bot)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную.")
    except Exception as e:
        logger.critical(f"❌ КРИТИЧЕСКИЙ СБОЙ В ЦИКЛЕ MAIN: {type(e).__name__} - {e}", exc_info=True)

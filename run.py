import asyncio
import logging
import os
import sys
from db_manager import DBManager
from aiogram.exceptions import TelegramAPIError

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.types import ErrorEvent, TelegramObject
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.methods import set_webhook
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from typing import Callable, Dict, Any, Awaitable

from config import TOKEN
from Handlers.start import router as start_router
from web_app_handler import WebAppHandler

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
            "⚠️ Переменная окружения PORT не установлена. Используется порт по умолчанию (8080) для локального Webhook или Polling.")
        PORT = 8080
    else:
        PORT = int(env_port)

    WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "final_secret_456")
    WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

    FULL_WEBHOOK_URL = f"{WEBHOOK_URL}{WEBHOOK_PATH}" if WEBHOOK_URL else None

    db_manager = DBManager(db_path='your_bot_shop.db')
    session = AiohttpSession(timeout=40)
    bot = Bot(token=TOKEN, session=session)
    dp = Dispatcher()
    dp.message.middleware(DBMiddleware(db_manager))
    dp.callback_query.middleware(DBMiddleware(db_manager))
    dp.include_router(start_router)

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
    if FULL_WEBHOOK_URL:
        logger.info(f"Setting Webhook to: {FULL_WEBHOOK_URL}")
        await bot(set_webhook.SetWebhook(url=FULL_WEBHOOK_URL, secret_token=WEBHOOK_SECRET))
        logger.info("🟢 Webhook успешно установлен.")
    else:
        logger.info("🔥 Очистка старого Webhook для запуска Polling...")
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("🟢 Webhook очищен.")


async def main():
    await on_startup(bot)

    if FULL_WEBHOOK_URL:
        logger.info(f"🤖 Бот запущен в режиме Webhook на порту {PORT}")

        app = web.Application()

        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=WEBHOOK_SECRET
        )

        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        app.router.add_get('/', WebAppHandler)
        setup_application(app, dp, bot=bot)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=PORT)
        await site.start()

        logger.info("⚡ Ожидание входящих Webhook запросов...")
        await asyncio.Event().wait()


    else:
        logger.info(f'🤖 Бот запущен в режиме Polling (локальный запуск)')
        await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную.")
    except Exception as e:
        logger.critical(f"❌ КРИТИЧЕСКИЙ СБОЙ В ЦИКЛЕ MAIN: {type(e).__name__} - {e}", exc_info=True)
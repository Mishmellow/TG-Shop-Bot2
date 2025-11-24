import asyncio
import logging
import os
from aiohttp import web
from db_manager import DBManager

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from config import TOKEN
from Handlers.start import router as start_router
from Handlers.registration import router as registration_router
from Handlers.order import router as order_router
from Handlers.profile import router as profile_router
from Handlers.admin import router as admin_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "my_super_secret_token_123")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

db_manager = DBManager(db_path='your_bot_shop.db')
session = AiohttpSession(timeout=40)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()


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
        except Exception:
            pass


async def on_startup(bot: Bot):
    if WEBHOOK_URL:
        full_webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"

        logger.info("--- ВХОД В on_startup ДЛЯ УСТАНОВКИ WEBHOOK ---")
        logger.info(f"✅ Установка Webhook: {full_webhook_url}")

        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(
            url=full_webhook_url,
            secret_token=WEBHOOK_SECRET
        )
        logger.info("🟢 Webhook успешно установлен.")
    else:
        logger.warning("⚠️ Переменная WEBHOOK_URL не задана. on_startup пропущен.")


async def on_shutdown(bot: Bot):
    if WEBHOOK_URL:
        logger.info("❌ Удаление Webhook...")
        await bot.delete_webhook()


async def health_check(request):
    logger.info("✅ Health Check (/) Received. Server is accessible.")
    return web.Response(text="OK - Server is healthy.")


async def main():
    dp.workflow_data['db'] = db_manager

    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(order_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)

    dp.shutdown.register(on_shutdown)

    if WEBHOOK_URL:
        logger.info(f"--- ПРОВЕРКА ПЕРЕМЕННЫХ ---")
        logger.info(f"WEBHOOK_URL (прочитан): {WEBHOOK_URL}")
        logger.info(f"WEBHOOK_PATH (ожидаемый): {WEBHOOK_PATH}")
        logger.info(f"Порт (ожидаемый): {PORT}")
        logger.info(f"---------------------------")

        await on_startup(bot)

        logger.info(f'🚀 Бот запущен в режиме Webhook на порту {PORT} (для Railway или ngrok)')

        app = web.Application()

        app.router.add_get("/", health_check)

        handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=WEBHOOK_SECRET
        )

        handler.register(app, path=WEBHOOK_PATH)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()

        logger.info(f"🌐 Веб-сервер AIOHTTP запущен на 0.0.0.0:{PORT}")

        await asyncio.Future()
    else:
        logger.info(f'🤖 Бот запущен в режиме Polling (локальный запуск)')
        await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную.")
import asyncio
import logging
import os
from aiohttp import web

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

from db_manager import DBManager

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8020))
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "my_super_secret_token_123")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"

db_manager = DBManager(db_path='your_bot_shop.db')
session = AiohttpSession(timeout=40)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()


@dp.errors()
async def global_error_handler(event: ErrorEvent):
    logging.error(
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

        print("--- ВХОД В on_startup ДЛЯ УСТАНОВКИ WEBHOOK ---")
        print(f"✅ Установка Webhook: {full_webhook_url}")

        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(
            url=full_webhook_url,
            secret_token=WEBHOOK_SECRET
        )
        print("🟢 Webhook успешно установлен.")
    else:
        print("⚠️ Переменная WEBHOOK_URL не задана. on_startup пропущен.")


async def on_shutdown(bot: Bot):
    if WEBHOOK_URL:
        print("❌ Удаление Webhook...")
        await bot.delete_webhook()


async def main():
    dp.workflow_data['db'] = db_manager

    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(order_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)

    dp.shutdown.register(on_shutdown)

    if WEBHOOK_URL:
        # --- ОТЛАДОЧНАЯ ПЕЧАТЬ ПЕРЕД ЗАПУСКОМ СЕРВЕРА ---
        print(f"--- ПРОВЕРКА ПЕРЕМЕННЫХ ---")
        print(f"WEBHOOK_URL (прочитан): {WEBHOOK_URL}")
        print(f"WEBHOOK_PATH (ожидаемый): {WEBHOOK_PATH}")
        print(f"Порт (ожидаемый): {PORT}")
        print(f"---------------------------")

        await on_startup(bot)

        print(f'🚀 Бот запущен в режиме Webhook на порту {PORT} (для Railway или ngrok)')

        app = web.Application()

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

        print(f"🌐 Веб-сервер AIOHTTP запущен на 0.0.0.0:{PORT}")

        await asyncio.Future()
    else:
        print(f'🤖 Бот запущен в режиме Polling (локальный запуск)')
        await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен вручную.")
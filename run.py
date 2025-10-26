import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent
from aiogram.client.session.aiohttp import AiohttpSession

from config import TOKEN
from Handlers.start import router as start_router
from Handlers.registration import router as registration_router
from Handlers.order import router as order_router
from Handlers.profile import router as profile_router
from Handlers.admin import router as admin_router

from data_base import init_db
from webhook import setup_webhook

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

async def main():

    init_db()

    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(order_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)

    use_webhook = await setup_webhook(bot, dp)

    if use_webhook:
        print('Бот запущен в режиме Webhook')

        from aiogram.webhook.aiohttp_server import SimpleRequestHandler
        from aiohttp import web
        import os
        app = web.Application()

        WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
        webhook_path = f"/webhook/{WEBHOOK_SECRET}"

        handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        handler.register(app, path=webhook_path)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", 8020)
        await site.start()

        print(f"🌐 Веб-сервер запущен на порту 8020")
        await asyncio.Future()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
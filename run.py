import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent

from config import TOKEN
from aiogram.client.session.aiohttp import AiohttpSession

from Handlers.start import router as start_router
from Handlers.registration import router as registration_router
from Handlers.order import router as order_router
from Handlers.profile import router as profile_router
from Handlers.admin import router as admin_router

from data_base import init_db

session = AiohttpSession(
    timeout=40,
    retry_delay= 1,
    max_retries= 3
)

bot = Bot(
    token=TOKEN,
    session=session
)

dp = Dispatcher()

@dp.error()
async def global_error_handler(event: ErrorEvent):
    print(f'⚠️ Глобальная ошибка: {type(event.exception).__name__}: {event.exception}')

async def main():
    init_db()
    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(order_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)


    print('🚀 Бот запускается...')


    await bot.delete_webhook(drop_pending_updates=True)
    print('✅ Вебхуки очищены')

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
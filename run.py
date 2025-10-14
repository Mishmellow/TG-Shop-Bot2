import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN

from Handlers.web_app_hand import router as webapp_router
from Handlers.start import router as start_router
from Handlers.registration import router as registration_router
from Handlers.order import router as order_router
from Handlers.profile import router as profile_router
from Handlers.admin import router as admin_router

from data_base import init_db

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    init_db()
    dp.include_router(webapp_router)
    print("✅ webapp_router подключен")

    dp.include_router(start_router)
    print("✅ start_router подключен")
    dp.include_router(registration_router)
    print("✅ registration_router подключен")
    dp.include_router(order_router)
    print("✅ order_router подключен")
    dp.include_router(profile_router)
    print("✅ profile_router подключен")
    dp.include_router(admin_router)
    print("✅ admin_router подключен")

    print('Бот запущен...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
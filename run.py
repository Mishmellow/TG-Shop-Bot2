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
        await asyncio.Future()
    else:
        print('Бот запущен в режиме Polling')
        await dp.start_polling()

    logging.info('🚀 Бот запускается...')


    await bot.delete_webhook(drop_pending_updates=True)
    logging.info('✅ Вебхуки очищены')


    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

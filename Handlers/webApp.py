from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message()
async def debug_all_messages(message: Message):
    print(f'Все что пришло: {message.web_app_data}')

    if message.web_app_data:
        print("Веб-ап данные")
        print(f'Данные: {message.web_app_data}')
        await message.answer('Даные получены')
        return

    return
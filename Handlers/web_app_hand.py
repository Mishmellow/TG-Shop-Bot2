from aiogram import Router
from aiogram.types import Message
import json

router = Router()

@router.message()
async def handle_webapp(message: Message):
    if message.web_app_data:
        print("🎯 WEBAPP ДАННЫЕ!")
        data = json.loads(message.web_app_data.data)
        await message.answer(f"✅ Заказ: {data}")
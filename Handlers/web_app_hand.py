from aiogram import Router
from aiogram.types import Message
import json
from data_base import add_order

router = Router()

@router.message()
async def handle_fucking_everything(message: Message):
    print(f"💀 ВСЁ ЧТО ПРИШЛО: {message}")

    try:
        if hasattr(message, 'web_app_data') and message.web_app_data:
            data_str = message.web_app_data.data
            print(f"🔥 WEBAPP DATA: {data_str}")

            data = json.loads(data_str)
            product = data.get('product')
            price = data.get('price')

            add_order(message.from_user.id, product, 1, 'WebApp')
            await message.answer(f"🎉 Заказ '{product}' за {price}₴ ПРИНЯТ!")
            return
    except Exception as e:
        print(f"❌ WebApp error: {e}")

    # Если обычное сообщение
    if message.text and message.text.startswith('/'):
        print(f"📝 Command: {message.text}")
    elif message.text:
        print(f"📝 Text: {message.text}")
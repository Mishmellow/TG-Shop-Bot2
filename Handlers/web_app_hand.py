from aiogram import Router
from aiogram.types import Message
import json
from data_base import add_order

router = Router()


@router.message()
async def handle_webapp_data(message: Message):
    if message.web_app_data:
        print(f"🎯 WebApp данные получены: {message.web_app_data.data}")
        data = json.loads(message.web_app_data.data)
        print(f"📦 Данные из WebApp: {data}")

        product = data.get('product', 'Неизвестный товар')

        add_order(
            user_id=message.from_user.id,
            product=product,
            quantity=1,
            address='Доставка из WebApp'
        )

        await message.answer(f"🎉 Заказ '{product}' принят!")
        return True
    return False
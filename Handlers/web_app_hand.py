from aiogram import Router, F
from aiogram.types import Message
import json
from data_base import add_order

router = Router()

@router.message(F.web_app_data)
async def handle_webapp_data(message: Message):
    print(f"🎯 WEBAPP TRIGGERED! User: {message.from_user.id}")

    try:
        data = json.loads(message.web_app_data.data)
        print(f"📦 Data: {data}")

        product = data.get('product', 'Unknown')
        price = data.get('price', 0)

        add_order(
            user_id=message.from_user.id,
            product=product,
            quantity=1,
            address='WebApp Delivery'
        )

        await message.answer(f"✅ Заказ '{product}' за {price}₴ принят!")
        print("✅ ORDER PROCESSED!")

    except Exception as e:
        print(f"❌ Error: {e}")
        await message.answer("❌ Ошибка")
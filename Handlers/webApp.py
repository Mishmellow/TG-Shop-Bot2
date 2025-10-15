from aiogram import Router
from aiogram.types import Message
import json

router = Router()


@router.message(lambda message: message.web_app_data is not None)
async def handle_webapp_data(message: Message):
    print("🎯 WEBAPP ДАННЫЕ ПРИШЛИ!")

    web_app_data = message.web_app_data
    print(f"📦 Данные: {web_app_data.data}")

    try:
        data = json.loads(web_app_data.data)
        product = data.get('product', 'Неизвестно')
        price = data.get('price', 0)

        from data_base import add_order
        add_order(
            user_id=message.from_user.id,
            product=product,
            quantity=1,
            address='WebApp Delivery'
        )

        await message.answer(
            f"✅ Заказ принят!\n"
            f"📦 Товар: {product}\n"
            f"💵 Цена: {price}₴\n"
            f"🚚 Доставка: WebApp"
        )
        print("✅ ЗАКАЗ СОХРАНЕН!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await message.answer("❌ Ошибка при обработке заказа")
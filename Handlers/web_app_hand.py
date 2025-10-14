from aiogram import Router
from aiogram.types import Message
import json
from data_base import add_order

router = Router()


@router.message()
async def handle_webapp_data(message: Message):
    if not message.web_app_data:
        return

    print(f"🎯🎯🎯 WEBAPP DATA RECEIVED!")
    print(f"👤 User: {message.from_user.id}")
    print(f"📦 WebApp data: {message.web_app_data}")

    try:
        data = json.loads(message.web_app_data.data)
        print(f"📊 Parsed JSON: {data}")

        product = data.get('product', 'Unknown Product')
        price = data.get('price', 0)

        print(f"🛍 Product: {product}, Price: {price}")


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
            f"🚚 Доставка: WebApp Delivery"
        )

        print("✅✅✅ ORDER PROCESSED SUCCESSFULLY!")

    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {e}")
        await message.answer("❌ Ошибка: неверный формат данных")
    except Exception as e:
        print(f"❌ General Error: {e}")
        await message.answer("❌ Ошибка при обработке заказа")
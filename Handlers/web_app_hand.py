from aiogram import Router, F
from aiogram.types import Message
import json
from data_base import add_order

router = Router()

@router.message(F.web_app_data)
async def handle_webapp_data(message: Message):
    print(f"🎯🎯🎯 WEBAPP TRIGGERED! User: {message.from_user.id}")
    print(f"🎯 FULL MESSAGE OBJECT: {message}")
    print(f"🎯 WebApp data object: {message.web_app_data}")
    print(f"🎯 WebApp data type: {type(message.web_app_data)}")

    if hasattr(message.web_app_data, 'data'):
        print(f"📦 Raw data: {message.web_app_data.data}")

        try:
            data = json.loads(message.web_app_data.data)
            print(f"📊 Parsed data: {data}")

            product = data.get('product', 'Неизвестный товар')
            price = data.get('price', 0)

            print(f"🛍 Товар: {product}, Цена: {price}")

            add_order(
                user_id=message.from_user.id,
                product=product,
                quantity=1,
                address='Доставка из WebApp'
            )

            await message.answer(f"🎉 Заказ '{product}' за {price}₴ принят!")
            print("✅✅✅ ЗАКАЗ УСПЕШНО ОБРАБОТАН!")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await message.answer("❌ Ошибка при оформлении заказа")
    else:
        print(f"❌ WebApp data не имеет атрибута 'data'")
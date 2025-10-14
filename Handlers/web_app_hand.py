from aiogram import Router, F
from aiogram.types import Message
import json
from data_base import add_order

router = Router()


@router.message(F.content_type == 'web_app_data')
async def handle_webapp_data(message: Message):
    print(f"🎯🎯🎯 WEBAPP TRIGGERED! User: {message.from_user.id}")

    web_app_data = message.web_app_data
    print(f"🎯 WebApp data: {web_app_data}")

    if web_app_data and hasattr(web_app_data, 'data'):
        print(f"📦 Raw data: {web_app_data.data}")

        try:
            data = json.loads(web_app_data.data)
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

        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            await message.answer("❌ Ошибка при обработке данных заказа")
        except Exception as e:
            print(f"❌ Общая ошибка: {e}")
            await message.answer("❌ Ошибка при оформлении заказа")
    else:
        print(f"❌ Нет данных WebApp")
        await message.answer("❌ Не получены данные из WebApp")
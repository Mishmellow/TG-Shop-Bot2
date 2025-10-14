from aiogram import Router
from aiogram.types import Message
import json
from data_base import add_order

router = Router()


@router.message()
async def handle_all_messages(message: Message):
    print(f"🔍 Получено сообщение от {message.from_user.id}:")
    print(f"   Текст: {message.text}")
    print(f"   Тип контента: {message.content_type}")
    print(f"   WebApp data: {message.web_app_data}")

    if message.web_app_data:
        print(f"🎯 WebApp данные обнаружены!")
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
            print("✅ Заказ успешно обработан!")

        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            await message.answer("❌ Ошибка обработки заказа")
        except Exception as e:
            print(f"❌ Общая ошибка: {e}")
            await message.answer("❌ Произошла ошибка при оформлении заказа")

    elif message.text and not message.text.startswith('/'):
        print(f"📝 Обычное текстовое сообщение: {message.text}")
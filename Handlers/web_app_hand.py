from aiogram import Router, F
from aiogram.types import Message
import json
from data_base import add_order

router = Router()


@router.message(F.web_app_data)
async def handle_webapp_data(message: Message):
    print(f"🎯 WebApp данные получены: {message.web_app_data.data}")

    try:
        data = json.loads(message.web_app_data.data)
        print(f"📦 Данные из WebApp: {data}")

        product = data.get('product', 'Неизвестный товар')
        price = data.get('price', 0)

        print(f"🛍 Товар: {product}, Цена: {price}")

        # Сохраняем заказ
        add_order(
            user_id=message.from_user.id,
            product=product,
            quantity=1,
            address='Доставка из WebApp'
        )

        await message.answer(
            f"🎉 Заказ '{product}' за {price}₴ принят!\n"
            f"📦 Ожидайте доставку по указанному адресу."
        )

    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        await message.answer("❌ Ошибка обработки заказа")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        await message.answer("❌ Произошла ошибка при оформлении заказа")
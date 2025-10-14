from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import json

router = Router()

@router.message(Command("shop"))
async def cmd_shop(message: Message):
    from aiogram.types import InlineKeyboardButton, WebAppInfo
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="🛍️ Открыть магазин",
        web_app=WebAppInfo(url="https://t.me/PractAPI_Bot/bot_market")
    ))

    await message.answer(
        "Нажми кнопку чтобы открыть магазин:",
        reply_markup=keyboard.as_markup()
    )


@router.message()
async def handle_all_messages(message: Message):
    print(f"🔍 Пришло сообщение, тип: {message.content_type}")

    # Если есть веб-апп данные
    if hasattr(message, 'web_app_data') and message.web_app_data:
        print("🎯🎯🎯 ДАННЫЕ ИЗ WEBAPP ПРИШЛИ!")
        print(f"📦 Raw данные: {message.web_app_data.data}")

        try:
            data = json.loads(message.web_app_data.data)
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

    elif message.text and message.text.startswith('/'):
        return
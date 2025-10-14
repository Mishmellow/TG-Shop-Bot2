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
        web_app=WebAppInfo(url="https://mishmellow.github.io/TG-Shop-Bot2/")
    ))

    await message.answer(
        "Нажми кнопку чтобы открыть магазин:",
        reply_markup=keyboard.as_markup()
    )


@router.message(lambda message: message.web_app_data is not None)
async def handle_webapp_data(message: Message):
    print("🎯🎯🎯 ДАННЫЕ ИЗ WEBAPP ПРИШЛИ!")

    web_app_data = message.web_app_data
    print(f"📦 Данные: {web_app_data.data}")

    try:
        data = json.loads(web_app_data.data)
        product = data.get('product', 'Неизвестно')
        price = data.get('price', 0)

        # Сохраняем заказ
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
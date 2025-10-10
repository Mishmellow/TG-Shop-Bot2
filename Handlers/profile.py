from aiogram.filters import Command
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from data_base import get_user_orders

router = Router()

class Order(StatesGroup):
    choosing_product = State()
    specifying_quantity = State()
    providing_address = State()
    confirm_order = State()

@router.message(Command('my_orders'))
async def show_my_orders(message: Message):
    orders = get_user_orders(message.from_user.id)

    if not orders:
        await message.answer("📭 У вас ещё нет заказов")
        return

    text = "📦 Ваши заказы:\n\n"
    for order in orders:
        text += f"🛍 {order['product']} x{order['quantity']}\n"
        text += f"📍 Адрес: {order['address']}\n"
        text += f"📅 {order['created_at'][:16]}\n\n"

    await message.answer(text)
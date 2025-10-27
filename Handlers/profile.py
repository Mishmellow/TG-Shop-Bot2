from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Command
from data_base import get_user_orders

router = Router()

class Order(StatesGroup):
    choosing_product = State()
    specifying_quantity = State()
    providing_address = State()
    confirm_order = State()

@router.message(Command('profile'))
async def profile_order(message: Message):
    user_id = message.from_user.id
    orders = get_user_orders(user_id)
    orders_count = len(orders)

    await message.answer(
        f"👤 <b>Ваш профиль</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"📦 Заказов: <b>{orders_count}</b>\n"
        f"📅 Имя: {message.from_user.first_name}\n"
        f"🔗 Юзернейм: @{message.from_user.username if message.from_user.username else 'нет'}\n\n"
        f"💫 Спасибо что пользуетесь нашим ботом!",
        parse_mode='HTML'
    )
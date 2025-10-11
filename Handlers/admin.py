from aiogram.filters import Command
from aiogram import Router
from aiogram.types import Message
from data_base import get_all_orders, get_users_count

router = Router()

ADMINS_IDS = [1499143658]

@router.message(Command('admin'))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMINS_IDS:
        await message.answer('❌ Нет доступа')
        return

    orders = get_all_orders()
    users_count = get_users_count()

    text = (
        "👑 **Панель администратора**\n\n"
        f"📊 Пользователей: {users_count}\n"
        f"📦 Заказов: {len(orders)}\n\n"
        "Команды:\n"
        "/admin_orders - все заказы\n"
        "/admin_users - список пользователей"
    )

    await message.answer(text)

@router.message(Command('admin_orders'))
async def show_all_orders(message: Message):
    if message.from_user.id not in ADMINS_IDS:
        return

    orders = get_all_orders()

    if not orders:
        await message.answer('📭 Заказов нет')
        return

    text = "📦 **ВСЕ ЗАКАЗЫ:**\n\n"
    for order in orders:
        text += f"👤 {order['first_name']} (@{order['username']})\n"
        text += f"🛍 {order['product']} x{order['quantity']}\n"
        text += f"📍 {order['address']}\n"
        text += f"📅 {order['created_at'][:16]}\n"
        text += "─" * 30 + "\n"

    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            await message.answer(text[i:i+4000])
    else:
        await message.answer(text)
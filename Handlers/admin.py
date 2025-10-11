from aiogram.filters import Command
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from data_base import get_all_orders, get_users_count, update_order_status, get_order_user_id
from app.keyboards import admin_order_actions

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

    for order in orders:
        keyboard = admin_order_actions(order['id'])  # ← с 's'!
        await message.answer(
            f"📦 Заказ #{order['id']}\n"
            f"👤 {order['first_name']} (@{order['username']})\n"
            f"🛍 {order['product']} x{order['quantity']}\n"
            f"📍 {order['address']}\n"
            f"📅 {order['created_at'][:16]}\n"
            f"📊 Статус: {order['status']}",
            reply_markup=keyboard
        )

@router.callback_query(F.data.startswith('admin_confirm_'))
async def admin_confirm_callback(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.replace('admin_confirm_', ''))
    update_order_status(order_id, 'confirmed')

    user_id = get_order_user_id(order_id)
    await bot.send_message(user_id, f'✅ Ваш заказ #{order_id} подтвержден администратором!')

    await callback.answer(f'✅ Заказ {order_id} подтвержден!')
    await callback.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data.startswith('admin_ship_'))
async def admin_ship_callback(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.replace('admin_ship_', ''))
    update_order_status(order_id, 'shipped')

    user_id = get_order_user_id(order_id)
    await bot.send_message(user_id, f'🚚 Ваш заказ #{order_id} передан в доставку!')

    await callback.answer(f'🚚 Заказ {order_id} передан в доставку!')
    await callback.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data.startswith('admin_complete_'))
async def admin_complete_callback(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.replace('admin_complete_', ''))
    update_order_status(order_id, 'completed')

    user_id = get_order_user_id(order_id)
    await bot.send_message(user_id, f'🎉 Ваш заказ #{order_id} выполнен!')

    await callback.answer(f'🎉 Заказ {order_id} выполнен!')
    await callback.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data.startswith('admin_cancel_'))
async def admin_cancel_callback(callback: CallbackQuery, bot: Bot):
    order_id = int(callback.data.replace('admin_cancel_', ''))
    update_order_status(order_id, 'cancelled')

    user_id = get_order_user_id(order_id)
    await bot.send_message(user_id, f'❌ Ваш заказ #{order_id} отменен администратором!')

    await callback.answer(f'❌ Заказ {order_id} отменен!')
    await callback.message.edit_reply_markup(reply_markup=None)

    print("✅ admin.py загружен и хендлеры зарегистрированы")
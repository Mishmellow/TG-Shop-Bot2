from aiogram.filters import Command
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from data_base import add_order, get_user_orders

from app.keyboards import main_menu, inline_categories, inline_confirm_order

router = Router()

class Order(StatesGroup):
    choosing_product = State()
    specifying_quantity = State()
    adding_comment = State()
    providing_address = State()
    confirm_order = State()

@router.callback_query(F.data == 'place_order')
async def place_order(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Order.choosing_product)
    await callback.message.edit_text(
        'Что хотите заказать?',
        reply_markup= inline_categories()
    )

@router.callback_query(F.data.startswith('category_'), Order.choosing_product)
async def choose_product(callback: CallbackQuery, state: FSMContext):
    print("🎯 1. Категория выбрана")
    product = callback.data.replace('category_', '')
    await state.update_data(product=product)
    await state.set_state(Order.specifying_quantity)
    await callback.message.edit_text(
        f'Вы выбрали: {product}\nВведите количество'
    )

@router.message(Order.specifying_quantity)
async def specifying_quantity(message: Message, state: FSMContext):
    print("🎯 2. Количество получено")
    if not message.text.isdigit():
        await message.answer('Введите число!')
        return

    await state.update_data(quantity=int(message.text))
    await state.set_state(Order.providing_address)
    await message.answer('Теперь введите адрес доставки')

@router.message(Order.providing_address)
async def process_address(message: Message, state: FSMContext):
    print("🎯 3. Адрес получен")
    await state.update_data(address=message.text)
    await state.set_state(Order.adding_comment)

    data = await state.get_data()
    await message.answer(
        f"Проверьте заказ:\n"
        f"Товар: {data['product']}\n"
        f"Количество: {data['quantity']}\n"
        f"Адрес: {data['address']}\n"
        f"Все верно?",
        reply_markup= inline_confirm_order()
    )

@router.callback_query(F.data == 'confirm_order', Order.confirm_order)
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    print("🎯 4. Подтверждение получено!")
    data = await state.get_data()
    print("Данные для сохранения:", data)

    try:
        add_order(
            user_id=callback.from_user.id,
            product=data['product'],
            quantity=data['quantity'],
            address=data['address'],
            comment=data.get('comment', '')
        )

        from aiogram import Bot
        from config import TOKEN
        bot = Bot(token=TOKEN)

        await bot.send_message(
            chat_id=1499143658,
            text=f"🛒 НОВЫЙ ЗАКАЗ!\n"
                 f"👤 Пользователь: @{callback.from_user.username or 'без username'}\n"
                 f"📦 Товар: {data['product']}\n"
                 f"🔢 Количество: {data['quantity']}\n"
                 f"📍 Адрес: {data['address']}"
        )

        order_info = (
            "🛒 *НОВЫЙ ЗАКАЗ #{}*\n"
            "👤 Пользователь: [{}](tg://user?id={})\n"
            "📦 Товар: {}\n"
            "🔢 Количество: {}\n"
            "📍 Адрес: {}\n"
            "⏰ Время: {}"
            "💬 Комментарий: {}"
        ).format(
            callback.from_user.first_name,
            callback.from_user.id,
            data['product'],
            data['quantity'],
            data['address'],
            data.get('comment', 'нет комментария')
        )

        await bot.send_message(
            chat_id=1499143658,
            text=order_info,
            parse_mode='Markdown'
        )

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await callback.answer(f'Ошибка: {e}', show_alert=True)
        return

    await callback.answer('Заказ подтвержден!', show_alert=True)
    await callback.message.edit_text(
        '✅ Ваш заказ принят в обработку! Ожидайте доставку.',
        reply_markup=main_menu()
    )
    await state.clear()

@router.message(Order.adding_comment)
async def process_comment(message: Message, state: FSMContext):
    print('Комментарий получен')
    await state.update_data(comment=message.text)
    await state.set_state(Order.adding_comment)

    data = await state.get_data()
    confirm_text = (
        f"Проверьте заказ:\n"
        f"Товар: {data['product']}\n"
        f"Количество: {data['quantity']}\n"
        f"Адрес: {data['address']}\n"
        f"Комментарий: {data['comment']}\n\n"
        f"Все верно?"
    )
    await message.answer(confirm_text, reply_markup=inline_confirm_order())


@router.callback_query(F.data == 'cancel_order')
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer('Заказ отменён')
    await callback.message.edit_text(
        '❌ Заказ отменён',
        reply_markup=main_menu()
    )

@router.message(Command('my_orders'))
async def show_my_orders(message: Message):
    print('🎯 /my_orders ВЫЗВАН!')

    orders = get_user_orders(message.from_user.id)

    if not orders:
        await message.answer('📭 У вас ещё нет заказов')
        return

    text = '📦 Ваши заказы:\n\n'
    for order in orders:
        text += f"🛍 {order['product']} x{order['quantity']}\n"
        text += f"📍 Адрес: {order['address']}\n"
        text += f"📅 {order['created_at'][:16]}\n\n"

    await message.answer(text)

@router.message(Command('cansel'))
@router.message(F.text.casefold() == 'Отмена')
async def cansel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Заказ отменен!', reply_markup=main_menu())

@router.message(Command('stats'))
async def show_stats(message: Message):
    if message.from_user.id != 1499143658:
        return

    from data_base import get_users_count, get_all_orders

    users_count = get_users_count()
    orders = get_all_orders()
    total_orders = len(orders)

    stats_text = (
        "📊 *Статистика бота*\n\n"
        f"👥 Пользователей: {users_count}\n"
        f"📦 Всего заказов: {total_orders}\n"
    )

    await message.answer(stats_text, parse_mode='Markdown')
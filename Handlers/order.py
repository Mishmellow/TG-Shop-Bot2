from aiogram.filters import Command
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from data_base import add_order, get_user_orders

from app.keyboards import main_menu, inline_categories, inline_confirm_order, inline_continue_order, inline_products
from aiogram import Bot
from config import TOKEN

bot = Bot(token=TOKEN)

router = Router()

class Order(StatesGroup):
    choosing_product = State()
    specifying_quantity = State()
    adding_comment = State()
    providing_address = State()
    confirm_order = State()
    continue_order = State()

@router.callback_query(F.data == 'place_order')
async def place_order(callback: CallbackQuery, state: FSMContext):
     await state.update_data(items=[], address="", comment="")
     await state.set_state(Order.choosing_product)
     await callback.message.edit_text(
         'Выберите категорию:',
         reply_markup=inline_categories()
     )

@router.callback_query(F.data.startswith('category_'))
async def choose_product(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace('category_', '')
    await callback.message.edit_text(
        f'Выберите товар из категории',
        reply_markup=inline_products(category)
    )

@router.callback_query(F.data.startswith('back_to_categories'))
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        'Выберите категорию:',
        reply_markup=inline_categories()
    )

@router.message(Order.specifying_quantity)
async def specifying_quantity(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Введите число')
        return

    data = await state.get_data()
    product = data['current_product']
    quantity = int(message.text)

    items = data.get("items", [])
    items.append({"product": product, "quantity": quantity})

    await state.update_data(items=items)

    if not data.get("address"):
        await state.set_state(Order.providing_address)
        await message.answer('Теперь введите адрес доставки')
    else:
        await state.set_state(Order.choosing_product)
        await message.answer(
            f'✅ Товар "{product}" x{quantity} добавлен в заказ!\n'
            'Хотите добавить еще товар или завершить заказ?',
            reply_markup=inline_continue_order()
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
    await state.update_data(address=message.text)
    await state.set_state(Order.adding_comment)
    await message.answer('💬 Хотите добавить комментарий к заказу? Если нет - напишите нет')


@router.callback_query(F.data == 'confirm_order')
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        for item in data['items']:
            add_order(
                user_id=callback.from_user.id,
                product=item['product'],
                quantity=item['quantity'],
                address=data['address'],
                comment=data.get('comment', '')
            )

        order_info = "🛒 *НОВЫЙ ЗАКАЗ!*\n\n"
        order_info += f"👤 Пользователь: @{callback.from_user.username or 'без username'}\n"
        order_info += f"📍 Адрес: {data['address']}\n"
        order_info += f"💬 Комментарий: {data.get('comment', 'нет комментария')}\n\n"
        order_info += "📦 Состав заказа:\n"

        total_quantity = 0
        for item in data['items']:
            order_info += f"• {item['product']} x{item['quantity']}\n"
            total_quantity += item['quantity']

        order_info += f"\n📊 Итого: {len(data['items'])} позиций, {total_quantity} шт."

        await bot.send_message(
            chat_id=1499143658,
            text=order_info,
            parse_mode='Markdown'
        )

        await callback.message.edit_text(
            '✅ Ваш заказ принят в обработку! Ожидайте доставку.',
            reply_markup=main_menu()
        )
        await state.clear()

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await callback.answer(f'Ошибка: {e}', show_alert=True)


@router.callback_query(F.data == 'continue_order')
async def continue_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    current_order = '📦 Текущий заказ:\n'
    for item in data['items']:
        current_order += f"• {item['product']} x{item['quantity']}\n"

    current_order += f"\n📍 Адрес: {data['address']}"
    current_order += f"\n💬 Комментарий: {data.get('comment', 'нет комментария')}"
    current_order += f"\n\nВыберите следующий товар:"

    await state.set_state(Order.continue_order)
    await callback.message.edit_text(
        current_order,
        reply_markup=inline_categories()
    )

@router.callback_query(F.data == 'finish_order')
async def finish_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        '🎉 Ваш заказ завершен! Ожидайте доставку.',
        reply_markup=main_menu()
    )
    await state.clear()


@router.message(Order.adding_comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text if message.text.lower() not in ['нет', 'no', 'без комментария'] else ''
    await state.update_data(comment=comment)

    data = await state.get_data()

    order_text = "📦 Ваш заказ:\n\n"
    total_items = 0

    for item in data['items']:
        order_text += f"• {item['product']} x{item['quantity']}\n"
        total_items += item['quantity']

    order_text += f"\n📍 Адрес: {data['address']}"
    order_text += f"\n💬 Комментарий: {comment or 'нет'}"
    order_text += f"\n\nВсего товаров: {total_items} шт."
    order_text += f"\n\nВсё верно?"

    await state.set_state(Order.confirm_order)
    await message.answer(order_text, reply_markup=inline_confirm_order())


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
    orders = get_user_orders(message.from_user.id)

    if not orders:
        await message.answer('📭 У вас ещё нет заказов')
        return

    orders_by_group = {}
    for order in orders:
        key = f"{order['address']}_{order['created_at'][:16]}"
        if key not in orders_by_group:
            orders_by_group[key] = []
        orders_by_group[key].append(order)

    text = '📦 Ваши заказы:\n\n'
    for group_key, order_list in orders_by_group.items():
        text += f"📍 Адрес: {order_list[0]['address']}\n"
        text += f"📅 {order_list[0]['created_at'][:16]}\n"
        for order in order_list:
            text += f"   • {order['product']} x{order['quantity']}\n"
        text += "\n"

    await message.answer(text)

@router.message(Command('cancel'))
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
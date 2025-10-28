from aiogram.filters import Command
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.keyboards import inline_cart_keyboard, inline_continue_shopping
from data_base import save_cart_to_db, clear_cart_from_db
import logging
import json

from data_base import add_order, get_user_orders, load_cart_from_db
from data_base import get_product_price
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from app.keyboards import get_web_app_keyboard, inline_categories, inline_confirm_order, inline_continue_order, inline_products

ADMIN_ID = 1499143658

router = Router()

class Order(StatesGroup):
    choosing_product = State()
    specifying_quantity = State()
    adding_comment = State()
    providing_address = State()
    confirm_order = State()
    continue_order = State()

@router.message(F.web_app_data)
async def handle_web_app_order(message: Message, bot: Bot):
    chat_id = message.chat.id
    raw_data = message.web_app_data.data

    try:
        order_data = json.loads(raw_data)
    except json.JSONDecodeError:
        await message.answer("❌ Ошибка обработки данных заказа. Попробуйте снова.")
        return

    product_name = order_data.get('name', 'Неизвестный товар')
    price = order_data.get('price', 0)

    await message.answer(
        f"✅ Ваш заказ принят!\n"
        f"Товар: **{product_name}**\n"
        f"Сумма: **{price} грн**",
        parse_mode='Markdown'
    )
    await bot.send_message(ADMIN_ID, "НОВЫЙ ЗАКАЗ!!!...")

@router.callback_query(F.data == 'place_order')
async def place_order(callback: CallbackQuery, state: FSMContext):
    user_id = callback.message.from_user.id

    cart_items = load_cart_from_db(user_id)

    if cart_items:
        await state.update_data(
            items=cart_items,
            address="",
            comment="",
        )
        text = '🛒 Восстановлена ваша корзина!'
    else:
        await state.update_data(
            items=[],
            address="",
            comment=""
        )
        text = 'Выберите категорию:'

    await state.set_state(Order.choosing_product)
    await callback.message.edit_text(
        text,
        reply_markup=inline_categories()
    )

@router.callback_query(F.data.startswith('category_'))
async def handle_category_click(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace('category_', '')
    await callback.message.edit_text(
        f'Выберите товар из категории {category}:',
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

    save_cart_to_db(message.from_user.id, items)

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

@router.message(Order.providing_address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(Order.adding_comment)
    await message.answer('💬 Хотите добавить комментарий к заказу? Если нет - напишите нет')


@router.callback_query(F.data == 'confirm_order')
async def confirm_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    total_amount = 0
    total_quantity = 0

    if 'items' not in data or not data['items']:
        await callback.answer("❌ Корзина пуста. Пожалуйста, соберите заказ заново.", show_alert=True)
        await state.clear()
        return

    try:
        items_for_display = []

        for item in data['items']:
            product_price = get_product_price(item['product'])

            item_total = product_price * item['quantity']
            total_amount += item_total
            total_quantity += item['quantity']

            add_order(
                user_id=callback.from_user.id,
                product=item['product'],
                quantity=item['quantity'],
                address=data['address'],
                comment=data.get('comment', ''),
                price=product_price
            )

            items_for_display.append({
                'product': item['product'],
                'quantity': item['quantity'],
                'price': product_price
            })

        order_info = "🛒 *НОВЫЙ ЗАКАЗ!*\n\n"
        order_info += f"👤 Пользователь: @{callback.from_user.username or 'без username'}\n"
        order_info += f"📍 Адрес: {data['address']}\n"
        order_info += f"💬 Комментарий: {data.get('comment', 'нет комментария')}\n\n"
        order_info += "📦 Состав заказа:\n"

        for item in items_for_display:
            item_total = item['price'] * item['quantity']
            order_info += f"• {item['product']} x{item['quantity']} - {item_total}₴\n"

        order_info += f'\n💰 Общая сумма: {total_amount}₴'
        order_info += f'\n📊 Итого: {len(items_for_display)} позиций, {total_quantity} шт.'

        await bot.send_message(
            chat_id=1499143658,
            text=order_info,
            parse_mode='Markdown'
        )

        await callback.message.edit_text(
            f'✅ Ваш заказ принят в обработку!\n💰 Сумма заказа: {total_amount}₴\nОжидайте доставку! ',
            reply_markup=get_web_app_keyboard()
        )

        clear_cart_from_db(callback.from_user.id)
        await state.clear()

    except (TelegramBadRequest, TelegramForbiddenError) as api_error:
        logging.error(f"❌ Ошибка Telegram API: {api_error}", exc_info=True)
        await callback.answer("⚠️ Не удалось отправить сообщение. Обратитесь к администратору.", show_alert=True)
    except Exception as e:
        logging.error(f"❌ Непредвиденная ошибка в confirm_order: {e}", exc_info=True)
        await callback.answer("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.", show_alert=True)

    finally:
        await callback.answer()

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
        reply_markup=get_web_app_keyboard()
    )
    await state.clear()

@router.callback_query(F.data.startswith('product_'))
async def choose_product(callback: CallbackQuery, state: FSMContext):
    product_name = callback.data.replace('product_', '')
    await state.update_data(current_product=product_name)
    await state.set_state(Order.specifying_quantity)
    await callback.message.edit_text(
        f'Вы выбрали: {product_name}\nВведите количество:'
    )

@router.message(Order.adding_comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text if message.text.lower() not in ['нет', 'no', 'без комментария'] else ''
    await state.update_data(comment=comment)

    data = await state.get_data()

    order_text = "📦 Ваш заказ:\n\n"
    total_items = 0
    total_amount = 0

    for item in data['items']:
        price = get_product_price(item['product'])
        item_total = price * item['quantity']
        order_text += f"• {item['product']} x{item['quantity']} - {item_total}₴\n"
        total_items += item['quantity']
        total_amount += item_total

    order_text += f"\n📍 Адрес: {data['address']}"
    order_text += f"\n💬 Комментарий: {comment or 'нет'}"
    order_text += f"\n💰 Общая сумма: {total_amount}₴"
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
        reply_markup=get_web_app_keyboard()
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
    await message.answer('Заказ отменен!', reply_markup=get_web_app_keyboard())

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

@router.callback_query(F.data == 'clear_cart')
async def cleat_cart(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    await state.update_data(items=[])
    clear_cart_from_db(user_id)

    await callback.answer('🗑️ Корзина очищена!')
    await callback.message.edit.text(
        '🛒 Ваша корзина пуста',
        reply_markup=inline_confirm_order()
    )


@router.message(Command('cart'))
@router.callback_query(F.data == 'view_cart')
async def view_cart(update: Message | CallbackQuery, state: FSMContext):
    user_id = update.from_user.id if isinstance(update, CallbackQuery) else update.from_user.id

    data = await state.get_data()
    items_from_state = data.get('items', [])


    if not items_from_state:
        items_from_db = load_cart_from_db(user_id)
        if items_from_db:
            await state.update_data(items=items_from_db)
            items = items_from_db
        else:
            items = []
    else:
        items = items_from_state

    if not items:
        text = '🛒 Ваша корзина пуста'
        keyboard = inline_continue_shopping()
    else:
        text = '📦 Ваша корзина:\n\n'
        total_amount = 0
        total_quantity = 0

        for item in items:
            price = get_product_price(item['product'])
            item_total = price * item['quantity']
            text += f'• {item["product"]} x{item["quantity"]} - {item_total}₴\n'
            total_amount += item_total
            total_quantity += item['quantity']

        text += f'\n💰 Общая сумма: {total_amount}₴'
        text += f'\n📊 Товаров: {total_quantity} шт.'

        keyboard = inline_cart_keyboard()

    if isinstance(update, Message):
        await update.answer(text, reply_markup=keyboard)
    else:
        await update.message.edit_text(text, reply_markup=keyboard)

@router.message(F.text == '📞 Контакты')
async def handler_contact(message: Message):
    contact_text = (
        "📞 **Наши Контакты**\n"
        "Оператор: +380 50 123 4567\n"
        "Email: support@tgshop.com\n"
        "Мы работаем с 9:00 до 21:00 ежедневно."
    )
    await message.answer(
        contact_text,
        parse_mode='Markdown'
    )

@router.message(F.text == 'ℹ️ О нас')
async def handler_about(message: Message):
    about_text = (
        "ℹ️ **О Нашем Магазине**\n"
        "Мы — лучший магазин свежего кофе и пиццы в вашем городе! "
        "Мы используем только высококачественные ингредиенты и готовим с любовью.\n"
        "Начните заказ, нажав на кнопку '🛍️ Сделать Заказ' ниже."
    )
    await message.answer(
        about_text,
        parse_mode='Markdown'
    )
from aiogram.filters import Command
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.keyboards import inline_cart_keyboard, inline_continue_shopping
from data_base import clear_cart_from_db
import logging
import json

from data_base import add_order, get_user_orders, load_cart_from_db
from data_base import get_product_price
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from app.keyboards import get_web_app_keyboard,  inline_confirm_order

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
async def handle_web_app_order(message: Message, state: FSMContext):
    raw_data = message.web_app_data.data
    chat_id = message.chat.id

    try:
        data_from_webapp = json.loads(raw_data)

        if 'items' not in data_from_webapp or not data_from_webapp['items']:
            await message.answer("❌ Корзина пуста. Добавьте товары в WebApp.")
            return

        await state.update_data(
            items=data_from_webapp['items'],
            address=None,
            comment=None
        )

        await state.set_state(Order.providing_address)

        await message.answer(
            "📍 Отлично!"
            "Мы получили ваш заказ из WebApp. "
            "Теперь, пожалуйста, введите адрес доставки:",
            reply_markup=ReplyKeyboardRemove()
        )

    except json.JSONDecodeError:
        await message.answer("⚠️ Ошибка в формате данных WebApp. Попробуйте снова.")
    except Exception as e:
        logging.error(f"❌ Критическая ошибка при получении данных WebApp: {e}", exc_info=True)
        await message.answer("❌ Произошла непредвиденная ошибка при получении данных.")


@router.message(Order.providing_address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)

    await state.set_state(Order.adding_comment)
    await message.answer(
        "📝 **Почти готово!"
        "Введите, пожалуйста, любой комментарий к заказу (например, "
        "домофон, код подъезда, этаж) или нажмите Пропустить.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='➡️ Пропустить', callback_data='skip_comment')],
        ])
    )

@router.callback_query(F.data == 'confirm_order')
async def confirm_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    total_amount = 0
    total_quantity = 0

    if 'items' not in data or not data['items']:
        await callback.answer("❌ Корзина пуста. Пожалуйста, соберите заказ заново", show_alert=True)
        await state.clear()
        return

    try:
        items_for_display = []

        for item in data['items']:
            product_price = item.get('price', 0)
            quantity = item.get('quantity', 1)

            item_total = product_price * quantity
            total_amount += item_total
            total_quantity += quantity

            add_order(
                user_id=callback.from_user.id,
                product=item['product'],
                quantity=quantity,
                address=data.get('address', 'Не указан!'),
                comment=data.get('comment', ''),
                price=product_price
            )

            items_for_display.append({
                'product': item['name'],
                'quantity': quantity,
                'price': product_price
            })

        order_info = "🛒 *НОВЫЙ ЗАКАЗ!*\n\n"
        order_info += f"👤 Пользователь: @{callback.from_user.username or 'без username'}\n"
        order_info += f"📍 Адрес: {data.get('address', 'Не указан')}\n"
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
            # reply_markup=get_web_app_keyboard()
        )
        await state.clear()

    except (TelegramBadRequest, TelegramForbiddenError) as api_error:
        logging.error(f"❌ Ошибка Telegram API: {api_error}", exc_info=True)
        await callback.answer("⚠️ Не удалось отправить сообщение. Обратитесь к администратору.", show_alert=True)
    except Exception as e:
        logging.error(f"❌ Непредвиденная ошибка в confirm_order: {e}", exc_info=True)
        await callback.answer("⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.", show_alert=True)

    finally:
        await callback.answer()

@router.message(Order.adding_comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text if message.text.lower() not in ['Нет', 'not', 'без коментария'] else ''
    await state.update_data(comment=comment)
    await state.set_state(Order.confirm_order)
    await show_order_summary(message, state)


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

async def show_order_summary(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'items' not in data or not data['items']:
        await message.answer("❌ Корзина пуста. Пожалуйста, начните сначала.")
        await state.clear()
        return

    total_amount = 0
    summary_text = "👀 **Проверьте ваш заказ:**\n"

    for item in data['items']:
        price = item.get('price', 0)
        quantity = item.get('quantity', 1)
        item_total = price * quantity
        total_amount += item_total

        summary_text += f"- {item['name']} x{quantity} ({price} грн)\n"

    summary_text += f"\n📍 Адрес: {data.get('address', 'Не указан')}\n"
    summary_text += f"💬 Комментарий: {data.get('comment', 'Нет')}\n"
    summary_text += f"\n💰 **Общая сумма:** {total_amount} грн."

    await message.answer(
        summary_text,
        reply_markup=inline_confirm_order(),
        parse_mode='Markdown'
    )

@router.callback_query(F.data == 'skip_comment', Order.adding_comment)
async def skip_comment(callback: CallbackQuery, state: FSMContext):
    await state.update_data(comment="Нет комментария")

    await callback.message.delete()
    await show_order_summary(callback.message, state)
    await callback.answer()
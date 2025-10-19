from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu():
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text='🛍️ Сделать заказ', callback_data='place_order')
    )

    keyboard.row(
        InlineKeyboardButton(text='📞 Контакты', callback_data='contacts'),
        InlineKeyboardButton(text='ℹ️ О нас', callback_data='about_us')
    )

    return keyboard.as_markup()

def inline_continue_order():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='✅ Добавить еще товар', callback_data='continue_order'),
        InlineKeyboardButton(text='🚀 Завершить заказ', callback_data='finish_order')
    )
    return keyboard.adjust(1).as_markup()

def inline_categories():
    keyboard = InlineKeyboardBuilder()

    categories = {
        '🍕 Еда': 'еда',
        '🎁 Товары': 'товары',
        '🔧 Услуги': 'услуги'
    }

    for display_name, category in categories.items():
        keyboard.add(InlineKeyboardButton(
            text=display_name,
            callback_data=f'categories_{category}'
        ))

        return

def inline_products(category):
    keyboard = InlineKeyboardBuilder()

    from data_base import get_products_by_category
    products = get_products_by_category(category)

    for product in products:
        keyboard.add(InlineKeyboardButton(
            text=f"{product['name']} - {product['price']}₴",
            callback_data=f"product_{product['name']}"
        ))

    keyboard.add(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_categories"
    ))

    return keyboard.adjust(1).as_markup()

def inline_confirm_order():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='✅ Подтвердить заказ', callback_data='confirm_order'),
        InlineKeyboardButton(text='❌ Отменить', callback_data='cancel_order')
    )
    return keyboard.adjust(2).as_markup()

def admin_order_actions(order_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='✅ Подтвердить', callback_data=f'admin_confirm_{order_id}'),
        InlineKeyboardButton(text='🚚 В доставку', callback_data=f'admin_ship_{order_id}'),
        InlineKeyboardButton(text='✅ Выполнено', callback_data=f'admin_complete_{order_id}'),
        InlineKeyboardButton(text='❌ Отменить', callback_data=f'admin_cancel_{order_id}')
    )
    return keyboard.adjust(2).as_markup()
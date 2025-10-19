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
            callback_data=f'category_{category}'
        ))

    return keyboard.adjust(2).as_markup()


def inline_products(category):
    keyboard = InlineKeyboardBuilder()

    products_data = {
        'еда': [
            '🍕 Пицца Маргарита - 209₴',
            '☕ Кофе Латте - 70₴',
            '🍔 Бургер Комбо - 189₴',
            '🥗 Салат Цезарь - 120₴'
        ],
        'товары': [
            '👕 Футболка - 150₴',
            '☕ Кружка - 100₴',
            '📱 Чехол для телефона - 200₴'
        ],
        'услуги': [
            '🚚 Доставка - 40₴',
            '🎁 Упаковка подарка - 50₴',
            '💬 Консультация - 100₴'
        ]
    }

    for product_text in products_data.get(category, []):
        product_name = product_text.split(' - ')[0].strip()
        keyboard.add(InlineKeyboardButton(
            text=product_text,
            callback_data=f"product_{product_name}"
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
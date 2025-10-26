from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

WEB_APP_URL = 'https://mishmellow.github.io/TG-Shop-Bot2/'

def main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🌐 WebApp магазин', web_app=WebAppInfo(url=WEB_APP_URL))],
            [KeyboardButton(text='🛍️ Сделать заказ'), KeyboardButton(text='📞 Контакты')],
            [KeyboardButton(text='ℹ️ О нас')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )
    return keyboard

def web_app_only_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🌐 Открыть магазин', web_app=WebAppInfo(url=WEB_APP_URL))]
        ],
        resize_keyboard=True
    )
    return keyboard

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
            ('🍕 Пицца Маргарита - 209₴', 'Пицца Маргарита'),
            ('☕ Кофе Латте - 70₴', 'Кофе Латте'),
            ('🍔 Бургер Комбо - 189₴', 'Бургер Комбо'),
            ('🥗 Салат Цезарь - 120₴', 'Салат Цезарь')
        ],
        'товары': [
            ('👕 Футболка - 150₴', 'Футболка'),
            ('☕ Кружка - 100₴', 'Кружка'),
            ('📱 Чехол для телефона - 200₴', 'Чехол для телефона')
        ],
        'услуги': [
            ('🚚 Доставка - 40₴', 'Доставка'),
            ('🎁 Упаковка подарка - 50₴', 'Упаковка подарка'),
            ('💬 Консультация - 100₴', 'Консультация')
        ]
    }

    for product_text, product_name in products_data.get(category, []):
        keyboard.add(InlineKeyboardButton(
            text=product_text,
            callback_data=f'product_{product_name}'
        ))

    keyboard.add(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back_to_categories"
    ))

    return keyboard.adjust(1).as_markup()

def inline_cart_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text='🛒 Продолжить покупки',
        callback_data='back_to_categories'
    ))
    keyboard.add(InlineKeyboardButton(
        text='✅ Оформить заказ',
        callback_data='finish_order'
    ))
    keyboard.add(InlineKeyboardButton(
        text='🗑️ Очистить корзину',
        callback_data='clear_cart'
    ))

    return keyboard.adjust(1).as_markup()

def inline_continue_shopping():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='🛒 Начать покупки',
        callback_data='place_order'
    ))
    return keyboard.as_markup()

def inline_confirm_order():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='✅ Подтвердить заказ', callback_data='confirm_order'),
        InlineKeyboardButton(text='❌ Отменить', callback_data='cancel_order')
    )
    return keyboard.adjust(2).as_markup()

def admin_order_actions(order_id):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text="👨‍🍳 Принять в работу",
        callback_data=f"admin_confirm_{order_id}"
    ))
    keyboard.add(InlineKeyboardButton(
        text="🚚 В доставку",
        callback_data=f"admin_ship_{order_id}"
    ))
    keyboard.add(InlineKeyboardButton(
        text="✅ Доставлен",
        callback_data=f"admin_complete_{order_id}"
    ))
    keyboard.add(InlineKeyboardButton(
        text="❌ Отменить",
        callback_data=f"admin_cancel_{order_id}"
    ))

    return keyboard.adjust(2).as_markup()
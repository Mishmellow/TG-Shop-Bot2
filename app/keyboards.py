from aiogram.types import InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu():
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text='🛍️ Сделать заказ', callback_data='place_order')
    )
    keyboard.row(
        InlineKeyboardButton(text='🌐 WebApp магазин',
                             web_app=WebAppInfo(url='https://mishmellow.github.io/TG-Shop-Bot2/docs/web_app_hand.html'))
    )
    keyboard.row(
        InlineKeyboardButton(text='📞 Контакты', callback_data='contacts'),
        InlineKeyboardButton(text='ℹ️ О нас', callback_data='about_us')
    )

    return keyboard.as_markup()

def inline_categories():
    keyboard = InlineKeyboardBuilder()
    categories = [
        '🍕 Еда',
        '🎁 Товары',
        '🔧 Услуги',
        '📦 Доставка'
    ]
    for category in categories:
        callback_data = category.split(' ')[1].lower()
        keyboard.add(InlineKeyboardButton(text=category, callback_data=f'category_{callback_data}'))
    return keyboard.adjust(2).as_markup()

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
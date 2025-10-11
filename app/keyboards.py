from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🛍️ Сделать заказ', callback_data='place_order')],
    [InlineKeyboardButton(text='📞 Контакты', callback_data='contacts'),
     InlineKeyboardButton(text='ℹ️ О нас', callback_data='about_us')]
])

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
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from data_base import add_user, user_conn_ref
from app.keyboards import main_menu

router = Router()

print("🎯 start.py загружен!")

@router.message(CommandStart())
async def cmd_start(message: Message):
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith('ref_'):
        try:
            referrer_id = int(args[1].replace('ref_', ''))
        except ValueError:
            pass

    add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        referrer_id=referrer_id
    )

    await message.reply(
        f'Добро пожаловать!.\nТвой ID: {message.from_user.id}\nИмя: {message.from_user.first_name}\nВыберите действие:',
        reply_markup=main_menu()
    )

@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Это команда /help')

@router.callback_query(F.data == 'about_us')
async def show_about(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ О нашем сервисе:\n"
        "Мы доставляем лучшие товары с 2025 года!\n"
        "Быстро, качественно, с гарантией.",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == 'contacts')
async def contacts(callback: CallbackQuery):
    await callback.message.edit_text(
        "📞 Наши контакты:\n"
        "📍 Адрес: Киев, ул. Примерная, 123\n"
        "📱 Телефон: +380 (99) 123-45-67\n"
        "⏰ График работы: Пн-Пт 9:00-18:00",
        reply_markup=main_menu()
    )

@router.message(Command('ref'))
async def ref_user(message: Message):
    ref_count = user_conn_ref(message.from_user.id)
    ref_link = f"https://t.me/твой_бот?start=ref_{message.from_user.id}"
    await message.answer(
        f"🎁 Реферальная система\n"
        f"Приглашено друзей: {ref_count}\n"
        f"Твоя ссылка: {ref_link}"
    )
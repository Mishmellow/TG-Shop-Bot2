from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import asyncio
import logging
import json

try:
    from app.keyboards import get_web_app_keyboard
except ImportError:
    def get_web_app_keyboard():
        return None
    print("⚠️ ВНИМАНИЕ: Не удалось импортировать get_web_app_keyboard. Проверьте путь.")

router = Router()
logger = logging.getLogger(__name__)

print("🎯 start.py загружен!")


@router.message(CommandStart())
async def cmd_start(message: Message, db):
    try:
        args = message.text.split()
        referrer_id = None
        if len(args) > 1 and args[1].startswith('ref_'):
            try:
                referrer_id = int(args[1].replace('ref_', ''))
            except ValueError:
                pass

        logger.info(f"➡️ Обработка /start для пользователя {message.from_user.id}. Реферер: {referrer_id}")

        await asyncio.to_thread(
            db.add_user,
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            referrer_id=referrer_id
        )
        logger.info(f"✅ Пользователь {message.from_user.id} успешно добавлен/обновлен.")

        cart_items = await asyncio.to_thread(db.load_cart_from_db, message.from_user.id)
        logger.info(f"✅ Корзина для {message.from_user.id} загружена. Товаров: {len(cart_items) if cart_items else 0}.")

        if cart_items:
            welcome_text = f'🛒 Добро пожаловать! В вашей корзине {len(cart_items)} товаров.\nТвой ID: {message.from_user.id}\nИмя: {message.from_user.first_name}\nВыберите действие:'
        else:
            welcome_text = f'Добро пожаловать!\nТвой ID: {message.from_user.id}\nИмя: {message.from_user.first_name}\nВыберите действие:'

        await message.reply(
            welcome_text,
            reply_markup=get_web_app_keyboard()
        )
        logger.info(f"✅ Ответ пользователю {message.from_user.id} отправлен.")

    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА в cmd_start для {message.from_user.id}: {type(e).__name__} - {e}",
                     exc_info=True)
        try:
            import sys, traceback
            print(f"❌❌ КРИТИЧЕСКАЯ ОШИБКА В cmd_start: {type(e).__name__} - {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            await message.answer(f"❌ Внутренняя ошибка ({type(e).__name__}). Проверьте логи.")
        except Exception:
            logger.error(f"❌ Не удалось отправить ответ пользователю после ошибки.")


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer(
        '📖 Помощь по боту:\n\n'
        '/start - Главное меню\n'
        '/help - Эта справка\n'
        '/ref - Реферальная система\n'
        '/test - Проверка работы бота\n\n'
        'Используйте кнопку "Магазин" для выбора товаров.'
    )


@router.message(Command('ref'))
async def ref_user(message: Message, db):
    try:
        ref_count = await asyncio.to_thread(db.user_conn_ref, message.from_user.id)

        ref_link = f"https://t.me/PractAPI_Bot?start=ref_{message.from_user.id}"
        await message.answer(
            f"🎁 Реферальная система\n"
            f"Приглашено друзей: {ref_count}\n"
            f"Твоя ссылка: {ref_link}"
        )
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА в cmd_ref: {type(e).__name__} - {e}", exc_info=True)
        await message.answer("❌ Ошибка при загрузке реферальной информации.")


@router.message(Command("test"))
async def test_command(message: Message):
    logger.info(f"✅ Тестовая команда получена от {message.from_user.id}")
    await message.answer("✅ Бот работает! WebApp данные должны приходить сейчас.")


@router.message(F.web_app_data)
async def handle_webapp_data(message: Message, db):
    try:
        data = json.loads(message.web_app_data.data)

        logger.info(f"📦 Получены данные WebApp от {message.from_user.id}: {data}")

        items = data.get('items', [])
        total_sum = data.get('total_sum', 0)
        order_message = data.get('order_message', '')

        if not items:
            await message.answer("❌ Корзина пуста!")
            return

        order_text = f"✅ Заказ оформлен!\n\n{order_message}\n\n"
        order_text += f"💳 К оплате: {total_sum} грн\n\n"
        order_text += "Ожидайте подтверждения от оператора."

        await message.answer(order_text)

        try:
            await asyncio.to_thread(db.save_order, message.from_user.id, items, total_sum)
            logger.info(f"✅ Заказ сохранен в БД")
        except Exception as db_error:
            logger.error(f"❌ Ошибка сохранения в БД: {db_error}")

        ADMIN_ID = 1499143658
        try:
            await message.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"🆕 НОВЫЙ ЗАКАЗ!\n\n"
                    f"👤 От: {message.from_user.full_name} (@{message.from_user.username or 'без username'})\n"
                    f"🆔 ID: {message.from_user.id}\n\n"
                    f"{order_message}"
                )
            )
            logger.info(f"✅ Уведомление отправлено администратору")
        except Exception as admin_error:
            logger.error(f"❌ Ошибка отправки админу: {admin_error}")
            # Не показываем ошибку пользователю

        logger.info(f"✅ Заказ от {message.from_user.id} успешно обработан")

    except json.JSONDecodeError as e:
        logger.error(f"❌ Ошибка парсинга JSON от WebApp: {e}")
        await message.answer("❌ Ошибка обработки данных. Попробуйте снова.")
    except Exception as e:
        logger.error(f"❌ Ошибка обработки WebApp данных: {type(e).__name__} - {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при оформлении заказа.")


@router.callback_query(F.data == 'about_us')
async def show_about(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ О нашем сервисе:\n"
        "Мы доставляем лучшие товары с 2025 года!\n"
        "Быстро, качественно, с гарантией.",
        reply_markup=get_web_app_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == 'contacts')
async def contacts(callback: CallbackQuery):
    await callback.message.edit_text(
        "📞 Наши контакты:\n"
        "📍 Адрес: Киев, ул. Примерная, 123\n"
        "📱 Телефон: +380 (99) 123-45-67\n"
        "⏰ График работы: Пн-Пт 9:00-18:00",
        reply_markup=get_web_app_keyboard()
    )
    await callback.answer()
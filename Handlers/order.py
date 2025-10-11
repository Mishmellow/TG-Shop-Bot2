from aiogram.filters import Command
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from data_base import add_order

from app.keyboards import main, inline_categories, inline_confirm_order

router = Router()

class Order(StatesGroup):
    choosing_product = State()
    specifying_quantity = State()
    providing_address = State()
    confirm_order = State()

# @router.callback_query(F.data == 'place_order')
# async def place_order(callback: CallbackQuery, state: FSMContext):
#     await state.set_state(Order.choosing_product)
#     await callback.message.edit_text(
#         'Что хотите заказать?',
#         reply_markup= inline_categories()
#     )

# @router.callback_query(F.data.startswith('category_'), Order.choosing_product)
# async def choose_product(callback: CallbackQuery, state: FSMContext):
#     print("🎯 1. Категория выбрана")
#     product = callback.data.replace('category_', '')
#     await state.update_data(product=product)
#     await state.set_state(Order.specifying_quantity)
#     await callback.message.edit_text(
#         f'Вы выбрали: {product}\nВведите количество'
#     )

# @router.message(Order.specifying_quantity)
# async def specifying_quantity(message: Message, state: FSMContext):
#     print("🎯 2. Количество получено")
#     if not message.text.isdigit():
#         await message.answer('Введите число!')
#         return
#
#     await state.update_data(quantity=int(message.text))
#     await state.set_state(Order.providing_address)
#     await message.answer('Теперь введите адрес доставки')
#
# @router.message(Order.providing_address)
# async def process_address(message: Message, state: FSMContext):
#     print("🎯 3. Адрес получен")
#     await state.update_data(address=message.text)
#     await state.set_state(Order.confirm_order)
#
#     data = await state.get_data()
#     await message.answer(
#         f"Проверьте заказ:\n"
#         f"Товар: {data['product']}\n"
#         f"Количество: {data['quantity']}\n"
#         f"Адрес: {data['address']}\n"
#         f"Все верно?",
#         reply_markup= inline_confirm_order()
#     )
#
# @router.callback_query(F.data == 'confirm_order', Order.confirm_order)
# async def confirm_order(callback: CallbackQuery, state: FSMContext):
#     print("🎯 4. Подтверждение получено!")
#     data = await state.get_data()
#     print("Данные для сохранения:", data)
#
#     try:
#         add_order(
#             user_id=callback.from_user.id,
#             product=data['product'],
#             quantity=data['quantity'],
#             address=data['address']
#         )
#
#     except Exception as e:
#         print(f"❌ Ошибка сохранения заказа: {e}")
#         await callback.answer(f'Ошибка: {e}', show_alert=True)
#         return
#
#     await callback.answer('Заказ подтвержден!', show_alert=True)
#     await callback.message.edit_text(
#         '✅ Ваш заказ принят в обработку! Ожидайте доставку.',
#         reply_markup=main
#     )
#     await state.clear()
#
# @router.callback_query(F.data == 'cancel_order')
# async def cancel_order(callback: CallbackQuery, state: FSMContext):
#     await state.clear()
#     await callback.answer('Заказ отменён')
#     await callback.message.edit_text(
#         '❌ Заказ отменён',
#         reply_markup=main
#     )

@router.message(Command('admin'))
async def admin_test(message: Message):
    print("🎯 АДМИНКА ВЫЗВАНА!")
    await message.answer("Админка работает!")

@router.message(Command('test'))
async def test_cmd(message: Message):
    print("🎯 TEST ВЫЗВАН!")
    await message.answer("Test работает!")
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router()

class Reg(StatesGroup):
    name = State()
    number = State()

@router.message(Command('start'))
async def start_reg(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer('Введите ваше имя:')

@router.message(Reg.name)
async def reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.number)
    await message.answer('Введите ваш номер телефона:')

@router.message(Reg.number)
async def reg_number(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    phone = ''.join(filter(str.isdigit, message.text))
    if len(phone) < 10:
        await message.answer("❌ Введите нормальный номер!")
        return

    await state.update_data(number=phone)
    data = await state.get_data()
    await message.answer(
        f'Спасибо, регистрация завершена!\nИмя: {data["name"]}\nНомер: {data["number"]}'
    )

    await state.clear()
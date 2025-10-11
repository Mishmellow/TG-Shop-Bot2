from aiogram import Router
from aiogram.fsm.state import StatesGroup, State

router = Router()

class Order(StatesGroup):
    choosing_product = State()
    specifying_quantity = State()
    providing_address = State()
    confirm_order = State()
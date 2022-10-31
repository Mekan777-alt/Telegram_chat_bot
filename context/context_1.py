from aiogram.dispatcher.filters.state import StatesGroup, State


class UserState(StatesGroup):
    name = State()
    city = State()
    phone_number = State()
    email = State()
    comment = State()

from aiogram.types import ReplyKeyboardMarkup

back_message = '👈 Назад'


def back_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)

    return markup







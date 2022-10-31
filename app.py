import logging
from config import dp, loop
import heandlers
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext


@dp.message_handler(commands="start", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Кто вы?', 'Зачем мне это?')
    markup.add('Описать проблему и оставить данные')
    await message.answer("Добрый день!\n"
                         "Я — Евгений, виртуальный ассистент проекта i-Mediator.\n"
                         "Чем могу быть полезен?", reply_markup=markup)


async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup, loop=loop)

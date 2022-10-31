import asyncio
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = "5153177753:AAGN27mmyBzn_nDbc3Wqx7TJwYIG2UQdBMs"
storage = MemoryStorage()
loop = asyncio.get_event_loop()

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage, loop=loop)

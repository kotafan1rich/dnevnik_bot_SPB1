import os

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

from dotenv import load_dotenv


TOKEN = '5439011304:AAGF_03sJSmc8GR7gkUhjG_3SEvadUPz3oI'
storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

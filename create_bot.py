import os

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv('TOKEN')
storage = MemoryStorage()

bot = Bot(token=TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)

from aiogram.utils import executor
from create_bot import dp
from handlers import client

import os

try:
    os.mkdir('cookies')
except OSError as ex:
    ...

client.register_handlers_client(dp)

executor.start_polling(dp, skip_updates=True)

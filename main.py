from aiogram.utils import executor
from create_bot import dp
from handlers import client

import os

try:
    os.rmdir('~/dnevnik_bot_SPB1/cookies')
except OSError as ex:
    print(ex)
    pass

client.register_handlers_client(dp)

executor.start_polling(dp, skip_updates=True)

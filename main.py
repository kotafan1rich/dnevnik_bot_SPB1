#!/usr/bin/python
# vim: set fileencoding=UTF-8
from aiogram.utils import executor
from create_bot import dp
from handlers import client, admin

import os

try:
    os.mkdir('cookies')
except OSError as ex:
    ...

admin.register_handlers_client(dp)
client.register_handlers_client(dp)

executor.start_polling(dp, skip_updates=True)

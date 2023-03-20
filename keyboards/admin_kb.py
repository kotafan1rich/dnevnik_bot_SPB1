from aiogram.types import KeyboardButton
from keyboards.client_kb import kb_client

b1 = KeyboardButton('Добавить рассылку')

kb_admin = kb_client.row(b1)

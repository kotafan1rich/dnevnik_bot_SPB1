from aiogram.types import KeyboardButton
from keyboards.client_kb import kb_client, kb_client_login

b1 = KeyboardButton('Добавить рассылку')

kb_sender_admin = kb_client_login
kb_admin = kb_client.row(b1)

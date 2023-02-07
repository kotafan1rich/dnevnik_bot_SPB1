from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('1 четверть')
b2 = KeyboardButton('2 четверть')
b3 = KeyboardButton('3 четверть')
b4 = KeyboardButton('4 четверть')
b5 = KeyboardButton('Год')
b7 = KeyboardButton('help')
b8 = KeyboardButton('Изменить логин и пароль')
b9 = KeyboardButton('Удалить Cookies')
b10 = KeyboardButton('Изменить имя')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client_login = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client_start = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.row(b1, b2, b3).row(b4, b5).row(b8, b10, b9).add(b7)
kb_client_login.row('Отмена')
# kb_client_start.row(b8)

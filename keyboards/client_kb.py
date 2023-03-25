from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('1 четверть')
b2 = KeyboardButton('2 четверть')
b3 = KeyboardButton('3 четверть')
b4 = KeyboardButton('4 четверть')
b5 = KeyboardButton('Год')
b7 = KeyboardButton('Помощь')
b8 = KeyboardButton('Изменить логин и пароль')
b9 = KeyboardButton('Удалить Cookies')
b10 = KeyboardButton('Изменить имя')
b11 = KeyboardButton('Настройки')
b12 = KeyboardButton('Отмена')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client_login = ReplyKeyboardMarkup(resize_keyboard=True)
# kb_client_start = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client_settings = ReplyKeyboardMarkup(resize_keyboard=True)


kb_client.row(b1, b2, b3).row(b4, b5).row(b11, b7)
kb_client_login.row(b12)
kb_client_settings.row(b8, b9, b10).row(b12)
# kb_client_start.row(b8)

import os

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import bot
from handlers import other
from keyboards import kb_client, kb_client_login
from db import Database

db = Database('db_dnevnik_tg_bot.db')

help = '''
[1] Чтобы начать пользоваться ботом необходимо добавить логин и пароль от гос услуг для доступа к вашим оценкам. 
[2] Для получения своего среднего балла нажмите на соответствующие кнопки.
[3] Все вопросы и отзывы сюда --> https://t.me/Gohdot.
!!! Полученные данные не используютя в посторонних целях и не передаются третим лицам !!!
'''


class FSMLoginEsia(StatesGroup):
    login = State()
    password = State()


async def get_message(message: types.Message, quater: int):
    res = None
    try:
        await bot.send_message(message.chat.id, 'Подождите...')
        res = other.get_m_result(quater, user_id=message.from_user.id)
    except AttributeError:
        res = 'Ошибка... Оценки не найдены, попробуйте ещё раз'
    finally:
        await bot.send_message(message.chat.id, res, reply_markup=kb_client)


async def add_login_password_db(state, user_id):
    async with state.proxy() as data:
        login = data['login']
        password = data['password']
        db.set_login(user_id=user_id, login=login)
        db.set_password(user_id=user_id, password=password)
        try:
            os.remove(f'cookies/cookies{user_id}')
        except FileNotFoundError:
            pass


async def get_start(message: types.Message):
    user_id = message.from_user.id

    if not db.user_exists(user_id=user_id):
        db.add_user(user_id=user_id)

        login = db.get_login_and_password(user_id=user_id)[0]
        password = db.get_login_and_password(user_id=user_id)[1]

        if login is None or password is None:
            await FSMLoginEsia.login.set()
            await bot.send_message(message.chat.id, 'Введите логин', reply_markup=kb_client_login)
    else:
        await bot.send_message(message.chat.id, 'Снова здравствуйте', reply_markup=kb_client)


async def login_users(message: types.Message):

    await FSMLoginEsia.login.set()
    await bot.send_message(message.chat.id, 'Введите логин', reply_markup=kb_client_login)


async def get_login(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['login'] = message.text
    await FSMLoginEsia.next()
    await bot.send_message(message.chat.id, 'Введите пароль', reply_markup=kb_client_login)


async def get_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text
    await add_login_password_db(state=state, user_id=message.from_user.id)
    await bot.send_message(message.chat.id, 'Логин и пароль добавлены', reply_markup=kb_client)
    await state.finish()


async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.chat.id, 'Отмена, так отмена', reply_markup=kb_client)


async def get_marks_quater(message: types.Message):
    quater = message.text[0]
    if quater == 'Год':
        quater = 5
        await get_message(message, quater)
    else:
        await get_message(message, int(quater))



async def get_help(message: types.Message):
    await bot.send_message(message.chat.id, help)


async def del_cookies(message: types.Message):
    res = None
    user_id = message.chat.id
    try:
        os.remove(f'cookies/cookies{user_id}')
        res = 'Cookies были удалены'
    except FileNotFoundError:
        res = 'У нас нету ваших Cookies'
    finally:
        await bot.send_message(user_id, res, reply_markup=kb_client)


async def unknow_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Упс... Я тебя не понял')
    await bot.send_message(message.chat.id, help, reply_markup=kb_client)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(get_start, commands='start')
    dp.register_message_handler(get_help, text=['help'])
    dp.register_message_handler(del_cookies, text=['Удалить Cookies'])
    dp.register_message_handler(cancel_handler, state='*', text=['Отмена'])
    dp.register_message_handler(login_users, text=['Изменить логин и пароль'], state=None)
    dp.register_message_handler(get_password, state=FSMLoginEsia.password)
    dp.register_message_handler(get_login, state=FSMLoginEsia.login)
    dp.register_message_handler(cancel_handler, state='*', text=['Отмена'])
    dp.register_message_handler(get_marks_quater, text=['1 четверть', '2 четверть','3 четверть','4 четверть', 'Год'])
    dp.register_message_handler(unknow_command)

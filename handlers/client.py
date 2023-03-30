import os

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import bot
from handlers import other
from keyboards import kb_client, kb_client_login, kb_admin, kb_client_settings
from db import Database

db = Database('db_dnevnik_tg_bot.db')

admins = [1324716819,]

HELP = '''
!!! Работает только через ЕСИА !!!
1) Чтобы начать пользоваться ботом необходимо добавить логин и пароль от госю услуг для доступа к твоим оценкам с сайта 'Петербуржское образование' https://dnevnik2.petersburgedu.ru.
2) Для получения своего среднего балла нажми на соответствующие кнопки. Если кнопок нету введи любое сообщение и они должны появиться.
3) Оценки выводятся в формате:
ПРЕДМЕТ: ПОСЛЕДНИЕ_3 (КОЛ-ВО)  СР.БАЛЛ = ЧЕТВЕРТНАЯ
4) Все вопросы и отзывы сюда --> https://t.me/Gohdot.
!!! Полученные данные: парооль и логин от гос услуг, не используютя в посторонних целях и не передаются третьим лицам !!!
'''

SETTINGS = '''
Ты можешь:
- Изменить логин или пароль от гос. услуг
- Изменить имя ученика, которого хотите получать оценки
- Удалить Cookies
'''

ERROR_MES = 'Ошибка... Оценки не найдены, попробуй ещё раз'


class FSMLoginEsia(StatesGroup):
    login = State()
    password = State()
    name = State()


async def get_message(message: types.Message, quater: int):
    wait_message = None
    res = ERROR_MES
    try:
        wait_message = await bot.send_message(message.chat.id, 'Подожди...')
        res = other.get_m_result(quater, user_id=message.from_user.id)
    except:
        pass
    finally:
        await bot.edit_message_text(chat_id=message.from_user.id, message_id=wait_message.message_id, text=res)


async def add_login_password_db(state: FSMContext, user_id):
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
            if user_id in admins:
                await bot.send_message(message.chat.id, 'Здравствуйте', reply_markup=kb_admin)

    else:
        if user_id in admins:
            await bot.send_message(message.chat.id, 'Здравствуйте', reply_markup=kb_admin)
        else:
            await bot.send_message(message.chat.id, 'Снова здравствуйте', reply_markup=kb_client)


async def add_name(message: types.Message):
    await FSMLoginEsia.name.set()
    await bot.send_message(message.chat.id, 'Введите имя человека, чьи оценки будете получать', reply_markup=kb_client_login)


async def get_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        name = data['name']
        db.set_name(user_id=message.from_user.id, name=name)
        try:
            os.remove(f'cookies/cookies{message.from_user.id}')
        except FileNotFoundError:
            ...
        await state.finish()
        await bot.send_message(message.chat.id, 'Добавлено', reply_markup=kb_client)

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
    await bot.send_message(message.chat.id, 'Введите имя человека, чьи оценки будете получать', reply_markup=kb_client_login)
    await FSMLoginEsia.next()


async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.chat.id, 'Отмена, так отмена', reply_markup=kb_client)


async def get_marks_quater(message: types.Message):
    quater = message.text.split()[0]
    if quater == 'Год':
        quater = 20
        await get_message(message, quater)
    else:
        await get_message(message, int(quater))


async def get_help(message: types.Message):
    await bot.send_message(message.chat.id, HELP)


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

async def get_settings(message: types.Message):
    await bot.send_message(message.from_user.id, SETTINGS, reply_markup=kb_client_settings)


async def unknow_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Упс... Я тебя не понял')
    await bot.send_message(message.chat.id, HELP, reply_markup=kb_client)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(get_start, commands='start')
    dp.register_message_handler(get_help, text=['Помощь'])
    dp.register_message_handler(del_cookies, text=['Удалить Cookies'])
    dp.register_message_handler(cancel_handler, state='*', text=['Отмена'])
    dp.register_message_handler(add_name, text=['Изменить имя'], state=None)
    dp.register_message_handler(get_name, state=FSMLoginEsia.name)
    dp.register_message_handler(login_users, text=['Изменить логин и пароль'], state=None)
    dp.register_message_handler(get_password, state=FSMLoginEsia.password)
    dp.register_message_handler(get_login, state=FSMLoginEsia.login)
    dp.register_message_handler(cancel_handler, state='*', text=['Отмена'])
    dp.register_message_handler(get_marks_quater, text=['1 четверть', '2 четверть','3 четверть','4 четверть', 'Год'])
    dp.register_message_handler(get_settings, text=['Настройки'])
    dp.register_message_handler(unknow_command)

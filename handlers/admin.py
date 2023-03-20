#!/usr/bin/python
# vim: set fileencoding=UTF-8

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import bot
from keyboards import kb_admin
from handlers.client import db


class FSMAdmin(StatesGroup):
    message_send = State()

async def sender(message):
    user_id = db.get_all_user_id()
    for user in user_id:
        await bot.send_message(user, message)

async def start_sender(message: types.Message):
    await FSMAdmin.message_send.set()
    await bot.send_message(message.chat.id, 'Введите сообщение')


async def get_mess_send(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['message_send'] = message.text
    await bot.send_message(message.chat.id, 'Рассылка началась')
    await state.finish()
    await sender(message.text)
    await bot.send_message(message.chat.id, 'Рассылка окончена', reply_markup=kb_admin)



def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start_sender, text=['Добавить рассылку'])
    dp.register_message_handler(get_mess_send, state=FSMAdmin.message_send)

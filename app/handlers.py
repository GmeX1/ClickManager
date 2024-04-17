from aiogram import F, Router
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger
from pyrogram import Client
from pyrogram.errors.exceptions import bad_request_400

import app.key as k
from Private import api_hash, api_id
from db.functions import db_add_user, db_check_user_exists, db_update_user

router = Router()


# TODO: Дописать настройки кликера, БД, отчет ошибок

class Reg(StatesGroup):
    number = State()
    kod = State()
    sCode = State()
    Clients = State()


class Max(StatesGroup):
    max_ = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    if await db_check_user_exists(message.from_user.id):
        await message.reply(f'Привет. \nТвой ID:{message.from_user.id} ты есть в нашей системе.\n'
                            f'Тебе осталось зарегистрироваться по команде /reg', reply_markup=k.main)
    else:
        logger.warning(f'Неизвестный пользователь: {message.from_user.username} ({message.from_user.id})')


@router.message(Command('add'))  # Пока что добавление в систему происходит напрямую
async def add_user(message: Message, command: CommandObject):
    user_id = command.args
    if type(user_id) != int:
        user_id = int(user_id)
        logger.info(user_id)
    result = await db_add_user('ref', user_id)
    if result:
        await message.answer('✅Пользователь успешно добавлен!')
    else:
        await message.answer('❌Не удалось добавить пользователя')


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer(f'/help - показывает функции бота'
                         f'\n "Профиль" - показывает сколько намайнил кликер'
                         f'\n /start - запускает бота'
                         f'\n "Запустить кликер наарбузы🍉" - Запускает кликер  ')


@router.message(F.text == '🆘Помощь')
async def get_prof(message: Message):
    await message.answer('Можете задать вопрос админу или сообщить ему об ошибке - @Mr_Mangex')


@router.message(F.text == '👤Профиль')
async def get_prof(message: Message):
    await message.answer('Инф')


@router.message(F.text == '🍉Запустить кликер на арбузы')
async def get_prof(message: Message):
    await message.reply('✅Кликер включен', reply_markup=k.OFF)


@router.callback_query(F.data == 'OFF')
async def back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Кликер выключен', reply_markup=k.ON)


@router.callback_query(F.data == 'ON')
async def back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Кликер включен', reply_markup=k.OFF)


@router.message(F.text == 'Профиль')
async def get_prof(message: Message):
    await message.answer('Инф')


@router.message(Command('reg'))
async def reg(callback: CallbackQuery):
    await callback.answer('Отправьте свой контакт', reply_markup=k.contact_btn)


# Проверка, что пользователь ввел свой номер телефона
@router.message(F.contact)  # TODO: Нельзя напрямую отправлять код 0_о
async def save_phone_number(message: Message, state: FSMContext):
    if message.contact.user_id == message.from_user.id:
        await state.update_data(number=message.contact.phone_number)
        client = Client(str(message.from_user.id), api_id, api_hash)
        await client.connect()
        sCode = await client.send_code(message.contact.phone_number)
        await state.update_data(Clients=client, sCode=sCode)
        await message.answer('Введите код (⚠️⚠️⚠️ОБЯЗАТЕЛЬНО⚠️⚠️⚠️: поставьте пробел внутри кода, место не важно)')
        await state.set_state(Reg.kod)


@router.message(Reg.kod)
async def reg_kod(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        await data["Clients"].sign_in(data["number"], data["sCode"].phone_code_hash, message.text.replace(' ', ''))
        await message.answer("Спасибо")
        await state.clear()
    except bad_request_400:
        await message.answer('Ошибка входа. Отправьте контакт заново и перечитайте условия')


@router.message(F.text == '🤝Поделиться с другом')
async def get_ref(message: Message):
    await message.answer(f'Вот ваша реферальная ссылка: https://t.me/ClickManagerbot?start={message.from_user.id}')


@router.message(F.text == '⚙️Настройки кликера')
async def setr_klik(message: Message):
    await message.reply('Выберите действие: ', reply_markup=k.Settings)


@router.callback_query(F.data == 'Klik')
async def klik(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Включить или выключить автоматическую покупку кликов', reply_markup=k.Yes_or_No_K)


@router.callback_query(F.data == 'YesK')
async def YesK(callback: CallbackQuery):
    change = await db_update_user(callback.from_user.id, {'BUY_CLICK': True})
    if change:
        await callback.answer('Операция была успешно выполнена.')
    else:
        await callback.answer('Не удалось совершить операцию!')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'NoK')
async def NoK(callback: CallbackQuery):
    change = await db_update_user(callback.from_user.id, {'BUY_CLICK': False})
    if change:
        await callback.answer('Операция была успешно выполнена.')
    else:
        await callback.answer('Не удалось совершить операцию!')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'Avto_klik')
async def Avto_klik(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Включить или выключить автоматическую покупку Авто кликов',
                                     reply_markup=k.Yes_or_No_A)


@router.callback_query(F.data == 'YesA')
async def YesA(callback: CallbackQuery):
    change = await db_update_user(callback.from_user.id, {'BUY_MINER': True})
    if change:
        await callback.answer('Операция была успешно выполнена.')
    else:
        await callback.answer('Не удалось совершить операцию!')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'NoA')
async def NoA(callback: CallbackQuery):
    change = await db_update_user(callback.from_user.id, {'BUY_MINER': False})
    if change:
        await callback.answer('Операция была успешно выполнена.')
    else:
        await callback.answer('Не удалось совершить операцию!')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'Energy')
async def Energy(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Включить или выключить автоматическую покупку энергии"',
                                     reply_markup=k.Yes_or_No_E)


@router.callback_query(F.data == 'YesE')
async def YesE(callback: CallbackQuery):
    await callback.answer('Опперация была успешно выполнена')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'NoE')
async def NoE(callback: CallbackQuery):
    await callback.answer('Опперация была успешно выполнена')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'Max_lvl')
async def klik(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Напишите какой лимит хотите поставить (цифра)')
    await state.set_state(Max.max_)


@router.message(Max.max_)
async def max_message(message: Message, state: FSMContext):
    try:
        await state.update_data(max_=int(message.text))
        await message.answer('Опперация была успешно выполнена✅')
    except ValueError:
        await state.set_state(Max.max_)

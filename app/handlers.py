import traceback

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger
from pyrogram import Client
from pyrogram.errors.exceptions import SessionPasswordNeeded

import app.key as k
from Private import api_hash, api_id, admin
from app.md5_hash import generate_referral_hash

from db.functions import (db_add_hash, db_callbacks_add, db_check_hash, db_del_hesh, db_settings_add_user,
                          db_settings_check_user_exists, db_settings_get_user, db_settings_update_user,
                          db_stats_get_sum)

# import aiohttp гифки
router = Router()


# TODO сделать гифки(навыключение кликераm, на профиль), сделать админ панель, отладка ошибок

class Reg(StatesGroup):
    number = State()
    code = State()
    sCode = State()
    Clients = State()
    v_cod = State()


class Max(StatesGroup):
    max_lvl = State()


@router.message(Command('callback'))
async def test_db_callback(message: Message, command: CommandObject):
    """Функция для ручного создания callback запроса"""
    user_id, column, value = command.args.split()
    await db_callbacks_add(user_id, column, value)
    await message.answer('Callback создан.')


@router.message(CommandStart())
async def cmd_start(message: Message):
    if await db_settings_check_user_exists(message.from_user.id):
        res = await db_settings_get_user(message.from_user.id)
        if res.active == 1:
            await message.reply(f'Привет. \nТвой ID:{message.from_user.id} ты есть в нашей системе.\n',
                                reply_markup=k.main)
        else:
            await message.reply(f'Привет. \nТвой ID:{message.from_user.id} ты есть в нашей системе.\n'
                                f'Тебе осталось зарегистрироваться по команде /reg', reply_markup=k.main)

    else:
        if await db_check_hash(message.text[7:]):
            logger.info(message.from_user.id)
            result = await db_settings_add_user('ref', message.from_user.id)
            await db_del_hesh(message.text[7:])
            await message.reply(f'Привет. \nТвой ID:{message.from_user.id} ты есть в нашей системе.\n'
                                f'Тебе осталось зарегистрироваться по команде /reg', reply_markup=k.main)
            if not result:
                await message.answer('Нельзя переходить по собственной ссылке')
        else:
            logger.warning(f'Неизвестный пользователь: {message.from_user.username} ({message.from_user.id})')


@router.message(Command('add'))
async def add_user(message: Message, command: CommandObject):
    if message.from_user.id in admin:
        """Функция для ручного добавления пользователя в БД"""
        user_id = command.args
        if type(user_id) != int:
            user_id = int(user_id)
            logger.info(user_id)
        result = await db_settings_add_user('ref', user_id)
        if result:
            await message.answer('✅Пользователь успешно добавлен!')
        else:
            await message.answer('❌Не удалось добавить пользователя')


@router.message(Command('ref'))
async def add_user(message: Message):
    if message.from_user.id in admin:
        hash_a = await generate_referral_hash()
        await db_add_hash(hash_a)
        await message.answer(f'https://t.me/ClickManagerbot?start={hash_a}')


@router.message(Command('help'))
async def get_help(message: Message):
    if await db_settings_check_user_exists(message.from_user.id):
        await message.answer(f'/help - показывает функции бота'
                             f'\n "Профиль" - показывает сколько вы заработали.'
                             f'\n /start - запускает бота.'
                             f'\n "Запустить кликер на арбузы🍉" - Запускает кликер+.')


@router.message(F.text == '🆘Помощь')
async def get_help(message: Message):
    if await db_settings_check_user_exists(message.from_user.id):
        await message.answer('Можете задать вопрос админу или сообщить ему об ошибке - @Mr_Mangex')


@router.message(F.text == '👤Профиль')
async def get_prof(message: Message):
    if await db_settings_check_user_exists(message.from_user.id):
        res = await db_stats_get_sum(message.from_user.id)
        await message.answer(f'Благодаря нашему боту вы заработали: {res.summary}\n'
                             f'Было куплено бустов: {0}"')


# TODO: переписать с получением статуса кликера (во избежание наслаивания callback'ов)
@router.message(F.text == '🍉Запустить кликер на арбузы')
async def get_clicker(message: Message):
    if await db_settings_check_user_exists(message.from_user.id):
        await message.reply('✅ Кликер включен', reply_markup=k.OFF)
        await db_callbacks_add(message.from_user.id, 'do_click', '1')


@router.callback_query(F.data == 'OFF')
async def clicker_off(callback: CallbackQuery):
    await callback.answer()
    await db_callbacks_add(callback.from_user.id, 'do_click', '2')
    await callback.message.edit_text('❌ Кликер выключен', reply_markup=k.ON)


@router.callback_query(F.data == 'ON')
async def clicker_on(callback: CallbackQuery):
    await callback.answer()
    await db_callbacks_add(callback.from_user.id, 'do_click', '1')
    await callback.message.edit_text('✅ Кликер включен', reply_markup=k.OFF)


@router.message(Command('reg'))
async def reg(callback: CallbackQuery):
    if await db_settings_check_user_exists(callback.from_user.id):
        if (await db_settings_get_user(callback.from_user.id)).active == 0:
            await callback.answer('Отправьте свой контакт', reply_markup=k.contact_btn)


@router.message(F.contact)  # Нельзя напрямую отправлять код 0_о
async def save_phone_number(message: Message, state: FSMContext):
    if await db_settings_check_user_exists(message.from_user.id):
        if (await db_settings_get_user(message.from_user.id)).active == 0:
            if message.contact.user_id == message.from_user.id:
                await state.update_data(number=message.contact.phone_number)
                client = Client(str(message.from_user.id), api_id, api_hash)
                await client.connect()
                sCode = await client.send_code(message.contact.phone_number)
                await state.update_data(Clients=client, sCode=sCode)
                await message.answer(
                    'Введите код (⚠️⚠️⚠️ОБЯЗАТЕЛЬНО⚠️⚠️⚠️: поставьте пробел внутри кода, место не важно)')
                await state.set_state(Reg.code)


@router.message(Reg.code)
async def reg_code(message: Message, state: FSMContext):
    if await db_settings_check_user_exists(message.from_user.id):
        try:
            data = await state.get_data()
            await data["Clients"].sign_in(data["number"], data["sCode"].phone_code_hash, message.text.replace(' ', ''))
            await db_settings_update_user(message.from_user.id, {'active': True})
            await db_callbacks_add(message.from_user.id, 'active', await data['Clients'].export_session_string())
            await message.answer("Спасибо")
            await message.reply(f'Привет. \nТвой ID:{message.from_user.id} ты есть в нашей системе.\n',
                                reply_markup=k.main)
            await state.clear()
        except SessionPasswordNeeded:
            await state.update_data(code=message.text.replace(' ', ''))
            await message.answer('У вас установлен 2fa. Пожалуйста, введите мастер-пароль.')
            await state.set_state(Reg.v_cod)
        except Exception as ex:
            logger.error(f'{ex.__class__.__name__}: {ex}')
            await message.answer('Ошибка входа. Отправьте контакт заново и перечитайте условия')


@router.message(Reg.v_cod)
async def reg_code(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        await data["Clients"].check_password(message.text)
        await data["Clients"].sign_in(data["number"], data["sCode"].phone_code_hash, data['code'])
        await db_settings_update_user(message.from_user.id, {'active': True})
        await db_callbacks_add(message.from_user.id, 'active', await data['Clients'].export_session_string())
        await message.answer("Спасибо")
        await message.reply(f'Привет. \nТвой ID:{message.from_user.id} ты есть в нашей системе.\n',
                            reply_markup=k.main)
        await state.clear()
    except Exception as ex:
        logger.error(f'{ex.__class__.__name__}: {ex}')
        traceback.print_tb(ex.__traceback__)
        await message.answer('Ошибка входа. Отправьте контакт заново и перечитайте условия')


@router.message(F.text == '⚙️Настройки кликера')
async def set_click(message: Message):
    if await db_settings_check_user_exists(message.from_user.id):
        await message.reply('Выберите действие: ', reply_markup=k.Settings)


@router.callback_query(F.data == 'Klik')
async def buy_click(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Включить или выключить автоматическую покупку кликов', reply_markup=k.Yes_or_No_K)


@router.callback_query(F.data == 'YesK')
async def yes_click(callback: CallbackQuery):
    change = await db_settings_update_user(callback.from_user.id, {'BUY_CLICK': True})
    if change:
        await callback.answer('Операция была успешно выполнена.')
        await db_callbacks_add(callback.from_user.id, 'settings', 'BUY_CLICK')
    else:
        await callback.answer('Не удалось совершить операцию!')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'NoK')
async def no_click(callback: CallbackQuery):
    change = await db_settings_update_user(callback.from_user.id, {'BUY_CLICK': False})
    if change:
        await callback.answer('Операция была успешно выполнена.')
        await db_callbacks_add(callback.from_user.id, 'settings', 'BUY_CLICK')
    else:
        await callback.answer('Не удалось совершить операцию!')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'Avto_klik')
async def auto_click(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Включить или выключить автоматическую покупку Авто кликов',
                                     reply_markup=k.Yes_or_No_A)


@router.callback_query(F.data == 'YesA')
async def yes_miner(callback: CallbackQuery):
    change = await db_settings_update_user(callback.from_user.id, {'BUY_MINER': True})
    if change:
        await callback.answer('Операция была успешно выполнена.')
        await db_callbacks_add(callback.from_user.id, 'settings', 'BUY_MINER')
    else:
        await callback.answer('Не удалось совершить операцию!')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'NoA')
async def no_miner(callback: CallbackQuery):
    change = await db_settings_update_user(callback.from_user.id, {'BUY_MINER': False})
    if change:
        await callback.answer('Операция была успешно выполнена.')
        await db_callbacks_add(callback.from_user.id, 'settings', 'BUY_MINER')
    else:
        await callback.answer('Не удалось совершить операцию!')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'Energy')
async def buy_energy(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Включить или выключить автоматическую покупку энергии"',
                                     reply_markup=k.Yes_or_No_E)


@router.callback_query(F.data == 'YesE')
async def yes_energy(callback: CallbackQuery):
    change = await db_settings_update_user(callback.from_user.id, {'BUY_ENERGY': True})
    if change:
        await callback.answer('Операция была успешно выполнена.')
        await db_callbacks_add(callback.from_user.id, 'settings', 'BUY_ENERGY')
    else:
        await callback.answer('Не удалось совершить операцию!')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'NoE')
async def no_energy(callback: CallbackQuery):
    change = await db_settings_update_user(callback.from_user.id, {'BUY_ENERGY': False})
    if change:
        await callback.answer('Операция была успешно выполнена.')
        await db_callbacks_add(callback.from_user.id, 'settings', 'BUY_ENERGY')
    else:
        await callback.answer('Не удалось совершить операцию!')
    await callback.message.edit_text('Выберите действие: ', reply_markup=k.Settings)
    pass


@router.callback_query(F.data == 'Max_lvl')
async def buy_lvl(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Напишите какой лимит хотите поставить (целое число)')
    await state.set_state(Max.max_lvl)


@router.message(Max.max_lvl)
async def change_lvl(message: Message, state: FSMContext):
    if await db_settings_check_user_exists(message.from_user.id):
        try:
            value = message.text
            change = await db_settings_update_user(message.from_user.id, {'BUY_MAX_LVL': int(value)})
            if change:
                await message.answer('✅Операция была успешно выполнена.')
                await db_callbacks_add(message.from_user.id, 'settings', value)
        except ValueError:
            await message.answer('❌Не удалось совершить операцию! Введите число заново: ')
            await state.set_state(Max.max_lvl)

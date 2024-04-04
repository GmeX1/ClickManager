from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import app.key as k

router = Router()


@router.message(CommandStart())
async def cmd_start(massage: Message):
    await massage.reply(f'Привет. \nТвой ID:{massage.from_user.id} ты есть в нашей системе', reply_markup=k.main)


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer(f'/help - показывает функции бота'
                         f'\n "Профиль" - показывает сколько намайнил кликер'
                         f'\n /start - запускает бота'
                         f'\n "Запустить кликер на арбузы🍉" - Запускает кликер  ')


@router.message(F.text == '🆘Помощь')
async def get_prof(message: Message):
    await message.answer(' можете задать вопрос админу или сообщить ему об ошибке - ....')


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


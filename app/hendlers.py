from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
router = Router()
@router.message(CommandStart())
async def cmd_start(massage: Message):
    await massage.reply(f'Привет. \nТвой ID:{massage.from_user.id} ты есть в нашей системе')


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('....')


@router.message(F.text == 'Инф')
async def get_prof(message: Message):
    await message.answer('Инф')


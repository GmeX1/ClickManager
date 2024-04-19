import asyncio
import sys

from aiogram import Bot, Dispatcher
from loguru import logger

from Private import TOKEN
from app.handlers import router
from db.functions import init, db_settings_update_user

bot = Bot(token=TOKEN)
dp = Dispatcher()


# TODO: Использовать md5 для реферальной системы
async def main_tg():
    await init()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logger.add(sys.stderr, level='DEBUG', enqueue=True, colorize=True)
    try:
        asyncio.run(main_tg())
    except KeyboardInterrupt:
        print('Exit')

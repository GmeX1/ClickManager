import time

import pyrogram
from aiogram import Bot, Dispatcher

from Private import TOKEN
from app.handlers import router

import asyncio
import sys
from app.core.clicker import ClickerClient
from loguru import logger
from app.core.utils.scripts import get_clients, run_client
from db.functions import init
from temp_vars import LOG_LEVEL
from multiprocessing import Pool
from time import sleep
from concurrent.futures import ProcessPoolExecutor

bot = Bot(token=TOKEN)
dp = Dispatcher()
clicker = ClickerClient

# TODO: Отслеживать изменения в БД, разобраться с прокси
def test():  # Позволяет запускать в 2 потока
    while True:
        for _ in range(100):
            print(f'TEST {_}')
            time.sleep(3)


@logger.catch
async def main():
    global clicker
    await init()
    # clients = get_clients()
    # clicker_clients = [await run_client(client) for client in clients]
    # clicker = clicker_clients[0]
    # click_handler.setup(clicker_clients)

    loop = asyncio.get_event_loop()  # Позволяет запускать в 2 потока
    loop.run_in_executor(ProcessPoolExecutor(1), test)
    dp.include_router(router)
    # dp.startup.register(click_startup)
    await dp.start_polling(bot)
    print(123)



if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level=LOG_LEVEL, enqueue=True, colorize=True)
    logger.add('debug_log.log', level='INFO', enqueue=True, retention='3 days')
    asyncio.run(main())



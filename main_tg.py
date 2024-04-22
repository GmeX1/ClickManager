import asyncio
import sys
import traceback

from aiogram import Bot, Dispatcher
from aiogram.client.session import aiohttp
from loguru import logger
from Private import TOKEN
from app.handlers import router

from db.functions import init, db_callbacks_get_type, db_stats_get_session
from tortoise.connection import connections

bot = Bot(token=TOKEN)
dp = Dispatcher()
CAT_API_URL = 'https://api.thecatapi.com/v1/images/search?mime_types=gif'


async def get_cat_gif():
    async with aiohttp.ClientSession() as session:
        async with session.get(CAT_API_URL) as response:
            data = await response.json()
            gif_url = data[0]['url']
            return gif_url


async def callback_handler():
    await init()
    # Выдаёт ошибку
    stop = True
    while stop:
        try:
            callbacks = await db_callbacks_get_type('stats')
            if len(callbacks) > 0:
                for callback in callbacks:
                    gif_url = await get_cat_gif()
                    res = await db_stats_get_session(callback.id_tg)
                    await bot.send_animation(chat_id=callback.id_tg, caption=f'За последнюю сессию вы '
                                                                             f'заработали: {res.summary}\n'
                                                                             f'Бустов было куплено: {0} \n'
                                                                             f'Совершено кликов: {res.clicked}',
                                             animation=gif_url)
                    await callback.delete()
            await asyncio.sleep(1)
        except Exception as ex:
            traceback.print_tb(ex.__traceback__)


async def main_tg():
    # await init()
    dp.include_router(router)
    await asyncio.gather(callback_handler(), dp.start_polling(bot))


if __name__ == '__main__':
    logger.add(sys.stderr, level='DEBUG', enqueue=True, colorize=True)
    try:
        asyncio.run(main_tg())
    except KeyboardInterrupt:
        asyncio.run(connections.close_all(discard=True))
        print('Exit')

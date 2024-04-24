import asyncio
import sys
import traceback
from threading import Event

from aiogram import Bot, Dispatcher
from loguru import logger

from Private import TOKEN, admin
from app.core.utils.exceptions import StopSignal
from app.core.utils.scripts import get_cat_gif
from app.handlers import router
from db.functions import db_callbacks_get_type, db_stats_get_session, init

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def callback_handler(event: Event):  # TODO: сделать смайлики
    await init()
    runner = True
    while runner:
        try:
            if event.is_set():
                runner = False
                raise StopSignal('Frontend: флажок найден')

            stats = await db_callbacks_get_type('stats')
            if len(stats) > 0:
                for callback in stats:
                    gif_url = await get_cat_gif()
                    res = await db_stats_get_session(callback.id_tg)
                    caption = [f'За последнюю сессию вы заработали: {round(res.summary)}',
                               f'Бустов было куплено: {round(res.boosts_bought)}',
                               f'Совершено кликов: {round(res.clicked)}',
                               f'К долгу было прибавлено: {round(res.debt)}']
                    if callback.value == 'limit':
                        caption.append('')
                        caption.append('ВНИМАНИЕ! Ваш аккаунт достиг суточного лимита по сумме чеков.')
                        caption.append(
                            'Пожалуйста, переведите в рейтинг больше очков, чтобы не ударяться в порог в дальнейшем')
                    await bot.send_animation(
                        chat_id=callback.id_tg,
                        caption='\n'.join(caption),
                        animation=gif_url
                    )
                    await callback.delete()
            joins = await db_callbacks_get_type('join')
            if len(joins) > 0:
                for callback in joins:
                    value = eval(callback.value)
                    for admin_id in admin:
                        await bot.send_message(
                            chat_id=admin_id,
                            text='\n'.join(['⚠️К системе подключён новый пользователь!',
                                            f'Никнейм: @{value["link"]}',
                                            f'Имя: {value["name"]}'])
                        )
                    await callback.delete()
            await asyncio.sleep(1)
        except RuntimeError as ex:
            # logger.error(ex)
            logger.warning('Frontend: что-то взаимодействует с БД, ждём разблокировки...')
            await asyncio.sleep(2.3)
        except StopSignal as ex:
            raise ex
        except Exception as ex:
            traceback.print_tb(ex.__traceback__)


async def main_tg(event: Event):
    await init()
    dp.include_router(router)
    try:
        logger.info('Запуск цикла frontend...')
        await asyncio.gather(callback_handler(event), dp.start_polling(bot))
    except StopSignal:
        logger.warning('Закрываем frontend...')


if __name__ == '__main__':
    logger.add(sys.stderr, level='DEBUG', enqueue=True, colorize=True)
    try:
        asyncio.run(main_tg(Event()))
    except KeyboardInterrupt:
        logger.info('Закрываем frontend...')

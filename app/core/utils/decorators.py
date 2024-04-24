import asyncio
import traceback

from loguru import logger
from pyrogram.errors import AuthKeyUnregistered
from pyrogram.errors.exceptions.unauthorized_401 import AuthKeyUnregistered as AuthKeyUnregistered_401


def db_handler(tries=float('inf')):
    def wrapper(func):
        async def wrap(*args, **kwargs):
            nonlocal tries
            cur_tries = tries
            while cur_tries > 0:
                try:
                    cur_tries -= 1
                    result = await func(*args, **kwargs)
                    return result
                except RuntimeError:
                    logger.debug('Что-то уже заняло бд, ожидаем...')
                    await asyncio.sleep(1.5)

        return wrap

    return wrapper


def request_handler(tries=3, log=False):
    """
    Декоратор для функций, производящих POST/GET запросы. Его функция - отслеживать статус запроса, делать повторные
    попытки при возникновении проблем, облегчать ведение логов при наличии ошибок.
    Позволяет значительно сократить количество повторяющегося кода.
    """
    if log:
        logger.debug(f'Вошёл в обработчик запросов, попыток: {tries}')

    async def get_status(response):
        """
        Если вместе с результатом запроса возвращаются другие данные.
        *ОБЯЗАТЕЛЬНО* ставить результат запроса В САМЫЙ КОНЕЦ
        """
        try:
            if len(response) > 1:
                status = response[-1].status
            else:
                status = response.status
        except TypeError:
            status = response.status
        return status

    def wrapper(func):
        if log:
            logger.debug(f'Вошёл во wrapper с функцией: {func}')

        async def wrap(*args, **kwargs):
            if log:
                logger.debug(f'Вошёл в async wrap с: {args}, {kwargs}')
                await logger.complete()

            nonlocal tries
            cur_tries = tries
            while cur_tries > -1:
                try:
                    if log:
                        logger.debug(f'Пытаемся сделать запрос...')
                    result = await func(*args, **kwargs)  # Здесь выполняется оборачиваемая функция

                    status = await get_status(result)
                    if status != 200:
                        logger.error(f'Статус запроса: {status}')
                        logger.debug(await result.text())
                        # raise Exception(result, status)

                    return result
                except (TimeoutError, asyncio.TimeoutError):
                    logger.warning('Таймаут! Спим 10 секунд...', backtrace=False, diagose=False)
                    await asyncio.sleep(10)
                    cur_tries -= 1
                except (AuthKeyUnregistered, AuthKeyUnregistered_401) as auth:
                    raise auth
                except Exception as ex:
                    logger.critical(f'Неизвестная ошибка от {ex.__class__.__name__}: {ex}')
                    traceback.print_tb(ex.__traceback__)
                    return None
                await logger.complete()
            else:
                logger.error('Закончились попытки подключения! Попробуйте позже.')
                await logger.complete()
                return None

        return wrap

    return wrapper

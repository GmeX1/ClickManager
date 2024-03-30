import asyncio

from loguru import logger


def request_handler(tries=10, log=False):
    if log:
        logger.debug(f'Got into request decorator, tries: {tries}')

    def wrapper(func):
        if log:
            logger.debug(f'Got into wrapper with: {func}')

        async def wrap(*args, **kwargs):
            if log:
                logger.debug(f'Got into async wrap with: {args}, {kwargs}')
                await logger.complete()

            nonlocal tries
            while tries > 0:
                try:
                    if log:
                        logger.debug(f'Trying to request...')
                    result = func(*args, **kwargs)
                    return await result
                except TimeoutError or asyncio.TimeoutError:
                    tries -= 1
                    logger.exception('Таймаут! Спим 10 секунд...')
                    await asyncio.sleep(10)
                except Exception as ex:
                    logger.critical(f'Неизвестная ошибка от {ex.__class__.__name__}: {ex}')
                    return None
                await logger.complete()
            else:
                logger.error('Закончились попытки подключения! Попробуйте позже.')
                await logger.complete()
                return None

        return wrap

    return wrapper

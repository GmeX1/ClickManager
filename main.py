import asyncio
import sys

from loguru import logger
from python_socks import ProxyConnectionError
from core.proxy import ProxyHandler
from core.utils.scripts import get_clients, run_client
from temp_vars import LOG_LEVEL
from asyncio import IncompleteReadError

clients, tasks, clicker_clients = list(), list(), list()
proxies = ProxyHandler()


async def async_input():  # TODO: Инпут работает всего пару раз, а потом перестаёт вызываться.
    """
    ВНИМАНИЕ!!!! Инпут работает очень криво, в связи с чем команду можно вводить всего несколько раз :(
    Использовать ТОЛЬКО в качестве примера того, как можно соеденить ТГ бота с клиентами (количество не важно)
    """
    global clicker_clients
    loop = asyncio.get_event_loop()
    while True:
        msg = await loop.run_in_executor(None, input, 'Пичатаи: ')
        if msg == 'stop':
            for client in clicker_clients:
                client.do_click = 0
        elif msg == 'start':
            for client in clicker_clients:
                client.do_click = 1
        elif msg == 'end':
            for client in clicker_clients:
                client.do_click = 2
            break
        await asyncio.sleep(0.05)
    print('return')
    return None


async def decorator_handler(client):  # TODO: Иногда появляется Cloudflare и просит включить куки :/
    global proxies, clients
    update = False
    while client.do_click != 2:
        try:
            if update:
                if len(proxies.good_proxies) == 0:
                    proxies.update_proxies(proxies.get_proxies(), int(len(clients) * 1.5))
                logger.warning('UPDATE')
                update_try = await client.update_proxy(proxies.get_proxy())
                if update_try:
                    update = False
                else:
                    logger.error('Не удалось обновить прокси!')
                    raise ProxyConnectionError
            result = await client.run()
        except AttributeError as ex:
            if 'NoneType' in repr(ex) or 'json' in repr(ex):
                logger.debug('Меняем прокси...')
                update = True
            else:
                logger.debug(f'Неизвестная ошибка атрибута: {ex}')
        except (ProxyConnectionError, TimeoutError, OSError, IncompleteReadError) as ex:
            logger.debug(f'Меняем прокси... {ex}')
            update = True
        except Exception as ex:
            logger.critical(f'Неизвестная ошибка от {ex.__class__.__name__}: {ex}')
            await client.stop()
            break
        finally:
            await logger.complete()


@logger.catch  # Должно помочь с трейсингом ошибок
async def run_tasks():  # Код грязный. Почищу, когда разберусь с дистанционным управлением аккаунтами
    global clients, clicker_clients, tasks, proxies
    clients = get_clients()
    proxies.update_proxies(proxies.get_proxies(), int(len(clients) * 1.5))
    clicker_clients = [await run_client(client, proxies.get_proxy()) for client in clients]
    tasks = [asyncio.create_task(decorator_handler(client)) for client in clicker_clients]
    # tasks.append(asyncio.create_task(async_input()))  # Подключение инпута
    await asyncio.gather(*tasks)


# TODO: ввести ядро под каждую сессию в threading
if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level=LOG_LEVEL, enqueue=True, colorize=True)
    logger.add('debug_log.log', level='INFO', enqueue=True, retention='3 days')
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_tasks())

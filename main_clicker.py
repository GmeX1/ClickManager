import asyncio
import sys
from asyncio import IncompleteReadError

from tortoise.connection import connections
from loguru import logger
from python_socks import ProxyConnectionError, ProxyTimeoutError
import traceback
from app.core.proxy import ProxyHandler
from app.core.utils.scripts import get_clients, run_client
from db.functions import init, db_callbacks_get_user, db_callbacks_get_type, db_callbacks_add, db_settings_update_user
from temp_vars import LOG_LEVEL
from temp_vars_local import RECEIPTS
from pyrogram import Client
from time import time
from pyrogram.errors.exceptions.unauthorized_401 import AuthKeyUnregistered as AuthKeyUnregistered_401
from pyrogram.errors import AuthKeyUnregistered
import os
clients, clicker_clients = list(), list()
proxies = ProxyHandler()


async def async_input():
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

async def session_checker(task_group):
    """Дополнительный модуль, запускаемый рядом с кликерами для добавления доп. сессий"""
    global clients, clicker_clients
    await init()
    while True:
        callbacks = await db_callbacks_get_type('active')
        if callbacks:
            for callback in callbacks:
                pack = (callback.id_tg, Client(str(callback.id_tg), session_string=callback.value))
                clients.append(pack)
                client = await run_client(*pack)
                clicker_clients.append(client)

                task_group.create_task(decorator_handler(client))
                await callback.delete()
        logger.trace('CHECKING CALLBACK')
        await asyncio.sleep(10)


async def decorator_handler(client):  # Иногда появляется Cloudflare и просит включить куки :/
    global proxies, clients
    await init()
    update = False
    client.do_click = 2
    receipt_timer = 0  # Таймер для активации чеков
    while client.do_click != 3:
        try:
            if update:
                if len(proxies.good_proxies) == 0:
                    proxies.update_proxies(proxies.get_proxies(), round(len(clients) * 1.5))
                update_try = await client.update_proxy(proxies.get_proxy())
                if update_try:
                    update = False
                else:
                    logger.error('Не удалось обновить прокси!')
                    raise ProxyConnectionError
            if client.do_click == 2:
                row = await db_callbacks_get_user(id_tg=client.id, column='do_click')
                if row:
                    client.do_click = int(row.value)
                    await row.delete()
                    logger.debug(f'Статус кликера {client.id}: {row.value}')
                else:
                    await asyncio.sleep(3)
            else:
                await client.run()
            if client.id in RECEIPTS:
                if time() - receipt_timer > 30:
                    statuses = await db_callbacks_get_type(column='receipt')
                    for status in statuses:
                        if status:
                            value = eval(status.value)
                            if client.id in value['ids']:
                                logger.debug(
                                    f'{client.id} | Получен callback на активацию: {value["receiptId"]}')
                                await client.receipt_activate(value['receiptId'])
                                value['ids'].remove(client.id)
                                if len(value['ids']) > 0:
                                    await db_callbacks_add(status.id_tg, status.column, str(value))
                                await status.delete()
                        await asyncio.sleep(1)
                    receipt_timer = time()

        except AttributeError as ex:
            if 'NoneType' in repr(ex) and 'json' in repr(ex):
                logger.debug('Меняем прокси...')
                update = True
            else:
                logger.debug(f'Неизвестная ошибка атрибута: {ex}')
                traceback.print_tb(ex.__traceback__)
        except (ProxyConnectionError, TimeoutError, OSError, IncompleteReadError, ProxyTimeoutError,
                ConnectionResetError) as ex:
            logger.debug(f'Меняем прокси... {ex}')
            update = True
        except (AuthKeyUnregistered_401, AuthKeyUnregistered):
            logger.error('Пользователь закрыл сессию! Завершаем работу...')
            await client.stop()
            await db_settings_update_user(str(client.id), {'active': False})
            if client.client.is_connected:
                await client.client.terminate()
            os.remove(f'{str(client.id)}.session')
            break
        except Exception as ex:
            logger.critical(f'Неизвестная ошибка от {ex.__class__.__name__}: {ex}')
            traceback.print_tb(ex.__traceback__)
            await client.stop()
            break
        finally:
            await logger.complete()


@logger.catch  # Помогает с трейсингом ошибок
async def run_tasks():
    global clients, clicker_clients, proxies
    await init()
    clients = await get_clients()
    proxies.update_proxies(proxies.get_proxies(), round(len(clients) * 1.5))
    clicker_clients = [await run_client(*client, proxies.get_proxy()) for client in clients]
    async with asyncio.TaskGroup() as task_group:
        for client in clicker_clients:
            if client is not None:
                task_group.create_task(decorator_handler(client))
        task_group.create_task(session_checker(task_group))
    # tasks.append(asyncio.create_task(async_input()))  # Подключение инпута
    # [await task for task in tasks]


async def stop_app():
    global proxies, clicker_clients
    await proxies.close()
    for client in clicker_clients:
        await client.stop()
    await connections.close_all(discard=True)


if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level=LOG_LEVEL, enqueue=True, colorize=True)
    logger.add('debug_log.log', level='INFO', enqueue=True, retention='3 days')
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(run_tasks())
    except KeyboardInterrupt:
        asyncio.run(stop_app())


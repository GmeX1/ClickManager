import asyncio
import os
import sys
import traceback
from asyncio import IncompleteReadError
from threading import Event
from time import time

from loguru import logger
from pyrogram import Client
from pyrogram.errors import AuthKeyUnregistered
from pyrogram.errors.exceptions.unauthorized_401 import AuthKeyUnregistered as AuthKeyUnregistered_401
from python_socks import ProxyConnectionError, ProxyTimeoutError
from app.core.utils.exceptions import StopSignal
from app.core.proxy import ProxyHandler
from app.core.utils.scripts import get_clients, run_client
from db.functions import db_callbacks_add, db_callbacks_get_type, db_callbacks_get_user, db_settings_update_user, init
from temp_vars import LOG_LEVEL
from privates import RECEIPTS

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


async def session_checker(task_group: asyncio.TaskGroup, event: Event):
    """Дополнительный модуль, запускаемый рядом с кликерами для добавления доп. сессий"""
    global clients, clicker_clients
    await init()
    runner = True
    while runner:
        try:
            if event.is_set():
                runner = False
                await stop_app()
                raise StopSignal('Backend: флажок найден')

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
            await asyncio.sleep(3)
        except RuntimeError:
            logger.warning('Backend: что-то взаимодействует с БД, ждём разблокировки...')
            await asyncio.sleep(4.4)
        except StopSignal as ex:
            raise ex


async def decorator_handler(client):  # Иногда появляется Cloudflare и просит включить куки :/
    global proxies, clients
    await init()
    update = False
    client.do_click = 2
    receipt_timer = 0  # Таймер для активации чеков
    receipt_blacklist = set()
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
                            if client.id == value['id'] and value["receiptId"] not in receipt_blacklist:
                                logger.debug(
                                    f'{client.id} | Получен callback на активацию: {value["receiptId"]}')
                                activate = await client.receipt_activate(value['receiptId'])
                                if activate:
                                    await status.delete()
                                receipt_blacklist.add(value["receiptId"])
                        await asyncio.sleep(0.3)
                    receipt_timer = time()
            await asyncio.sleep(0.01)

        except AttributeError as ex:
            if 'NoneType' in repr(ex):
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


async def stop_app():
    global proxies, clicker_clients, clients
    logger.warning('Закрываем backend...')
    proxies.close()
    for client in clicker_clients:
        if client.do_click == 1:
            client.do_click = 3
        else:
            client.do_click = 3
            await client.stop()


@logger.catch  # Помогает с трейсингом ошибок
async def run_tasks(event: Event):
    global clients, clicker_clients, proxies
    await init()
    clients = await get_clients()
    proxies.update_proxies(proxies.get_proxies(), round(len(clients) * 1.5))
    clicker_clients = [await run_client(*client, proxies.get_proxy()) for client in clients]
    try:
        logger.info('Запуск цикла backend...')
        async with asyncio.TaskGroup() as task_group:
            for client in clicker_clients:
                if client is not None:
                    task_group.create_task(decorator_handler(client))
            task_group.create_task(session_checker(task_group, event))
    except ExceptionGroup as group:
        for ex in group.exceptions:
            if ex.__class__ == StopSignal:
                pass
                # await stop_app()
            else:
                raise ex
    # tasks.append(asyncio.create_task(async_input()))  # Подключение инпута
    # [await task for task in tasks]


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logger.remove()
    logger.add(sys.stderr, level=LOG_LEVEL, enqueue=True, colorize=True)
    logger.add('debug_log.log', level=LOG_LEVEL, enqueue=True, retention='3 days')
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    my_event = Event()
    try:
        asyncio.run(run_tasks(my_event))
    except KeyboardInterrupt:
        logger.warning('Закрываем backend...')
        my_event.set()
        # asyncio.run(stop_app())

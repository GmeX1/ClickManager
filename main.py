import asyncio
import sys

from loguru import logger

from core.utils.scripts import get_clients, run_client
from temp_vars import LOG_LEVEL

clients, tasks, clicker_clients = list, list, list


async def async_input():  # TODO: Инпут работает всего пару раз, а потом перестаёт вызываться.
    """
    ВНИМАНИЕ!!!! Инпут работает очень криво, в связи с чем команду можно вводить всего несколько раз :(
    Использовать ТОЛЬКО в качестве примера того, как можно соеденить ТГ бота с клиентами (количество не важно)
    """
    global clicker_clients
    loop = asyncio.get_event_loop()
    msg = await loop.run_in_executor(None, input, 'Пичатаи: ')
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
        loop = asyncio.get_event_loop()
    print('return')
    return None


@logger.catch  # Должно помочь с трейсингом ошибок
async def run_tasks():  # Код грязный. Почищу, когда разберусь с дистанционным управлением аккаунтами
    global clients, clicker_clients, tasks
    clients = get_clients()
    clicker_clients = [await run_client(client) for client in clients]
    tasks = [asyncio.create_task(client.run()) for client in clicker_clients]
    tasks.append(asyncio.create_task(async_input()))  # Подключение инпута
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level=LOG_LEVEL, enqueue=True, colorize=True)
    logger.add('debug_log.log', level='INFO', enqueue=True, rotation='10 MB')
    asyncio.run(run_tasks())

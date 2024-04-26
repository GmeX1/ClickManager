import asyncio
import os
import sys
import threading
import time

from loguru import logger
from tortoise.connection import connections

from main_clicker import run_tasks
from main_tg import main_tg

if __name__ == '__main__':
    stop_signal = threading.Event()
    logger.remove()
    logger.add(sys.stderr, level='DEBUG', enqueue=True, colorize=True)
    logger.add('debug_log.log', level='DEBUG', enqueue=True, retention=2, rotation='3 days')
    threads = [
        threading.Thread(target=asyncio.run, args=(run_tasks(stop_signal),), name='backend'),
        threading.Thread(target=asyncio.run, args=(main_tg(stop_signal),), name='frontend')
    ]
    try:
        logger.info('Запускаем процессы...')
        for thread in threads:
            thread.start()
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        logger.warning('Завершаем работу...')
        stop_signal.set()
        for thread in threads:
            thread.join()
        asyncio.run(connections.close_all(discard=False))
        logger.info('Работа завершена.')
        time.sleep(1)
        os._exit(0)

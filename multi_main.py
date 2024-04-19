from loguru import logger
import sys
import threading
import asyncio
from main_clicker import run_tasks
from main_tg import main_tg


if __name__ == '__main__':  # TODO: Добавить проверку бд в мою часть кода
    logger.remove()
    logger.add(sys.stderr, level='DEBUG', enqueue=True, colorize=True)
    logger.add('debug_log.log', level='DEBUG', enqueue=True, retention=2, rotation='3 days')
    threads = [
        threading.Thread(target=asyncio.run, args=(run_tasks(),), name='backend'),
        threading.Thread(target=asyncio.run, args=(main_tg(),), name='frontend')
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


import sys

from loguru import logger

from utils.scripts import *

if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level='DEBUG', enqueue=True, colorize=True)
    logger.add('debug_log.log', level='TRACE', enqueue=True, rotation='10 MB')
    asyncio.run(run_tasks())

# last_click = client.get_profile()['lastClickSeconds']
# print(client.click(last_click))

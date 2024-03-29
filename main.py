import sys

from loguru import logger

from utils.scripts import *

if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, colorize=True, enqueue=True)
    logger.add('debug_log.log', level='TRACE')
    asyncio.run(run_tasks())

# last_click = client.get_profile()['lastClickSeconds']
# print(client.click(last_click))

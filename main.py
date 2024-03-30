from core.utils.scripts import run_client, get_session_names
from loguru import logger
import sys
import asyncio


async def run_tasks():
    tasks = [asyncio.create_task(run_client(item)) for item in get_session_names()]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level='DEBUG', enqueue=True, colorize=True)
    logger.add('debug_log.log', level='TRACE', enqueue=True, rotation='10 MB')
    asyncio.run(run_tasks())

# last_click = client.get_profile()['lastClickSeconds']
# print(client.click(last_click))

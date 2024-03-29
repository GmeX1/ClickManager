import asyncio
import glob

from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
from core.Clicker import ClickerClient
from temp_vars import BASE_URL


def get_session_names():
    session_names = glob.glob('*.session')
    session_names = list(map(lambda x: x.split('\\')[-1].split('.')[0], session_names))
    # session_names = list(map(lambda x: x.split('.')[0], session_names))
    return session_names


async def run_tasks():
    tasks = [asyncio.create_task(run_client(item)) for item in get_session_names()]
    await asyncio.gather(*tasks)


async def run_client(session_name):
    client = Client(session_name)
    await client.start()
    raw_peer = await client.resolve_peer('wmclick_bot')
    web_app = await client.invoke(
        RequestWebView(
            peer=raw_peer,
            bot=raw_peer,
            platform='android',
            from_bot_menu=False,
            url=f'{BASE_URL}/users/me'
        ))
    await ClickerClient(client, web_app).run()

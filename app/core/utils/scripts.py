import glob
import os

from aiogram.client.session import aiohttp
from loguru import logger
from pyrogram import Client
from pyrogram.errors import ActiveUserRequired, AuthKeyDuplicated, AuthKeyInvalid, AuthKeyPermEmpty, \
    AuthKeyUnregistered, SessionExpired, SessionPasswordNeeded, SessionRevoked, UserDeactivated, UserDeactivatedBan
from pyrogram.raw.functions.messages import RequestWebView

from app.core.clicker import ClickerClient
from db.functions import db_settings_check_user_exists, db_settings_get_user, db_settings_update_user
from temp_vars import BASE_URL


async def get_cat_gif():
    url = 'https://api.thecatapi.com/v1/images/search?mime_types=gif'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            gif_url = data[0]['url']
            return gif_url


def get_session_names():
    session_names = glob.glob('*.session')
    session_names = list(map(lambda x: x.split('\\')[-1].split('.')[0], session_names))
    return session_names


async def get_clients(check_db=True):
    """
    :param check_db: проверять ли айди (имя сессии) на существование в бд
    :return: Список клиентов Pyrogram
    """
    sessions = get_session_names()
    if check_db:
        sessions = [session for session in sessions if await db_settings_check_user_exists(session)]
    clients = [(session_name, Client(session_name)) for session_name in sessions]
    return clients


async def run_client(sess_name: str, client: Client, proxy=None):
    user = await db_settings_get_user(int(sess_name))
    status = await client_startup_auth_check(client)
    if not status:
        logger.warning(f'Найдена недействительная сессия: {sess_name}')
        if user.active != 0:
            await db_settings_update_user(int(sess_name), {'active': False})
        if client.is_connected:
            await client.terminate()
        os.remove(f'{sess_name}.session')
        return None
    user_id = (await client.get_me()).id
    raw_peer = await client.resolve_peer('wmclick_bot')
    web_app = await client.invoke(
        RequestWebView(
            peer=raw_peer,
            bot=raw_peer,
            platform='android',
            from_bot_menu=False,
            url=f'{BASE_URL}/users/me'
        ))
    if user.active == 0:
        await db_settings_update_user(user_id, {'active': True})
    return ClickerClient(client, user_id, web_app, proxy)


async def client_startup_auth_check(client: Client):
    try:
        info = await client.start()
        if info:
            return True
        return False
    except (
            ActiveUserRequired, AuthKeyInvalid, AuthKeyPermEmpty, AuthKeyUnregistered, AuthKeyDuplicated,
            SessionExpired,
            SessionPasswordNeeded, SessionRevoked, UserDeactivated, UserDeactivatedBan
    ):
        return False

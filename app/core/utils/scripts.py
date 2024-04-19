import glob
import os

from pyrogram import Client
from pyrogram.errors import ActiveUserRequired, AuthKeyDuplicated, AuthKeyInvalid, AuthKeyPermEmpty, \
    AuthKeyUnregistered, SessionExpired, SessionPasswordNeeded, SessionRevoked, UserDeactivated, UserDeactivatedBan
from pyrogram.raw.functions.messages import RequestWebView
from loguru import logger
from app.core.clicker import ClickerClient
from temp_vars import BASE_URL
from db.functions import db_settings_check_user_exists, db_settings_update_user, db_settings_get_user


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


async def run_client(sess_name, client, proxy=None):
    user = await db_settings_get_user(sess_name)
    status = await client_startup_auth_check(client)
    if not status:
        logger.warning(f'Найдена недействительная сессия: {sess_name}')
        if user.active != 0:
            await db_settings_update_user(sess_name, {'active': False})
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

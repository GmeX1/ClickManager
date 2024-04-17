import glob

from pyrogram import Client
from pyrogram.errors import ActiveUserRequired, AuthKeyDuplicated, AuthKeyInvalid, AuthKeyPermEmpty, \
    AuthKeyUnregistered, SessionExpired, SessionPasswordNeeded, SessionRevoked, UserDeactivated, UserDeactivatedBan
from pyrogram.raw.functions.messages import RequestWebView

from core.clicker import ClickerClient
from db.functions import db_get_user
from temp_vars import BASE_URL


def get_session_names():
    session_names = glob.glob('*.session')
    session_names = list(map(lambda x: x.split('\\')[-1].split('.')[0], session_names))
    return session_names


def get_clients():
    sessions = get_session_names()
    clients = [Client(session_name) for session_name in sessions]
    return clients


async def run_client(client, proxy=None):
    await client.start()
    user_id = (await client.get_me())['id']
    raw_peer = await client.resolve_peer('wmclick_bot')
    web_app = await client.invoke(
        RequestWebView(
            peer=raw_peer,
            bot=raw_peer,
            platform='android',
            from_bot_menu=False,
            url=f'{BASE_URL}/users/me'
        ))
    settings = await db_get_user(user_id)
    settings = {
        'BUY_CLICK': settings.BUY_CLICK,
        'BUY_MINER': settings.BUY_MINER,
        'BUY_ENERGY': settings.BUY_ENERGY,
        'BUY_MAX_LVL': settings.BUY_MAX_LVL
    }
    return ClickerClient(client, user_id, settings, web_app, proxy)


async def client_auth_check(client: Client):
    try:
        info = await client.get_me()
        if info:
            return True
        return False
    except (
            ActiveUserRequired, AuthKeyInvalid, AuthKeyPermEmpty, AuthKeyUnregistered, AuthKeyDuplicated,
            SessionExpired,
            SessionPasswordNeeded, SessionRevoked, UserDeactivated, UserDeactivatedBan
    ):
        return False

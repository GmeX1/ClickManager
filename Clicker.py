import hmac
from hashlib import sha256
from urllib.parse import unquote

import requests
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView

from temp_vars import BASE_URL, ENC_KEY


class ClickerClient:
    """Основной клиент кликера, создаваемый по имени сессии Pyrogram."""

    def __init__(self, session_name: str):
        """Создание клиента pyrogram, создание сессии для запросов"""
        self.client = Client(session_name)
        self.client.start()
        raw_peer = self.client.resolve_peer('wmclick_bot')
        self.webviewApp = self.client.invoke(
            RequestWebView(
                peer=raw_peer,
                bot=raw_peer,
                platform='android',
                from_bot_menu=False,
                url=f'{BASE_URL}/users/me'
            ))
        self.session = requests.sessions.Session()
        self.session.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": 'keep-alive',
            "Host": "arbuz.betty.games",
            "Origin": "https://arbuzapp.betty.games",
            "Referer": "https://arbuzapp.betty.games/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "TE": "trailers",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 "
                          "Mobile Safari/537.36",
            "X-Telegram-Init-Data": self.get_init_data()
        }

    def get_init_data(self):
        """Получение init даты для шапки запроса"""
        data = self.webviewApp.url.split('#tgWebAppData=')[1].replace("%3D", "=").split('&tgWebAppVersion=')[
            0].replace("%26", "&")
        user = data.split("&user=")[1].split("&auth")[0]
        data = data.replace(user, unquote(user))
        return data

    def get_profile(self):
        result = self.session.get(f'{BASE_URL}/users/me', timeout=5)
        return result.json()

    def click(self, click_tick):
        msg = f'{self.client.get_me().id}:{click_tick}'.encode()
        hashed = hmac.new(ENC_KEY.encode('UTF-8'), msg, sha256).hexdigest()
        result = self.session.post(f'{BASE_URL}/click/apply', timeout=5, json={
            'count': 1,  # TODO: Сделать вариацию в кликах
            'hash': hashed
        })
        return result.json()

    def stop(self):
        self.client.stop()

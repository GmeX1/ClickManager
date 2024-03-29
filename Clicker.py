import requests
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
from urllib.parse import unquote


class ClickerClient:
    def __init__(self, session_name: str):
        self.client = Client(session_name)
        self.client.start()
        raw_peer = self.client.resolve_peer('wmclick_bot')
        self.webviewApp = self.client.invoke(
            RequestWebView(
                peer=raw_peer,
                bot=raw_peer,
                platform='android',
                from_bot_menu=False,
                url='https://arbuz.betty.games/api/users/me'
            ))
        self.session = requests.sessions.Session()
        self.session.headers = {
            "Host": "arbuz.betty.games",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": 'keep-alive',
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

    def run(self):
        result = self.session.get('https://arbuz.betty.games/api/users/me')
        print(result.json())

    def stop(self):
        self.client.stop()

    def get_init_data(self):
        data = self.webviewApp.url.split('#tgWebAppData=')[1].replace("%3D", "=").split('&tgWebAppVersion=')[
            0].replace("%26", "&")
        user = data.split("&user=")[1].split("&auth")[0]
        data = data.replace(user, unquote(user))
        return data

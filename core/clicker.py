import asyncio
import hmac
import random
from hashlib import sha256
from time import time
from urllib.parse import unquote

import aiohttp
from loguru import logger
from pyrogram import Client
from pyrogram.raw.types.web_view_result_url import WebViewResultUrl

from temp_vars import BASE_URL, CLICKS_AMOUNT, CLICKS_SLEEP, ENC_KEY, BUY_CLICK, BUY_MINER, BUY_ENERGY, BUY_MAX_LVL
from .utils.decorators import request_handler


class ClickerClient:
    """Основной клиент кликера, создаваемый по имени сессии Pyrogram."""

    def __init__(self, client: Client, web_app: WebViewResultUrl):
        """Создание клиента pyrogram, создание сессии для запросов"""
        self.client = client
        self.webviewApp = web_app
        self.session = aiohttp.ClientSession(headers={
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
        })
        self.buy_type = {
            'CLICK_POWER': BUY_CLICK,
            'MINER': BUY_MINER,
            'ENERGY_RECOVERY': BUY_ENERGY
        }
        self.buy_listing = {
            'CLICK_POWER': list(),
            'CLICK_POWER_MINS': list(),
            'MINER': list(),
            'MINER_MINS': list(),
            'ENERGY_RECOVERY': list(),
            'ENERGY_RECOVERY_MINS': list()
        }
        self.do_click = 1

    def get_init_data(self):
        """Получение init даты для шапки запроса"""
        data = self.webviewApp.url.split('#tgWebAppData=')[1].replace("%3D", "=")
        data = data.split('&tgWebAppVersion=')[0].replace("%26", "&")
        user = data.split("&user=")[1].split("&auth")[0]
        data = data.replace(user, unquote(user))
        return data

    async def sort_boosts(self):  # TODO: Сделать разбив всех бустов, купленных бустов. Вывести минимальные цены.
        all_response = await self.get_boosts_all()
        all_data = await all_response.json()
        all_data = all_data.get('items', None)

        purchased_response = await self.get_boosts_purchased()
        purchased_data = await purchased_response.json()
        purchased_data = purchased_data.get('items', None)

        logger.debug(all_data)
        logger.debug(purchased_data)
        await logger.complete()

        # if all_data is not None:
        #     click_power = map(lambda x: {x["id"], filter(lambda x: x.get('type') == 'CLICK_POWER', all_data))
        #     self.buy_listing['CLICK_POWER'] =
        #     self.buy_listing['CLICK_POWER'] = map()
        #     self.buy_listing['MINER'] = list(filter(lambda x: x.get('type') == 'MINER', all_data))
        #     self.buy_listing['ENERGY_RECOVERY'] = list(filter(lambda x: x.get('type') == 'ENERGY_RECOVERY', all_data))
        #     logger.debug('Списки магазина успешно обновлены.')
        # else:
        #     logger.critical('В json магазина отсутствует список товаров!')

    @request_handler()
    async def get_profile_request(self):
        result = await self.session.get(f'{BASE_URL}/users/me', timeout=10)
        return result

    @request_handler()
    async def get_boosts_all(self):
        result = await self.session.get(f'{BASE_URL}/boosts/metas', timeout=10)
        return result

    @request_handler()
    async def get_boosts_purchased(self):
        result = await self.session.get(f'{BASE_URL}/boosts/active', timeout=10)
        return result

    @request_handler()
    async def buy_boost(self, meta_id: int):
        result = await self.session.post(f'{BASE_URL}/boosts/purchase', timeout=10, json={
            'metaId': meta_id
        })
        return result

    async def skins(self, skin_id):
        """
        Нашёл функционал для скинов, ковыряясь в приложении через FireFox.
        Get запросы дают адекватные ответы, но что-либо купить пока что невозможно, ибо в самом приложении нет скинов.
        (Видимо, *пока что* нет скинов)
        """
        res_get1 = await self.session.get(f'{BASE_URL}/skin/all', timeout=10)  # Все скины
        res_get2 = await self.session.get(f'{BASE_URL}/skin/available', timeout=10)  # Доступные скины
        # Покупка скина
        res_post = await self.session.post(f'{BASE_URL}/skin/activate', timeout=10, json={'ids': [skin_id]})
        return [res_get1, res_get2, res_post]

    @request_handler()
    async def click(self, count, click_tick):
        logger.debug(f'Пробуем сделать {count} клик(ов)...')
        me = await self.client.get_me()
        msg = f'{me.id}:{click_tick}'.encode()
        hashed = hmac.new(ENC_KEY.encode('UTF-8'), msg, sha256).hexdigest()
        result = await self.session.post(f'{BASE_URL}/click/apply', timeout=10, json={
            'count': count,
            'hash': hashed
        })
        return hashed, result

    async def run(self):  # TODO: Сделать сбор статистики за цикл работы.
        try:
            profile = await self.get_profile_request()
            if profile is None:
                raise Exception('Не удалось получить профиль!')
            elif profile.status != 200:
                raise Exception(f'Не удалось получить профиль! Код сервера: {profile.status}')

            profile = await profile.json()
            logger.debug(f'Получена информация о профиле {profile.get("id", 0)}')
            await logger.complete()
            if profile.get('banned', ''):
                raise Exception('Ваш аккаунт был заблокирован приложением! Останавливаем работу...')

            energy = profile.get('energy', 0)
            balance = profile.get('clicks', 0)
            last_click = profile.get('lastClickSeconds', 0)

            recovery_time = profile.get('energyLimit', 0) // profile.get('energyBoostSum', 0)
            recovery_start = -1

            await self.sort_boosts()

            logger.debug(f'Текущая информация о профиле:\nЭнергия: {energy}\nВремя восстановления энергии:'
                         f'{recovery_time}\nБаланс:{balance}\nВремя последнего клика:{last_click}')
            while True:
                if any(self.buy_type.values()):  # TODO: Система авто покупок + Авто обновление баланса
                    pass

                if self.do_click == 1 and energy > 10 and recovery_start == -1:
                    count = random.randint(CLICKS_AMOUNT[0], min(CLICKS_AMOUNT[1], int(energy)))
                    hashed, click = await self.click(count, last_click)
                    if click.status != 200:
                        logger.error(f'Не удалось сделать клик! Код ошибки: {click.status}. Сплю 30 секунд...')
                        await asyncio.sleep(30)
                    else:
                        click = await click.json()
                        energy = click.get('currentEnergy', 0)
                        last_click = click.get('lastClickSeconds', 0)
                        sleep_time = random.randint(*CLICKS_SLEEP)

                        logger.info(
                            f'Клики ({count}) успешно отправлены!  |  {energy}⚡ | +{click.get("count", 0)}🍉  |  '
                            f'HASH: {hashed}')
                        logger.info(f'Спим {sleep_time} секунд после клика...')
                        await asyncio.sleep(random.randint(*CLICKS_SLEEP))

                elif self.do_click != 2 and energy <= 10 and recovery_start == -1:
                    logger.info(f'Энергия закончилась! Спим {recovery_time} до восстановления...')
                    recovery_start = time()

                elif self.do_click != 2 and recovery_start != -1:
                    if time() - recovery_start >= recovery_time:
                        logger.info('Восстановление энергии закончено, продолжаем работу!')
                        recovery_start = -1

                elif self.do_click == 2:
                    logger.info(f'Останавливаем клиент {profile["id"]}')
                    await logger.complete()
                    await self.stop()
                    break

        except Exception as ex:
            logger.exception(f'Неизвестная ошибка от {ex.__class__.__name__}: {ex}')
            await logger.complete()
            await self.stop()

    async def stop(self):
        await self.session.close()
        await self.client.stop()

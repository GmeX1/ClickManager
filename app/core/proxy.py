import multiprocessing
from random import shuffle

import aiohttp
import requests
from aiohttp_socks import ProxyConnectionError, ProxyConnector, ProxyTimeoutError
from loguru import logger
from requests.exceptions import ConnectTimeout, ConnectionError, ReadTimeout, SSLError


class AsyncProxyHandler:
    """Использование данного класса нежелательно: многопоточная версия хэндлера работает значительно быстрее и
    стабильнее. Очень мала вероятность того, что кто-то продолжит работать над данным классом, поэтому его можно
    считать устаревшим."""

    def __init__(self):
        self.url = ('https://poeai.click/proxy.php/v2/?request=getproxies&protocol=socks4&timeout=5000&country=all&ssl'
                    '=all&anonymity=elite')
        self.url_file = ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4'
                         '/data.txt')
        self.session = aiohttp.ClientSession()
        self.good_proxies = set()
        self.judges = [
            'http://httpbin.org/get?show_env',
            'https://httpbin.org/get?show_env',
            'http://azenv.net/',
            'https://www.proxy-listen.de/azenv.php',
            'http://www.proxyfire.net/fastenv'
            # 'http://proxyjudge.us/azenv.php',
            # 'http://ip.spys.ru/',
            # 'http://www.proxy-listen.de/azenv.php'
        ]
        self.ip = None

    async def get_my_ip(self):
        response = await self.session.get('https://api.ipify.org/')
        if response.status == 200:
            self.ip = await response.text()
            logger.debug(f'Получен ip: {self.ip}')
        else:
            logger.critical(f'Неизвестная ошибка при получении ip: {response.status} ({response})')
            self.ip = None
        await logger.complete()
        return True if self.ip is not None else False

    async def update_proxies(self, amount: int = 10, req_type: str = 'site'):
        if self.ip is None:
            await self.get_my_ip()
        self.good_proxies = set()

        if req_type == 'site':
            request = await self.session.get(self.url)
            if request.status != 200:
                logger.critical(f'Не удалось получить прокси! Код: {request.status} ({await request.text()})')
                return False
            proxies = (await request.text()).split()
        else:
            request = await self.session.get(self.url_file)
            if request.status != 200:
                logger.critical(f'Не удалось получить прокси! Код: {request.status} ({await request.text()})')
                return False
            proxies = list(map(lambda x: x.split('://')[-1], (await request.text()).split()))

        for proxy in proxies:
            result = await self.check_proxy(proxy)
            if result is not None:
                # if any(i in result for i in [  # Проверка на элитность прокси пока что не требуется
                #     'via', 'x-forwarded-for', 'x-forwarded', 'forwarded-for', 'forwarded-for-ip', 'forwarded',
                #     'client-ip', 'proxy-connection'
                # ]):
                if self.ip not in result:
                    self.good_proxies.add(proxy)
                else:
                    logger.warning('Прозрачный прокси пропущен.')
            if len(self.good_proxies) >= amount:
                break

        logger.debug(f'Хорошие прокси: {self.good_proxies}')
        await logger.complete()
        return True

    async def check_proxy(self, address):
        try:
            copy_list = self.judges.copy()
            shuffle(copy_list)
            connector = ProxyConnector.from_url(f'socks4://{address}', verify_ssl=False, timeout_ceil_threshold=15)
            for site in copy_list:
                async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
                    async with await session.get(site) as response:
                        if response.status == 200:
                            logger.debug(address)
                            await logger.complete()
                            return await response.text()
                        else:
                            logger.error(f'{response.status}:{site}')
                    await logger.complete()
            return None
        except (ProxyTimeoutError, ProxyConnectionError) as ex:
            # await session.close()
            logger.error(f'Прокси {address} не работает!\n({ex})')
        except Exception as ex:
            # await session.close()
            logger.critical(f'Неизвестная ошибка {ex.__class__.__name__} при проверке прокси: {ex}')
        await logger.complete()
        return None

    async def close(self):
        await self.session.close()


class ProxyHandler:
    def __init__(self):
        self.url = ('https://poeai.click/proxy.php/v2/?request=getproxies&protocol=socks4&timeout=5000&country=all&ssl'
                    '=all&anonymity=elite')
        self.url_file = ('https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4'
                         '/data.txt')
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "*",
            "Connection": "keep-alive",
        }
        self.good_proxies = set()
        self.blacklist = set()
        self.judges = [
            'http://httpbin.org/get?show_env',
            'https://httpbin.org/get?show_env',
            'http://azenv.net/',
            'https://www.proxy-listen.de/azenv.php',
            'http://www.proxyfire.net/fastenv'
            'http://proxyjudge.us/azenv.php',
            'http://ip.spys.ru/',
            'http://www.proxy-listen.de/azenv.php'
        ]
        self.ip = None

    def get_my_ip(self):
        response = self.session.get('https://api.ipify.org/')
        if response.status_code == 200:
            self.ip = response.text
            logger.debug(f'Получен ip: {self.ip}')
        else:
            logger.critical(f'Неизвестная ошибка при получении ip: {response.status_code} ({response.text})')
            self.ip = None
        return True if self.ip is not None else False

    def get_proxies(self, req_type: str = 'site', recursion=False):
        retries = 0
        while retries < 3:
            try:
                if req_type == 'site':
                    request = self.session.get(self.url)
                    if request.status_code != 200:
                        logger.critical(f'Не удалось получить прокси! Код: {request.status_code} ({request.text})')
                        return None
                    proxies = request.text.split()
                else:
                    request = self.session.get(self.url_file)
                    if request.status_code != 200:
                        logger.critical(f'Не удалось получить прокси! Код: {request.status_code} ({request.text})')
                        return None
                    proxies = list(map(lambda x: x.split('://')[-1], request.text.split()))
                shuffle(proxies)
                return proxies
            except ConnectTimeout:
                retries += 1
        else:
            if not recursion:
                return self.get_proxies('file' if req_type == 'site' else 'site', True)

    def get_proxy(self):
        if len(self.good_proxies) > 0:
            proxy = self.good_proxies.pop()
            self.blacklist.add(proxy)
            return proxy
        return None

    def update_proxies(self, proxies: list[str], amount: int = 10):
        if self.ip is None:
            self.get_my_ip()

        proxies.extend(list(self.good_proxies))
        self.good_proxies = set()
        with multiprocessing.Pool() as p:
            for proxy_addr, result in p.imap_unordered(self.check_proxy, proxies, chunksize=8):
                if result:
                    self.good_proxies.add(proxy_addr)
                if len(self.good_proxies) >= amount:
                    p.terminate()
                    break

        logger.debug(f'Хорошие прокси: {self.good_proxies}')
        return True

    def check_proxy(self, proxy: str):
        proxy_address = f"socks4://{proxy}"
        # if proxy_address in self.blacklist or '45.81.232.17' in proxy_address:
        if proxy_address in self.blacklist:
            return proxy_address, False
        try:
            res = requests.get(
                "https://api.ipify.org?format=json",
                proxies={"http": proxy_address, "https": proxy_address},
                headers=self.headers,
                timeout=1.5
            )
            res.raise_for_status()
            if self.ip not in res:
                return proxy_address, True
            logger.warning('Прозрачный прокси пропущен.')
            return proxy_address, False
        except (ConnectTimeout, SSLError, ConnectionError, ReadTimeout):
            logger.trace(f'Не удалось подключиться: {proxy}')
            return proxy_address, False
        except Exception as ex:
            logger.critical(f'Ошибка {ex.__class__.__name__} при проверке прокси: {ex}')
            return proxy_address, False

    def close(self):
        self.session.close()

# if __name__ == '__main__':  # Для проверки класса прокси
#     handler = ProxyHandler()
#     handler.get_my_ip()
#     timer = time()
#     handler.update_proxies(handler.get_proxies(req_type='site'))
#     print(f'Операция заняла ~{time() - timer:.2f} секунд')

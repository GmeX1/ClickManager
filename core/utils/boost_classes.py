from loguru import logger

from .exceptions import EmptyBoostList, UnknownBoostType


class BoostHandler:
    def __init__(self):
        self.type_list = {
            'CLICK_POWER': BoostList('CLICK_POWER'),
            'MINER': BoostList('MINER'),
            'ENERGY_RECOVERY': BoostList('ENERGY_RECOVERY')
        }
        self.enabled_keys = list()
        self.min_buy = float('inf')
        self.min_upgrade = float('inf')

    def set_keys(self, click: bool = False, miner: bool = False, energy: bool = False):
        """Используется для выбора покупаемых разделов. Если ключ = True: покупать можно"""
        out = list()
        if click:
            out.append('CLICK_POWER')
        if miner:
            out.append('MINER')
        if energy:
            out.append('ENERGY_RECOVERY')
        self.enabled_keys = out.copy()

    def update_data(self, json_data: list[dict] = None, own_data: list[dict] = None, boost_types: list[str] = None,
                    level: int = None):
        """Обновление данных json и статистики"""
        if boost_types is None:
            for key in self.enabled_keys:
                self.type_list[key].update_data(json_data, own_data)
        else:
            for key in boost_types:
                self.type_list[key].update_data(json_data, own_data)
        self.update_stats(boost_types=boost_types, level=level)

    def update_stats(self, boost_types: list[str] = None, level: int = None):
        if boost_types is None:
            for key in self.enabled_keys:
                self.type_list[key].update_stats(level=level)
        else:
            for key in boost_types:
                self.type_list[key].update_stats(level=level)

        self.min_buy = min([self.type_list[i].min_buy for i in self.enabled_keys])
        self.min_upgrade = min([self.type_list[i].min_upgrade for i in self.enabled_keys])

    def get_min_boost(self):
        boosts = filter(lambda x: x is not None, [self.type_list[i].get_min_boost() for i in self.enabled_keys])
        boosts = list(filter(lambda x: x.get_price() == self.get_min_price(), boosts))
        if len(boosts) == 0:
            raise EmptyBoostList('Не удалось получить минимальный по цене буст!')
        elif len(boosts) > 1:
            logger.warning('Найдено более 1 совпадающего по цене буста!')
        return boosts[0]

    def get_min_price(self):
        return min(self.min_buy, self.min_upgrade)

    def get_boost_by_type(self, boost_type: str):
        if boost_type in self.type_list.keys():
            return self.type_list[boost_type]
        raise UnknownBoostType(f'Неизвестный ключ буста: {boost_type}')

    def is_enabled(self):
        return len(self.enabled_keys) > 0


class BoostList:
    # TODO: Выдавать id минимального к покупке/улучшению буста
    def __init__(self, boost_type: str, all_boosts: list[dict] = None, owned_boosts: list[dict] = None):
        self.type = boost_type
        self.boosts: list[Boost] = list()
        self.ids: list[int] = list()
        if all_boosts or owned_boosts:
            self.update_data(all_boosts, owned_boosts)
        self.min_buy = 0
        self.min_upgrade = 0
        self.max_level = 0

    def set_max_level(self, level: int):
        self.max_level = level

    def update_data(self, all_boosts: list[dict] = None, owned_boosts: list[dict] = None):
        """Обновление данных json и статистики"""
        if all_boosts is not None:
            self.boosts = [Boost(i) for i in filter(lambda x: x.get('type') == self.type, all_boosts)]
            self.ids = self.get_ids()
        if owned_boosts is not None:
            if len(self.boosts) < 1:
                raise EmptyBoostList('Список бустов пуст! Обновите список и попробуйте снова.')
            for boost in owned_boosts:
                meta_id = boost.get('metaId', -1)
                if meta_id in self.ids:
                    self.get_boost_by_id(meta_id).set_buy_state(boost)
        if all_boosts is not None or owned_boosts is not None:
            self.update_stats()

    def update_stats(self, level: int = None):
        """Использовать, если нет необходимости обновлять json данные"""
        if level is not None:
            self.set_max_level(level)
        self.update_min_buy()
        self.update_min_upgrade()

    def update_min_upgrade(self):
        boosts = list(filter(lambda x: x.is_bought() and x.level < self.max_level, self.boosts))
        if not boosts:
            self.min_upgrade = float('inf')
        else:
            self.min_upgrade = min(map(lambda x: x.get_price(), boosts))

    def update_min_buy(self):
        boosts = list(filter(lambda x: not x.is_bought(), self.boosts))
        if not boosts:
            self.min_buy = float('inf')
        else:
            self.min_buy = min(map(lambda x: x.get_price(), boosts))

    def get_min_boost(self):
        boosts = list(filter(
            lambda x: (x.get_price() == self.min_upgrade and x.level != -1) or (
                    x.get_price() == self.min_buy and x.level == -1),
            self.boosts))
        if len(boosts) == 0:
            raise EmptyBoostList('Минимальный буст не найден!')
        return min(boosts, key=lambda x: x.get_price())

    def get_boost_by_id(self, boost_id: int):
        boost = list(filter(lambda x: x.id == boost_id, self.boosts))
        if boost:
            return boost[0]
        return None

    def get_ids(self):
        return list(map(lambda x: x.id, self.boosts))

    def __repr__(self):
        return f'{self.boosts}'


class Boost:
    def __init__(self, json_data: dict, json_bought: dict = None):
        self.id = json_data.get('id', '')
        self.name = json_data.get('name', '')
        self.icon = json_data.get('iconEmoji', '')
        self.type = json_data.get('type', '')
        self.price_base = json_data.get('price', '')
        self.price_mod = json_data.get('priceModifier', '')

        if json_bought is not None:
            self.level = json_bought.get('level', '')
        else:
            self.level = -1

    def set_buy_state(self, item_json: dict):
        self.level = item_json.get('level', '')

    def get_price(self):
        if self.level != -1:
            return self.price_base * self.price_mod * (self.level + 1)
        else:
            return self.price_base

    def is_bought(self):
        if self.level != -1:
            return True
        return False

    def __repr__(self):
        return f'Boost(id={self.id}, name={self.name}, level={self.level})'

from .exceptions import EmptyBoostList, UnknownBoostType


class BoostHandler:
    def __init__(self):
        self.type_list = {
            'CLICK_POWER': BoostList('CLICK_POWER'),
            'MINER': BoostList('MINER'),
            'ENERGY_RECOVERY': BoostList('ENERGY_RECOVERY')
        }
        self.enabled_keys = list()

    def get_boost_by_type(self, boost_type: str):
        if boost_type in self.type_list.keys():
            return self.type_list[boost_type]
        raise UnknownBoostType(f'Неизвестный ключ буста: {boost_type}')

    def update_keys(self, click: bool = False, miner: bool = False, energy: bool = False):
        out = list()
        if click:
            out.append('CLICK_POWER')
        if miner:
            out.append('MINER')
        if energy:
            out.append('ENERGY_RECOVERY')
        self.enabled_keys = out.copy()

    def update_data(self, json_data: list[dict] = None, own_data: list[dict] = None, boost_types: list[str] = None):
        """Полное обновление данных, включая json и статистику"""
        if boost_types is None:
            for key in self.type_list.keys():
                self.type_list[key].update_data(json_data, own_data)
        else:
            for key in boost_types:
                self.type_list[key].update_data(json_data, own_data)

    def update_stats(self, boost_types: list[str] = None):
        """Использовать, если нет необходимости обновлять json данные"""
        if boost_types is None:
            for key in self.type_list.keys():
                self.type_list[key].update_stats()
        else:
            for key in boost_types:
                self.type_list[key].update_stats()

    def get_min_buy(self, boost_type: str):
        if boost_type in self.type_list.keys():
            return self.type_list[boost_type].min_buy
        raise UnknownBoostType(f'Неизвестный ключ буста: {boost_type}')

    def get_min_upgrade(self, boost_type: str):
        if boost_type in self.type_list.keys():
            return self.type_list[boost_type].min_upgrade
        raise UnknownBoostType(f'Неизвестный ключ буста: {boost_type}')

    def get_min(self, boost_type: str):
        if boost_type in self.type_list.keys():
            upgrade = self.type_list[boost_type].min_upgrade
            buy = self.type_list[boost_type].min_buy
            if min(buy, upgrade) == buy:
                return buy, 'buy'
            return upgrade, 'upgrade'
        raise UnknownBoostType(f'Неизвестный ключ буста: {boost_type}')


class BoostList:
    # TODO: объеденить форматирование (id и metaId) для совместимости между собой. Унифицировать апгрейды/покупки
    def __init__(self, boost_type: str, all_boosts: list[dict] = None, owned_boosts: list[dict] = None):
        self.type = boost_type
        self.boosts: list[Boost] = list()
        self.ids: list[int] = list()
        if all_boosts or owned_boosts:
            self.update_data(all_boosts, owned_boosts)
        self.min_buy = 0
        self.min_upgrade = 0

    def update_data(self, all_boosts: list[dict] = None, owned_boosts: list[dict] = None):
        """Полное обновление данных, включая json и статистику"""
        if all_boosts is not None:
            self.boosts = [Boost(i) for i in filter(lambda x: x.get('type') == self.type, all_boosts)]
            self.ids = self.get_ids()
            self.update_min_buy()
        if owned_boosts is not None:
            if len(self.boosts) < 1:
                raise EmptyBoostList('Список бустов пуст! Обновите список и попробуйте снова.')
            for boost in owned_boosts:
                meta_id = boost.get('metaId', -1)
                if meta_id in self.ids:
                    self.get_boost_by_id(meta_id).update_buy_state(boost)
            self.update_min_upgrade()

    def update_stats(self):
        """Использовать, если нет необходимости обновлять json данные"""
        self.update_min_buy()
        self.update_min_upgrade()

    def update_min_upgrade(self):
        self.min_upgrade = min(map(lambda x: x.get_price(), filter(lambda x: x.is_bought(), self.boosts)))

    def update_min_buy(self):
        self.min_buy = min(map(lambda x: x.get_price(), filter(lambda x: not x.is_bought(), self.boosts)))

    def get_boost_by_id(self, boost_id: int):
        return list(filter(lambda x: x.id == boost_id, self.boosts))[0]

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

    def get_price(self):
        if self.level != -1:
            return self.price_base * self.price_mod * (self.level + 1)
        else:
            return self.price_base

    def is_bought(self):
        if self.level != -1:
            return True
        return False

    def update_buy_state(self, item_json: dict):
        self.level = item_json.get('level', '')

    def __repr__(self):
        return f'Boost(id={self.id}, name={self.name}, level={self.level})'

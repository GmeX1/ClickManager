from tortoise import Tortoise, fields
from tortoise.models import Model


class Settings(Model):
    id = fields.IntField(pk=True)
    id_tg = fields.IntField()
    BUY_MAX_LVL = fields.IntField(default=15)
    BUY_CLICK = fields.BooleanField(default=False)
    BUY_MINER = fields.BooleanField(default=False)
    BUY_ENERGY = fields.BooleanField(default=False)
    ref = fields.CharField(max_length=20)


async def init():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['__main__']},
    )
    await Tortoise.generate_schemas()


async def add_user(ref: str, id_tg: int, BUY_MAX_LVL: int = 15, BUY_CLICK=False, BUY_MINER=False, BUY_ENERGY=False):
    existing_user = await Settings.filter(id_tg=id_tg).first()
    if existing_user:
        print("Пользователь с таким именем уже существует.")
        return None
    else:
        user = await Settings.create(id_tg=id_tg, ref=ref, BUY_ENERGY=BUY_ENERGY, BUY_CLICK=BUY_CLICK,
                                     BUY_MINER=BUY_MINER, BUY_MAX_LVL=BUY_MAX_LVL)
        print("Пользователь успешно добавлен.")
        return user


async def check_user_exists(id_tg):
    existing_user = await Settings.filter(id_tg=id_tg).first()
    if existing_user:
        print("Пользователь с таким id_tg уже существует.")
        return True
    else:
        print("Пользователь с таким id_tg не найден.")
        return False


async def main():
    await init()

    await add_user('ref', 123, 15, True, True, True)


import asyncio

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

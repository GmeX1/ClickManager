from loguru import logger
from tortoise import Tortoise

from db.models import Settings


async def init():
    await Tortoise.init(
        db_url='sqlite://db/db.sqlite3',
        modules={'models': ['db.models']},
    )
    await Tortoise.generate_schemas()


async def db_get_user(id_tg: int):
    existing_user = await Settings.filter(id_tg=id_tg).first()
    if existing_user:
        logger.trace(f"Пользователь {id_tg} найден")
        return existing_user
    else:
        logger.trace(f"Пользователь {id_tg} НЕ найден.")
        return None


async def db_add_user(ref: str, id_tg: int, buy_max_lvl: int = 15, buy_click=False, buy_miner=False, buy_energy=False):
    existing_user = await Settings.filter(id_tg=id_tg).first()
    if existing_user:
        logger.debug("Пользователь с таким именем уже существует.")
        return None
    else:
        user = await Settings.create(id_tg=id_tg, ref=ref, BUY_ENERGY=buy_energy, BUY_CLICK=buy_click,
                                     BUY_MINER=buy_miner, BUY_MAX_LVL=buy_max_lvl)
        await user.save()
        logger.debug("Пользователь успешно добавлен.")
        return user


async def db_check_user_exists(id_tg):
    existing_user = await Settings.filter(id_tg=id_tg).first()
    if existing_user:
        logger.trace("Пользователь с таким id_tg уже существует.")
        return id_tg
    else:
        logger.trace("Пользователь с таким id_tg не найден.")
        return False


async def db_update_user(id_tg, data: dict):
    user = await Settings.filter(id_tg=id_tg).first()
    try:
        result = await user.update_from_dict(data)
        await user.save()
        logger.debug(result)
        return True
    except Exception as ex:
        raise ex


async def main():
    await init()

    await db_add_user('ref', 123, 15, True, True, True)

# import asyncio
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())

from loguru import logger
from tortoise import Tortoise

from db.models import Callbacks, SessionStats, Settings, SummaryStats


async def init():
    await Tortoise.init(
        db_url='sqlite://db/db.sqlite3',
        modules={'models': ['db.models']},
    )
    await Tortoise.generate_schemas()


async def db_settings_get_user(id_tg: int):
    existing_user = await Settings.filter(id_tg=id_tg).first()
    if existing_user:
        logger.trace(f"Пользователь {id_tg} найден")
        return existing_user
    else:
        logger.trace(f"Пользователь {id_tg} НЕ найден.")
        return None


async def db_settings_add_user(ref: str, id_tg: int, buy_max_lvl: int = 15, buy_click=False, buy_miner=False,
                               buy_energy=False):
    existing_user = await Settings.filter(id_tg=id_tg).first()
    if existing_user:
        logger.debug("Пользователь с таким именем уже существует.")
        return None
    else:
        user = await Settings.create(id_tg=id_tg, ref=ref, BUY_ENERGY=buy_energy, BUY_CLICK=buy_click,
                                     BUY_MINER=buy_miner, BUY_MAX_LVL=buy_max_lvl)
        await user.save()
        cur_stats = await SessionStats.create(id_tg=id_tg)
        await cur_stats.save()
        sum_stats = await SummaryStats.create(id_tg=id_tg)
        await sum_stats.save()
        logger.debug("Пользователь успешно добавлен.")
        return user


async def db_settings_check_user_exists(id_tg):
    existing_user = await Settings.filter(id_tg=id_tg).first()
    if existing_user:
        logger.trace("Пользователь с таким id_tg уже существует.")
        return id_tg
    else:
        logger.trace("Пользователь с таким id_tg не найден.")
        return False


async def db_settings_update_user(id_tg, data: dict):
    user = await Settings.filter(id_tg=id_tg).first()
    try:
        result = await user.update_from_dict(data)
        await user.save()
        logger.debug(result)
        return True
    except Exception as ex:
        raise ex


async def db_callbacks_get_user(id_tg, column=None, value=None):
    if not (column or value):
        return await Callbacks.filter(id_tg=id_tg).all()
    elif column and value:
        return await Callbacks.filter(id_tg=id_tg, column=column, value=value).first()
    elif column:
        return await Callbacks.filter(id_tg=id_tg, column=column).first()
    elif value:
        return await Callbacks.filter(id_tg=id_tg, value=value).first()
    return None


async def db_callbacks_get_type(column=None, value=None):
    if column and value:
        return await Callbacks.filter(column=column, value=value).all()
    elif column:
        return await Callbacks.filter(column=column).all()
    elif value:
        return await Callbacks.filter(value=value).all()
    return None


async def db_callbacks_add(id_tg, column, value):
    callback = await Callbacks.create(id_tg=id_tg, column=column, value=value)
    await callback.save()
    logger.trace("Callback успешно создан")
    return callback


async def db_stats_update(data: dict):
    cur_stats = await SessionStats.filter(id_tg=data['id_tg']).first()
    sum_stats = await SummaryStats.filter(id_tg=data['id_tg']).first()
    # sum_data = {
    #     'id_tg': sum_stats.id_tg,
    #     'summary': sum_stats.summary + data['summary'],
    #     'boosts': sum_stats.boosts + data['boosts'],
    #     'clicked': sum_stats.clicked + data['clicked'],
    #     'debt': sum_stats.debt + data['debt']
    # }
    sum_data = {key: data.get(key, '') for key in data.keys() if data.get(key, '') != ''}
    try:
        await cur_stats.update_from_dict(data)
        await cur_stats.save()
        await sum_stats.update_from_dict(sum_data)
        await sum_stats.save()
        return True
    except Exception as ex:
        raise ex


async def db_stats_get_sum(id_tg):
    user = await SummaryStats.filter(id_tg=id_tg).first()
    if user:
        return user
    return None


# async def main():
#     await init()
#
#     await db_settings_add_user('ref', 123, 15, True, True, True)
#
# import asyncio
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())

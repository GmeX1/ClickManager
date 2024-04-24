from loguru import logger
from tortoise import Tortoise
from app.core.utils.decorators import db_handler
from db.models import Callbacks, SessionStats, Settings, SummaryStats, Hash


async def init():
    await Tortoise.init(
        db_url='sqlite://db/db.sqlite3',
        modules={'models': ['db.models']},
    )
    await Tortoise.generate_schemas(safe=True)  # АКТИВИРОВАТЬ ТОЛЬКО ДЛЯ СОЗДАНИЯ БД


@db_handler()
async def db_settings_get_user(id_tg: int):
    existing_user = await Settings.filter(id_tg=id_tg).first()
    if existing_user:
        logger.trace(f"Пользователь {id_tg} найден")
        return existing_user
    else:
        logger.trace(f"Пользователь {id_tg} НЕ найден.")
        return None


@db_handler()
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


@db_handler()
async def db_settings_check_user_exists(id_tg):
    existing_user = await Settings.filter(id_tg=id_tg).first()
    if existing_user:
        logger.trace("Пользователь с таким id_tg уже существует.")
        return id_tg
    else:
        logger.trace("Пользователь с таким id_tg не найден.")
        return False


@db_handler()
async def db_settings_update_user(id_tg, data: dict):
    user = await Settings.filter(id_tg=id_tg).first()
    try:
        result = await user.update_from_dict(data)
        await user.save()
        logger.debug(result)
        return True
    except Exception as ex:
        raise ex


@db_handler()
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


@db_handler()
async def db_callbacks_get_type(column=None, value=None):
    if column and value:
        return await Callbacks.filter(column=column, value=value).all()
    elif column:
        return await Callbacks.filter(column=column).all()
    elif value:
        return await Callbacks.filter(value=value).all()
    return None


@db_handler()
async def db_callbacks_add(id_tg, column, value):
    callback = await Callbacks.create(id_tg=id_tg, column=column, value=value)
    await callback.save()
    logger.trace("Callback успешно создан")
    return callback


@db_handler()
async def db_stats_update(data: dict):
    cur_stats = await SessionStats.filter(id_tg=data['id_tg']).first()
    sum_stats = await SummaryStats.filter(id_tg=data['id_tg']).first()
    sum_data = {
        'summary': sum_stats.summary + data.get('summary', 0),
        'boosts': sum_stats.boosts + data.get('boosts', 0),
        'boosts_bought': sum_stats.summary + data.get('boosts_bought', 0),
        'clicked': sum_stats.summary + data.get('clicked', 0),
        'debt': sum_stats.summary + data.get('debt', 0),
    }
    # sum_data = {key: data.get(key, '') for key in data.keys() if data.get(key, '') != ''}
    try:
        await cur_stats.update_from_dict(data)
        await cur_stats.save()
        await sum_stats.update_from_dict(sum_data)
        await sum_stats.save()
        return True
    except Exception as ex:
        raise ex


@db_handler()  # За всё время
async def db_stats_get_sum(id_tg):
    user = await SummaryStats.filter(id_tg=id_tg).first()
    if user:
        return user
    return None


@db_handler()  # За последнюю сессию
async def db_stats_get_session(id_tg):
    user = await SessionStats.filter(id_tg=id_tg).first()
    if user:
        return user
    return None


@db_handler()
async def db_add_hash(anton_hash):
    hash_p = await Hash.create(temporary_hash=anton_hash)
    await hash_p.save()
    logger.trace("Hash успешно создан")
    return hash_p


@db_handler()
async def db_check_hash(user_hash):
    hash_user = await Hash.filter(temporary_hash=user_hash)
    if hash_user:
        logger.trace("Пользователь с таким hash уже существует.")
        return True
    else:
        logger.trace("Пользователь с таким hash не найден.")
        return False


@db_handler()
async def db_del_hesh(del_hash):
    del_hash_ = await Hash.filter(temporary_hash=del_hash).first()
    await del_hash_.delete()

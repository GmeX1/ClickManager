from tortoise import fields
from tortoise.models import Model


class Settings(Model):
    id = fields.IntField(pk=True)
    id_tg = fields.IntField()
    BUY_MAX_LVL = fields.IntField(default=15)
    BUY_CLICK = fields.BooleanField(default=False)
    BUY_MINER = fields.BooleanField(default=False)
    BUY_ENERGY = fields.BooleanField(default=False)


class Callbacks(Model):
    id = fields.IntField(pk=True)
    id_tg = fields.IntField()
    column = fields.CharField(999)
    value = fields.CharField(999, default=None)

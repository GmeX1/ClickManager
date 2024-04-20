from tortoise import fields
from tortoise.models import Model


class Settings(Model):
    id = fields.IntField(pk=True)
    id_tg = fields.IntField(required=True)
    active = fields.BooleanField(default=False)
    BUY_MAX_LVL = fields.IntField(default=15)
    BUY_CLICK = fields.BooleanField(default=False)
    BUY_MINER = fields.BooleanField(default=False)
    BUY_ENERGY = fields.BooleanField(default=False)


class Callbacks(Model):
    id = fields.IntField(pk=True)
    id_tg = fields.IntField(required=True)
    column = fields.CharField(999)
    value = fields.CharField(999, default=None)


class SessionStats(Model):
    id = fields.IntField(pk=True)
    id_tg = fields.IntField(required=True)
    summary = fields.FloatField(default=0)
    boosts = fields.FloatField(default=0)
    clicked = fields.FloatField(default=0)
    debt = fields.FloatField(default=0)


class SummaryStats(Model):
    id = fields.IntField(pk=True)
    id_tg = fields.IntField(required=True)
    summary = fields.FloatField(default=0)
    boosts = fields.FloatField(default=0)
    clicked = fields.FloatField(default=0)
    debt = fields.FloatField(default=0)

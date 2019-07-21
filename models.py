# coding=utf-8
from peewee import *
import os

path = os.path.dirname(__file__)
# db = MySQLDatabase('jd', user='', host='', password='')
db = SqliteDatabase(os.path.join(path, 'jd.db'))


class ShopSign(Model):
    shopid = CharField(unique=True)
    beans = IntegerField(default=0)

    class Meta:
        database = db


class Account(Model):
    name = CharField(default="")
    nick = CharField()
    cookie = TextField(default="")
    cookie_mobile = TextField(default="")

    class Meta:
        database = db

    def __str__(self):
        return '<Account:{nick}>'.format(nick=self.nick)


class Goods(Model):
    cid = PrimaryKeyField()
    count = IntegerField()
    skuid = CharField()
    name = CharField()
    money = FloatField()
    endt = BigIntegerField()

    class Meta:
        database = db

    def to_json(self):
        data = {
            'name': self.name,
            'cid': self.cid,
            'count': self.count,
            'money': self.money,
            'endt': self.endt,
            'skuid': self.skuid
        }
        return data

# db.drop_tables([Account])
db.create_tables([Account, ShopSign,Goods])

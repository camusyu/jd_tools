# coding=utf-8
from peewee import *
import time

db = MySQLDatabase('jd', user='root', host='115.159.110.11', password='771251091')


class ShopSign(Model):
    shopid = CharField(unique=True)
    beans = IntegerField(default=0)

    class Meta:
        database = db

class Account(Model):
    name = CharField()
    nick = CharField()
    time = TimestampField(default=time.time)
    valid = BooleanField(default=True)
    apply = BooleanField(default=False)
    cookie = TextField()
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

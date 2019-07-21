# coding=utf-8

import json
from models import *
from jd_request import *


class Jd:
    def __init__(self, nick):
        account = Account.select().where(Account.nick == nick).first()
        if not account:
            raise FileNotFoundError
        self.nick = account.nick
        self.name = account.name
        self.pc = json.loads(account.cookie)
        self.mobile = json.loads(account.cookie_mobile)
        self.model = account

    def is_login(self):
        return valid_pc_cookie(self.pc), valid_mobile_cookie(self.mobile)

    @property
    def pc_valid(self):
        return True if valid_pc_cookie(self.pc) else False

    @property
    def mobile_valid(self):
        return True if valid_mobile_cookie(self.mobile) else False

    @property
    def beans(self):
        return get_beans(self.mobile)


class Good:
    def __init__(self, cid: str, name: str, count: int, money: float, endt: int, skuid: str):
        self.cid = cid
        self.name = name
        self.count = count
        self.money = money
        self.endt = endt
        self.skuid = skuid
        self.shopid = None

    def __str__(self):
        return '<class:Good>{name},$:{money}'.format(name=self.name, money=self.money)

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



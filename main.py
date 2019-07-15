#!/usr/bin/env python3
# coding=utf-8
import functools
import json
import logging
import os
import random
import re
import sys
import time
import threading
from http.cookiejar import LWPCookieJar
from add_shop import json_to_object

import requests
from requests import RequestException

from models import Account, ShopSign
from tools import magic, Gtime, Datetime2readable, readabletime, Smail

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def all_sign(nick):
    jd = JD(nick)
    count = jd.beans
    jd.do_sign()
    msg = '[{time}]{name}签到完成，获得{beans}京豆\n'.format(
        time=readabletime(),
        name=jd.nick,
        beans=jd.beans - count
    )
    print(msg)



class JD:
    login_url = 'https://passport.jd.com/uc/login'
    qr_code_url = 'https://qr.m.jd.com/show?appid=133&size=147&t={time}'
    qr_state_url = 'https://qr.m.jd.com/check?callback=jQuery436268&appid=133&token={token}&_={time}'
    qr_valid_url = 'https://passport.jd.com/uc/qrCodeTicketValidation?t={ticket}'
    login_server_url = 'https://passport.jd.com/loginservice.aspx?method=Login&callback=jsonpLogin&_={time}'
    cookie_path = 'cookies'
    qd_file = 'qd'
    bean_nums_url = 'http://bean.jd.com/myJingBean/getListDetail'




    @property
    def beans(self):
        url = 'https://home.jd.com/2014/data/account/profile.action'
        try:
            jsond = self.session.post(url, headers=self.headers).json()
            count = jsond['jingdou']
        except Exception:
            count = 0
            logging.error('获取京豆接口出错')
        return count

    def __init__(self, nick=None):
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0",
                        "Referer": "https://www.jd.com/"
                        }
        self.session = requests.session()
        self.login = False
        self.nick = ''
        self.name = ''
        if nick:
            self.load_cookie(nick)

    def set_new_env(self):
        # 设置新环境
        self.session = requests.session()
        self.login = False
        self.nick = ''
        self.name = ''

    def get_new_session(self):
        # 获取新连接
        with open("/dev/null", "w") as noOut:
            sys.stdout = noOut
            self.session.close()
            self.session = requests.session()
            self.load_cookie(self.nick)
        sys.stdout = sys.__stdout__

    def get(self, *args, **kwargs):
        # get方法
        func = functools.partial(self.session.get, headers=self.headers)
        i = 0
        while i < 10:
            try:
                return func(*args, **kwargs)
            except RequestException as e:
                i += 1
                time.sleep(2)

    def post(self, *args, **kwargs):
        # post方法
        func = functools.partial(self.session.post, headers=self.headers)
        i = 0
        while i < 10:
            try:
                return func(*args, **kwargs)
            except RequestException as e:
                i += 1
                time.sleep(2)

    def menu(self):
        msg = '''
        1.更换别的账号
        2.一键签到
        3.一键取关
        0.退出软件
        '''
        print(msg)
        x = input('请输入你的选择：')
        try:
            x = int(x)
            if x == 1:
                self.select_cookie()
            elif x == 2:
                self.do_sign()
            elif x == 3:
                self.remove_follow()
            elif x == 0:
                return 0
        except Exception:
            return 0


    def shop_sign(self):
        # 店铺签到
        ids = ShopSign.select().order_by(ShopSign.beans).paginate(1, 50)
        for shop in ids:
            try:
                beans1 = self.beans
                html = self.get('https://mall.jd.com/shopSign-{}.html'.format(shop.shopid))
                time.sleep(random.uniform(0.01, 0.1))
                if 'error.aspx' in html.text:
                    shop.delete_instance()
                '''
                else:
                    c = self.beans - beans1
                    print("获得{}个京豆".format(c))
                    shop.beans += c if c > 0 else -1
                    shop.save()
                '''
            except Exception as e:
                print(e)
        return True

    def save_cookie(self):
        user = Account.select().where(Account.name == self.name).first()
        if not user:
            user = Account(name=self.name, nick=self.nick)
        cookie = LWPCookieJar()
        requests.utils.cookiejar_from_dict({c.name: c.value for c in self.session.cookies}, cookie)
        content = cookie.cookie2str(ignore_discard=True, ignore_expires=True)
        if user.cookie != content:
            user.cookie = content
            # user.time = time.time()
        user.valid = True
        user.save()
        print('{nick}的cookie保存成功'.format(nick=self.nick))
        return True

    def valid_account(self):
        html = self.get(self.login_server_url.format(time=Gtime())).text
        html = re.search(r'\{[\s\S]*\}', html).group(0)
        req = json.loads(html).get('Identity')
        if req.get('IsAuthenticated'):
            self.login = True
            self.nick = req.get('Unick')
            self.name = req.get('Name')

            print('{nick}登陆成功'.format(nick=self.nick))
            # self.save_cookie()
            user = Account.select().where(Account.name == self.name).first()
            # print('cookie信息已使用{}天{}时{}分'.format(*Datetime2readable(user.time, time.time())))
            print('京豆数量:{}'.format(self.beans))
            return True
        else:
            print('登陆失败')
            return False

    def load_cookie(self, nick):
        #cookie = LWPCookieJar()
        user = Account.select().where(Account.nick == nick).first()
        #cookie.str2cookie(user.cookie, ignore_discard=True, ignore_expires=True)
        #cookie = requests.utils.dict_from_cookiejar(cookie)
        # self.session.cookies = requests.utils.cookiejar_from_dict(cookie)
        self.session.cookies = requests.utils.cookiejar_from_dict(json.loads(user.cookie))
        if not self.valid_account():
            user.valid = False
            user.save()
            return False
        return True

    def do_sign(self):
        beans = self.beans
        self.other_sign()
        # 店铺签到
        self.shop_sign()
        return self.beans - beans

    @classmethod
    def auto_sign(cls):
        users = Account.select()# .where(Account.valid == True)
        task = []
        msg = ''
        for user in users:
            t = threading.Thread(target=all_sign, args=(user.nick,))
            task.append(t)
            t.start()
        [t.join() for t in task]
        Smail('签到完成', msg)

    @classmethod
    def clean_account(cls):
        users = Account.select() #.where(Account.valid == True)
        for user in users:
            jd = cls(user.nick)
            jd.remove_follow()

    def select_cookie(self):
        self.set_new_env()
        users = Account.select()# .where(Account.valid == True)
        for i, j in enumerate(users, start=1):
            print(i, ':', j.nick)
        x = input('请输入序号选择加载的cookie，输入其他结束:')
        try:
            x = int(x)
            if 1 <= x <= len(users):
                # 加载cookie
                self.cookie = self.load_cookie(users[x - 1].nick)
            else:
                exit(0)
        except Exception as e:
            print(e)
            return

    @classmethod
    def check_fail_cookie(cls):
        for i in Account.select():
            cls(i.nick)
        users = Account.select()# .where(Account.valid == False)#, Account.apply == True)
        if users:
            msg = '、'.join([user.nick for user in users])
            Smail('登陆失效提醒', '{users}已失效，请尽快重新登陆！'.format(users=msg))
            return False
        return True

    def remove_follow(self):
        # 取关店铺
        unfollow_url = 'https://t.jd.com/follow/vender/unfollow.do?venderId={id}&_={time}'
        count = 0
        while True:
            res = self.get('https://t.jd.com/follow/vender/qryCategories.do').json()
            if len(res['data']):
                for type in res['data']:
                    for Id in type['entityIdSet']:
                        u = unfollow_url.format(id=Id, time=Gtime())
                        r = self.get(u).json()
                        if r['success']:
                            count += 1
            else:
                break
        print('已取消{}家店铺的关注'.format(count))
        # 取关商品
        #unfollow_good_api = 'https://follow-soa.jd.com/rpc/product/unfollow?sysName=t.jd.com&productId={skuid}'
        unfollow_good_api = 'https://api.m.jd.com/api?functionId=cancelFavorite&body={{"wareId":"{skuid}"}}&appid=follow_for_concert'
        count = 0
        while True:
            html = self.get('https://t.jd.com/follow/product').text
            good_list = re.findall(r'skuid="(\d*)"', html)
            if good_list:
                for skuid in good_list:
                    self.get(unfollow_good_api.format(skuid=skuid)).text
                    count += 1
                time.sleep(0.5)
            else:
                break
        print('已取消{}个商品的关注'.format(count))

    def other_sign(self):
        data = [
            ('http://vip.jr.jd.com/newSign/doSign', self.post),
            ('https://vip.jd.com/sign/index', self.get),
            ('https://datawallet.jd.com/web/json/sign.action', self.get),
            ('https://datawallet.jd.com/web/json/doKeyWord.action?keyWord=流量加油站', self.get),
            ('http://huan.jd.com/json/sign/signIn.action', self.post),
            (
            'https://api.m.jd.com/api?functionId=getCoupons&loginType=3&appid=u&body=%7B%22platform%22%3A%223%22%2C%22unionActId%22%3A%2231036%22%2C%22actId%22%3A%222CXzsrrEnh3d3zYsG6oPoddB9X9g%22%2C%22unionShareId%22%3A%22%22%7D',
            self.get),
        ]
        for i in data:
            i[1](i[0])

    @classmethod
    def add_shops(cls):
        users = Account.select()# .where(Account.valid == True)
        user = users[0]
        jd = cls(user.nick)
        jd.get('https://bean.jd.com/myJingBean/list')
        print("增加{}个商铺".format(json_to_object(jd.get('https://bean.jd.com/myJingBean/getPopSign').text)))



if __name__ == '__main__':
    magic()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    if len(sys.argv) > 1:
        if sys.argv[1] == '-h':
            print('Usage:python3 main.py [auto/-h]')
        elif sys.argv[1] == 'sign':
            # 自动签到
            JD.add_shops()
            JD.auto_sign()
        elif sys.argv[1] == 'check':
            # 检测cookie有效性
            JD.check_fail_cookie()
        elif sys.argv[1] == 'clean':
            # 清理账号
            JD.clean_account()
        elif sys.argv[1] == 'shop':
            # 添加签到店铺
            JD.add_shops()

    else:
        jd = JD()
        jd.select_cookie()
        while True:
            if jd.login:
                if jd.menu() == 0:
                    break
            else:
                jd.select_cookie()

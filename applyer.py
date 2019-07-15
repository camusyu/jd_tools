#!/usr/bin/env python3
# coding=utf-8
from main import JD
import re
import time
from bs4 import BeautifulSoup
import requests
import functools
from models import Account
import threading
import json
import sys
from tools import magic, Gtime, Smail, get_parser
import os


parser = get_parser()

name2cids = {
    '手机数码': '652,9987',
    '家用电器': '737',
    '电脑办公': '670',
    '家居家装': '1620,6728,9847,9855,6196,15248',
    '美妆护肤': '1316',
    '服饰鞋包': '1315,1672,1318,11729',
    '母婴玩具': '1319,6233',
    '生鲜美食': '12218',
    '图书音像': '1713,4051,4052,4053,7191,7192,5272',
    '钟表奢侈': '5025,6144',
    '个人护理': '16750',
    '家庭清洁': '15901',
    '食品饮料': '1320,12259',
    # '更多惊喜': '4938,13314,6994,9192,12473,6196,5272,12379,13678,15083,15126,15980',
}


class Good:
    def __init__(self, cid: str, name: str, count: int, money: float, endt: int, skuid: str):
        self.cid = cid
        self.name = name
        self.count = count
        self.money = money
        self.endt = endt
        self.skuid = skuid

    def __str__(self):
        return '<class:Good>{name}'.format(name=self.name)

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


class Apply:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
        "Referer": "http://try.jd.com/"
    }
    main_url = 'http://try.jd.com/'
    apply_goods_url = 'http://try.jd.com/migrate/apply?activityId={id}&source=0'
    follow_shop_url = 'https://fts.jd.com/follow/vender/follow?venderId={shopid}&sysName=item.jd.com'
    follow_good_url = 'https://t.jd.com/product/followProduct.action?productId={skuid}'
    apply_state_url = 'http://try.jd.com/user/getApplyStateByActivityIds?activityIds={ids}'
    goods_list_url = 'http://try.jd.com/activity/getActivityList?page={page}&cids={cids}'
    goods_money_url = 'http://p.3.cn/prices/mgets?skuIds={skuids}'

    def __init__(self, jd, count=30, money=14.9):
        self.jd = jd
        self.count_max = count
        self.money_min = money
        self.type = ''
        self.buf = []

    def get(self, *args, **kwargs):
        func = functools.partial(self.jd.get, headers=self.headers)
        return func(*args, **kwargs)

    def post(self, *args, **kwargs):
        func = functools.partial(self.jd.post, headers=self.headers)
        return func(*args, **kwargs)

    def filter(self, good, opt, time_limit=1000 * 60 ** 2 * 24):
        '''
        设置过滤条件
        flag == True为白名单模式
        '''
        if good.endt - Gtime() > time_limit:
            return False
        if good.money < opt.get('money', self.money_min):
            return False
        if good.count > opt.get('count', self.count_max):
            return False
        # 先用黑名单过滤一遍
        for i in opt.get('deny', []):
            if isinstance(i, list):
                name = i[0]
                money = i[1]
            else:
                name = i
                money = 99999
            if name in good.name and good.money < money:
                return False
        # 再用白名单过滤
        for i in opt.get('allow', []):
            if isinstance(i, list):
                name = i[0]
                money = i[1]
            else:
                name = i
                money = 0
            if name in good.name and good.money > money:
                return True
        # 如果时白名单模式则返回true
        return not opt.get('mode', True)

    def get_non_apply(self, goods):
        if not goods:
            return []
        ids = ','.join([good.cid for good in goods])
        res = self.get(self.apply_state_url.format(ids=ids)).json()
        applyed = [str(i['activityId']) for i in res]
        return filter(lambda good: good.cid not in applyed, goods)

    def follow_shop(self, shopid):
        headers = {
            'Referer': 'https://item.jd.com/5129535.html',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        }

        params = (
        ('callback', 'jQuery858886'),
        ('venderId', str(shopid)),
        ('sysName', 'item.jd.com'),
        ('_', str(Gtime())),
        )
        #cookie = requests.utils.dict_from_cookiejar(self.session.cookies)
        resp = self.get('https://fts.jd.com/follow/vender/follow',headers=headers, params=params)
        print(resp.text)


    def apply_good(self, good):
        self.buf.append(good)
        # 关注店铺
        html = self.get('https://item.jd.com/{skuid}.html'.format(skuid=good.skuid)).text
        val = re.search(r'data-vid="(\d*)"', html)
        if val:
            # jd自营的无法关注店铺
            shopid = val.group(1)
            #resp = self.get(self.follow_shop_url.format(shopid=shopid))
            self.follow_shop(shopid)
        # 关注商品
        self.get(self.follow_good_url.format(skuid=good.skuid))
        time.sleep(0.5)

        # 申请单件商品
        while True:
            try:
                res = self.get(self.apply_goods_url.format(id=good.cid)).json()
                ret = res['message'] + ' : ' + good.name
                break
            except requests.ConnectionError:
                time.sleep(5)

        return ret

    def apply_hot(self):
        # 申请热门商品
        html = self.get(self.main_url)
        html.encoding = 'utf-8'
        html = html.text
        soup = BeautifulSoup(html, parser)
        s = soup.find('div', class_='content')
        each = s.find_all('li')
        goods = []
        for i in each:
            count = int(re.search(r'提供([0-9]*)份', i.text).group(1))
            cid = i.attrs['activity_id']
            endt = int(i.attrs['end_time'])
            skuid = i.attrs['sku_id']
            name = i.find('div', class_='p-name').text
            good = Good(cid, name, count, 0, endt, skuid)
            goods.append(good)
        non_apply = self.get_non_apply(goods)
        for good in non_apply:
            print(self.apply_good(good))
            time.sleep(5.2)
        print('热门商品申请成功')

    def get_max_page(self, url):
        html = self.get(url)
        html.encoding = 'utf-8'
        html = html.text
        soup = BeautifulSoup(html, parser)
        max_page = int(re.search(r'共([0-9]*)页', soup.text).group(1))
        return max_page

    def get_money_by_skuids(self, goods):
        skuids = ','.join(['J_' + good.skuid for good in goods])
        res = self.get(self.goods_money_url.format(skuids=skuids)).json()
        data = {}
        for item in res:
            skuid = item.get('id', '')[2:]
            money = float(item.get('p', '0'))
            data[skuid] = money
        for good in goods:
            if good.skuid in data:
                good.money = data[good.skuid]

    def apply_type(self, cids, opt):
        url = self.goods_list_url.format(cids=cids, page=1)
        for page in range(1, self.get_max_page(url) + 1):
            # 更新会话
            self.jd.get_new_session()
            html = self.get(self.goods_list_url.format(cids=cids, page=page))
            html.encoding = 'utf-8'
            html = html.text
            soup = BeautifulSoup(html, parser)
            items = soup.find_all('li', class_='item')
            goods = []
            for i in items:
                count = int(re.search(r'提供([0-9]*)份', i.text).group(1))
                cid = i.attrs['activity_id']
                endt = int(i.attrs['end_time'])
                skuid = i.attrs['sku_id']
                name = i.find('div', class_='p-name').text
                good = Good(cid, name, count, 0, endt, skuid)
                goods.append(good)
            self.get_money_by_skuids(goods)
            goods = [good for good in goods if self.filter(good, opt)]
            non_apply = self.get_non_apply(goods)
            for good in non_apply:
                res = self.apply_good(good)
                print(res)
                time.sleep(6)
                if "上限" in res:
                    return 0
        print('申请完毕')

    def get_goods_by_type(self, type):
        url = self.goods_list_url.format(cids=type, page=1)
        for page in range(1, self.get_max_page(url) + 1):
            html = self.get(self.goods_list_url.format(cids=type, page=page))
            html.encoding = 'utf-8'
            html = html.text
            soup = BeautifulSoup(html, parser)
            items = soup.find_all('li', class_='item')
            goods = []
            for i in items:
                count = int(re.search(r'提供([0-9]*)份', i.text).group(1))
                cid = i.attrs['activity_id']
                endt = int(i.attrs['end_time'])
                skuid = i.attrs['sku_id']
                name = i.find('div', class_='p-name').text
                good = Good(cid, name, count, 0, endt, skuid)
                goods.append(good)
            self.get_money_by_skuids(goods)
            yield goods
            time.sleep(0.3)

    def get_rich_good(self, money_min=499, time_limit=1000 * 60 ** 2 * 24):
        data = {}
        for name in name2cids.keys():
            data[name] = []
            for goods in self.get_goods_by_type(name2cids.get(name)):
                rich_goods = filter(lambda
                                        good: good.money >= money_min and good.endt - Gtime() <= time_limit and good.count <= self.count_max,
                                    goods)
                # 保存这些高价商品
                [data[name].append(good.to_json()) for good in rich_goods]
            self.jd.set_new_env()
            print('{}类别高价已筛选完毕'.format(name))
            time.sleep(3)
        with open('rich.json', 'w') as f:
            f.write(json.dumps(data))

    def apply_rich_goods(self):
        if not os.path.exists('rich.json'):
            print("rich文件不存在，跳过申请高价物品!")
            return
        with open('rich.json') as f:
            data = json.load(f)
        f.close()
        goods = []
        for key in data.keys():
            goods.clear()
            for good in data[key]:
                goods.append(Good(**good))
            for good in self.get_non_apply(goods):
                print(self.apply_good(good))
                time.sleep(6)
        print('高价物品申请完毕')


def do_task(nick):
    jd = JD()
    jd.load_cookie(nick)
    app = Apply(jd, 30)
    app.apply_rich_goods()
    with open('filter.json') as f:
        task = json.load(f)
    for name, opt in task.items():
        cids = name2cids.get(name, None)
        if cids:
            app.type = name
            app.apply_type(cids, opt)
    msg = '{user} 完成今日的试用申请\n'.format(user=nick)
    gl = ['[{money}]{name}'.format(name=good.name, money=good.money) for good in app.buf]
    msg += '\n'.join(gl)
    Smail('申请试用完毕', msg)


if __name__ == '__main__':
    magic()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    if len(sys.argv) > 1:
        if sys.argv[1] == '-h':
            print('Usage:python3 applyer.py [rich/-h]')
        elif sys.argv[1] == 'rich':
            # 获取当日即将结束的高价物品
            app = Apply(JD())
            app.get_rich_good()
    else:
        users = Account.select()# .where(Account.valid == True)
        tasks = []
        for user in users:
            t = threading.Thread(target=do_task, args=(user.nick,))
            tasks.append(t)
            t.start()
        for t in tasks:
            t.join()
            # pass
        print('所有任务已经完成！')

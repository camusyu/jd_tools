#!/usr/bin/env python3
# coding=utf-8
import sys

from main import JD
import re
import time
from bs4 import BeautifulSoup
import functools
from models import Goods
from tools import magic, get_parser
from peewee import PeeweeException


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
    '更多惊喜': '4938,13314,6994,9192,12473,6196,5272,12379,13678,15083,15126,15980',
}


class Apply:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
        "Referer": "http://try.jd.com/"
    }
    main_url = 'http://try.jd.com/'
    apply_goods_url = 'http://try.jd.com/migrate/apply?activityId={id}&source=0'
    follow_shop_url = 'https://follow-soa.jd.com/rpc/vender/follow?sysName=try.jd.com&venderId={shopid}'
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
                cid = int(i.attrs['activity_id'])
                endt = int(i.attrs['end_time'])
                skuid = i.attrs['sku_id']
                name = i.find('div', class_='p-name').text
                good = Goods(cid=cid, name=name, count=count, endt=endt, skuid=skuid)
                goods.append(good)
            self.get_money_by_skuids(goods)
            yield goods
            time.sleep(0.3)

    def save_good(self):
        for name in name2cids.keys():
            for goods in self.get_goods_by_type(name2cids.get(name)):
                for good in goods:
                    try:
                        if not Goods.get_or_none(Goods.cid == good.cid):
                            Goods.create(**good.to_json())
                    except PeeweeException as e:
                        print(e)
                        pass
            self.jd.set_new_env()
            print('{}类保存完毕'.format(name))


def delete_overtime():
    now = int(time.time() * 1000)
    goods = Goods.select().filter(Goods.endt < now)
    [good.delete_instance() for good in goods]
    print("删除{}个过期物品".format(len(goods)))


if __name__ == '__main__':
    magic()
    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            delete_overtime()
    else:
        delete_overtime()
        # 获取当日即将结束的高价物品
        app = Apply(JD())
        app.save_good()

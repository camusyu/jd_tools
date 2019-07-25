# coding=utf-8

import requests
import time
import re
import json
from retrying import retry
from tools import Gtime

'''
def retry(times=3):
    def outer(func):
        def inner(*args, **kwargs):
            t = 0
            res = None
            while t < times:
                try:
                    t += 1
                    res = func(*args, **kwargs)
                    break
                except Exception as e:
                    print(e)
                    time.sleep(1)
            if not res:
                print(res)
                raise MemoryError
            else:
                return res
        return inner
    return outer
'''


def unfollow_shops(cookie_dict, shops):
    # shops 最多50
    headers = {
        'Referer': 'https://wqs.jd.com/my/fav/shop_fav.shtml?ptag=7155.1.9&sceneval=2',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    }

    params = (
        ('shopId', shops),
        #('_', '1564068426838'),
        ('sceneval', '2'),
        ('g_login_type', '1'),
        ('callback', 'jsonpCBKR'),
        #('g_ty', 'ls'),
    )

    response = requests.get('https://wq.jd.com/fav/shop/batchunfollow', headers=headers, params=params, cookies=cookie_dict)
    print(response.text)


def get_follow_shop_list(cookie_dict, page=1, count=10):
    headers = {
        'Referer': 'https://wqs.jd.com/my/fav/shop_fav.shtml',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    }

    params = (
        ('cp', page),
        ('pageSize', count),
        #('lastlogintime', '1564067507'),
        #('_', '1564067534335'),
        ('sceneval', '2'),
        #('g_login_type', '1'),
        ('callback', 'jsonpCBKJ'),
        #('g_ty', 'ls'),
    )

    response = requests.get('https://wq.jd.com/fav/shop/QueryShopFavList', headers=headers, params=params, cookies=cookie_dict)
    return (json.loads(response.text[14:-13])['data'])


def get_follow_good_list(cookie_dict, page=1, count=10):
    headers = {
        'Referer': 'https://wqs.jd.com/my/fav/goods_fav.shtml?ptag=7155.1.8&sceneval=2',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    }

    params = (
        ('cp', page),
        ('pageSize', count),
        ('category', '0'),
        ('promote', '0'),
        ('cutPrice', '0'),
        ('coupon', '0'),
        ('stock', '0'),
        ('areaNo', '1_72_4139_0'),
        ('_', '1564068917192'),
        ('sceneval', '2'),
        ('g_login_type', '1'),
        ('callback', 'jsonpCBKK'),
        ('g_ty', 'ls'),
    )

    response = requests.get('https://wq.jd.com/fav/comm/FavCommQueryFilter', headers=headers, params=params, cookies=cookie_dict)
    return (json.loads(response.text[14:-13])['data'])


def unfollow_goods(cookie_dict, goods):
    headers = {
        'Referer': 'https://wqs.jd.com/my/fav/goods_fav.shtml',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    }

    params = (
        ('commId',goods),
        # '50734324835,41849305084,48699119391,35698593899,50573717298,52704152265,52850281032,15380051645,50736151849,41803999624'),
        ('_', '1564071086620'),
        ('sceneval', '2'),
        ('g_login_type', '1'),
        ('callback', 'jsonpCBKK'),
        ('g_ty', 'ls'),
    )

    response = requests.get('https://wq.jd.com/fav/comm/FavCommBatchDel', headers=headers, params=params, cookies=cookie_dict)

    print(response.text)


@retry(stop_max_attempt_number=7, wait_fixed=200)
def valid_mobile_cookie(cookie_dict):
    headers = {
        'Referer': 'https://home.m.jd.com/myJd/newhome.action',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    }

    response = requests.get('https://wq.jd.com/user/info/QueryJDUserInfo?sceneval=2', headers=headers, cookies=cookie_dict)
    return response.json()['base']['nickname']


@retry(stop_max_attempt_number=7, wait_fixed=200)
def apply_good(id, cookie_dict):
    headers = {
        'Referer': 'https://try.m.jd.com/activity',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    }

    params = (
        ('activityId', id),
        ('source', '1'),
        ('_s', 'm'),
        ('_', Gtime()),
    )

    response = requests.get('https://try.jd.com/migrate/apply', headers=headers, params=params, cookies=cookie_dict)
    return response.json()


# 根据申请商品id获取店铺id
@retry(stop_max_attempt_number=7, wait_fixed=200)
def get_shop_id_by_applyid(id):
    headers = {
        'Referer': 'https://try.m.jd.com/activity',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    }
    #print(id)
    response = requests.get('https://try.m.jd.com/activity?id={}'.format(id), headers=headers)
    #print(response.text)
    shop_id = re.search(r"shopId = '(\d*)'", response.text).group(1)
    return shop_id



# 根据cid 获取已申请的商品
def get_noapply_good(goods, cookie_dict):
    headers = {
        'Accept': '*/*',
        'Referer': 'https://try.m.jd.com/activities',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    }

    ids = ','.join([str(good.cid) for good in goods])

    response = requests.get('https://try.m.jd.com/getApplyStateByActivityIds?activityIds={}'.format(ids), headers=headers, cookies=cookie_dict)
    selected = [i['activityId'] for i in response.json()]
    return filter(lambda good: good.cid not in selected, goods)


@retry(stop_max_attempt_number=7, wait_fixed=200)
def follow_shop(shopid, cookie_dict):
    headers = {
        'Accept': 'application/json',
        'Referer': 'https://try.m.jd.com/activity',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    }
    response = requests.get('https://try.m.jd.com/followShop?id={}'.format(shopid), headers=headers, cookies=cookie_dict)
    return response.json()

@retry(stop_max_attempt_number=7, wait_fixed=200)
def get_beans(cookie_dict):
    headers = {
        'Referer': 'https://home.m.jd.com/myJd/newhome.action',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    }

    response = requests.get('https://wq.jd.com/user/info/QueryJDUserInfo?sceneval=2', headers=headers,
                            cookies=cookie_dict)
    return response.json()['base']['jdNum']


@retry(stop_max_attempt_number=7, wait_fixed=200)
def valid_pc_cookie(cookie_dict):
    headers = {
        'Referer': 'https://www.jd.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    }

    response = requests.get('https://passport.jd.com/loginservice.aspx?method=Login', headers=headers,
                            cookies=cookie_dict)
    return response.json()['Identity']['Unick']

@retry(stop_max_attempt_number=7, wait_fixed=200)
def get_apply_items(cids, page):
    url = 'https://try.m.jd.com/activity/list?pb=1&cids={cids}&page={page}&type=&state=0'
    headers = {
        'Referer': 'https://try.m.jd.com/',
        'User-Agent': 'Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
    }
    response = requests.get(url.format(cids=cids,page=page), headers=headers)
    return response.json()


def get_type_all(cids):
    rsp = get_apply_items(cids, 1)
    pages = rsp['data']['pages']
    for page in range(1, pages + 1):
        rsp = get_apply_items(cids, page)
        yield rsp['data']['data']
        time.sleep(0.3)

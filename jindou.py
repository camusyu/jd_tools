#!/usr/bin/env python3
#coding=utf-8
import requests, json, time
from models import Account
from tools import Gtime
import sys

def valid_mobile_cookie(cookie_dict):
    headers = {
        'Referer': 'https://home.m.jd.com/myJd/newhome.action',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    }

    response = requests.get('https://wq.jd.com/user/info/QueryJDUserInfo?sceneval=2', headers=headers, cookies=cookie_dict)
    return response.json()['base']['nickname']


def shouhuo(cookie_dict):
    # 收获金果
    headers = {
        'Origin': 'https://uuj.jr.jd.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    }

    data = {
        'reqData': '{"source":2,"sharePin":""}'
    }

    response = requests.post('https://ms.jr.jd.com/gw/generic/uc/h5/m/harvest?_={}'.format(Gtime()),
                                 headers=headers, data=data, cookies=cookie_dict)
   # print(response.json())


def sell_fruit(cookie_dict):
    # 卖出金果
    headers = {
        'Origin': 'https://uuj.jr.jd.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    }

    data = 'reqData={"source":2,"sharePin":null,"riskDeviceParam":""}'
    response = requests.post('https://ms.jr.jd.com/gw/generic/uc/h5/m/sell?_={}'.format(Gtime()),
                             headers=headers, data=data, cookies=cookie_dict)
    # print(response.json())


def sign(cookie_dict):
    # 签到
    headers = {
        'Origin': 'https://uuj.jr.jd.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    }
    data = 'reqData={"source":2,"workType":1,"opType":2}'

    response = requests.post('https://ms.jr.jd.com/gw/generic/uc/h5/m/doWork', headers=headers,
                             cookies=cookie_dict, data=data)
    # print(response.json())


def share(cookie_dict):
    # 分享任务
    headers = {
        'Origin': 'https://uuj.jr.jd.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    }
    data = 'reqData={"source":2,"workType":2,"opType":1}'
    response = requests.post('https://ms.jr.jd.com/gw/generic/uc/h5/m/doWork', headers=headers,
                             cookies=cookie_dict, data=data)
    time.sleep(2)
    data = 'reqData={"source":2,"workType":2,"opType":2}'
    response = requests.post('https://ms.jr.jd.com/gw/generic/uc/h5/m/doWork', headers=headers,
                             cookies=cookie_dict, data=data)
    # print(response.json())


def help_othres(cookie_dict):
    sharePin = [
        'TRJqSOe2BFV5SKL6QWxIPsAdoUJQ3Dik',
        '9_F8TGySa988werHZiLH4MAdoUJQ3Dik',
    ]
    headers = {
        'Origin': 'https://uuj.jr.jd.com',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    }
    '''
    headers = {
        'Host': 'ms.jr.jd.com',
        'Accept': 'application/json',
        'Origin': 'https://uuj.jr.jd.com',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; MIX 2S Build/PKQ1.180729.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044807 Mobile Safari/537.36 MMWEBID/6718 MicroMessenger/7.0.5.1440(0x27000537) Process/tools NetType/WIFI Language/zh_CN',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Referer': 'https://uuj.jr.jd.com/wxgrowing/moneytree7/index.html?channelLV=sy&shareType=1&sharePin=9_F8TGySa988werHZiLH4MAdoUJQ3Dik&utm_source=Android*url*1562934293067&utm_medium=jrappshare&utm_term=wxfriends&from=singlemessage',
        'Accept-Language': 'zh-CN,en-US;q=0.9',
        'X-Requested-With': 'com.tencent.mm',
    }
    '''

    for i in sharePin:
        data = 'reqData=%7B%22sharePin%22%3A%22{}%22%2C%22shareType%22%3A%221%22%2C%22channel%22%3A%22sy%22%2C%22source%22%3A0%2C%22riskDeviceParam%22%3A%22%7B%5C%22fp%5C%22%3A%5C%22%5C%22%2C%5C%22eid%5C%22%3A%5C%22%5C%22%2C%5C%22sdkToken%5C%22%3A%5C%22%5C%22%2C%5C%22sid%5C%22%3A%5C%22%5C%22%7D%22%7D'.format(i)
        response = requests.post('https://ms.jr.jd.com/gw/generic/uc/h5/m/login?_='.format(Gtime()), headers=headers,
                                 cookies=cookie_dict, data=data)
        time.sleep(1)
        #print(response.json())




if __name__ == '__main__':
    users = Account.select()
    for i in users:
        cookie_dict = {}
        try:
            cookie_dict = json.loads(i.cookie_mobile)
        except Exception:
            pass
        if valid_mobile_cookie(cookie_dict):
            if len(sys.argv) > 1:
                if sys.argv[1] == '-h':
                    pass
                elif sys.argv[1] == 'sign':
                    sign(cookie_dict)
                elif sys.argv[1] == 'share':
                    share(cookie_dict)
                elif sys.argv[1] == 'sell':
                    sell_fruit(cookie_dict)
                elif sys.argv[1] == 'help':
                    help_othres(cookie_dict)
                else:
                    shouhuo(cookie_dict)
            shouhuo(cookie_dict)
        else:
            print('{} {}登录已经失效'.format(time.time(), i.nick))

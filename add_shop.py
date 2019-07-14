# coding=utf-8
import json
import requests
import re
from models import ShopSign


def get_shop_id(url):
    html = requests.get(url).text
    ids='0'
    try:
        ids = re.search(r'id="shop_id" value="(\d*)"', html).group(1)
    except Exception:
        print(html)
        exit(1)
    return ids


def save_to_db(shops):
    print(shops)
    counts = 0
    for i in shops:
        if not ShopSign.select().filter(shopid=i):
            counts += 1
            ShopSign(shopid=i).save()
    return counts


def json_to_object(jsons):
    data = json.loads(jsons).get("data", [])
    shops = []
    for i in data:
        url = i.get("shopUrl", "")
        ids = get_shop_id(url)
        shops.append(ids)
    return save_to_db(shops)


def url_to_object(urls):
    shops = []
    for i in urls.split('\n'):
        ids = re.search(r'https://mall.jd.com/shopSign-(\d*).html', i)
        if ids:
            ids = ids.group(1)
            shops.append(ids)
    return save_to_db(shops)

if __name__ == "__main__":
    x = '''
    https://mall.jd.com/shopSign-1000005289.html?cu=true
https://mall.jd.com/shopSign-1000002241.html?cu=true
https://mall.jd.com/shopSign-1000086643.html?cu=true
https://mall.jd.com/shopSign-1000003795.html?cu=true
https://mall.jd.com/shopSign-1000080646.html?cu=true
https://mall.jd.com/shopSign-1000146461.html?cu=true
https://mall.jd.com/shopSign-1000108110.html?cu=true
https://mall.jd.com/shopSign-675899.html?cu=true
    '''
    #print(url_to_object(x))
    x = input()
    print(json_to_object(x))

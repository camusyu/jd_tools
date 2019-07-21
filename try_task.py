# coding=utf-8

from jd_request import *
from domain import Good, Jd
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED
import json
from threading import Thread

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


#过滤商品
def filter_goods(good, opt, time_limit=1000 * 60 ** 2 * 24):
    '''
    设置过滤条件
    flag == True为白名单模式
    '''
    if good.endt - Gtime() > time_limit:
        return False
    if good.money < opt.get('money', 14.9):
        return False
    if good.count > opt.get('count', 30):
        return False

    # 先用白名单过滤
    for i in opt.get('allow', []):
        if isinstance(i, list):
            name = i[0]
            money = i[1]
        else:
            name = i
            money = 0
        if name in good.name and good.money > money:
            return True

    # 再用黑名单过滤一遍
    for i in opt.get('deny', []):
        if isinstance(i, list):
            name = i[0]
            money = i[1]
        else:
            name = i
            money = 99999
        if name in good.name and good.money < money:
            return False

    # 如果时白名单模式则返回true
    return not opt.get('mode', True)


def do_applys(goods, cookie_dict, opt):
    noapply = get_noapply_good(goods, cookie_dict)
    goods = [good for good in list(noapply) if filter_goods(good, opt)]
    for good in goods:
        follow_shop(good.shopid, cookie_dict)
        apply_good(good.cid, cookie_dict)
        time.sleep(5.2)


if __name__ == "__main__":
    with open('filter.json') as f:
        filters = json.load(f)


    users = []
    users.append(Jd('sqlness'))
    users.append(Jd('special_wen'))
    print(len(users))
    executor = ThreadPoolExecutor(max_workers=len(users))
    for name, cids in name2cids.items():
        print('开始查找{}'.format(name))

        opt = filters.get(name, {})
        for res in get_type_all(cids):
            goods = []
            #jd = Jd('sqlness')
            for item in res:
                # print(item['trialName'])
                good = Good(name=item['trialName'], count=item['supplyCount'],
                            endt=item['endTime'], money=item['jdPrice'],
                            skuid=item['trialSkuId'], cid=item['id'])

                good.shopid = get_shop_id_by_applyid(good.cid)
                goods.append(good)
                # print(follow_shop(shopid, jd.mobile))
                # print(apply_good(good.cid, jd.mobile))
                # exit(0)
            # 取到了12条数据
            tasks = [Thread(target=do_applys, args=(goods, user.mobile, opt,)) for user in users]
            [task.start() for task in tasks]
            [task.join() for task in tasks]

    executor.close()

# coding=utf-8
import gevent
from gevent import monkey
import time
monkey.patch_all()
from main import JD, Gtime


def mytime():
    return int(time.time() % (60 **2 * 24))

start = (60 ** 2 * 60 * 19) + (60 ** 1 * 59) + (60 ** 0 * 50)
end = (60 ** 2 * 60 * 20) + (60 ** 1 * 0) + (60 ** 0 * 10)

if __name__ == '__main__':
    jd = JD()
    jd.load_cookie('sqlness')
    urls = [
        'https://coupon.jd.com/ilink/couponSendFront/send_index.action?key=297e27e0b46c4af69b2abe915a9ddf27&roleId=15012289&to=https://sale.jd.com/act/fpgmdSRPst.html',
        'https://act-jshop.jd.com/couponSend.html?callback=jQuery9413490&ruleId=15011152&key=e9e67bd20b5e4f0db1afa4ac17dc3ee8&eid=E6WCHJPMOTTQR5HCFRJXEKDBVDLXQHTNXQYUALSU2IWTDAL3NJWMX65R7TEOLTRMJZ25ZAQNHT6QVU7YXWDUWMSQN4&fp=2cbc6beb3390417debe42a838e20d5ae&shshshfp=a7dd06189496692c2f9b7f79d35408df&shshshfpa=40e6ff62-5ab3-be9b-ff28-b1377a6b3d98-1537873595&shshshfpb=1691a425151004413aa19107674554230a36f8058e92dfa035baa16bb5&jda=122270672.1513593894937825999244.1513593895.1539931591.1540106278.17&pageClickKey=pageclick%7Ckeycount%7Ccoupon_simple_38517749_3%7C0&platform=0&applicationId=1649755&_={time}',
        'https://act-jshop.jd.com/couponSend.html?callback=jQuery9282416&ruleId=15011186&key=fd25ce7744d64de6a92feb03ba27c205&eid=E6WCHJPMOTTQR5HCFRJXEKDBVDLXQHTNXQYUALSU2IWTDAL3NJWMX65R7TEOLTRMJZ25ZAQNHT6QVU7YXWDUWMSQN4&fp=2cbc6beb3390417debe42a838e20d5ae&shshshfp=a7dd06189496692c2f9b7f79d35408df&shshshfpa=40e6ff62-5ab3-be9b-ff28-b1377a6b3d98-1537873595&shshshfpb=1691a425151004413aa19107674554230a36f8058e92dfa035baa16bb5&jda=122270672.1513593894937825999244.1513593895.1539931591.1540106278.17&pageClickKey=pageclick%7Ckeycount%7Ccoupon_simple_38517749_4%7C0&platform=0&applicationId=1649755&_={time}'
    ]
    while True:
        if mytime() < start:
            time.sleep(1)
        if mytime() > start:
            g = []
            for _ in range(10):
                for url in urls:
                    g.append(gevent.spawn(jd.down, url))
            gevent.joinall(g)
        if mytime() > end:
            break

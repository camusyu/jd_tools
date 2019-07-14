# coding=utf-8
import requests
import time
import random
import string
import datetime
import logging
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from http.cookiejar import LWPCookieJar
from http.cookiejar import LoadError
from http.cookiejar import split_header_words
from http.cookiejar import iso2time
from http.cookiejar import Cookie
from http.cookiejar import _warn_unhandled_exception


def readabletime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_parser():
    try:
        import lxml
        return 'lxml'
    except ModuleNotFoundError:
        return 'html.parser'


def Gtime():
    return int(time.time() * 1000)


def Datetime2readable(t1,t2):
    t1 =time.mktime(t1.timetuple())
    t = int(t2 - t1)
    day = t // (24 * 60**2)
    t -= (24 * 60**2) * day
    hour = t // (60**2)
    t -= (60**2) * hour
    minu = t // 60
    return day, hour, minu


def RandomName(length=10):
    ret = ''.join([random.choice(string.ascii_letters) for _ in range(length)])
    return ret


def cookie2str(self, ignore_discard=False, ignore_expires=False):
    cookie = ''
    cookie += "#LWP-Cookies-2.0\n"
    cookie += self.as_lwp_str(ignore_discard, ignore_expires)
    return cookie


def str2cookie(self, cookstr, ignore_discard, ignore_expires):
    magic = cookstr.split('\n')[0]
    if not self.magic_re.search(magic):
        msg = ("It does not look like a Set-Cookie3 (LWP) format "
               "string")
        raise LoadError(msg)

    now = time.time()

    header = "Set-Cookie3:"
    boolean_attrs = ("port_spec", "path_spec", "domain_dot",
                     "secure", "discard")
    value_attrs = ("version",
                   "port", "path", "domain",
                   "expires",
                   "comment", "commenturl")

    try:
        for line in cookstr.split('\n'):
        # while 1:
            # line = f.readline()
            if line == "": break
            if not line.startswith(header):
                continue
            line = line[len(header):].strip()

            for data in split_header_words([line]):
                name, value = data[0]
                standard = {}
                rest = {}
                for k in boolean_attrs:
                    standard[k] = False
                for k, v in data[1:]:
                    if k is not None:
                        lc = k.lower()
                    else:
                        lc = None
                    # don't lose case distinction for unknown fields
                    if (lc in value_attrs) or (lc in boolean_attrs):
                        k = lc
                    if k in boolean_attrs:
                        if v is None: v = True
                        standard[k] = v
                    elif k in value_attrs:
                        standard[k] = v
                    else:
                        rest[k] = v

                h = standard.get
                expires = h("expires")
                discard = h("discard")
                if expires is not None:
                    expires = iso2time(expires)
                if expires is None:
                    discard = True
                domain = h("domain")
                domain_specified = domain.startswith(".")
                c = Cookie(h("version"), name, value,
                           h("port"), h("port_spec"),
                           domain, domain_specified, h("domain_dot"),
                           h("path"), h("path_spec"),
                           h("secure"),
                           expires,
                           discard,
                           h("comment"),
                           h("commenturl"),
                           rest)
                if not ignore_discard and c.discard:
                    continue
                if not ignore_expires and c.is_expired(now):
                    continue
                self.set_cookie(c)
    except OSError:
        raise
    except Exception:
        _warn_unhandled_exception()
        raise LoadError("invalid Set-Cookie3 format string")


def magic():
    LWPCookieJar.cookie2str = cookie2str
    LWPCookieJar.str2cookie = str2cookie


class Smail:
    def __init__(self, title, msg):
        self.smtp = smtplib.SMTP()
        self.smtp.connect('smtp.139.com', 25)
        self.smtp.login('15829619731@139.com', 'hao360com')
        message = MIMEText(msg, 'plain', 'utf-8')
        message['Subject'] = Header(title, 'utf-8')
        message['From'] = Header('京东助手 <15829619731@139.com>', 'utf-8')
        message['To'] = "1041984720@qq.com"
        for _ in range(10):
            try:
                self.smtp.sendmail('15829619731@139.com', ['1041984720@qq.com'], message.as_string())
                break
            except Exception:
                if _ == 9:
                    logging.error('邮件发送失败！:{}'.format(message.as_string()))
        self.smtp.quit()


if __name__ == "__main__":
    session = requests.Session()
    session.get('http://www.baidu.com')
    cookie = LWPCookieJar()
    requests.utils.cookiejar_from_dict({c.name: c.value for c in session.cookies}, cookie)
    a = cookie.cookie2str(ignore_discard=True, ignore_expires=True)
    print(a)
    cookie = LWPCookieJar()
    cookie.str2cookie(a, ignore_discard=True, ignore_expires=True)
    cookie = requests.utils.dict_from_cookiejar(cookie)
    session = requests.Session()
    session.cookies = requests.utils.cookiejar_from_dict(cookie)
    print(session.cookies)
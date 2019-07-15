# coding=utf-8
from flask import Flask, jsonify, render_template, session,current_app,request
import os, time
import requests
from datetime import timedelta
import logging
import json
from models import Account

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.qr_list = {}




def valid_mobile_cookie(cookie_dict):
    headers = {
        'Referer': 'https://home.m.jd.com/myJd/newhome.action',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    }

    response = requests.get('https://wq.jd.com/user/info/QueryJDUserInfo?sceneval=2', headers=headers, cookies=cookie_dict)
    return response.json()['base']['nickname']


def valid_pc_cookie(cookie_dict):
    headers = {
        'Referer': 'https://www.jd.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    }

    response = requests.get('https://passport.jd.com/loginservice.aspx?method=Login', headers=headers,
                            cookies=cookie_dict)
    return response.json()['Identity']['Unick']



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cookie", methods=['POST',])
def get_cookie():
    cookie_str = request.json.get('cookie', '')
    print(cookie_str)
    cookie_dict = dict()
    try:
        cookie_dict = dict([i.split('=', 1) for i in cookie_str.split(';')])
    except Exception:
        pass
    # 0:mobile 1: PC
    style = 0
    nick = valid_mobile_cookie(cookie_dict)
    if not nick:
        nick = valid_pc_cookie(cookie_dict)
        style = 1
    if nick:
        user = Account.select().where(Account.nick == nick).first()
        if not user:
            user = Account(nick=nick)
        if not style:
            user.cookie_mobile = json.dumps(cookie_dict)
        else:
            user.cookie = json.dumps(cookie_dict)
            print(user)
        user.save()
        return jsonify({'msg': '已保存{}的{}端cookie'.format(nick, 'PC' if style else '移动')})

    else:
        return jsonify({'msg': 'cookie无效！'})




@app.route("/api/state")
def getUserstate():
    users = Account.select()
    data = {
        'code': 200,
        'data': [user.to_json() for user in users]
    }
    return jsonify(data)



if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8849)

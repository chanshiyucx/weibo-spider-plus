from urllib import parse
import requests
import base64
import time
import logging


class Login:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        logging.debug('登录模块初始化完成！')

    # 加密用户名
    def get_su(self):
        username_qoute = parse.quote_plus(self.username)
        su = base64.b64encode(username_qoute.encode('utf-8')).decode('utf-8')
        logging.debug('用户名加密：%s', su)
        return su

    # 预登录
    def get_prelogin_args(self, su):
        params = {
            "entry": "weibo",
            "callback": "sinaSSOController.preloginCallBack",
            "rsakt": "mod",
            "checkpin": "1",
            "client": "ssologin.js(v1.4.19)",
            "su": su,
            "_": int(time.time()*1000),
        }
        return params

    # linkstart
    def login(self):
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4482.400 QQBrowser/9.7.13001.400'})
        self.su = self.get_su()
        self.prelogin_args = self.get_prelogin_args(self.su)

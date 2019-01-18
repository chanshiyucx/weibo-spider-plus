from urllib import parse
import requests
import base64
import time
import re
import json
import logging

login_url = "https://login.sina.com.cn/sso/prelogin.php"


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
        try:
            response = self.session.get(login_url, params=params)
            logging.info("返回结果：%s", response.text)
            prelogin_args = json.loads(
                re.search(r"\((?P<data>.*)\)", response.text).group("data"))
        except Exception as excep:
            prelogin_args = {}
            logging.error("预登录出错！:%s" % excep)

        logging.debug("预登录返回数据: %s", prelogin_args)
        return prelogin_args

    # linkstart
    def login(self):
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4482.400 QQBrowser/9.7.13001.400'})
        self.su = self.get_su()
        self.prelogin_args = self.get_prelogin_args(self.su)

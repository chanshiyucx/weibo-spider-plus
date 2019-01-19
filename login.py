from urllib import parse
import requests
import base64
import time
import re
import json
import rsa
import binascii
import os
import platform
import subprocess
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
        logging.debug('加密用户名 su：%s' % su)
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
            prelogin_url = "https://login.sina.com.cn/sso/prelogin.php"
            response = self.session.get(prelogin_url, params=params)
            logging.info("返回结果：%s" % response.text)
            prelogin_args = json.loads(
                re.search(r"\((?P<data>.*)\)", response.text).group("data"))
        except Exception as excep:
            prelogin_args = {}
            logging.error("预登录出错！:%s" % excep)

        logging.debug("预登录返回数据: %s" % prelogin_args)
        return prelogin_args

    # 加密密码
    def get_sp(self, servertime, nonce, pubkey):
        string = (str(servertime) + "\t" + str(nonce) +
                  "\n" + str(self.password)).encode("utf-8")
        public_key = rsa.PublicKey(int(pubkey, 16), int("10001", 16))
        password = rsa.encrypt(string, public_key)
        sp = binascii.b2a_hex(password).decode()
        logging.debug("加密密码 sp: %s" % sp)
        return sp

    # 模拟登录
    def get_postdata(self, su, sp, prelogin_args):
        postdata = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "qrcode_flag": 'false',
            "useticket": "1",
            "pagerefer": "",
            "vsnf": "1",
            "su": su,
            "service": "miniblog",
            "servertime": prelogin_args['servertime'],
            "nonce": prelogin_args['nonce'],
            "pwencode": "rsa2",
            "rsakv": prelogin_args['rsakv'],
            "sp": sp,
            "sr": "1366*768",
            "encoding": "UTF-8",
            "prelt": "1085",
            "url": "https://www.weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "META"
        }
        if 'showpin' in prelogin_args.keys():
            if prelogin_args['showpin'] == 1:
                pin_url = 'https://login.sina.com.cn/cgi/pin.php?r=%s&s=0&p=%s' % (
                    int(time.time()*1000), prelogin_args["pcid"])
                try:
                    pic = self.session.get(pin_url).content
                except Exception as excep:
                    pic = b''
                    logging.error("获取验证码错误:%s" % excep)
                with open("pin.png", "wb") as file_out:
                    file_out.write(pic)
                self.open_pin()
                code = input("请输入验证码:")
                postdata["pcid"] = prelogin_args["pcid"]
                postdata["door"] = code
            else:
                pass
        else:
            pass
        logging.debug("登录表单数据: %s" % postdata)
        return postdata

    # 打开文件
    def open_pin(self):
        base_folder = os.path.abspath(os.path.dirname(__file__))
        file = 'pin.png'
        pin_path = os.path.join(base_folder, file)
        os_name = platform.system()
        if os_name == 'Darwin':
            subprocess.call(['open', pin_path])
        elif os_name == 'Windows':
            subprocess.call(['explorer', pin_path])
        elif os_name == 'Linux':
            subprocess.call(['xdg-open', pin_path])
        else:
            logging.error("你的系统不支持自动预览验证码，请手动打开文件夹:%s" % os_name)

    # linkstart
    def login(self):
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4482.400 QQBrowser/9.7.13001.400'})
        self.su = self.get_su()
        self.prelogin_args = self.get_prelogin_args(self.su)
        if not self.prelogin_args:
            logging.error('预登录失败！')
        else:
            self.sp = self.get_sp(
                self.prelogin_args["servertime"], self.prelogin_args["nonce"], self.prelogin_args["pubkey"])
            self.postdata = self.get_postdata(
                self.su, self.sp, self.prelogin_args)
            login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
            try:
                login_page = self.session.post(login_url, data=self.postdata)
            except Exception as excep:
                logging.error("获取登录页错误:%s" % excep)
                return False
            login_redirect = login_page.content.decode("GBK")
            pa = r'location\.replace\([\'"](.*?)[\'"]\)'
            redirect_url = re.findall(pa, login_redirect)[0]
            try:
                login_index = self.session.get(redirect_url)
            except Exception as excep:
                logging.error("获取重定向页失败:%s" % excep)
                return False
            try:
                result = json.loads(
                    re.search(r"\((?P<data>.*)\)", login_index.text).group('data'))
                if result['result']:
                    logging.debug('登录成功！')
                    return self.session
                    # return True
                else:
                    logging.debug('登录失败！')
                    return False
            except:
                logging.debug('登录失败！')
                return False

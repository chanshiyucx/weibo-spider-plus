import logging
import configparser
import os
import shutil
import requests
from requests_html import HTML
from login import Login

# 设置日志级别
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s\t%(levelname)s\t%(message)s")

config = configparser.ConfigParser()
config.read("spider.conf")


class Weibo:
    def __init__(self):
        self.session = ''
        self.pages = 1
        self.curPage = 1
        self.curUrl = ''
        self.full_path = ''

    # 登录
    def login(self):
        # username = input('你的账号：').strip()
        # password = input('你的密码：').strip()
        username = config["profile"]["username"]
        password = config["profile"]["password"]

        logging.debug("正在登录账号 %s" % username)
        my_login = Login(username, password)
        session = my_login.login()
        if session:
            self.session = session

    # 获取收藏
    def get_fav(self):
        logging.debug('获取收藏夹')
        self.curUrl = "https://www.weibo.com/fav?leftnav=" + str(self.curPage)
        try:
            response = self.session.get(self.curUrl)
            file = "fav.txt"
            with open(file, "w", encoding="utf-8") as fout:
                fout.write(response.text)
        except Exception as excep:
            logging.error("收藏夹获取失败:%s" % excep)
            return False

    # 启动
    def start(self):
        # 1.登录
        # self.login()
        # # 2.获取收藏夹
        # if self.session:
        #     self.get_fav()
        # 3. 创建文件夹
        self.get_or_create_folder()

        with open("fav.txt", "r", encoding="utf-8") as fin:
            file = fin.read()

        doc = file.split("pl.content.favoriteFeed.index")[1].split(
            '"html":"')[1].split('"})</script>')[0]
        html = HTML(html=doc)
        # 总页数
        page = html.find('.W_pages')
        if page:
            logging.debug('page: %s', page)
        # 该页图片
        img = html.find('img[src*="thumb150"]')
        src_list = []
        for item in img:
            src = item.attrs['src']
            src = src.replace("\\", "")
            src = src.replace('"', "")
            src = src.replace("thumb150", "large")
            src_list.append(src)
        logging.debug('找到 %d 张图片', len(src_list))

        for src in src_list:
            name = src.split('large/')[1].replace('"', '')
            self.download_img(name, src)

    # 保存图片
    def download_img(self, name, src):
        logging.debug('下载图片： %s', src)
        response = requests.get("https:" + src, stream=True)
        data = response.raw
        file_name = os.path.join(self.full_path, name)
        with open(file_name, 'wb') as fout:
            shutil.copyfileobj(data, fout)

    # 获取或创建文件夹
    def get_or_create_folder(self):
        base_folder = os.path.abspath(os.path.dirname(__file__))
        full_path = os.path.join(base_folder, "picture")

        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            os.mkdir(full_path)

        self.full_path = full_path


# 新建实例
weibo = Weibo()
weibo.start()

import logging
import configparser
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

    #

    # 启动
    def start(self):
        # 1.登录
        # self.login()
        # # 2.获取收藏夹
        # if self.session:
        #     self.get_fav()
        with open("fav.txt", "r", encoding="utf-8") as fin:
            file = fin.read()

        doc = file.split("pl.content.favoriteFeed.index")[1].split(
            '"html":"')[1].split('"})</script>')[0]
        html = HTML(html=doc)
        img = html.find('img')
        src_list = []
        for item in img:
            src = item.attrs['src']
            src = src.replace("\\", "")
            src = src.replace("thumb150", "large")
            src_list.append(src)
        logging.debug('src:%s', src_list)


# 新建实例
weibo = Weibo()
weibo.start()

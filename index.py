import logging
from login import Login

# 设置日志级别
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s\t%(levelname)s\t%(message)s")

class God:
  def __init__(self):
    self.pages = 1
    self.curPage = 1
    self.curUrl = ''
  
  # 登录
  def login(self):
    username = input('你的账号：').strip()
    password = input('你的密码：').strip()
    logging.debug('正在登录账号 %s...', username)
    my_login = Login(username, password)

  
  # 启动
  def start(self):
    self.login()

# 新建实例
god = God()
god.start()
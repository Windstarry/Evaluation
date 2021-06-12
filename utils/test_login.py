import json
import os
import time
from playwright.sync_api import sync_playwright
from datetime import datetime
from pathlib import Path 
from utils.config import USENAME,PASSWORD


class Test_loggin(object):
 
    def __init__(self, login_url,cookie_path='./source',cookie_name = 'cookies_bjxxk.txt', expiration_time = 30):
        '''
        :param login_url: 登录网址
        :param home_url: 首页网址
        :param cookie_path: cookie文件存放路径
        :param cookie_path: 文件命名
        :param expiration_time: cookie过期时间,默认30分钟
        '''
        self.login_url = login_url
        self.cookie_path = cookie_path
        self.cookie_name = cookie_name
        self.expiration_time = expiration_time
 

    def get_cookie(self):
        '''登录获取cookie'''
        playwright = sync_playwright().start()
        #无头浏览器模式
        browser = playwright.chromium.launch()
        #打开浏览器模式
        #browser = playwright.chromium.launch(headless=False,slowMo=200)
        context = browser.new_context()
        #设置防爬的参数
        context.add_init_script("""
                        const newProto = navigator.__proto__;
                        delete newProto.webdriver;
                        navigator.__proto__ = newProto;
            """
            ) 
        #设置超时时间为30s
        context.set_default_timeout(30000)
        page = context.new_page()
        #打开政务服务网登陆网址
        page.goto(self.login_url,wait_until="load")
        # Fill input[name="username"]
        page.fill("input[name=\"username\"]", USENAME)
        # Fill input[name="password"]
        page.fill("input[name=\"password\"]", PASSWORD)
        # Check input[name="noLogin"]
        page.check("input[name=\"noLogin\"]")
        with page.expect_navigation():
            page.click("//button[normalize-space(.)='登录']")
        print("登陆成功")
        page.wait_for_selector("//li[normalize-space(.)='办件信息库']/img")
        with page.expect_popup() as popup_info:
            page.click("//li[normalize-space(.)='办件信息库']/img")
        page1 = popup_info.value
        time.sleep(3)
        with open('./source/cookies_bjxxk.txt', 'w') as cookief:
        # 将cookies保存为json格式
            cookief.write(json.dumps(context.cookies()))
        print("cookies保存完成")
        page1.close()
        context.close()
        browser.close()

    
    def judge_cookie(self):
        '''获取最新的cookie文件，判断是否过期'''
        my_file = Path("./source/cookies_bjxxk.txt")
        if my_file.is_file():
            new_cookie = os.path.join(self.cookie_path, "cookies_bjxxk.txt")
            #new_cookie = os.path.join(self.cookie_path, cookie_list2[-1])    # 获取最新cookie文件的全路径 
            file_time = os.path.getmtime(new_cookie)  # 获取最新文件的修改时间，返回为时间戳1590113596.768411
            t = datetime.fromtimestamp(file_time)  # 时间戳转化为字符串日期时间
            print('当前时间：', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print('最新cookie文件修改时间：', t.strftime("%Y-%m-%d %H:%M:%S"))
            date = (datetime.now() - t).seconds // 60  # 时间之差，seconds返回相距秒数//60,返回分数
            print('相距分钟:{0}分钟'.format(date))
            if date > self.expiration_time:  # 默认判断大于30分钟，即重新手动登录获取cookie
                print("cookie已经过期，请重新登录获取")
                return self.get_cookie()
            else:
                print("cookie未过期")
        else:
            self.get_cookie()


    def get_jsessionid(self):
        '''获取JSESSIONID操作'''
        self.judge_cookie()  # 首先判断cookie是否已获取，是否过期
        print("获取JSESSIONID中")
        with open(os.path.join(self.cookie_path, self.cookie_name),'r') as cookief:
            #使用json读取cookies 注意读取的是文件 所以用load而不是loads
            cookieslist = json.load(cookief)
            # 方法1删除该字段
            cookies_dict = dict()
            for cookie in cookieslist:
                #该字段有问题所以删除就可以,浏览器打开后记得刷新页面 有的网页注入cookie后仍需要刷新一下
                if 'expiry' in cookie:
                    del cookie['expiry']
                cookies_dict[cookie['name']] = cookie['value']
        print(cookies_dict)
        jsessionid=cookies_dict['JSESSIONID']
        return jsessionid


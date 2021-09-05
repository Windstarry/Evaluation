# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
import os
from datetime import datetime
from pathlib import Path
import requests
from utils.config import USENAME,PASSWORD,EVALUATIONNAME


class TestLogin(object):
 
    def __init__(self, login_url,home_url,cookie_path='.\source',cookie_name = 'cookies_bjxxk.txt', expiration_time = 60):
        '''
        :param login_url: 登录网址
        :param home_url: 首页网址
        :param cookie_path: cookie文件存放路径
        :param cookie_path: 文件命名
        :param expiration_time: cookie过期时间,默认60分钟
        '''
        self.login_url = login_url
        self.home_url= home_url
        self.cookie_path = cookie_path
        self.cookie_name = cookie_name
        self.expiration_time = expiration_time


    def get_cookie(self):
        '''登录获取cookie'''
        #设置driver启动参数
        driver_path='.\source\chromedriver.exe'
        option = Options()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(executable_path=driver_path,options=option)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
                })
            """
            })
        driver.maximize_window()
        driver.implicitly_wait(10)
        #完成获取cookie步骤
        driver.get(self.login_url)
        driver.find_element_by_name('username').send_keys(USENAME)
        driver.find_element_by_name('password').send_keys(PASSWORD)
        driver.find_element_by_name('noLogin').click()
        driver.find_element_by_id('btn-submit-login').click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'system')))
        driver.find_element_by_xpath(r'//li[@class="appLi"][9]').click()
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)
        driver.get(self.home_url)
        time.sleep(2)
        #创建文本覆盖保存cookie
        with open(os.path.join(self.cookie_path, self.cookie_name), 'w') as cookief:    
            # 将cookies保存为json格式
            cookief.write(json.dumps(driver.get_cookies()))
        print("cookie保存成功")
        driver.close()


    def judge_cookie(self):
        '''获取最新的cookie文件，判断是否过期'''
        my_file = Path(".\source\cookies_bjxxk.txt")
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

    
    def get_session_value(self):
        '''获取JSESSIONID操作'''
        self.judge_cookie()  # 首先判断cookie是否已获取，是否过期
        print("获取SESSION中")
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
        session_value=cookies_dict["SESSION"]
        return session_value


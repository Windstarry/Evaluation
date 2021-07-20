import os,re,json,time,random
import requests
import asyncio
import aiohttp
import aiofiles
import pandas as pd
from fake_useragent import UserAgent
from lxml import etree
from functools import wraps
from asyncio.proactor_events import _ProactorBasePipeTransport
from playwright.sync_api import sync_playwright
from datetime import datetime
from pathlib import Path 
from utils.config import USENAME,PASSWORD
from utils.config import login_url,contents,savefile,filecontents,setindex_col,headers
from utils.servicecode import gic


def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != 'Event loop is closed':
                raise 
    return wrapper


def write_excle(content,savefile):
    df=pd.DataFrame.from_dict(content)
    df.set_index(df.columns[0],inplace=True)
    df.to_excel(savefile)


class Test_loggin(object):
 
    def __init__(self, login_url,cookie_path='./source',cookie_name = 'cookies_bjxxk.txt', expiration_time = 60):
        '''
        :param login_url: 登录网址
        :param home_url: 首页网址
        :param cookie_path: cookie文件存放路径
        :param cookie_path: 文件命名
        :param expiration_time: cookie过期时间,默认60分钟
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


class HandleExcle(object):
    
    def __init__(self,filename):
        self.filename = filename
        self.df=pd.read_excel(filename,dtype=str)
        self.max_num=self.df.shape[0]
        self.column_list=list(self.df.columns)
        self.first_url = "http://59.207.104.196:8081/ycslypt_web/pingjia.action?sid={}&projid={}&projectname={}&cardnumber={}&evaluatorName={}&evaluatefrom=4&projectNo={}&proStatus=3"
        self.second_url = "http://59.207.104.196:8081/ycslypt_web/pingjia.action?sid={}&projid={}&projectname={}&cardnumber={}&evaluatorName={}&evaluatefrom=4&projectNo={}&proStatus=2&evaluteCount=2&evaluatecount=2"
        self.third_url = "http://59.207.104.196:8081/ycslypt_web/pingjia.action?sid={}&projid={}&projectname={}&cardnumber={}&evaluatorName={}&evaluatefrom=4&projectNo={}&proStatus=1&evaluteCount=3&evaluatecount=3"

    
    def get_tel(self,x):
        tel=self.df["手机号码"].at[x]
        if pd.isnull(tel):
            tel = '0391-7118602'
        else:   
            tel = self.tel_num_judge(tel)
        return tel


    def get_projname(self,x):
        url=self.df["办件名称"].at[x]
        return url 
    
    
    def get_name(self,x):
        name=self.df["申请人"].at[x]
        return name

    
    def get_idcard(self,x):
        idcard=self.df["证件号码"].at[x]
        return idcard


    def get_projid(self,x):
        projid=self.df['申报号'].at[x]
        return projid


    def get_servicename(self,x):
        servicename=self.df['办件名称'].at[x]
        return servicename
   

    def get_result(self,x):
        result=self.df["评价状态"].at[x]
        return result
    
    def get_servicecode(self,x):
        servicecode=str(self.df["事项编码"].at[x])
        return servicecode


    def get_implementcode(self,x):
        servicecode = self.get_servicecode(x)
        projid = self.get_projid(x)
        if servicecode in gic.keys():
            implementcode=str(gic[servicecode])+projid[7:15]+projid[-4:]
            return implementcode
        else:
            implementcode="错误"
            print("没有找到该事项")
            return implementcode


    def resultstate(self,x):
        self.df.loc[x,"评价状态"]="已评价"
    
    
    def save_excle(self,savefile):
        df=self.df.set_index("申报号")
        df.to_excel(savefile)

    
    def insert_column(self):
        self.df.insert(1,"评价状态",'未评价')

    
    def get_url(self,x):
        servicecode=self.get_servicecode(x)
        projid=self.get_projid(x)
        servicename =self.get_servicename(x)
        idcard =self.get_idcard(x)
        name =self.get_name(x)
        tel =self.get_tel(x)
        projectno =self.get_implementcode(x)
        first_url = self.first_url.format(servicecode,projid,servicename,idcard,name,tel,projectno)
        return first_url

    
    @staticmethod
    def tel_num_judge(tel_num):
        ret = '\d{3}\*{7}\d{1}'
        tel_judge = re.match(ret,tel_num)
        tel_judge_two = re.match('\*{7}',tel_num)
        if tel_judge:
            tel_num = "0391-7873031"
        elif tel_judge_two:
            tel_num = "0391-7873031"
        return tel_num


class ProjectContent:
    
    def __init__(self,startpage,endpage,cityid,cityname,user_agent,jsessionid):
        self.url = "http://59.207.104.4:8060/rsp/view.action"
        self.startpage = startpage
        self.endpage = endpage
        self.cityid=cityid
        self.cityname=cityname
        self.headers = {
                    'Connection': 'keep-alive',
                    'Content-Length': '138',
                    'Host': '59.207.104.9:8060' , 
                    'Origin':'http://59.207.104.9:8060',
                    'Upgrade-Insecure-Requests':'1',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': f'{user_agent}',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9', 
                    'Cookie': f'JSESSIONID={jsessionid}',
                    }
        

    async def post_date(self,payload):
            async with aiohttp.ClientSession() as client:
                async with await client.post(self.url, headers=self.headers,data=payload,) as resp:
                    if resp.status == 200:
                        return await resp.text()
                    else:
                        print('请求出错')


    async def get_projectlist(self,num,semaphore):
            async with semaphore:
                payload = {
                    '_search':'0',
                    'ID': f'{self.cityid}',
                    'TREENODE_NAME':f'{self.cityname}',
                    'viewId': 'A97604BB8E12B56595743D8BAF0651CC',
                    'fn': 'grid_list',
                    'page': f'{num}',
                    'rows': '50',
                    }
                resp = await self.post_date(payload)
                pro_contents = json.loads(resp)
                # requests.packages.urllib3.disable_warnings()
                # resp = requests.post(self.url, data=payload, headers=self.headers,verify=False)
                # pro_contents=resp.json()
                if 'rows' in pro_contents.keys():
                    pro_lists=pro_contents['rows']
                    if len(pro_lists) > 0:
                        for pro_list in pro_lists:
                            projid=pro_list["PROJID"]
                            servicecode=pro_list["SERVICECODE"]
                            transact_name=pro_list["PROJECTNAME"]
                            card_num=pro_list["APPLY_CARDNUMBER"]
                            tel_num=pro_list["TELPHONE"]
                            applicant=pro_list["APPLYNAME"]
                            dept_name=pro_list["DEPTNAME"]
                            time=pro_list["TRANSACTTIME"]
                            result=pro_list["HANDLESTATE"]
                            content={
                                "申报号":projid,
                                '办理单位':dept_name,
                                "事项编码":servicecode,
                                "办件名称":transact_name,
                                "证件号码":str(card_num),
                                "手机号码":str(tel_num),
                                "申请人":applicant,
                                "办结时间":time,
                                "办件状态":result
                            }
                            print(content)
                            contents.append(content)
           

    async def main(self):
        start_time = time.time()
        semaphore = asyncio.Semaphore(3)
        tasks = [asyncio.create_task(self.get_projectlist(num,semaphore)) for num in range(self.startpage,self.endpage)]
        await asyncio.wait(tasks)
        end_time = time.time()
        print(f'完成{self.endpage - self.startpage}页，共耗时{end_time - start_time}秒')



if __name__ == '__main__':
    cityid='001003018006016'
    cityname='修武县'
    pagestart=1
    pageend=620
    #运行程序
    _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
    location = './source/fake_useragent.json'
    user_agent = UserAgent(path=location).random
    test_loggin = Test_loggin(login_url=login_url)
    jsessionid=test_loggin.get_jsessionid()
    p = ProjectContent(pagestart,pageend,cityid,cityname,user_agent,jsessionid)
    asyncio.run(p.main())
    write_excle(contents,savefile)
    print("{}保存完毕".format(savefile))

    
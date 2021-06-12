# coding:utf-8
import pandas as pd
from utils.servicecode import gic
import re
from utils.config import savefile
from playwright.sync_api import sync_playwright
from playwright.sync_api import BrowserContext
import time
import requests,json,os

class HandleExcle(object):
    
    def __init__(self,filename):
        self.filename = filename
        self.df=pd.read_excel(filename,dtype=str)
        self.max_num=self.df.shape[0]
        self.column_list=list(self.df.columns)
        self.first_url = "http://59.207.104.196:8081/ycslypt_web/pingjia.action?sid={}&projid={}&projectname={}&cardnumber={}&evaluatorName={}&evaluatefrom=4&projectNo={}&proStatus=3"
        self.second_url = "http://59.207.104.196:8081/ycslypt_web/pingjia.action?sid={}&projid={}&projectname={}&cardnumber={}&evaluatorName={}&evaluatefrom=4&projectNo={}&proStatus=2&evaluteCount=2&evaluatecount=2"
        self.third_url = "http://59.207.104.196:8081/ycslypt_web/pingjia.action?sid={}&projid={}&projectname={}&cardnumber={}&evaluatorName={}&evaluatefrom=4&projectNo={}&proStatus=1&evaluteCount=3&evaluatecount=3"
        #self.base_url = "http://59.207.104.196:8081/ycslypt_web/pingjia.action?fn=save&projid={}&serviceCode={}&evaluatefrom=4&userType&evaluatorName={}&evaluteCount=2&projectname={}&isOpened=1&checkState=1&evaluateContent&satisfactionEvaluate=5&syncStatus=I&isAboveLegalday=2&isMediation=2&serviceAttitudeEvaluate=1&isAnonymity=2&serviceAttitudeReason&workAttitudeEvaluate=1&workAttitudeReason=&evaluatorCardnumber={}&belongsystem&evaluatecount=2&evaluatorPhone={}&token=cdeb4ce0a0ea48b86c7be8fba9a412ca&huaKuaiFlag=true&checkFlag=notRobot&projectNo={}&proStatus=2&evaluateDetail="
    
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
        # second_url = self.second_url.format(servicecode,projid,servicename,idcard,name,tel,projectno)
        # third_url = self.third_url.format(servicecode,projid,servicename,idcard,name,tel,projectno)
        #url=self.base_url.format(projid,servicecode,name,servicename,idcard,tel,projectno)
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


def get_url_token(responsetext):
    pattern = 'id="token" value="(.*?)">'
    token_list = re.findall(pattern,responsetext)
    if len(token_list) != 0:
        token = token_list[0]
    else:
        token = ''
    return token


def first_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno):
        payload = {
                'fn': 'save',
                'projid': f'{projid}',
                'serviceCode': f'{servicecode}',
                'evaluatefrom':'4',
                'userType':'', 
                'evaluatorName': f'{evaluatorname}',
                'evaluteCount': '1',
                'projectname': f'{projectname}',
                'isOpened': '1',
                'checkState': '1',
                'evaluateContent':'',
                'satisfactionEvaluate': '5',
                'evaluateDetail': '510',
                'syncStatus': 'I',
                'isAboveLegalday': '2',
                'isMediation': '2',
                'serviceAttitudeEvaluate': '1',
                'isAnonymity': '2',
                'serviceAttitudeReason': '',
                'workAttitudeEvaluate': '1',
                'workAttitudeReason': '',
                'evaluatorCardnumber': f'{cardnumber}',
                'belongsystem': '',
                'evaluatecount': '1',
                'evaluatorPhone': f'{tel}',
                'token': f'{token}',
                'evaluateDetailArray[]': '510',
                'huaKuaiFlag': 'true',
                'checkFlag': 'notRobot',
                'projectNo': f'{projectno}',
                'proStatus': '3',
         } 
        requests.packages.urllib3.disable_warnings()
        resp = requests.post(url=url, headers=headers, data=payload,verify=False,timeout=200)
        print(resp.json())


def second_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno):
        payload = {
                'fn': 'save',
                'projid': f'{projid}',
                'serviceCode': f'{servicecode}',
                'evaluatefrom':'4',
                'userType':'', 
                'evaluatorName': f'{evaluatorname}',
                'evaluteCount': '2',
                'projectname': f'{projectname}',
                'isOpened': '1',
                'checkState': '1',
                'evaluateContent':'',
                'satisfactionEvaluate': '5',
                'evaluateDetail': '510',
                'syncStatus': 'I',
                'isAboveLegalday': '2',
                'isMediation': '2',
                'serviceAttitudeEvaluate': '1',
                'isAnonymity': '2',
                'serviceAttitudeReason': '',
                'workAttitudeEvaluate': '1',
                'workAttitudeReason': '',
                'evaluatorCardnumber': f'{cardnumber}',
                'belongsystem': '',
                'evaluatecount': '2',
                'evaluatorPhone': f'{tel}',
                'token': f'{token}',
                'evaluateDetailArray[]': '510',
                'huaKuaiFlag': 'true',
                'checkFlag': 'notRobot',
                'projectNo': f'{projectno}',
                'proStatus': '2',
         } 
        requests.packages.urllib3.disable_warnings()
        resp = requests.post(url=url, headers=headers, data=payload,verify=False,timeout=200)
        print(resp.json())


def third_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno):
        payload = {
                'fn': 'save',
                'projid': f'{projid}',
                'serviceCode': f'{servicecode}',
                'evaluatefrom':'4',
                'userType':'', 
                'evaluatorName': f'{evaluatorname}',
                'evaluteCount': '3',
                'projectname': f'{projectname}',
                'isOpened': '1',
                'checkState': '1',
                'evaluateContent':'',
                'satisfactionEvaluate': '5',
                'evaluateDetail': '510',
                'syncStatus': 'I',
                'isAboveLegalday': '2',
                'isMediation': '2',
                'serviceAttitudeEvaluate': '1',
                'isAnonymity': '2',
                'serviceAttitudeReason': '',
                'workAttitudeEvaluate': '1',
                'workAttitudeReason': '',
                'evaluatorCardnumber': f'{cardnumber}',
                'belongsystem': '',
                'evaluatecount': '3',
                'evaluatorPhone': f'{tel}',
                'token': f'{token}',
                'evaluateDetailArray[]': '510',
                'huaKuaiFlag': 'true',
                'checkFlag': 'notRobot',
                'projectNo': f'{projectno}',
                'proStatus': '1',
         } 
        requests.packages.urllib3.disable_warnings()
        resp = requests.post(url=url, headers=headers, data=payload,verify=False,timeout=200)
        print(resp.json())


def get_cookie(responsecookies):
    cookies = requests.utils.dict_from_cookiejar(responsecookies)
    jsession = cookies.get('JSESSIONID')
    app_cook = cookies.get('app_cook')
    cookie ={
        'cookie':f'JSESSIONID={jsession}; app_cook={app_cook}', 
    }
    return cookie


if __name__ == '__main__':
    headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9', 
                'Connection': 'keep-alive',
                'Content-Length': '991',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Host': 'was.hnzwfw.gov.cn' , 
                'Origin':'http://was.hnzwfw.gov.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                }
    he=HandleExcle(savefile)
    for i in range(0,he.max_num): 
        result = he.get_result(i)
        tel = he.get_tel(i)
        url = he.get_url(i)
        projid = he.get_projid(i)
        servicecode = he.get_servicecode(i)
        evaluatorname = he.get_name(i)
        projectname = he.get_servicename(i)
        cardnumber = he.get_idcard(i)
        projectno = he.get_implementcode(i)
        resp = requests.get(url, headers=headers)
        token = get_url_token(resp.text)        
        cookie = get_cookie(resp.cookies)
        headers.update(cookie)
        first_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno)
        second_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno)
        third_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno)




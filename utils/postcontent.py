# coding:utf-8
import requests
from utils.handleexcel import write_excle
from utils.config import contents,savefile
import json

class ProjectContent(object):
     
    def __init__(self,date_time,start_time,cityid,cityname,session_value):
        self.url ="http://59.207.104.4:8062/bjxt/preApasinfo/list"
        self.headers ={
                    'Connection': 'keep-alive',
                    'Content-Length': '58',
                    'Host': '59.207.104.4:8062 ' , 
                    'Origin':'http://59.207.104.4:8060',
                    'X-Requested-With':'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6', 
                    'Cookie': f'SESSION={session_value}',  
                    }
        self.date_time=date_time
        self.start_time = start_time
        self.cityid=cityid
        self.cityname=cityname
    

    def get_projectlist(self):
        payload = {
                "date_end": self.date_time,
                "date_start": self.start_time,
                "order": "asc",
                "offset":0,
                "limit": 100,
                "idCard": "",
                "projid": "",
                "serviceCode": "",
                "deptid": f"{self.cityid}",
                "advance": {},
                }
        requests.packages.urllib3.disable_warnings()
        resp = requests.post(self.url, data=payload, headers=self.headers,verify=False,timeout=500)
        pro_contents=resp.json()
        if "total" in pro_contents.keys():
            max_num = int(pro_contents["total"])
            page_num = max_num//100+1
            for i in range(page_num):
                offset_num = i*100
                self.get_projectlist_page(offset_num)
            write_excle(contents,savefile)

    def get_projectlist_page(self,offset_num):
        payload = {
                "date_end": self.date_time,
                "date_start": self.start_time,
                "order": "desc",
                "offset":offset_num,
                "limit": 100,
                "idCard": "",
                "projid": "",
                "serviceCode": "",
                "deptid": self.cityid,
                "advance": {},
                }
        requests.packages.urllib3.disable_warnings()
        resp = requests.post(self.url, data=payload, headers=self.headers,verify=False,timeout=500)
        pro_contents=resp.json()
        if 'rows' in pro_contents.keys():
            pro_lists=pro_contents['rows']
            if len(pro_lists) > 0:
                for pro_list in pro_lists:
                    projid=pro_list["projid"]
                    servicecode=pro_list["servicecode"]
                    transact_name=pro_list["projectname"]
                    card_num=pro_list["applyCardnumber"]
                    contactman =pro_list["contactman"]
                    contactman_cardnumber = pro_list["contactmanCardnumber"]
                    tel_num=pro_list["telphone"]
                    applicant=pro_list["applyname"]
                    dept_name=pro_list["deptname"]
                    time=pro_list["transacttime"]
                    result=pro_list["handlestate"]
                    projectNo = pro_list["gbProjectNo"]
                    content={
                        "申报号":projid,
                        '办理单位':dept_name,
                        "事项编码":servicecode,
                        "办件名称":transact_name,
                        "证件号码":str(card_num),
                        "联系人":contactman,
                        '联系人证件号码':contactman_cardnumber,
                        "手机号码":str(tel_num),
                        "申请人":applicant,
                        "办结时间":time,
                        "办件状态":result,
                        "办件号":projectNo,
                    }
                    print(content)
                    contents.append(content)
        





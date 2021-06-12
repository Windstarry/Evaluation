# coding:utf-8
from utils.handleexcel import HandleExcle,ExcleRemoveDupl,ExcelConcat,write_excle
from utils.postcontent import ProjectContent,CommitContent
from utils.test_login import Test_loggin
from utils.config import login_url,contents,savefile,filecontents,setindex_col,headers
import requests,re

def main():
    #运行程序
    test_loggin = Test_loggin(login_url=login_url)
    jsessionid=test_loggin.get_jsessionid()
    for i in range(pagestart,pageend):
        procontens=ProjectContent(i,cityid,cityname,jsessionid).get_projectlist()
    write_excle(contents,savefile)
    print("{}保存完毕".format(savefile))
    #去除申报号在已评价事项里办件信息
    erd=ExcleRemoveDupl(savefile,filecontents,savefile,setindex_col)
    erd.excle_removedupl()


def first_evaluate():
    he=HandleExcle(savefile)
    if "评价状态" not in he.column_list:
        he.insert_column()
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
        if result=="已评价":
            print(f"第{i}件事项已评价")
        else:
            resp = requests.get(url, headers=headers)
            token = get_url_token(resp.text)        
            cookie = get_cookie(resp.cookies)
            headers.update(cookie)
            first_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno)
            second_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno)
            third_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno)
            msg=first_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno)['msg']
            if msg =='评价成功！' or msg =='重复评价！！！':
                he.resultstate(i)
            if i%400==0:
                he.save_excle(savefile)
    he.save_excle(savefile)
    #将已评价完的数据保持到汇总表中
    ec=ExcelConcat(savefile,filecontents,filecontents,setindex_col)
    ec.excle_concat()

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
        return resp.json()


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
    cityid='001003018006016'
    cityname='修武县'
    # cityid='001003018006016003017'
    # cityname='县税务局'
    # cityid='001003018006016003018'
    # cityname='修武县人力资源和社会保障局'
    #设置读取页面起始结束页
    # cityid="001003018006016003009"
    # cityname="修武县市场监督管理局"
    pagestart=1
    pageend=3
    # #运行程序
    main()
    first_evaluate()



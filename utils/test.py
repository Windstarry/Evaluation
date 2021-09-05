# coding:utf-8
from utils.handleexcel import HandleExcle,ExcleRemoveDupl,ExcelConcat,write_excle
from utils.postcontent import ProjectContent
from utils.test_login import TestLogin
from utils.config import login_url,home_url,contents,savefile,filecontents,setindex_col,headers
import requests,re,time,datetime


def main(date_time,start_time,cityid,cityname):
    #运行程序
    test_loggin = TestLogin(login_url=login_url,home_url=home_url)
    session_value=test_loggin.get_session_value()
    procontens=ProjectContent(date_time,start_time,cityid,cityname,session_value).get_projectlist()
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
            msg=first_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno)['msg']
            # first_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno)
            # second_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno)
            # third_post_data(url,headers,projid,servicecode,evaluatorname,projectname,cardnumber,tel,token,projectno)            
            if msg =='评价成功！' or msg =='重复评价！！！':
                he.resultstate(i)
            if i%2000==0:
                he.save_excle(savefile)
        #time.sleep(1)
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
        post_url = "http://59.207.104.196:8081/evaluation-web/api/v1/zwfw/evaluate/save.do"
        resp = requests.post(url=post_url, headers=headers, data=payload,verify=False,timeout=200)
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
        post_url = "http://59.207.104.196:8081/evaluation-web/api/v1/zwfw/evaluate/save.do"
        resp = requests.post(url=post_url, headers=headers, data=payload,verify=False,timeout=200)
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
        post_url = "http://59.207.104.196:8081/evaluation-web/api/v1/zwfw/evaluate/save.do"
        resp = requests.post(url=post_url, headers=headers, data=payload,verify=False,timeout=200)
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
    # #运行程序
    date_time = datetime.date.today()
    start_time = datetime.date.today()-datetime.timedelta(days=10)
    main(date_time,start_time,cityid,cityname)
    first_evaluate()
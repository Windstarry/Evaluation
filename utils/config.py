# coding:utf-8

#test_login类中需要的参数
login_url = 'http://59.207.104.12:8090//login'
USENAME="焦作市政数局_政务2019"
PASSWORD="Abc123#$"
#电话邀评账号
TELUSENAME="焦作市修武县_电话邀评"
TELPASSWORD="Abc123#$"
EVALUATIONNAME="焦作市修武县_电话邀评"

#postcontent中，文件保存的地址
contents=[]
savefile = ".\date\办件详情信息.xlsx"
#和已评价的数据进行对比的文件
setindex_col='申报号'
filecontents=".\date\已评价办件信息汇总.xlsx"

#电话邀评人，联系电话
offerorname="薛玉莹"
offerortelphone='0391-7118602'

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
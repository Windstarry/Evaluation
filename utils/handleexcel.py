# coding:utf-8
import pandas as pd
from utils.servicecode import gic
import re

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
        if idcard=='空':
            idcard=self.df["联系人证件号码"].at[x]
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
        # servicecode = self.get_servicecode(x)
        # projid = self.get_projid(x)
        # if servicecode in gic.keys():
        #     implementcode=str(gic[servicecode])+projid[7:15]+projid[-4:]
        #     return implementcode
        # else:
        #     implementcode="错误"
        #     print("没有找到该事项")
        #     return implementcode
        implementcode = self.df["评价状态"].at[x]
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
        elif tel_num == '无':
            tel_num = "0391-7118602"
        return tel_num


class ExcleRemoveDupl(object):
    
    def __init__(self,fileA,fileB,fileSave,setindex_col):
        self.fileA = fileA
        self.fileB = fileB
        self.fileSave = fileSave
        self.setindex_col = setindex_col


    def excle_removedupl(self):
        df1=pd.read_excel(self.fileA)
        df2=pd.read_excel(self.fileB)
        projids=list(df2[self.setindex_col])
        #去除申报号在已评价事项里办件信息
        result=df1[~df1[self.setindex_col].isin(projids)]
        #设置表格的index
        result.set_index(self.setindex_col,inplace=True)
        result.to_excel(self.fileSave)


class ExcelConcat(object):
    
    def __init__(self,fileA,fileB,fileSave,setindex_col):
        self.fileA = fileA
        self.fileB = fileB
        self.fileSave = fileSave
        self.setindex_col = setindex_col

    def excle_concat(self):
        df1=pd.read_excel(self.fileA)
        df2=pd.read_excel(self.fileB)
        #读取两个excle文件合并
        result = pd.concat((df1,df2))
        #以setindex_col为基准去掉重复数据
        result.drop_duplicates(subset=[self.setindex_col],keep='first',inplace=True)
        #设置表格的index
        result.set_index(self.setindex_col,inplace=True)
        result.to_excel(self.fileSave)


def write_excle(content,savefile):
    df=pd.DataFrame.from_dict(content)
    df.set_index(df.columns[0],inplace=True)
    df.to_excel(savefile)



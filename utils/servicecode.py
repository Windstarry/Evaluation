# coding:utf-8
import pandas as pd


class GetImplementCode(object):
    
    def __init__(self,filename):
        self.filename = filename

    def get_implementcode(self):
        df=pd.read_excel(self.filename)
        servicecode_dict={}
        for i in range(0,df.shape[0]):
            servicecode=df["事项编码"].at[i]
            implementcode=df["实施编码"].at[i]
            servicecode_dict[servicecode]=implementcode
        return servicecode_dict

    def get_codename(self):
        df=pd.read_excel(self.filename)
        codename_dict={}
        for i in range(0,df.shape[0]):
            servicecode=df["事项编码"].at[i]
            codename=df["业务办理项名称"].at[i]
            codename_dict[codename]=servicecode
        return codename_dict


gic=GetImplementCode("./source/修武县政务服务事项编码&实施编码.xlsx").get_implementcode()
gic_name=GetImplementCode("./source/修武县政务服务事项编码&实施编码.xlsx").get_codename()

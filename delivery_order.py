# -*-coding=utf-8-*-
import re

__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
#交割单处理 保存交割单到数据库
import os,datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot  as plt
from setting import  get_engine
engine = get_engine('db_stock')
pd.set_option('display.max_rows',None)

class Delivery_Order():
    def __init__(self):
        print "Start"
        path=os.path.join(os.getcwd(),'private/2016/')
        if os.path.exists(path)==False:
            os.mkdir(path)
        os.chdir(path)

    #合并一年的交割单
    def years(self):
        df_list=[]
        k=[str(i) for i in range(1,13)]
        # print k
        j=[i for i in range(1,13)]
        result=[]
        for i in range(1,13):
            filename='2016-%s.xls' %str(i).zfill(2)
            #print filename
            t=pd.read_table(filename,encoding='gbk',dtype={u'证券代码':np.str})
            # fee=t[u'手续费'].sum()+t[u'印花税'].sum()+t[u'其他杂费'].sum()
            # print i," fee: "
            # print fee
            df_list.append(t)
            # result.append(fee)
        df=pd.concat(df_list)
        df[u'成交日期']=pd.to_datetime(df[u'成交日期'],format='%Y%m%d')
        # df[u'成交日期']=map(lambda x:datetime.datetime.strptime(str(x),"%Y%m%d"),df[u'成交日期'])
        df=df[df[u'摘要']!=u'申购配号']
        df=df[df[u'摘要']!=u'质押回购拆出']
        df=df[df[u'摘要']!=u'拆出质押购回']
        # print df.info()
        # print df
        # print df['2017-01']
        del df[u'合同编号']
        del df[u'备注']
        del df[u'股东帐户']
        del df[u'结算汇率']
        del df[u'Unnamed: 16']

        df=df.sort_values(by=u'成交日期')
        df=df.set_index(u'成交日期')

        df.to_sql('tb_delivery',engine,if_exists='append')
        # df=df[(df[u'摘要']==u'证券卖出') | (df[u'摘要']==u'证券买入')]
        # df= df.groupby(df[u'证券名称'])
        # print df.describe()
        # print df[u'手续费'].sum()
        # print df[u'印花税'].sum()
        df1=df[[u'证券名称',u'证券代码',u'成交数量',	u'成交均价'	,u'成交金额',u'手续费',	u'印花税',u'发生金额',u'操作']]
        # print df1[u'证券名称'].value_counts()
        print df.groupby(by=[u'证券名称'])[u'发生金额'].sum()
        # df1.to_excel('2017-all.xls')
        # print df1.groupby(df1[u'证券名称']).describe()
        # print df1['2017-02']
        #df.to_excel('2016_delivery_order.xls')
        # self.caculation(df)
        # plt.plot(j,result)
        # plt.show()

    def caculation(self,df):
        fee=df[u'手续费'].sum()+df[u'印花税'].sum()+df[u'其他杂费'].sum()
        print fee
    #计算每个月的费用
    def month(self):
        pass

# 银转证
def bank_account():
    folder_path = os.path.join(os.path.dirname(__file__),'private')
    os.chdir(folder_path)

    df_list=[]
    for file in os.listdir(folder_path):
        if re.search('2',file.decode('gbk')):
            df = pd.read_table(file,encoding='gbk')
            # df[df['']]
            # print df
            # df_list.append(df[[u'日期',u'操作',u'发生金额']])
            df_list.append(df)
    total_df=pd.concat(df_list)
    # total_df=total_df.reset_index()
    # del total_df[u'level_0']
    del total_df[u'货币单位']
    del total_df[u'合同编号']
    del total_df[u'Unnamed: 8']
    del total_df[u'银行名称']
    # print total_df
    # f=total_df[total_df[u'操作']==u'证券转银行'][u'发生金额']*-1
    total_df[u'发生金额']=map(lambda x,y:x*-1 if y==u'证券转银行' else x, total_df[u'发生金额'],total_df[u'操作'])
    # print total_df.columns
    # print total_df5
    # total_df=total_df.reset_index()
    # total_df=total_df.set_index('index')
    # total_df=total_df.reset_index(drop=True)
    total_df[u'委托时间']=map(lambda x:str(x).zfill(6),total_df[u'委托时间'])

    total_df[u'日期']=map(lambda x,y:str(x)+ " "+y,total_df[u'日期'],total_df[u'委托时间'])
    total_df[u'日期']=pd.to_datetime(total_df[u'日期'],format='%Y%m%d %H%M%S')
    total_df=total_df.set_index(u'日期')

    df= total_df[total_df[u'备注']==u'成功[[0000]交易成功]']
    # print df
    # print total_df.iloc[131]
    # print total_df[u'备注'].values
    print df[u'发生金额'].sum()
    # df.dropna('')
    del df[u'备注']
    del df[u'委托时间']
    df.to_sql('tb_bank_cash',engine,if_exists='replace')
    # print df['2018']
def main():
    obj=Delivery_Order()
    obj.years()
    # bank_account()

main()



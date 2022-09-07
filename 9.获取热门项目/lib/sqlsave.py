import sys
import os
import pymysql
sys.path.append(os.path.abspath('.')+'/pro/')
from conf.setting import *
import pandas as pd
df = pd.read_csv('D://vscodefile/pro/db/ave2022-09-02 09更新.csv')
conn = pymysql.connect(host=host,port=port,user=user,password=password,database=database,charset="utf8")
cursor = conn.cursor()
# sql="""create table hotcoin (
#     序号 INT,
#     名称 CHAR(20),
#     价格 INT,
#     24h涨幅 CHAR,
#     合约 CHAR,
#     所属链 CHAR,
#     推特 CHAR,
#     电报 CHAR,
#     更新时间 DATETIME
#     )"""
sql = """insert into hotcoin (序号,名称,价格) VALUEs (1,"KFC",0.000045)"""
res=cursor.execute(sql)
conn.commit()
conn.close()
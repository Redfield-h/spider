import json
import time
import datetime
import re
import os
import sys
import subprocess
import pandas as pd
import pytesseract
from bs4 import BeautifulSoup
from tqdm import tqdm
from PIL import Image
import base64
import cv2 as cv
from itertools import zip_longest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import threading
import pymysql
sys.path.append(os.path.abspath('.')+'/pro/')
from conf.setting import *
driver_path = "D://vscodefile/8.获取热门代币"
save_path = 'D://vscodefile//pro//db'

class GetAve:
    
    def __init__(self,no):
        self.no = no  #前no项代币
        chrome_options = Options()
        chrome_options.add_argument('headless') #无界面
        chrome_options.add_argument('--ignore-certificate-errors')  #忽略证书错误
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  #忽略错误提示
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation']) #防检测
        self.driver = webdriver.Chrome(service=Service(driver_path+"/chromedriver.exe"),options=chrome_options)
        self.driver.set_window_size(1920,1080)  #设置分辨率
        self.cookies = {
            'domain': 'avedex.cc',
            'expiry': 1662347549,
            'httpOnly': False,
            'name': 'ave_token',
            'path': '/',
            'secure': False,
            'value': '133561fcb642e3599bd1b79f6abd33331661742728595159144'
            }
        #链接数据库
        self.conn = pymysql.connect(host=host,port=port,user=user,password=password,database=database,charset="utf8")
        self.cursor = self.conn.cursor()

    def sqlsave(self,coindata):
        """
        存储数据库
        """
        sql = f"""insert into hotcoin ({list(coindata.keys())}) VALUEs ({list(coindata.values())})"""
        self.cursor.execute(sql)
        
    def login(self):
        """
        链接页面
        """
        while True:
            try:
                self.driver.get("https://avedex.cc/market")
                self.driver.add_cookie(cookie_dict = self.cookies)  #免验证cookie
                self.driver.get("https://avedex.cc/market")
                time.sleep(2)
        
                #新币榜
                page_value = '/html/body/div[1]/main/section/div[1]/div[1]/ul/li[3]/label/span'
                self.driver.find_element(by=By.XPATH,value=page_value).click()
                time.sleep(2)

                #按24h增长率排序
                page_value = "/html/body/div[1]/main/section/div[2]/div/div[1]/div[2]/table/thead/tr/th[4]/div/span/i[1]"
                self.driver.find_element(by=By.XPATH,value=page_value).click()
                time.sleep(2)
                return
            except:
                time.sleep(2) #等候2s重试
                continue
        
    def get_coin(self,result,pool_sema):
        """
        获取详细详细
        """
        self.login()
        
        page = self.no
     
        page_value = f'/html/body/div[1]/main/section/div[2]/div/div[1]/div[3]/div/div[1]/div/table/tbody/tr[{page}]'
        self.driver.implicitly_wait(5)  #隐式等待5秒
        coin = self.driver.find_element(by=By.XPATH,value=page_value).text.split('\n')[:-3]  #代币信息->列表
        ans = ['序号','名称','价格','24h涨幅']
        res = dict(zip_longest(ans,coin))
    
        #跳转到详细页面
        page_value = f'/html/body/div[1]/main/section/div[2]/div/div[1]/div[3]/div/div[1]/div/table/tbody/tr[{page}]'
        self.driver.implicitly_wait(5)  #隐式等待5秒
        self.driver.find_element(by=By.XPATH,value=page_value).click()

        #点击info
        time.sleep(2)
        page_value = '/html/body/div[1]/main/section/div[1]/div[4]/section/div[1]/div[1]/div/div[2]'
        self.driver.implicitly_wait(5)  #隐式等待5秒
        self.driver.find_element(by=By.XPATH,value=page_value).click()

        #代币合约&所属链
        current_url = self.driver.current_url
        contract = re.search('(?<=token/).*?(?=-)',current_url).group()
        chain = re.search('(?<=-).*',current_url).group()
        res['合约'] = contract
        res['所属链'] = chain

        #相关链接
        try:
            page_value = '/html/body/div[1]/main/section/div[1]/div[4]/section/div[2]/div[1]/div/ul/li'
            length = len(self.driver.find_elements(by=By.XPATH,value=page_value))
            page_value = f'/html/body/div[1]/main/section/div[1]/div[4]/section/div[2]/div[1]/div/ul/li[{length}]/div/a'
            for i in self.driver.find_elements(by=By.XPATH,value=page_value):
                link = i.get_attribute('href')
                if 'twitter' in link:
                    res['推特'] = link
                elif 't.me' in link:
                    res['电报'] = link
                elif 'facebook' in link:
                    res['facebook'] = link
                else:
                    res['其它链接'] = link
        except:
            pass
    
        result.append(res)    
        self.sqlsave(res)
        self.conn.close()
        self.driver.close()
        pool_sema.release() #释放已完成线程
        
        
def GA_main():
    result = []
    max_connection = 4 #4线程
    pool_sema = threading.BoundedSemaphore(max_connection) #最大线程量
    thread_list = []
    for i in tqdm(range(1,11)):
        pool_sema.acquire()
        thread = threading.Thread(target=GetAve(i).get_coin,args=[result,pool_sema])
        thread.start()
        thread_list.append(thread)
        
    for t in thread_list:
        t.join()

    date_ = datetime.datetime.now().strftime('%Y-%m-%d %H')   #更新时间
    df = pd.DataFrame(result)
    df['序号'] = df['序号'].map(lambda i:int(i))
    df['更新时间'] = date_
    df = df.sort_values('序号')
    df.to_csv(save_path+f'/ave{date_}更新.csv',index=False)

    return df
    
if __name__ == "__main__":
    GA_main()
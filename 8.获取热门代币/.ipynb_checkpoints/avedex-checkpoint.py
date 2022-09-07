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
import threading

class GetAve:
    
    def __init__(self,no):
       
        chrome_options = Options()
        chrome_options.add_argument('headless') #无界面
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation']) #防检测
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(1920,1080)  #设置分辨率
        self.no = no  #前no项代币
        
        self.cookies = {
            'domain': 'avedex.cc',
            'expiry': 1662347549,
            'httpOnly': False,
            'name': 'ave_token',
            'path': '/',
            'secure': False,
            'value': '133561fcb642e3599bd1b79f6abd33331661742728595159144'
            }
        
    def login(self):
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
        
    def get_coin(self):
        self.login()
        # print('===>正在获取中')
        global result
        page = self.no
     
        page_value = f'/html/body/div[1]/main/section/div[2]/div/div[1]/div[3]/div/div[1]/div/table/tbody/tr[{page}]'
        self.driver.implicitly_wait(5)  #隐式等待5秒
        coin = self.driver.find_element(by=By.XPATH,value=page_value).text.split('\n')  #代币信息->列表
        ans = ['序号','币种','最新价格','24h涨幅','流通量','开盘价','风险性']
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
        links = []
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
                else:
                    res['其它链接'] = link
        except:
            pass
    
        result.append(res)    
        
        self.driver.close()
        pool_sema.release() #释放已完成线程
        
        
def main():
    thread_list = []
    for i in tqdm(range(1,11)):
        pool_sema.acquire()
        thread = threading.Thread(target=GetAve(i).get_coin)
        thread.start()
        thread_list.append(thread)
        
    for t in thread_list:
        t.join()

    date_ = datetime.datetime.now().strftime('%Y-%m-%d %H')   #更新时间
    df = pd.DataFrame(result)
    df['序号'] = df['序号'].map(lambda i:int(i))
    df['更新时间'] = date_
    df = df.sort_values('序号')
    df.to_csv(f'./save/ave{date_}更新.csv',index=False)
    
if __name__ == "__main__":
    result = []
    max_connection = 4 #4线程
    pool_sema = threading.BoundedSemaphore(max_connection) #最大线程量
    main()
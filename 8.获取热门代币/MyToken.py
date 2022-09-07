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
path = "D://vscodefile/8.获取热门代币"

class GetMyToken:

    def __init__(self,no) -> None:
        chrome_options = Options()
        chrome_options.add_argument('--headless') #无界面
        # chrome_options.add_argument('blink-settings=imagesEnabled=false') #不加载图片
        chrome_options.add_argument('--ignore-certificate-errors')  #忽略证书错误
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  #忽略错误提示
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation']) #防检测
        # driver = webdriver.Chrome(options=chrome_options)
        self.driver = webdriver.Chrome(service=Service(path+"/chromedriver.exe"),options=chrome_options)
        self.driver.maximize_window()  #最大化窗口
        # driver.set_window_size(1920,1080)  #设置分辨率
        self.no = no
    
    def login(self):
        while True:
            try:
                self.driver.get("https://www.mytoken.io/zh/latest/")
                time.sleep(2)

                #关闭弹窗
                page_value = '/html/body/div[2]/div/div[2]/div/div[2]/button/span'
                self.driver.implicitly_wait(5)  #隐式等待5秒
                self.driver.find_element(by=By.XPATH,value=page_value).click()
                time.sleep(2)

                #按24h增长率排序
                page_value = "/html/body/div/div/main/div/div/div[3]/table/thead/tr/th[5]/div/div/img[2]"
                self.driver.find_element(by=By.XPATH,value=page_value).click()
                time.sleep(2)
                return
            except:
                time.sleep(2)
                continue


    def request_url(self):
        self.login()
        global result
        
        #一般信息
        page_value = f"/html/body/div/div/main/div/div/div[3]/table/tbody/tr[{self.no}]"
        self.driver.implicitly_wait(30)  #隐式等待5秒
        coin = self.driver.find_element(by=By.XPATH,value=page_value).text.split('\n')[:-3]
        ans = ['序号','名称1','名称2','价格','24h','7d']
        res = dict(zip_longest(ans,coin))
        del res['名称2']
        
        #跳转到详细页面
        page_value = f"/html/body/div/div/main/div/div/div[3]/table/tbody/tr[{self.no}]"
        self.driver.implicitly_wait(30)  #隐式等待5秒
        self.driver.find_element(by=By.XPATH,value=page_value).click()
        time.sleep(5)
        
        
        #跳过公告弹窗
        try:
            page_value = '/html/body/div[2]/div/div[2]/div/div[2]/button/span'
            self.driver.implicitly_wait(5)  #隐式等待5秒
            self.driver.find_element(by=By.XPATH,value=page_value).click()
        except:
            pass
        time.sleep(2)  #等待资源加载
        
        page_value = f"/html/body/div[1]/div/main/div/div/div[3]/div[2]/div[2]/div/div"
        for i in self.driver.find_elements(by=By.XPATH,value=page_value):
            basedata = i.text.split('\n')
            res[basedata[0]] = basedata[1]

        page_value = f"/html/body/div[1]/div/main/div/div/div[3]/div[2]/div[3]/div/div"
        for i in self.driver.find_elements(by=By.XPATH,value=page_value):
            links = i.text.split('\n')
            res[links[0]] = links[1]
        
#         #所属链
#         try:
#             page_value = f"/html/body/div[1]/div/main/div/div/div[3]/div[2]/div[3]/div/div[1]"
#             self.driver.implicitly_wait(5)  #隐式等待5秒
#             chain = self.driver.find_element(by=By.XPATH,value=page_value).text
#             if chain.split('\n')[0] == '基础链':
#                 res['所属链'] = chain.split('\n')[-1]
#         except:
#             pass
            
#         #合约
#         try:
#             page_value = f"/html/body/div[1]/div/main/div/div/div[3]/div[2]/div[3]/div/div[2]"
#             self.driver.implicitly_wait(5)  #隐式等待5秒
#             contract = self.driver.find_element(by=By.XPATH,value=page_value).text
#             if contract.split('\n')[0] in ['BSC','Ethereum','Polygon']:
#                 res['合约'] = contract.split('\n')[1]
#         except:
#             pass
            
#         #链接
#         links = []
#         try:
#             page_value = f"/html/body/div[1]/div/main/div/div/div[3]/div[2]/div[4]/div/div"
#             self.driver.implicitly_wait(5)  #隐式等待5秒
#             link_list = self.driver.find_elements(by=By.XPATH,value=page_value)
#             length = len(link_list)
#             for i in range(length):
#                 if link_list[i].text.split('\n')[0] == '官网':
#                     page_value = f"/html/body/div[1]/div/main/div/div/div[3]/div[2]/div[4]/div/div[{i+1}]/a"
#                     res['官网'] = self.driver.find_element(by=By.XPATH,value=page_value).get_attribute('href')

#                 elif link_list[i].text.split('\n')[0] == '社交媒体':
#                     page_value = f"/html/body/div[1]/div/main/div/div/div[3]/div[2]/div[4]/div/div[{i+1}]/div/a"
#                     for j in (self.driver.find_elements(by=By.XPATH,value=page_value)):
#                         link = j.get_attribute('href')
#                         if 'twitter' in link:
#                             res['推特'] = link
#                         elif 't.me' in link:
#                             res['电报'] = link
#                         else:
#                             res['其它链接'] = link
#                     #     links.append(j.get_attribute('href'))
#                     # res['相关链接'] = links
#         except:
#             pass
        
        
        
        
        result.append(res)    
        
        self.driver.close()
        pool_sema.release() #释放已完成线程

def main():
    thread_list = []
    for i in tqdm(range(1,11)):
        pool_sema.acquire() 
        thread = threading.Thread(target=GetMyToken(i).request_url)
        thread.start()
        thread_list.append(thread)

    for t in thread_list:
        t.join()

    date_ = datetime.datetime.now().strftime('%Y-%m-%d %H')   #更新时间
    df = pd.DataFrame(result)
    df['序号'] = df['序号'].map(lambda i:int(i))
    df['更新时间'] = date_
    df = df.sort_values('序号')
    #只保留有合约或官网信息的代币
    df.to_csv(path+f'/save/Mytoken{date_}更新.csv',index=False)
    
if __name__ == "__main__":
    result = []
    lock = threading.Lock() #设置线程锁
    max_connection = 4 #10线程
    pool_sema = threading.BoundedSemaphore(max_connection) #最大线程量
    main()
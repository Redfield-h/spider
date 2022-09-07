import json
import time
import datetime
from tqdm.contrib import tzip
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
# from itertools import zip_longest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import threading

#浏览器驱动路径
driver_path = "D://vscodefile//pro//conf"
#文件保存路径
save_path = 'D://vscodefile//pro//db'
#合约地址读取路径
contrac_addr = "D://vscodefile//pro//conf"

class GetPool:
    
    def __init__(self,addr):
        self.token = addr
        url = "https://avedex.cc/token/"
        self.addr = url + addr + "-bsc"
    
        chrome_options = Options()
        chrome_options.add_argument('headless') #无界面
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation']) #防检测
        self.driver = webdriver.Chrome(service=Service(driver_path+"/chromedriver.exe"),options=chrome_options)
        self.driver.maximize_window()  #最大化窗口
        # driver.set_window_size(1920,1080)  #设置分辨率
        self.cookie = {
            'domain': 'avedex.cc',
            'expiry': 1662540177,
            'httpOnly': False,
            'name': 'ave_token',
            'path': '/',
            'secure': False,
            'value': 'd410b464d9e16b54849d9ccef35ac5921661935370609837145'
            }
    
    def login(self):
        while True:
            try:
                self.driver.get(self.addr)
                self.driver.add_cookie(cookie_dict = self.cookie)
                self.driver.get(self.addr)
                time.sleep(5)
                return
            except:
                time.sleep(2)
                continue
    
    def request_(self,result,pool_sema):
        self.login()  #登录页面
        
        ans = dict()
        ans['合约'] = self.token
        
        #
        page_value = "/html/body/div[1]/main/section/div[1]/div[1]/div/div[1]/div[2]/div[1]/span"
        self.driver.implicitly_wait(5)  #隐式等待5秒
        name = self.driver.find_element(by=By.XPATH,value=page_value).text
        ans['名称'] = name
        
        #
        page_value = "/html/body/div[1]/main/section/div[1]/div[4]/section/div[2]/div[1]/div/div/table/tr[2]/td[4]/span[2]"
        self.driver.implicitly_wait(5)  #隐式等待5秒
        num = self.driver.find_element(by=By.XPATH,value=page_value).text.replace('/','').replace(',','')
        ans['数量'] = num
        
        #
        page_value = "/html/body/div[1]/main/section/div[1]/div[4]/section/div[2]/div[1]/div/div/table/tr[2]/td[2]/span[2]"
        self.driver.implicitly_wait(5)  #隐式等待5秒
        type_ = self.driver.find_element(by=By.XPATH,value=page_value).text.replace('/','')
        ans['种类'] = type_

        self.driver.close()
        result.append(ans)
        pool_sema.release() #释放已完成线程


def GP_main():
    lock = threading.Lock() #设置线程锁
    max_connection = 4 #4线程
    pool_sema = threading.BoundedSemaphore(max_connection) #最大线程量
    result = []
    thread_list = []
    with open(contrac_addr+'/地址.txt','r',encoding='utf-8') as f:
        addrs = f.read()
        for addr in tqdm(addrs.split('\n')):
            #爬取池子余额
            pool_sema.acquire()
            thread = threading.Thread(target=GetPool(addr).request_,args=[result,pool_sema])
            thread.start()
            thread_list.append(thread)

        for t in thread_list:
            t.join()
        
    df = pd.DataFrame(result)
    df['数量'] = df['数量'].map(lambda i:float(i))        
    df.sort_values('数量',ascending=False).reset_index(drop=True).to_csv(save_path+'/线索余额.csv')
 
if __name__ == "__main__":
    GP_main()
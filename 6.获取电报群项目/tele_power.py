import json
import time
import re
import os
import sys
import subprocess
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains #模拟鼠标
from selenium.webdriver.common.by import By


class TeleGram:
    
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('headless') #不显示界面
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://web.telegram.org/z/")
        print('===》正在后台打开chrome浏览器')
        time.sleep(10)
        pass
    
    def login(self):
        #登录窗
        page_value = "/html/body/div[1]/div/div/div/div/div/button[1]"
        self.driver.find_element(by=By.XPATH,value=page_value).click()
        print('===》正在打开登录页面')
        time.sleep(10)
        #输入手机号登录
        page_value = "/html/body/div[1]/div/div/div/div/div/form/div[2]/input"
        self.driver.find_element(by=By.XPATH,value=page_value).clear()
        time.sleep(1)
        self.driver.find_element(by=By.XPATH,value=page_value).send_keys(input("===>请输入手机号+86"))
        time.sleep(1)
        #登录
        page_value = "/html/body/div[1]/div/div/div/div/div/form/button[1]/div"
        self.driver.find_element(by=By.XPATH,value=page_value).click()
        print('===》接收验证码中')
        time.sleep(10)
        #输入验证码
        page_value = "/html/body/div[1]/div/div/div/div/div/div[2]/input"
        self.driver.find_element(by=By.XPATH,value=page_value).send_keys(input("===>请输入验证码"))
        print('===》正在登录')
        time.sleep(10)
        
    def get_group(self):
        print('===》正在爬取当日发布项目')
        #转到项目发布群页面
        page_value = '/html/body/div[1]/div/div/div/div/div[1]/div[1]/div/div/div[2]/div/div/div[1]/div[2]/span'
        self.driver.find_element(by=By.XPATH,value=page_value).click()
        #全部的项目发布群
        page_value = "/html/body/div[1]/div/div/div/div/div[1]/div[1]/div/div/div[2]/div/div/div[2]/div[2]/div/div/div"
        all_groups = self.driver.find_elements(by=By.XPATH,value=page_value)
        time.sleep(5)
        for i in range(len(all_groups)):
            ###测试亮剑社区
            if '亮剑社区' in all_groups[i].text:
                all_groups[i].click()
                time.sleep(2)
                ###获取当日发布项目详细页面（若存在）
                page_value = '/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[1]/div[2]/button/i'
                self.driver.find_element(by=By.XPATH,value=page_value).click()
                #今日项目
                k = 1
                while k<=50:
                    try:
                        page_value = f"/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[2]/div[1]/div/div[{k}]/div[1]/span"
                        date = self.driver.find_element(by=By.XPATH,value=page_value).text
                    except:
                        k+=1
                        continue

                    if date == 'Today':
                        page_value = f"/html/body/div[1]/div/div/div/div/div[2]/div[3]/div[2]/div[2]/div[1]/div/div[{k}]"
                        dr = self.driver.find_element(by=By.XPATH,value=page_value).text
                        ans = {'项目名称':[],'项目机制':[],'合约地址':[],'中文电报':[],'官方电报':[],'官方网站':[],'官方推特':[]}
                        for pro in re.findall("(?=项目名称).*?(?=＿＿＿＿＿)",dr.replace('\n','')):
                            ans['项目名称'].append(re.search('(?<=项目名称：).*?(?=项目机制)',pro).group())
                            ans['项目机制'].append(re.search('(?<=项目机制：).*?(?=合约地址)',pro).group())
                            ans['合约地址'].append(re.search('(?<=合约地址：).*?(?=中文电报)',pro).group())
                            ans['中文电报'].append(re.search('(?<=中文电报：).*?(?=官方电报)',pro).group())
                            ans['官方电报'].append(re.search('(?<=官方电报：).*?(?=官方网站)',pro).group())
                            ans['官方网站'].append(re.search('(?<=官方网站：).*?(?=官方推特)',pro).group())
                            ans['官方推特'].append(re.search('(?<=官方推特：).*',pro).group())
                        break
                    else:
                        k+=1
        self.driver.close()         
        return ans
    
if __name__ == "__main__":
    TG = TeleGram()
    TG.login()
    res = TG.get_group()
    print(pd.DataFrame(res))
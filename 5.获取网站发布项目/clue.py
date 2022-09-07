import requests
import re
import json
import datetime
import time
import pandas as pd
import numpy as np
from tqdm import tqdm
from urllib.request import urlopen
from bs4 import BeautifulSoup
from tqdm import tqdm
from tqdm.contrib import tzip
import pymysql

class FetchClue:
    def __init__(self):
        self.webclue = pd.DataFrame(columns=['platform','url','title','author','date'])
        self.now = str(time.strftime("%Y-%m-%d"))
        self.yesterday = (datetime.datetime.now()+datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
        self.path = "D:/vscodefile/5.webclue/clues/"
        self.key_words = ['元宇宙','区块链','链游','项目','公链']
        
    def sql_save(self):
        """
        写入数据库
        """
        db = pymysql.connect(host="192.168.11.22",port=3306,user="root",password="!Q2w3e4r",database="cure",charset="utf8")
        cursor = db.cursor()
        for platform,url,title,author,date in \
        zip(self.webclue.platform,self.webclue.url,self.webclue.title,self.webclue.author,self.webclue.date):
            sql = f"insert into metaverse(platform,url,title,author,date) values ('{platform}','{url}','{title}','{author}','{date}')"
            cursor.execute(sql)
        db.commit()
        db.close()
        
    def save(self):
        """
        保持到本地excel
        """
        df = self.webclue.drop_duplicates('title')
        return df.to_excel(self.path+'clue.xlsx',index=False)
    
    def requesturl(self,url):
        """
        请求网页
        """
        while True:
            try:
                myURL = urlopen(url).read()
            except Exception as e:
                print(e)
                time.sleep(3)
                continue
            return myURL
        
    
    def web1(self):
        #首码网
        url = "https://www.shouma.net/sm/"
        while True:
            try:
                myURL = urlopen(url).read()
            except Exception as e:
                print(e)
                time.sleep(3)
                continue
                
            soup = BeautifulSoup(myURL,"lxml")
            for i,j in (tzip(soup.find_all(class_="post-link"),soup.find_all(class_="lazy"))):
                url_ = i.get("href")#文章索引
                title_ = j.get("alt")#标题
                for word in self.key_words:
                    if word in title_:
                        childURL = self.requesturl(url_)
                        soup_ = BeautifulSoup(childURL,"lxml")
                        author_ = soup_.find(class_="author-avatar").get('alt')#作者
                        date_ = str(soup_.find(class_="single-time").get('title')).replace("年",'-').replace('月','-').replace('日','')#时间
                        date_today = datetime.datetime.strptime(date_,"%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") #保留年月日
                        if date_today >= self.yesterday:
                            #爬取昨天到今天文章
                            self.webclue.loc[len(self.webclue)] = ["首码网",url_,title_,author_,date_today]
                            
                        break

            return self.webclue
            
    def web2(self):
        #币快报
        url = "https://www.beekuaibao.com"
        while True:
            try:
                myURL = requests.get(url).text
            except Exception as e:
                print(e)
                time.sleep(3)
                continue
            soup = BeautifulSoup(myURL,"lxml")
            for i in tqdm(soup.find_all(class_="content-item KBH")):
                url_ = url + i.get('href')
                title_ = re.search("(?<=>).*(?=<)",str(i.find(class_="title"))).group(0)
                for word in self.key_words:
                    if word in title_:
                        childURL = self.requesturl(url_)
                        soup_ = BeautifulSoup(childURL,"lxml")
                        author_ = soup_.find(class_='detail-container KBH').find(class_='nickName').contents[0]
                        date_ = str(soup_.find(class_='detail-container KBH').find(class_='desc').contents[0].contents[0])
                        if len(date_)<=5:#爬取24小时内的数据
                            hour_ = date_[:-3]
                            new_date = (datetime.datetime.now()+datetime.timedelta(hours=-int(hour_))).strftime("%Y-%m-%d")
                            self.webclue.loc[len(self.webclue)] = ["币快报",url_,title_,author_,new_date]
                            
                        break

            return self.webclue
    
    
        
    def web3(self):
        #币界网
        url = "https://www.528btc.com"
        while True:
            try:
                myURL = requests.get(url).text
            except Exception as e:
                print(e)
                time.sleep(3)
                continue
            soup = BeautifulSoup(myURL,"lxml")
            for i in tqdm(soup.find_all(class_="normal-card list-card")):
                title_ = i.find('a').find('img').get("alt")
                url_ = url + str(i.find('a').get('href'))
                for word in self.key_words:
                    if word in title_:
                        childURL = self.requesturl(url_)
                        soup_ = BeautifulSoup(childURL,"lxml")
                        author_ = soup_.find(class_='infoxx xxbt').contents[1].contents[0]
                        date_ = str(soup_.find(class_='infoxx xxbt').contents[3].contents[0])
                        date_today = datetime.datetime.strptime(date_,"%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                        if date_today >= self.yesterday:
                            self.webclue.loc[len(self.webclue)] = ["币界网",url_,title_,author_,date_today]
                           
                        break

            return self.webclue
        
    def web4(self):
        #以太财经
        url = "http://www.bishije.com/tnews"
        while True:
            try:
                myURL = requests.get(url).text
            except Exception as e:
                print(e)
                time.sleep(3)
                continue
            soup = BeautifulSoup(myURL,"lxml")
            for i in tqdm(soup.find_all(class_='item')[:10]):
                url_ = i.find("a").get("href")
                title_ = i.find("a").get("title")
                for word in self.key_words:
                    if word in title_:
                        childURL = self.requesturl(url_)
                        soup_ = BeautifulSoup(childURL,"lxml")
                        author_ = soup_.find(class_="nickname url fn j-user-card").contents[0]
                        date_ = str(soup_.find(class_="entry-date published").get('datetime')).replace('T',' ').replace('+08:00>','')
                        date_today = datetime.datetime.strptime(date_,"%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                        if date_today >= self.yesterday:
                            self.webclue.loc[len(self.webclue)] = ["以太财经",url_,title_,author_,date_today]
                            
                        break

            return self.webclue
        
    def web5(self):
        #零度财经
        url = "http://www.zerohello.cn/"
        while True:
            try:
                myURL = requests.get(url).text
            except Exception as e:
                print(e)
                time.sleep(3)
                continue
            soup = BeautifulSoup(myURL,"lxml")
            for i in tqdm(soup.find_all(class_='ajaxpost')):
                url_ = i.find(class_='imgeffect').get("href")
                title_ = i.find(class_='imgeffect').find("img").get("alt")
                for word in self.key_words:
                    if word in title_:
                        childURL = self.requesturl(url_)
                        soup_ = BeautifulSoup(childURL,"lxml")
                        author_ = "零度财经"
                        date_ = str(soup_.find(class_="date").contents[0]). \
                        replace('<b>','').replace('</b>',''). \
                        replace("年",'-').replace('月','-').replace('日','')#时间
                        date_today = datetime.datetime.strptime(date_,"%Y-%m-%d").strftime("%Y-%m-%d")
                        if date_today >= self.yesterday:
                            self.webclue.loc[len(self.webclue)] = ["零度财经",url_,title_,author_,date_today]
                           
                        break

            return self.webclue
    
def main():
    FC = FetchClue()
    FC.web1()
    FC.web2()
    FC.web3()
    FC.web4()
    FC.web5()
    FC.save()
    FC.sql_save()
    
if __name__ == "__main__":
    main()
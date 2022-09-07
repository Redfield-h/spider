from pydoc import pager
import requests
import json
import time
import pandas as pd
import numpy as np
from tqdm import tqdm

class Bsc:
    def __init__(self,addr):
        self.addr = addr
        self.page = 1
        self.size = 100

    def start(self):
        print("开始爬取tx_hash信息")
        tx_lst = []
        while True:
            url = f"https://explorer-web.api.btc.com/v1/eth/accounts/{self.addr}/txns?page={self.page}&size={self.size}"
            tx = self.request(url)
            print(f"爬取{url}")
            if len(tx['data']['list'])>0:
                for i in tx['data']['list']:
                    tx_lst.append(i['tx_hash'])
                time.sleep(3)
                self.page+=1
            else:
                print(f"tx_hash爬取完毕")
                break
        
        print("开始爬取交易信息")
        data = pd.DataFrame()
        for txs in tqdm(tx_lst):
            url = f"https://explorer-web.api.btc.com/v1/eth/tokentxns/{txs}"
            trade = self.request(url)
            if len(trade['data']['list'])>0:
                data = pd.concat([data,pd.DataFrame(trade['data']['list'])])
            else:
                print(url)
        print('爬取完毕')

        self.save(data,"./doc/")

    def request(self,url):
        headers = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
            }
        try:
            r = requests.get(url,headers=headers)
        except Exception as e:
            print(e)
            print("捕获异常，等待 {} 秒后继续尝试请求！".format(3))
            time.sleep(3)

        return r.json()

    def save(self,data,path):
        return data.to_csv(path+f'res.csv',index=False)

if __name__ == "__main__":
    addr = "0xf0acf8949e705e0ebb6cb42c2164b0b986454223"
    Bsc(addr).start()


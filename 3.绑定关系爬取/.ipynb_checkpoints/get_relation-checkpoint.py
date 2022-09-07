import requests
import time
import re
import pandas as pd
import tqdm
import pymysql
from multiprocessing.dummy import Pool
addr = "0x2d50c01669949df3bd21142f8f20ab14c48d1567"
key = "ckey_2545e4a689bb4d4c87d64889755"

class GetERC20:
    def __init__(self,addr):
        #合约地址
        self.addr = addr
        #链接数据库
        self.db = pymysql.connect(host="192.168.11.22",port=3306,user="root",password="!Q2w3e4r",database="cure",charset="utf8")
        self.cursor = self.db.cursor()
        
    def save_sql(self,date,tx_hash,from_address,to_address):
        """
        写入数据库
        """
        sql = f"insert into relation2(date,tx_hash,from_address,to_address) values ('{date}','{tx_hash}','{from_address}','{to_address}')"
        self.cursor.execute(sql)
        self.db.commit()
        
    def request(self):
        """
        请求网页
        """
        # global error_url
        # global res
        page_number = 1
        page_size = 1000
        while True:
            params = {
                "page-number":f"{page_number}",
                "page-size":f"{page_size}",
                "key":"ckey_2545e4a689bb4d4c87d64889755"
                }
            url = f"https://api.covalenthq.com/v1/56/address/{self.addr}/transactions_v2/?quote-currency=USD&page-size={page_size}&page-number={page_number}"
            try:
                r = requests.get(url,params=params)
            except Exception as e:
                # print(f"捕获异常{e}")
                # print("捕获异常，等待 {} 秒后继续尝试请求！".format(3))
                # time.sleep(3)
                continue
            
            if (r.status_code == 200) and (len(r.json()['data']['items'])>0):
                for i in r.json()['data']['items']:
                    try:
                        if (i['successful'] == True) and (0 < len(i['log_events']) <= 2) and (i["to_address_label"]==None):
                            date = i['block_signed_at'].replace('T',' ').replace('Z','') #交易日期
                            tx_hash = i['tx_hash'] #交易哈希
                            from_address = i['from_address'] #交易来源
                            raw_log_data = i['log_events'][-1]['raw_log_data'] #交易日志
                            to_address = '0x'+raw_log_data[-40:] #交易去处
                            # res['date'].append(date)
                            # res['tx_hash'].append(tx_hash)
                            # res['from_address'].append(from_address)
                            # res['to_address'].append(to_address)
                            self.save_sql(date,tx_hash,from_address,to_address)
                    except Exception as e:
                        continue
                page_number+=1
                age = len(res['tx_hash'])
                if age//2500>0:
                    print(f"已爬取{age}条")
            elif (r.status_code == 200) and (len(r.json()['data']['items'])==0):
                print('爬取完毕')
                self.db.close()
                break
            elif r.status_code != 200: 
                time.sleep(5)
                continue
        
                

                

    def save(self,ans):
        return ans.to_excel(f'./result/{self.addr}.xlsx',index=False)
        
        

def main():
    # res = {'date':[],'tx_hash':[],'from_address':[],'to_address':[]}
    ER = GetERC20(addr)
    ER.request()
    # ER.save(ans)

if __name__ == "__main__":
    main()
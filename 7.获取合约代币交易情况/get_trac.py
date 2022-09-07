import requests
import time
import threading
import re
import pandas as pd
from tqdm import tqdm
import pymysql
from multiprocessing.dummy import Pool

        
def request_(addr,contract_address,page_number):
    """
    请求网页
    """
    # global error_url
    global result
    ans = {'transfer_type':[],'from':[],'to':[],'value':[],'symbol':[],'tx_hash':[]}

    while True:
        page_size = 100
        params = {
            "page-number":f"{page_number}",
            "page-size":f"{page_size}",
            "key":"ckey_2545e4a689bb4d4c87d64889755",  #密钥
            'contract-address':contract_address  #代币地址
            }
        url = f"https://api.covalenthq.com/v1/56/address/{addr}/transfers_v2/?quote-currency=USD"
        try:
            r = requests.get(url,params=params)
        except Exception as e:
            # print(f"捕获异常{e}")
            # print("捕获异常，等待 {} 秒后继续尝试请求！".format(1))
            print(r.text)
            # time.sleep(1)
            continue

        if (r.status_code == 200) and (len(r.json()['data']['items'])>0):
            for i in (r.json()['data']['items']):
                if i['successful'] == True:
                    tx_hash = i['tx_hash']
                    from_address = i['transfers'][0]['from_address']
                    to_address = i['transfers'][0]['to_address']
                    value_ = i['transfers'][0]['delta']
                    contract_ticker_symbol = i['transfers'][0]['contract_ticker_symbol']
                    transfer_type = i['transfers'][0]['transfer_type']
                    ###
                    ans['tx_hash'].append(tx_hash)
                    ans['from'].append(from_address)
                    ans['to'].append(to_address)
                    ans['value'].append(value_)
                    ans['symbol'].append(contract_ticker_symbol)
                    ans['transfer_type'].append(transfer_type)

                    lock.acquire()    #线程锁
                    result.append(ans)
                    lock.release()    #释放锁

        elif (r.status_code == 200) and (len(r.json()['data']['items'])==0):
            break
        elif r.status_code != 200: 
            time.sleep(2)
            continue

    pool_sema.release() #释放已完成线程
                
                
result = []

lock = threading.Lock() #设置线程锁
max_connection = 4 #8线程
pool_sema = threading.BoundedSemaphore(max_connection) #最大线程量

thread_list = []
for page_number in tqdm(range(1,50)):
    pool_sema.acquire() 
    
    addr = "0x976B6A629E5aDA34F2508e75266879D988EA0921"  #池子地址
    contract_address="0x55d398326f99059fF775485246999027B3197955"    #usdt
    thread = threading.Thread(target=request_,args=[addr,contract_address,page_number])
    
    thread.start()
    thread_list.append(thread)

for t in thread_list:
    t.join()
    
pd.DataFrame(result).to_csv('test.csv')
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from tqdm.contrib import tzip
# from multiprocessing.dummy import Pool

class GetTokenInfo:
    def __init__(self,contract):
        self.con = contract
        self.key = 'ckey_2545e4a689bb4d4c87d64889755'
        self.apikey = 'GJWTUG7H93ND156DPIH57AZ953EQDI7IQZ'
    
    #获取池子名称
    def get_pair(self,addr):
        url = f'https://api.bscscan.com/api?module=contract'
        params = {
            "action":"getsourcecode",
            "address":addr,
            "apikey":self.apikey
            }
        r = requests.get(url,params=params)
        return r.json()['result'][0]['ContractName']
        
    #筛选池子地址
    def token_holders(self):
        # holders = {'contract_name':[],'addr':[],'per':[]}
        self.pair_addr = None
        params = {
            "key":self.key,
            'page-number':0,
            'page-size':100,
            'format':"JSON"
            }
        url = f'https://api.covalenthq.com/v1/56/tokens/{self.con}/token_holders/?quote-currency=USD'
        while True:
            try:
                r = requests.get(url,params=params)
            except:
                time.sleep(1)
                continue
            
            if r.status_code == 200:
                for i in r.json()['data']['items']:
                    #代币名
                    self.contract_name = i['contract_name']
                    #持有地址
                    addr = i['address']
                    #池子地址
                    if self.get_pair(addr) == 'PancakePair':
                        self.pair_addr = addr
                        break
                break
            else:
                continue
            #其它代币持有者
        #     per = (int(i['balance'])/int(i['total_supply']))*100
        #     holders['contract_name'].append(self.contract_name)
        #     holders['addr'].append(addr)
        #     holders['per'].append(per)
        # return holders
    
    #获取池子USDT
    def get_quote(self):
        quote = 0
        if self.pair_addr:
            params = {
                "key":self.key,
                'format':"JSON"
                }
            url = f"https://api.covalenthq.com/v1/56/address/{self.pair_addr}/balances_v2/?quote-currency=USD"
            r = requests.get(url,params=params)

            for i in r.json()['data']['items']:
                if i['contract_ticker_symbol'] in ['USDT','WBNB'] :
                    quote = i['quote']
                    break
        else:
            quote = 0

        return round(quote,2)

def main():
    print('----------开始更新数据----------')
    ans = {'代币':[],'池子金额$':[],'合约':[]}
    #加载地址数据
    with open('./doc/地址.json','r',encoding='utf-8') as fw:
        xs = json.load(fw)
    #爬取池子余额
    for name,addr in (tzip(xs.keys(),xs.values())):
        try:
            GTI = GetTokenInfo(addr)
            GTI.token_holders()
            num = GTI.get_quote()

            ans['代币'].append(name)
            ans['池子金额$'].append(num)
            ans['合约'].append(addr)
        except Exception as e:
            print(f"{addr}该地址更新错误,错误信息{e},请手动更新!")
            continue
    #保存数据
    pd.DataFrame(ans).sort_values('池子金额$',ascending=False).reset_index(drop=True).to_excel('./doc/线索余额.xlsx')
    print('-----------更新完成-----------')

if __name__ == '__main__':
    main()
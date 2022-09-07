import scrapy
import json
from tqdm import tqdm
from yaml import parse
from get_trac_scrapy.items import GetTracScrapyItem
# from scrapy.downloadermiddlewares.retry import RetryMiddleware


class TracSpider(scrapy.Spider):
    name = 'trac'
    # allowed_domains = ['api.covalenthq.com']
    # start_urls = ['http://api.covalenthq.com/']

    def parse(self, response):
        r = response
        if (r.status == 200) and (len(r.json()['data']['items'])>0):
            for i in (r.json()['data']['items']):
                if i['successful'] == True:
                    tx_hash = i['tx_hash']
                    from_address = i['transfers'][0]['from_address']
                    to_address = i['transfers'][0]['to_address']
                    value_ = i['transfers'][0]['delta']
                    contract_ticker_symbol = i['transfers'][0]['contract_ticker_symbol']
                    transfer_type = i['transfers'][0]['transfer_type']
                    ###
                    item = GetTracScrapyItem(tx_hash=tx_hash,from_address=from_address,to_address=to_address,
                                   value=value_,symbol = contract_ticker_symbol,transfer_type=transfer_type)
                    yield item
                    
    def start_requests(self):
        # addr = "0xbdd030fa56eb397c528e11499b5f6f5a10ed1d82"  #池子地址
        # contract_address="0x55d398326f99059fF775485246999027B3197955"    #交易代币地址usdt/BNB
        
        addr = "0x778fde75749b13C7ed8B8a58cE1B1ac5481E27fF"  #池子地址
        contract_address="0x55d398326f99059fF775485246999027B3197955"    #交易代币地址usdt/BNB
        page_size = 100
        for page_number in tqdm(range(1,50)):
            params = {
                "page-number":f"{page_number}",
                "page-size":f"{page_size}",
                "key":"ckey_2545e4a689bb4d4c87d64889755",  #密钥
                'contract-address':contract_address  #代币地址
                }
            next_url = f"https://api.covalenthq.com/v1/56/address/{addr}/transfers_v2/?quote-currency=USD&page-number={page_number}&page-size={page_size}&contract-address={contract_address}&key=ckey_2545e4a689bb4d4c87d64889755"
            page_number+=1
            yield scrapy.Request(next_url)


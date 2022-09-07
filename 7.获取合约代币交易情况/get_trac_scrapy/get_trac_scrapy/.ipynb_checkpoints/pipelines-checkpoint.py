# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import pandas as pd


class GetTracScrapyPipeline:
    def open_spider(self,spider):
        self.fp = open('res.txt','w',encoding='utf-8')
        
    def process_item(self, item, spider):
        item_json = json.dumps(dict(item),ensure_ascii=False)
        self.fp.write(item_json + '\n')
        return item
    
    def close_spider(self,spider):
        self.fp.close()

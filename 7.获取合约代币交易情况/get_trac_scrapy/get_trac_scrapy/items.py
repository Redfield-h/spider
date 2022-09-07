# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GetTracScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    tx_hash = scrapy.Field()
    from_address = scrapy.Field()
    to_address = scrapy.Field()
    value = scrapy.Field()
    symbol = scrapy.Field()
    transfer_type = scrapy.Field()

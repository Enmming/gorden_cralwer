# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy import Request
import re
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
import datetime
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.drug_store import DrugStoreSpider
#class ItemPmSpider(Spider):
class ItemDrugStoreSpider(ItemSpider):
    name = "item_drug_store"
    allowed_domains = ["item_drug_store.com"]
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    
    start_urls = [
        'http://www.drugstore.com/gnc-7-day-pill-organizer/qxp349385?catid=191623'
    ]
    def parse(self, response):
        item=BaseItem()
        item['type']='base'
        item['url'] = response.url
        return DrugStoreSpider().handle_parse_item(response, item)

# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
import scrapy
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from random import random
from urllib import quote
import re
import execjs
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.forzieri import ForzieriSpider, ForzieriBaseSpider


class ItemForzieriSpider(ItemSpider, ForzieriBaseSpider):
#class ForzieriSpider(RedisSpider):
    name = "item_forzieri"
    allowed_domains = ["forzieri.com"]
    
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''
    
    start_urls = (
        
    )
    
    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_TIMEOUT': 10,
    }
    
    base_url = 'http://www.forzieri.com'

    '''具体的解析规则'''
    def parse(self, response):
        sel = Selector(response)
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'forzieri'
        item['url'] = response.url

        return self.handle_parse_item(response, item)


# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

import re
import execjs
import json

from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.lacoste import LacosteSpider,LacosteBaseSpider

class ItemLacosteSpider(ItemSpider, LacosteBaseSpider):
    name = "item_lacoste"
    allowed_domains = ["lacoste.com"]
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = []

    base_url = 'http://www.lacoste.com'

    '''具体的解析规则'''
    def parse(self, response):
        itemB = {}
        itemB['type'] = 'base'
        itemB['from_site'] = 'lacoste'
        itemB['url'] = response.url

        # ls = LacosteSpider()
        
        return self.handle_parse_item(response,itemB)

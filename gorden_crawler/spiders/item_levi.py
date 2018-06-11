# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from urllib import quote
import re
import execjs

from scrapy.utils.response import get_base_url
import json

# import gc

# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.levi import LeviSpider

class ItemLeviSpider(ItemSpider):
    name = "item_levi"
    allowed_domains = ["levi.com"]
    
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''
    
    start_urls = (
        # 'http://www.levi.com/US/en_US/category/men/clothing/all',
        # 'http://www.levi.com/US/en_US/category/women/clothing/all',
        # 'http://www.levi.com/US/en_US/category/kids/_/N-2sZ1z13wzsZ8alZ1z13x71Z1z140oj',
        # 'http://www.levi.com/US/en_US/category/accessories/gender/male', 
        # 'http://www.levi.com/US/en_US/category/accessories/gender/female'
    )
    
    base_url = 'http://www.levi.com'

    '''具体的解析规则'''
    def parse(self, response):
        sel = Selector(response)
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'levi'
        item['url'] = response.url

        ls = LeviSpider()
        
        return ls.handle_parse_item(response, item)


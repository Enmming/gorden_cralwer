# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from gorden_crawler.spiders.shiji_base import ItemSpider

import re
from ..spiders.lookfantastic import LookfantasticSpider, BaseLookfantasticSpider


class ItemLookfantasticSpider(ItemSpider, BaseLookfantasticSpider):
    name = "item_lookfantastic"
    allowed_domains = ["lookfantastic.com"]
    
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''
    
    start_urls = (
    )
    
    base_url = 'https://www.lookfantastic.com'

    # def __init__(self, url='', *args, **kwargs):

    #     if len(re.findall(r'switchcurrency=USD',url)) < 1: #取美元处理
    #         url += '?switchcurrency=USD'
    #     ItemSpider.__init__(self,url,*args, **kwargs)
    #     # super(ItemLookfantasticSpider, self).__init__(url,*args, **kwargs) #功能同上行



    '''具体的解析规则'''
    def parse(self, response):
        sel = Selector(response)
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'lookfantastic'
        item['gender'] = 'women'
        item['url'] = response.url

        # lfs = LookfantasticSpider()
        
        return self.handle_parse_item(response, item)


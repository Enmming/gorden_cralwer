# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
import re

from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.ssense import SsenseSpider

class ItemSsenseSpider(ItemSpider):
    name = "item_ssense"
    allowed_domains = ["ssense.com"]
    
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''
    
    start_urls = (
    )
    
    base_url = 'https://www.ssense.com'

    custom_settings = {
        'COOKIES_ENABLED': True
    }
    
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, cookies={'forced_user_country': 'US', 'forcedCountry': 'US', 'forced_user_country_done': 'US'})

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, cookies={'forced_user_country': 'US', 'forcedCountry': 'US', 'forced_user_country_done': 'US'})

    '''具体的解析规则'''
    def parse(self, response):
        sel = Selector(response)
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'ssense'
        item['url'] = response.url
        item['cover'] = ''

        ss = SsenseSpider()
        
        return ss.handle_parse_item(response, item)


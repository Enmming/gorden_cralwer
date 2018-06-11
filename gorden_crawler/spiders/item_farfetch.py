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
from gorden_crawler.spiders.farfetch import FarfetchSpider

class ItemFarfetchSpider(ItemSpider):
    name = "item_farfetch"
    allowed_domains = ["farfetch.com"]
    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOADER_MIDDLEWARES': {
            # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyHttpsMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''
    
    start_urls = (
    )

    base_url = 'http://www.farfetch.com'

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, cookies={'ckm-ctx-sf': '/'})
    
    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, cookies={'ckm-ctx-sf': '/'})

    '''具体的解析规则'''
    def parse(self, response):

        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'farfetch'
        item['url'] = response.url

        return FarfetchSpider().handle_parse_item(response, item)


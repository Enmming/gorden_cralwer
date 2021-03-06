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

from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.mybag import MybagSpider

class ItemMybagSpider(ItemSpider):
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 40,
        'RETRY_TIMES': 20,
        #     # 'DOWNLOADER_MIDDLEWARES': {
        #     #     # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
        #     #     'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
        #     #     'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
        #     #     'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
        #     #     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        #     # }
    }

    start_urls = (
    )
    
    name = "item_mybag"

    base_url = "http://www.mybag.com"

    allowed_domains = ["mybag.com"]

    usd_suffix = 'switchcurrency=USD'

    '''具体的解析规则'''
    def parse(self, response):
        sel = Selector(response)
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'mybag'
        item['url'] = response.url

        ms = MybagSpider()
        
        return ms.handle_parse_item(response, item)


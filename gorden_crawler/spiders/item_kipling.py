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
from gorden_crawler.spiders.kipling import KiplingSpider

class ItemKiplingSpider(ItemSpider):
    name = "item_kipling"
    allowed_domains = ["kipling-usa.com","fluidretail.net"]
    custom_settings = {
#         'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOAD_TIMEOUT': 10
#         'DOWNLOADER_MIDDLEWARES': {
#             'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
#              'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
#              'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
#              'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
#              'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
#         }
    }
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''
    
    start_urls = (
    )
    
    base_url = 'http://www.kipling-usa.com'

    '''具体的解析规则'''
    def parse(self, response):
        
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'kipling'
        item['url'] = response.url
        
        return KiplingSpider().handle_parse_item(response, item)


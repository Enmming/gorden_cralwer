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
from gorden_crawler.spiders.lordandtaylor import LordandtaylorSpider

class ItemLordandtaylorSpider(ItemSpider):
#class zappoSpider(RedisSpider):
    name = "item_lordandtaylor"
    allowed_domains = ["lordandtaylor.com"]
    custom_settings = {
#         'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOADER_MIDDLEWARES': {
#             'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
             'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
             'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
             'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
             'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''
    
    start_urls = (
        #'http://couture.zappos.com/kate-spade-new-york-dawn-black-polished-calf-pumice-polished-calf',
        #'http://www.zappos.com/womens~1a',
        #'http://www.zappos.com/allen-allen-3-4-sleeve-v-angled-tunic-black',
        #'http://www.zappos.com/ogio-brooklyn-purse-red',
        #'http://www.zappos.com/ogio-hudson-pack-cobalt-cobalt-academy',
        #'http://www.zappos.com/natori-natori-yogi-convertible-underwire-sports-bra-731050-midnight-silver-dusk',
    )
    
    base_url = 'http://www.lordandtaylor.com'

    '''具体的解析规则'''
    def parse(self, response):
        
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'lordandtaylor'
        item['url'] = response.url
        
        ils = LordandtaylorSpider()
        
        return ils.handle_parse_item(response, item)


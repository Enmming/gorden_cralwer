# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from ..items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from urllib import quote
import re
import execjs

from scrapy.utils.response import get_base_url
import json

from ..spiders.shiji_base import ItemSpider
from ..spiders.michaelkors import MichaelkorsSpider


class ItemMichaelkorsSpider(ItemSpider):
    name = "item_michaelkors"
    allowed_domains = ["michaelkors.com"]

    custom_settings = {
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,

        'DOWNLOADER_MIDDLEWARES': {
            # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyHttpsUSADCMiddleware': 100,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }


    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''

    start_urls = (
    )

    base_url = 'https://www.michaelkors.com'

    '''具体的解析规则'''
    def parse(self, response):
        sel = Selector(response)
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'michaelkors'
        item['url'] = response.url

        mks = MichaelkorsSpider()

        return mks.handle_parse_item(response, item)

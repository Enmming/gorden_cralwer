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
import os
import base64
from ..spiders.shiji_base import BaseSpider
from ..spiders.amazon_usa_uk import AmazonUsaUkSpider


class ItemListAmazonUSAUKSpider(BaseSpider):
    name = "item_list_amazon_usa_uk"
    allowed_domains = ["amazon.cn"]

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,

        'DOWNLOADER_MIDDLEWARES': {
            # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyHttpsRandomMiddleware': 100,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }


    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''

    start_urls = (
        'http://api.qnmami.com/user/login'
    )

    base_url = 'https://www.amazon.cn'

    def start_requests(self):
        print os.environ.get('url')
        if os.environ.get('url'):
            yield Request(os.environ.get('url'))
        else:
            return

    '''具体的解析规则'''
    def parse(self, response):
        sel = Selector(response)
        goods_json = json.loads(base64.b64decode(os.environ.get('goods_json'))) if os.environ.get('goods_json') else None
        if goods_json:
            category = goods_json['category']
            gender = goods_json["gender"]
            product_type = goods_json['product_type']
        else:
            raise ValueError('NO GOODS JSON SPECIFIED')

        auus = AmazonUsaSpider()

        return auus.handle_parse_list(response, category, product_type, gender)

    def parse_item(self):
        pass
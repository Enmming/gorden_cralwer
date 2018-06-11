# -*- coding: utf-8 -*-
import os

from scrapy.selector import Selector

from ..items import BaseItem
from ..spiders.amazon_usa_uk import AmazonUsaUkSpider
from ..spiders.shiji_base import ItemSpider


class ItemAmazonUSAUKSpider(ItemSpider):
    name = "item_amazon_usa_uk"
    allowed_domains = ["amazon.cn"]

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,

        'DOWNLOADER_MIDDLEWARES': {
            # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyHttpsRandomMiddleware': 100,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        },

        'ITEM_PIPELINES': {
            'gorden_crawler.pipelines.mongodb.SingleMongodbPipeline': 303,
            'gorden_crawler.pipelines.realtime_handle_image.RealtimeHandleImage': 305,
        }
    }


    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''

    start_urls = (
    )

    base_url = 'https://www.amazon.cn'

    '''具体的解析规则'''
    def parse(self, response):
        sel = Selector(response)
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'amazon_usa_uk'
        item['url'] = response.url
        if os.environ.get('product_type_id'):
            item['product_type_id'] = os.environ.get('product_type_id')
            item['product_type'] = 'amazon_usa_uk_' + os.environ.get('product_type_id')
        if os.environ.get('category_id'):
            item['category_id'] = int(os.environ.get('category_id'))
            item['category'] = 'amazon_usa_uk_' + os.environ.get('category_id')
        if os.environ.get('gender'):
            item['gender'] = os.environ.get('gender')
        if os.environ.get('title'):
            item['title'] = os.environ.get('title')
        auus = AmazonUsaUkSpider()

        return auus.handle_parse_item(response, item)

# -*- coding: utf-8 -*-
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.disneystore import DisneystoreSpider


class ItemDisneystoreSpider(ItemSpider):
    name = "item_disneystore"
    allowed_domains = ["disneystore.com"]
    custom_settings = {
        # 'DOWNLOAD_DELAY': 0.5,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        # 'DOWNLOADER_MIDDLEWARES': {
        #     #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
        #     'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
        #     'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
        #     'gorden_crawler.middlewares.proxy_ats.ProxyHttpsUSAMiddleware': 100,
        #     # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        # }
    }
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''

    start_urls = (
    )

    base_url = 'https://www.disneystore.com/'

    image_base_url = 'https://cdn-ssl.s7.disneystore.com/'
    cover_url_suffix = '?$yetidetail$'
    image_url_suffix = '?$yetzoom$'

    paging_base_url = 'https://www.disneystore.com/disneystore/product/category/'

    '''具体的解析规则'''
    def parse(self, response):
        sel = Selector(response)
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'disneystore'
        item['url'] = response.url

        dss = DisneystoreSpider()

        return dss.handle_parse_item(response, item)


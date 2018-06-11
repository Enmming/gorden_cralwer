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

from ..spiders.shiji_base import ItemSpider
from ..spiders.tjzmall import TjzmallSpider


class ItemTjzmallSpider(ItemSpider):
    name = "item_tjzmall"
    allowed_domains = ["tjzmall.com"]

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,

    }


    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''

    start_urls = (
    )

    base_url = 'https://www.tjzmall.com'

    '''具体的解析规则'''
    def parse(self, response):
        sel = Selector(response)
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'tjzmall'
        item['url'] = response.url

        ts = TjzmallSpider()

        return ts.handle_parse_item(response, item)

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
from gorden_crawler.spiders.netaporter import NetAPorterSpider

class ItemNetAPorterSpider(ItemSpider):
    name = "item_netaporter"
    allowed_domains = ["net-a-port.com"]
    custom_settings = {
    }
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''

    start_urls = (
    )
    gender = 'women'
    base_url = 'https://www.net-a-porter.com/'


    '''具体的解析规则'''
    def parse(self, response):

        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'netaporter'
        item['url'] = response.url

        return NetAPorterSpider().handle_parse_item(response, item)


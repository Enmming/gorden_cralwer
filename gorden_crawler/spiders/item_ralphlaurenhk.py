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
from scrapy.utils.response import get_base_url
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.ralphlaurenhk import RalphlaurenhkSpider, RalphlaurenhkBaseSpider


class ItemRalphlaurenhkSpider(ItemSpider, RalphlaurenhkBaseSpider):
    name = "item_ralphlaurenhk"
    allowed_domains = ["ralphlauren.asia"]
    
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''
    
    start_urls = (
        
    )
    
    base_url = 'http://www.ralphlauren.asia'

    '''具体的解析规则'''
    def parse(self, response):
        sel = Selector(response)
        baseItem = BaseItem()
        baseItem['type'] = 'base'
        baseItem['from_site'] = 'ralphlauren'
        
        
        baseItem['show_product_id'] = sel.xpath('//input[contains(@id, "productId")]/@value').extract()[0] 
        baseItem['url'] = get_base_url(response)
        baseItem['cover'] = ""

        return self.handle_parse_item(response, baseItem)


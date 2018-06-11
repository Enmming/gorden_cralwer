# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
import scrapy
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from scrapy.utils.response import get_base_url
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.rebeccaminkoff import RebeccaminkoffSpider

class ItemRebeccaminkoffSpider(ItemSpider):
    name = "item_rebeccaminkoff"
    allowed_domains = ["rebeccaminkoff.com"]
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    
    start_urls = ()

    def parse(self, response):
        sel = Selector(response)
        item = BaseItem()
        item['type']='base'
        item['url'] = get_base_url(response)
        item['from_site'] = 'rebeccaminkoff'
        
        item['show_product_id'] = sel.xpath('//div[contains(@class, "no-display")]//input[1]/@value').extract()[0]
        rebeccaminkoff = RebeccaminkoffSpider()

        return rebeccaminkoff.handle_parse_item(response, item)

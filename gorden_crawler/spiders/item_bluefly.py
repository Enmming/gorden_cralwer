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
from gorden_crawler.spiders.bluefly import BlueflySpider

class ItemBlueflySpider(ItemSpider):
#class zappoSpider(RedisSpider):
    name = "item_bluefly"
    allowed_domains = ["bluefly.com"]
    
    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_TIMEOUT': 10
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
    
    base_url = 'http://www.bluefly.com'

    '''具体的解析规则'''
    def parse(self, response):
        
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'bluefly'
        item['url'] = response.url
        
        sel = Selector(response)
        product_id = re.findall('\s*var\s*prodId\s*=\s*([\d\.]+)',response.body)
        if product_id:
            product_id = product_id[0]
        else:
            return
#         product_id = sel.xpath('//section[@id="main-product-detail"]/@data-product-id').extract()[0]
        
        item['show_product_id'] = product_id
        
        bls = BlueflySpider()
        
        return bls.handle_parse_item(response, item)


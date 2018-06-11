# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from random import random
import re
from urllib import quote
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.diapers import DiapersSpider, DiapersBaseSpider

#class diapersSpider(Spider):
class ItemDiapersSpider(ItemSpider, DiapersBaseSpider):
    name = "item_diapers"
    allowed_domains = ["diapers.com"]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.2,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        'USER_AGENT': 'search_crawler (+http://www.shijisearch2.com)'
    }
    
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''
    start_urls = (
        #'http://www.diapers.com/cat=Toys-Books-8',
        #'http://www.diapers.com/subcat=Baby-Girls-10565/ONSALE_FLAG=Y?PageIndex=49',
        #'http://www.diapers.com/p/marimekko-kukatar-bodysuit-baby-multicolor-1207601',
#         'http://www.diapers.com/subcat=Baby-Girls-10565/ONSALE_FLAG=Y?PageIndex=50',
        #'http://www.diapers.com/p/adidas-toddler-peplum-fleece-set-ny-knicks-2t-1149937',
        #'http://www.diapers.com/p/little-me-bear-quilted-pram-baby-white-lt-blue-1209118',
        #'http://www.diapers.com/p/bravado-designs-seamless-panty-rose-1105792',
        #'http://www.diapers.com/p/burts-bees-baby-bleach-bottom-board-shorts-toddler-kid-midnight-1177434',
        #'http://www.diapers.com/cat=Clothing-Shoes-638',   
        #'http://www.diapers.com/subcat=Girls-10569',
        #'http://www.diapers.com/p/masala-shimmer-cardigan-toddler-kid-teal-1219768',
        #'http://www.diapers.com/subcat=Girls-Shoes-10605',
        #'http://www.diapers.com/subcat=Girls-10569/Categories=Tops',
    )
    
    base_url = 'http://www.diapers.com'

    '''具体的解析规则'''
    def parse(self, response):
        
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'diapers'
        item['url'] = response.url
        #item = response.meta['item']
        
        m = re.search(r'var pr_page_id[\s]*=[\s]*([^;]+);', response.body)
        if  m is not None: 
            product_id = eval(m.group(1))
            item['show_product_id'] = product_id
        
            return self.handle_parse_item(response, item)
        

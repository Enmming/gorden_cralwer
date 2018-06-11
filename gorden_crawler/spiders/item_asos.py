# -*- coding: utf-8 -*-
from gorden_crawler.items import BaseItem
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.asos import AsosSpider
from scrapy import Request

class ItemAsosSpider(ItemSpider):
#class ItemAsosSpider(RedisSpider):
    name = "item_asos"
    allowed_domains = ["us.asos.com", "asos-media.com"]
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    
    start_urls = [
        'http://us.asos.com/The-Jetset-Diaries-Mirage-Maxi-Dress-in-Moroccan-Tile/17ecbj/?iid=5521820&cid=15210&sh=0&pge=0&pgesize=36&sort=-1&clr=Moroccan+tile&totalstyles=1021&gridsize=3'
    ]

    custom_settings = {
        'COOKIES_ENABLED': True
    }
    
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, cookies={'asos': 'currencyid=1'})

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, cookies={'asos': 'currencyid=1'})

    #具体的解析规则
    def parse(self, response):
        item = BaseItem()
        item['type'] = 'base'
        item['url'] = response.url
        item['from_site'] = 'asos'
        
        return AsosSpider().handle_parse_item(response, item)


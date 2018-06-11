# -*- coding: utf-8 -*-
from gorden_crawler.items import BaseItem
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.shopbop import ShopBopSpider
from scrapy import Request
#class ItemShopbopSpider(Spider):
class ItemShopbopSpider(ItemSpider):
    name = "item_shopbop"
    allowed_domains = ["shopbop.com"]
    
    base_url = 'http://www.shopbop.com/'
    custom_settings = {
#         'USER_AGENT': 'search_crawler (+http://www.shijisearch.com)',
        'COOKIES_ENABLED' : True,
        'DOWNLOAD_TIMEOUT': 10
    }
    
    avoid_302_redirect_tail_str = '?switchToCurrency=USD&switchToLocation=US&switchToLanguage=zh'

    start_urls = [
        'http://www.carters.com/carters-baby-girl-sets/VC_239G028.html?dwvar_VC__239G028_size=12M&dwvar_VC__239G028_color=Pink'
    ]

    def parse(self, response):
        response_url = response.url
        url = response_url+self.avoid_302_redirect_tail_str
        yield Request(url, callback=self.parse_price)

    def parse_price(self, response):
        item=BaseItem()
        item['type']='base'
        item['url'] = response.url
        return ShopBopSpider().handle_parse_item(response, item)

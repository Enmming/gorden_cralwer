# -*- coding: utf-8 -*-
from gorden_crawler.items import BaseItem
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.eastdane import EastDaneSpider
#class ItemShopbopSpider(Spider):
class ItemShopbopSpider(ItemSpider):
    name = "item_eastdane"
    allowed_domains = ["eastdane.com"]
    
    base_url = 'http://www.eastdane.com/'
    
    start_urls = [
        'https://www.eastdane.com/chuck-taylor-all-star-premium/vp/v=1/1521582251.htm?folderID=19221&colorId=85838'
    ]
    def parse(self, response):
        item=BaseItem()
        item['type']='base'
        item['url'] = response.url
        return EastDaneSpider().handle_parse_item(response, item)

# -*- coding: utf-8 -*-
from gorden_crawler.items import BaseItem
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.sixpm import SixPmSpider
import re
#class ItemPmSpider(Spider):
class ItemPmSpider(ItemSpider):
    name = "item_sixpm"
    allowed_domains = ["6pm.com", "elasticbeanstalk.com"]
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    
    start_urls = [
        'http://www.6pm.com/hush-puppies-upbeat-black-leather'
    ]
    def parse(self, response):
        
        item=BaseItem()
        item['type']='base'
        item['url'] = response.url
        item['from_site'] = 'sixpm'
        
        product_id_json = re.search(r'var productId[\s]*=[\s]*([^;]+);', response.body)
        
        if product_id_json:
            product_id = eval(product_id_json.group(1))
        
            item['show_product_id'] = product_id
        
            return SixPmSpider().handle_parse_item(response, item)

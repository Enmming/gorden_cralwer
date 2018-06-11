# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
import re
from scrapy import Request

from gorden_crawler.spiders.shopbop_eastdane_common import ShopbopEastdaneCommon

class ShopBopSpider(ShopbopEastdaneCommon):
#class ShopBopSpider(Spider):
    name = "shopbop"
    allowed_domains = ["shopbop.com"]
    
    shopbop_base_url = 'https://www.shopbop.com'
    custom_settings = {
#         'USER_AGENT': 'search_crawler (+http://www.shijisearch.com)',
        'COOKIES_ENABLED' : True,
        'DOWNLOAD_TIMEOUT': 60,
        'RETRY_TIMES': 20,
    }

    start_urls = [
        'https://www.shopbop.com',
    ]
#
    gender_start_urls_map = {
        'https://cn.shopbop.com/clothing/br/v=1/2534374302155112.htm' : {'product_type' : 'clothing'},
        'https://cn.shopbop.com/shoes/br/v=1/2534374302024643.htm' : {'product_type' : 'shoes'},
        'https://cn.shopbop.com/bags/br/v=1/2534374302024667.htm' : {'product_type' : 'bags'},
        'https://cn.shopbop.com/accessories/br/v=1/2534374302024641.htm' : {'product_type' : 'accessories'},
    }
    def parse(self, response):
        url_suffixs = [
                    # shopbop
                    'https://www.shopbop.com/clothing/br/v=1/2534374302155112.htm',
                    'https://www.shopbop.com/shoes/br/v=1/2534374302024643.htm',
                    'https://www.shopbop.com/bags/br/v=1/2534374302024667.htm',
                    'https://www.shopbop.com/accessories/br/v=1/2534374302024641.htm'
                    ]
        avoid_302_redirect_tail_str = '?switchToCurrency=USD&switchToLocation=US&switchToLanguage=zh'
        for url_suffix in url_suffixs:
            url = url_suffix + avoid_302_redirect_tail_str
            yield Request(url, callback=self.parse_product_type)
            
    def parse_product_type(self, response):
        response_link=response.url
        product_type = self.gender_start_urls_map[response_link]['product_type']
        gender = 'women'
        sel = Selector(response)
        category_links = sel.xpath('//li[@class="leftNavCategoryLi nav-item"]/a')[1:]
        category_url={}
        for category_link in category_links:
            url =self.shopbop_base_url + category_link.xpath('./@href').extract()[0]
            category = category_link.xpath('./text()').extract()[0]
            if not re.search(r'Boutique', category):
                category_url[category] = url
                yield Request(url, callback=self.parse_pages, meta={'category' : category, 'product_type' : product_type, 'gender' : gender, 'category_url' : category_url})
# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem
from scrapy import Request
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.macys import MacysSpider


class ItemMacysSpider(ItemSpider):
#class zappoSpider(RedisSpider):
    name = "item_macys"
    allowed_domains = ["macys.com"]
    
    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_TIMEOUT': 20,
        'COOKIES_ENABLED': True
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
    
    base_url = 'http://www1.macys.com/'

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, cookies={'shippingCountry': 'US', 'currency': 'USD'})

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, cookies={'shippingCountry': 'US', 'currency': 'USD'})

    '''具体的解析规则'''
    def parse(self, response):
        
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'macys'
        item['url'] = response.url

        return MacysSpider().handle_parse_item(response, item)


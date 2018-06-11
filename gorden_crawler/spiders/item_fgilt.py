# -*- coding: utf-8 -*-
from gorden_crawler.items import SaleBaseItem
from gorden_crawler.spiders.shiji_base import GiltItemBaseSpider
from gorden_crawler.spiders.fgilt import BaseFgiltSpider
import datetime
import re

class ItemFgiltSpider(GiltItemBaseSpider, BaseFgiltSpider):
    name = "item_fgilt"
    allowed_domains = ["gilt.com"]
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_TIMEOUT': 40,
        'RETRY_TIMES': 20,
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyGiltMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    start_urls = [
        
    ]

    #具体的解析规则
    def parse(self, response):
        url = response.url
        # if re.search(r'\.json', url):
        #     saleBaseItem = SaleBaseItem()
        #     saleBaseItem['from_site'] = 'fgilt'
            
        #     return self.handle_parse_item(response, saleBaseItem)
        # else:
        saleBaseItem = SaleBaseItem()
        saleBaseItem['from_site'] = 'fgilt'
        saleBaseItem['url'] = url
        
        return self.parse_second_base_item(response, saleBaseItem)

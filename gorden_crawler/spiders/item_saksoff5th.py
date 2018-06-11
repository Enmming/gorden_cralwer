# -*- coding: utf-8 -*-
from gorden_crawler.items import BaseItem
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.saksoff5th import Saksoff5thSpider
#class ItemCartersSpider(Spider):
class ItemCartersSpider(ItemSpider):
    name = "item_saksoff5th"
    allowed_domains = ["saksoff5th.com"]
    
    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }
    
    base_url = 'http://www.saksoff5th.com/'
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    
    start_urls = [
		'http://www.saksoff5th.com/solid-sophie-sweater/0400087692212.html'
    ]
    def parse(self, response):
        item=BaseItem()
        item['type']='base'
        item['url'] = response.url
        return Saksoff5thSpider().handle_parse_item(response, item)

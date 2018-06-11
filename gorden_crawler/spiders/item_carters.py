# -*- coding: utf-8 -*-
from gorden_crawler.items import BaseItem
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.carters import CartersSpider
#class ItemCartersSpider(Spider):
class ItemCartersSpider(ItemSpider):
    name = "item_carters"
    allowed_domains = ["carters.com"]
    
    base_url = 'http://www.carters.com/'

    custom_settings = {
        # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 1,
        'RETRY_TIMES': 40,
        'DOWNLOADER_MIDDLEWARES': {
            # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware': 1,
            'gorden_crawler.middlewares.proxy_ats.ProxyUSAMiddleware': 100,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    
    start_urls = [
        'http://www.carters.com/carters-baby-girl-sets/VC_239G028.html?dwvar_VC__239G028_size=12M&dwvar_VC__239G028_color=Pink'
    ]
    def parse(self, response):
        item=BaseItem()
        item['type']='base'
        item['url'] = response.url
        return CartersSpider().handle_parse_item(response, item)

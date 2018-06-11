# -*- coding: utf-8 -*-
from gorden_crawler.items import BaseItem
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.oshkosh import OshKoshSpider
#class ItemOshkoshSpider(Spider):
class ItemOshkoshSpider(ItemSpider):
    name = "item_oshkosh"
    allowed_domains = ["oshkosh.com"]

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

    base_url = 'http://www.oshkosh.com/'
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    
    start_urls = [
        'http://www.oshkosh.com/oshkosh-baby-girl-tops/V_433G045.html?dwvar_V__433G045_color=Color&dwvar_V__433G045_size=12M'
    ]
    def parse(self, response):
        item=BaseItem()
        item['type']='base'
        item['url'] = response.url
        return OshKoshSpider().handle_parse_item(response, item)

# -*- coding: utf-8 -*-
# from gilt.rest import GiltApiClient
from scrapy.spiders import Spider
from scrapy import Request
import datetime

from gorden_crawler.items import SaleItem
from gorden_crawler.spiders.shiji_base import BaseSpider
import logging


class FgiltSaleSpider(Spider):
    name = "fgilt_sale"
    allowed_domains = ["gilt.com"]
    from_site = 'fgilt'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 1,
        'DOWNLOAD_TIMEOUT': 40,
        'RETRY_TIMES': 20,
        'DOWNLOADER_MIDDLEWARES': {
            # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyGiltMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }
    stores_gender_mapping = {
        'women': 'women',
        'men': 'men',
        'kids': 'baby',
        'home': 'unisex'
    }

    start_urls = [
        # # active
        # 'https://api.gilt.com/v1/sales/women/active.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # 'https://api.gilt.com/v1/sales/men/active.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        'https://api.gilt.com/v1/sales/kids/active.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # 'https://api.gilt.com/v1/sales/home/active.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # # #upcoming
        # 'https://api.gilt.com/v1/sales/women/upcoming.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # 'https://api.gilt.com/v1/sales/men/upcoming.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # 'https://api.gilt.com/v1/sales/kids/upcoming.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # 'https://api.gilt.com/v1/sales/home/upcoming.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b'
    ]
    # shiji
    API_KEY = '6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b'
    URL_API_KEY_SUFFIX = '?apikey=' + API_KEY

    UTC_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
    UTC_NOW = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        response_dict = eval(response.body)
        active_sales = response_dict['sales']
        saleItem = SaleItem()
        saleItem['from_site'] = self.from_site
        saleItem['type'] = 'sale'
        # import pdb;pdb.set_trace()
        print active_sales
        for active_sale in active_sales:
            begins = active_sale['begins']
            ends = active_sale['ends']
            sale_key = active_sale['sale_key']
            begins_temp = datetime.datetime.strptime(begins, self.UTC_FORMAT) + datetime.timedelta(hours=8)
            saleItem['begins'] = begins_temp.strftime("%Y-%m-%d %H:%M:%S")
            ends_temp = datetime.datetime.strptime(ends, self.UTC_FORMAT) + datetime.timedelta(hours=8)
            saleItem['ends'] = ends_temp.strftime("%Y-%m-%d %H:%M:%S")
            saleItem['name'] = active_sale['name']
            saleItem['sale_key'] = sale_key
            saleItem['sale_json_url'] = active_sale['sale']
            saleItem['sale_url'] = active_sale['sale_url']
            saleItem['desc'] = active_sale['description']
            store = active_sale['store']
            saleItem['store'] = store
            gender = self.stores_gender_mapping[store]
            saleItem['image_url'] = active_sale['image_urls']['2544x1344'][0]['url']
            if 'https' not in saleItem['sale_json_url'] and 'http' in saleItem['sale_json_url']:
                saleItem['sale_json_url'] = saleItem['sale_json_url'].replace('http', 'https')
            if 'https' not in saleItem['sale_url'] and 'http' in saleItem['sale_url']:
                saleItem['sale_url'] = saleItem['sale_url'].replace('http', 'https')
            if 'https' not in saleItem['image_url'] and 'http' in saleItem['image_url']:
                saleItem['image_url'] = saleItem['image_url'].replace('http', 'https')
            if active_sale.has_key('products') or begins > self.UTC_NOW:
                yield saleItem

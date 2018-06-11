# -*- coding: utf-8 -*-
import base64
from redis import Redis
import json

from scrapy import Request
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

from ..spiders.shiji_base import BaseSpider


class VictoriassecretSpider(BaseSpider):

    name = "victoriassecret"

    base_url = "https://www.victoriassecret.com/"

    gender = 'women'

    allowed_domains = ["victoriassecret.com"]

    start_urls = [
        'https://www.victoriassecret.com/bras/shop-all-bras',
        'https://www.victoriassecret.com/bralettes/all-bralettes',
        'https://www.victoriassecret.com/panties/shop-all-panties',
        'https://www.victoriassecret.com/lingerie/shop-all-lingerie',
        'https://www.victoriassecret.com/victorias-secret-sport/shop-all',
        'https://www.victoriassecret.com/sleepwear/shop-all-sleep',
        'https://www.victoriassecret.com/sale',
        'https://www.victoriassecret.com/beauty'
    ]

    url_category_maps = {
        'https://www.victoriassecret.com/bras/shop-all-bras': {'product_type': 'underwear', 'category': 'bras'},
        'https://www.victoriassecret.com/bralettes/all-bralettes': {'product_type': 'underwear', 'category': 'bralettes'},
        'https://www.victoriassecret.com/panties/shop-all-panties': {'product_type': 'underwear', 'category': 'panties'},
        'https://www.victoriassecret.com/lingerie/shop-all-lingerie': {'product_type': 'underwear', 'category': 'lingerie'},
        'https://www.victoriassecret.com/victorias-secret-sport/shop-all': {'product_type': 'underwear', 'category': 'sport'},
        'https://www.victoriassecret.com/sleepwear/shop-all-sleep': {'product_type': 'underwear', 'category': 'sleep'},
    }


    custom_settings = {
        # 'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 0.2,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,

    }

    def get_redis_connection(self):
        settings = get_project_settings()
        js_crawler_queue_host = settings.get('JS_CRAWLER_QUEUE_HOST')
        js_crawler_queue_port = settings.get('JS_CRAWLER_QUEUE_PORT')
        js_crawler_queue_password = settings.get('JS_CRAWLER_QUEUE_PASSWORD')

        if js_crawler_queue_password:
            js_crawler_queue_connection = Redis(host=js_crawler_queue_host, port=js_crawler_queue_port, password=js_crawler_queue_password)
        else:
            js_crawler_queue_connection = Redis(host=js_crawler_queue_host, port=js_crawler_queue_port)
        return js_crawler_queue_connection

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)
        response_url = response.url
        if response_url in self.url_category_maps.keys():
            category = self.url_category_maps[response_url]['category']
            product_type = self.url_category_maps[response_url]['product_type']
            yield Request(response_url, callback=self.parse_list, meta={"category": category, "product_type": product_type}, dont_filter=True)
        else:
            for product_type in ['beauty', 'sale']:
                if product_type in response_url:
                    product_type = product_type
                    cate_as = sel.xpath('//div[@class="' + product_type + '"]/div/div[1]/ul/li/span/a')
                    for cate_a in cate_as:
                        category = cate_a.xpath('./text()').extract()[0]
                        cat_url = self.base_url + cate_a.xpath('./@href').extract()[0]
                        yield Request(cat_url, callback=self.parse_list, meta={"category": category, "product_type": product_type}, dont_filter=True)

    def parse_list(self, response):
        sel = Selector(response)
        category = response.meta['category']
        product_type = response.meta['product_type']
        product_lis = sel.xpath('//ul[@class="products  grid-4-column "]/li')
        for product_li in product_lis:
            item = {}
            item['from_site'] = self.name
            item['type'] = 'base'
            item['category'] = category
            item['product_type'] = product_type
            item['gender'] = self.gender
            url = self.base_url + product_li.xpath('./a[@itemprop="url"]/@href').extract()[0]
            item['url'] = url
            item['cover'] = 'https:' + product_li.xpath('./div/a/span/img/@src').extract()[0]

            item = json.dumps(item)
            redis_conn = self.get_redis_connection()
            redis_conn.lpush('js_crawler_queue', self.name + ':' + base64.b64encode(url) + ':' + base64.b64encode(item))



            # yield Request(url, callback=self.parse_item, meta={"item": item})

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)

        item = json.dumps(item)
        redis_conn = self.get_redis_connection()
        redis_conn.lpush('js_crawler_queue', self.name + ':' + base64.b64encode(response.url) + ':' + base64.b64encode(item))

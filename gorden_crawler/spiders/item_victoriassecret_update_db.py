# -*- coding: utf-8 -*-
import os
import json
import base64

from scrapy.selector import Selector
from ..items import BaseItem, ImageItem, SkuItem, Color
import scrapy
from scrapy import Request
import re
from ..spiders.shiji_base import ItemSpider


class ItemVictoriassecretUpdateDBSpider(ItemSpider):

    name = 'item_victoriassecret_updatedb'
    allowed_domains = ["victoriassecret.com"]
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
    }

    start_urls = []
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''

    base_url = "https://www.victoriassecret.com/"

    gender = 'women'

    '''具体的解析规则'''
    def parse(self, response):
        item_data = json.loads(base64.b64decode(os.environ.get('js_crawler_item_data')))
        color_data = json.loads(base64.b64decode(os.environ.get('js_crawler_color_data')))
        sku_data = json.loads(base64.b64decode(os.environ.get('js_crawler_sku_data')))
        sel = Selector(response)
        item = item_data
        skus = sku_data

        product_detail = sel.xpath('//section[@class="product"]')
        product_id = product_detail.xpath('./@data-item-id').extract()[0]
        item['show_product_id'] = product_id
        item['from_site'] = 'victoriassecret'
        item['brand'] = "Victoria'S Secret"
        title = product_detail.xpath('.//div[@class="name"]/h2/text()').extract()[0] + product_detail.xpath('.//div[@class="name"]/h1/text()').extract()[0]
        item['title'] = title
        item['desc'] = sel.xpath('//section[@class="description"]/div[@class="long-description"]/text()').extract()[0]

        for color_item in color_data:
            color_item['show_product_id'] = product_id
            yield color_item

        for sku in skus:
            sku['show_product_id'] = product_id
            sku['id'] = product_id + '-' + sku['color'] + '-' + sku['size']

        item['skus'] = skus
        yield item

# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy import Request
import re
import execjs
from ..spiders.shiji_base import BaseSpider
from ..items import BaseItem, ImageItem, SkuItem, Color
import copy
import json
import logging
import os
from urllib import unquote


class ShangshangspSpider(BaseSpider):

    name = "shangshangsp"
    allowed_domains = ["shangshangsp.com"]
    start_urls = []
    base_url = "http://www.shangshangsp.com/"
    EU_CURRENCY = 10
    import_field_dict = {'gender': None, 'product_type_id': 0, 'category_id': 0, 'title': ''}

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        'COOKIES_ENABLED': True,

        'ITEM_PIPELINES': {
            'gorden_crawler.pipelines.mongodb.SingleMongodbPipeline': 303,
            'gorden_crawler.pipelines.realtime_handle_image.RealtimeHandleImage': 305,
        }
    }

    def __init__(self, name='shangshangsp', url=None, *args, **kwargs):
        super(ShangshangspSpider, self).__init__(name, **kwargs)
        if url:
            self.start_urls = [unquote(url)]
        for field in self.import_field_dict:
            self.import_field_dict[field] = os.environ.get(field)
        os.environ['main_process'] = 'True'
        os.environ['shangshangsp_spider'] = 'True'
        os.environ['need_size_transform'] = 'True'

    def parse(self, response):
        pass

    def parse_item(self, response):
        item=response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'shangshangsp'
        item['url'] = response.url

        for field in self.import_field_dict:
            item[field] = self.import_field_dict[field]

        if 'product_type_id' in item and item['product_type_id']:
            item['product_type'] = 'shangshangsp_' + item['product_type_id']
        if 'category' in item and item['product_type_id']:
            item['category'] = 'shangshangsp_' + item['category_id']

        if 'title' in item and not item['title']:
            item['title'] = sel.xpath('//div[@class="goods-property"]/h2/strong/text()').extract()[0]

        list_price_str = sel.xpath('//del/text()').extract()[0]
        list_price = float(re.search('\d+',list_price_str).group()) * self.EU_CURRENCY
        current_price_str = sel.xpath('//div[@class="goods-property"]/ul[@class="g-li"]/li[5]/i[last()]/font/text()').extract()[0]
        current_price = re.search('\d+', current_price_str).group()
        item['list_price'] = list_price
        item['current_price'] = current_price

        item['brand'] = sel.xpath('//div[@class="goods-property"]/ul[@class="g-li"]/li[1]/text()').extract()[0]
        item['desc'] = sel.xpath('//div[@class="goods-c"]/ul[1]/li/text()').extract()[0]
        item['show_product_id'] = sel.xpath('//input[@id="goodsId"]/@value').extract()[0]

        skus = []
        sizes = []
        i = 1
        if len(sel.xpath('//input[@name="goodsAttr_1"]'))>0:
            for size_input in sel.xpath('//input[@name="goodsAttr_1"]'):
                skuItem = SkuItem()
                skuItem['type'] = "sku"
                skuItem['from_site'] = item['from_site']
                skuItem['size'] = sel.xpath('//button[@name="spanbox"]['+ str(i) +']/text()').extract()[0]
                sizes.append(skuItem['size'])
                skuItem['color'] = 'One Color'
                skuItem['id'] = size_input.xpath('./@value').extract()[0]
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['current_price'] = item['current_price']
                skuItem['list_price'] = item['list_price']
                skus.append(skuItem)
                i+=1
        else:
            skuItem = SkuItem()
            skuItem['type'] = "sku"
            skuItem['from_site'] = item['from_site']
            skuItem['size'] = 'One Size'
            sizes.append(skuItem['size'])
            skuItem['color'] = 'One Color'
            skuItem['id'] = item['show_product_id'] + '_sku'
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['current_price'] = item['current_price']
            skuItem['list_price'] = item['list_price']
            skus.append(skuItem)

        images = []
        for img in sel.xpath('//div[@class="pot_xx"]/img'):
            imageItem = ImageItem()
            imageItem['image'] = img.xpath('./@src').extract()[0]
            imageItem['thumbnail'] = imageItem['image'].replace('l.jpg', 'm.jpg')
            images.append(imageItem)
        item['cover'] = images[0]['image']
        color = Color()
        color['type'] = 'color'
        color['from_site'] = item['from_site']
        color['show_product_id'] = item['show_product_id']
        color['images'] = images
        color['name'] = 'One Color'
        color['cover'] = item['cover']
        yield color

        item['colors'] = ['One Color']
        item['sizes'] = sizes
        item['skus'] = skus
        item['dimensions'] = ['size']
        yield item








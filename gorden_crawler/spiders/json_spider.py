# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy import Request
import os
import json
import time
import random
import hashlib
from urllib import quote, unquote
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy.exceptions import NotSupported
import logging


class JsonSpider(Spider):

    name = 'json_spider'
    start_urls = ['http://api.qnmami.com/user/login']

    custom_settings = {
        'ITEM_PIPELINES': {
            'gorden_crawler.pipelines.mongodb.SingleMongodbPipeline': 303,
            'gorden_crawler.pipelines.realtime_handle_image.RealtimeHandleImage': 305,
        }
    }
    def __init__(self, name='json_import', json_data=None, *args, **kwargs):
        super(JsonSpider, self).__init__(name, **kwargs)
        if json_data:
            self.json_data = json_data
            os.environ['main_process'] = 'True'
            os.environ['json_spider'] = 'True'
            os.environ['need_size_transform'] = 'True'

    def parse(self, response):
        goods_all = json.loads(self.json_data)

        skus = goods_all['skus']
        goods_colors = goods_all['goods_colors']
        goods = goods_all['goods']

        if 'title' not in goods.keys():
            raise NotSupported('No title in goods, Pls specify!!')
        title = ''.join(goods['title'].split()).lower()
        make_md5 = hashlib.md5()
        make_md5.update(quote(title, safe=''))
        show_product_id = make_md5.hexdigest()

        logging.warning('show_product_id: '+ show_product_id)
        logging.warning('title: ' + goods['title'])
        from_site = goods['from_site']

        skus_colors = []
        skus_sizes = []
        for sku in skus:
            if sku['color'] not in skus_colors:
                skus_colors.append(sku['color'])
            skus_sizes.append(sku['size'])
            if 'goods_current_price' not in dir() or goods_current_price > sku['current_price']:
                goods_current_price = sku['current_price']
            if 'goods_list_price' not in dir() or goods_list_price < sku['list_price']:
                goods_list_price = sku['list_price']
            sku['type'] = 'sku'
            sku['id'] = show_product_id + '-' + sku['color'] + '-' + sku['size']
            sku['is_outof_stock'] = False
            sku['from_site'] = from_site
            sku['show_product_id'] = show_product_id
        goods_colors_colors = []
        for goods_color in goods_colors:
            if 'name' not in goods_color.keys():
                raise NotSupported('ERROR! No name in (color)')
            goods_colors_colors.append(goods_color['name'])
            if 'cover' not in goods.keys():
                goods['cover'] = goods_color['images'][0]['image']
            if 'images' not in goods_color.keys() or len(goods_color['images']) == 0 or (len(goods_color['images']) == 1 and len(goods_color['images'][0]) == 0):
                goods_color['images'] = [{'image': goods['cover']}]
                goods_color['cover'] = goods['cover']
            else:
                goods_color['cover'] = goods_color['images'][0]['image']
            goods_color['from_site'] = from_site
            goods_color['show_product_id'] = show_product_id

        # if goods_colors_colors != list(set(goods_colors_colors)):
        #     raise NotSupported('ERROR! Dupelicate name in goods_colors')

        if goods_colors_colors == [] or skus_colors == [] or sorted(skus_colors) != sorted(goods_colors_colors):
            raise NotSupported('skus_colors: ' + str(skus_colors) + ', ' + 'goods_colors_colors: ' + str(goods_colors_colors) + ', \n' + 'goods_colors not equal sku_colors')

        for goods_color in goods_colors:
            colorItem = Color()
            colorItem = goods_color
            colorItem['type'] = 'color'
            yield colorItem

        item = BaseItem()
        item = goods
        item['type'] = 'base'
        item['product_type'] = 'json_import_' + goods['product_type_id']
        item['category'] = 'json_import_' + goods['category_id']
        item['product_type_id'] = goods['product_type_id']
        item['category_id'] = goods['category_id']
        item['title'] = goods['title']
        item['show_product_id'] = show_product_id
        item['from_site'] = from_site
        item['colors'] = skus_colors
        item['sizes'] = skus_sizes
        item['current_price'] = goods_current_price
        item['list_price'] = goods_list_price
        if 'groupbuy_num' in goods.keys():
            item['groupbuy_num'] = goods['groupbuy_num']
        item['skus'] = skus
        print 'skus',skus
        if 'desc' in goods.keys():
            item['desc'] = goods['desc']
        if 'weight' in goods.keys():
            item['weight'] = goods['weight']
        yield item

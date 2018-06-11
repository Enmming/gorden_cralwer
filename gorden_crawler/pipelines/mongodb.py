#!/usr/bin/python
# -*- coding: utf-8 -*-

from ..utils.item_field_handler import handle_price

from ..redisq.client import RedisqClient
from ..redisq.task import Task

from ..sizeregex.sizetransform import Singletransform
from ..bee_queue.client import BeeQueueClient
from ..bee_queue.bee_queue import Job

# from scrapy import log
from pprint import pprint
from scrapy.exceptions import DropItem
from urllib import quote, unquote
from HTMLParser import HTMLParser
from pymongo import MongoClient
from pymongo.mongo_replica_set_client import MongoReplicaSetClient
from pymongo.read_preferences import ReadPreference
from pymongo.operations import UpdateOne, InsertOne, UpdateMany
from pyquery import PyQuery

import logging
import re
import hashlib
import json
import time
import os
import redis
import base64

# import settings


def not_set(string):
    """ Check if a string is None or ''
    :returns: bool - True if the string is empty
    """
    if string is None:
        return True
    elif string == '':
        return True
    return False


class SingleMongodbPipeline(object):
    """
        save the data to mongodb.
    """

    '''
    currency
    1 RMB
    2 USD
    3 GBP
    4 EUR

    2 USA
    3 ENGLAND
    4 ITALY
    '''
    currency_country_map = {
        "lookfantastic": {'currency': 3, 'country_id': 3},
        "allsole": {'currency': 3, 'country_id': 3},
        "asos": {'currency': 2, 'country_id': 2},
        # "forzieri": {'currency': 4, 'country_id': 4}
    }

    country_sizetype_map = {
        2: 'us',
        3: 'uk',
        4: 'it'
    }

    # exchange_rate = {
    #     2: 6.45,
    #     3: 9.8,
    #     4: 6.95,
    # }

    # Default options
    config = {
        'uri': 'mongodb://localhost:27017',
        'shop_uri': 'mongodb://localhost:27017',
        'fsync': False,
        'write_concern': 0,
        'database': 'shiji_crawler_items',
        'shop_database': 'shiji_shop',
        'replica_set': None,
        'shop_replica_set': None,
        'item_notify_redis_host': 'localhost',
        'item_notify_redis_port': '6379',
        'image_handle_queue_redis_host': 'localhost',
        'image_handle_queue_redis_port': '6379'
    }

    sub_category_sites = ['asos', 'sixpm', 'zappos', 'bluefly']

    def load_spider(self, spider):
        self.crawler = spider.crawler
        self.settings = spider.settings

    def configure(self):
        """ Configure the MongoDB """

        # Set all regular options
        options = [
            ('uri', 'MONGODB_SERVER'),
            ('shop_uri', 'SHOP_MONGODB_SERVER'),
            ('fsync', 'MONGODB_FSYNC'),
            ('write_concern', 'MONGODB_REPLICA_SET_W'),
            ('database', 'MONGODB_DB'),
            ('shop_database', 'SHOP_MONGODB_DB'),
            ('replica_set', 'MONGODB_REPLICA_SET'),
            ('shop_replica_set', 'SHOP_MONGODB_REPLICA_SET'),
            ('item_notify_redis_host', 'ITEM_NOTIFY_REDIS_HOST'),
            ('item_notify_redis_port', 'ITEM_NOTIFY_REDIS_PORT'),
            ('item_notify_redis_password', 'ITEM_NOTIFY_REDIS_PASSWORD'),
            ('image_handle_queue_redis_host', 'IMGAE_HANDLE_QUEUE_REDIS_HOST'),
            ('image_handle_queue_redis_port', 'IMGAE_HANDLE_QUEUE_REDIS_PORT'),
            ('image_handle_queue_redis_password', 'IMGAE_HANDLE_QUEUE_REDIS_PASSWORD'),
            ('realtime_image_handle_queue_redis_host', 'REALTIME_IMAGE_HANDLE_QUEUE_REDIS_HOST'),
            ('realtime_image_handle_queue_redis_port', 'REALTIME_IMAGE_HANDLE_QUEUE_REDIS_PORT'),
            ('realtime_image_handle_queue_redis_password', 'REALTIME_IMAGE_HANDLE_QUEUE_REDIS_PASSWORD')
        ]

        for key, setting in options:
            if not not_set(self.settings[setting]):
                self.config[key] = self.settings[setting]

    def open_spider(self, spider):
        self.load_spider(spider)
        self.configure()

        if self.config['replica_set'] is not None:
            connection = MongoReplicaSetClient(
                self.config['uri'],
                replicaSet=self.config['replica_set'],
                w=self.config['write_concern'],
                fsync=self.config['fsync'],
                read_preference=ReadPreference.PRIMARY_PREFERRED)

            shop_connection = MongoReplicaSetClient(
                self.config['shop_uri'],
                replicaSet=self.config['replica_set'],
                w=self.config['write_concern'],
                fsync=self.config['fsync'],
                read_preference=ReadPreference.PRIMARY_PREFERRED)
        else:
            # Connecting to a stand alone MongoDB
            connection = MongoClient(
                self.config['uri'],
                fsync=self.config['fsync'],
                read_preference=ReadPreference.PRIMARY)

            shop_connection = MongoClient(
                self.config['shop_uri'],
                fsync=self.config['fsync'],
                read_preference=ReadPreference.PRIMARY)

        # Set up db
        self.db = connection[self.config['database']]
        self.db_category = connection['item_categories']
        self.shop_db = shop_connection[self.config['shop_database']]
        self.shop_db_category = shop_connection['item_categories']

        # self.image_handle_queue_redis = redis.Redis(host=self.config['image_handle_queue_redis_host'], port=self.config['image_handle_queue_redis_port'])
        # self.image_hamdle_queue = RedisqClient("crawler", host=self.config['image_handle_queue_redis_host'], port=self.config['image_handle_queue_redis_port'])
        if 'image_handle_queue_redis_password' in self.config.keys():
            self.image_handle_queue = BeeQueueClient("bq:crawler_handle_image:", host=self.config['image_handle_queue_redis_host'], port=self.config['image_handle_queue_redis_port'], password=self.config['image_handle_queue_redis_password'])
        else:
            self.image_handle_queue = BeeQueueClient("bq:crawler_handle_image:", host=self.config['image_handle_queue_redis_host'], port=self.config['image_handle_queue_redis_port'])

        self.need_notify_redis = (os.environ.get('item_update_notify_redis', 'False') == 'True')

        if self.need_notify_redis:
            if os.environ.get('single_item_mode', 'None') == 'realtime':
                if 'realtime_image_handle_queue_redis_password' in self.config.keys():
                    self.realtime_image_handle_queue = BeeQueueClient("bq:realtime_handle_image:", host=self.config['realtime_image_handle_queue_redis_host'], port=self.config['realtime_image_handle_queue_redis_port'], password=self.config['realtime_image_handle_queue_redis_password'])
                else:
                    self.realtime_image_handle_queue = BeeQueueClient("bq:realtime_handle_image:", host=self.config['realtime_image_handle_queue_redis_host'], port=self.config['realtime_image_handle_queue_redis_port'])

        if 'item_notify_redis_password' in self.config.keys():
            self.item_redis_connection = redis.Redis(host=self.config['item_notify_redis_host'], port=self.config['item_notify_redis_port'], password=self.config['item_notify_redis_password'])
        else:
            self.item_redis_connection = redis.Redis(host=self.config['item_notify_redis_host'], port=self.config['item_notify_redis_port'])

    def push_handle_image_to_queue(self, type, detail):
        data = None

        if type == 'c':
            data = {"t": "c", 'site': detail['from_site'], 'p_id':detail['show_product_id'], 'c_name': detail['color_flag']}

        elif type == 'i':
            data = {"t": "i", 'site': detail['from_site'], 'p_id':detail['show_product_id']}

        elif type == 'c_r':
            data = {"t": "c_r", 'site': detail['from_site'], 'p_id':detail['show_product_id'], 'c_name': detail['color_flag']}

        if data:
            if os.environ.get('single_item_mode', 'None') == 'realtime':
                make_md5 = hashlib.md5()
                if os.environ.get('single_item_realtime_url'):
                    make_md5.update(quote(os.environ.get('single_item_realtime_url'), safe=''))
                    data['md5_url'] = make_md5.hexdigest()
                    data['worker_type'] = 'realtime'
                self.realtime_image_handle_queue.pushJob(Job(data, options={"timeout": 10000, "retries": 2}))
            else:
                self.image_handle_queue.pushJob(Job(data, options={"timeout": 10000, "retries": 2}))

    def process_skus(self, skus, show_product_id, from_site):

        """统一下架"""
        crawl_bulk_operations = []
        shop_bulk_operations = []

        crawl_bulk_operations.append(UpdateMany({'from_site': from_site, 'show_product_id': show_product_id}, {'$set': {'is_outof_stock': True}}))
        shop_bulk_operations.append(UpdateMany({'from_site': from_site, 'show_product_id': show_product_id}, {'$set': {'is_outof_stock': True}}))

        min_list_price = None
        min_current_price = None

        for item in skus:
            sku_detail = {
                'scan_time': int(time.time()),
                'scan_date': time.strftime('%Y-%m-%d',time.localtime(time.time())),
                'show_product_id': str(item.get('show_product_id')),
                'from_site': item.get('from_site'),
                'id': item.get('id'),
                'list_price': handle_price(str(item.get('list_price'))),
                'current_price': handle_price(str(item.get('current_price'))),
                'color': item.get('color'),
                'size_num': item.get('size_num'),
                'groupbuy_price': item.get('groupbuy_price'),
                's_t': item.get('s_t')
            }

            s_color = sku_detail['color'].lower().strip()
            for c in s_color:
                s_color = re.sub("  ", " ", s_color)
            sku_detail['s_color'] = s_color

            for key in sku_detail.keys():
                if not sku_detail[key]:
                    del sku_detail[key]
                else:
                    if type(sku_detail[key]) == str:
                        sku_detail[key] = sku_detail[key].strip()

            if 'is_outof_stock' in item.keys():
                sku_detail['is_outof_stock'] = item.get('is_outof_stock')
            else:
                sku_detail['is_outof_stock'] = False

            if sku_detail['is_outof_stock'] == False:
                float_list_price = float(sku_detail['list_price'])
                if not min_list_price or min_list_price > float_list_price:
                    min_list_price = float_list_price

                float_current_price = float(sku_detail['current_price'])
                if not min_current_price or min_current_price > float_current_price:
                    min_current_price = float_current_price

            sku_size = item.get('size')
            if type(sku_size) == dict:
                for key in sku_size:
                    sku_detail[key] = sku_size[key]
            else:
                sku_detail['size'] = sku_size

            '''单个爬虫更新单个商品（测试使用）'''
            if self.settings['SIZE_TRANSFORM_TEST'] == 3:
                Singletransform().singletransform(from_site, sku_detail, self.settings['SIZE_TRANSFORM_LIST'])

            if 'quantity' in item.keys():
                sku_detail['quantity'] = item.get('quantity')

            sku_flag = str(sku_detail['id'])
            sku_flag = "".join(sku_flag.split())
            sku_flag = sku_flag.lower()
            spaces = ['\n', '\t', '\r']
            for s in spaces:
                if s in sku_flag:
                    sku_flag = re.sub(s, '', sku_flag)
            sku_detail['sku_flag'] = sku_flag

            sku_mongo = self.shop_db['skus'].find_one({'from_site': sku_detail['from_site'], 'show_product_id':sku_detail['show_product_id'], 'sku_flag': sku_detail['sku_flag']})

            if sku_detail['from_site'] in self.settings['SIZE_TRANSFORM_LIST']:
                if sku_mongo and 'size' in sku_mongo.keys():
                    if sku_detail['size'] != sku_mongo['size']:
                        sku_detail['handle_size'] = '1'
                else:
                    sku_detail['handle_size'] = '1'

            if sku_detail['from_site'] == 'ralphlauren':
                if not sku_mongo:
                    crawl_bulk_operations.append(UpdateOne(
                        {'from_site': sku_detail['from_site'], 'show_product_id':sku_detail['show_product_id'], 'color': sku_detail['color'], 'size': sku_detail['size']},
                        {'$set': sku_detail},
                        upsert=True
                    ))

                    shop_bulk_operations.append(UpdateOne(
                        {'from_site': sku_detail['from_site'], 'show_product_id':sku_detail['show_product_id'], 'color': sku_detail['color'], 'size': sku_detail['size']},
                        {'$set': sku_detail},
                        upsert=True
                    ))
                else:
                    crawl_bulk_operations.append(UpdateOne(
                        {'from_site': sku_detail['from_site'], 'show_product_id':sku_detail['show_product_id'], 'color': sku_detail['color'], 'size': sku_detail['size']},
                        {'$set': sku_detail}
                    ))

                    shop_bulk_operations.append(UpdateOne(
                        {'from_site': sku_detail['from_site'], 'show_product_id':sku_detail['show_product_id'], 'color': sku_detail['color'], 'size': sku_detail['size']},
                        {'$set': sku_detail}
                    ))
            else:
                if not sku_mongo:
                    crawl_bulk_operations.append(UpdateOne(
                        {'from_site': sku_detail['from_site'], 'show_product_id':sku_detail['show_product_id'], 'sku_flag': sku_detail['sku_flag']},
                        {'$set': sku_detail},
                        upsert=True
                    ))

                    shop_bulk_operations.append(UpdateOne(
                        {'from_site': sku_detail['from_site'], 'show_product_id':sku_detail['show_product_id'], 'sku_flag': sku_detail['sku_flag']},
                        {'$set': sku_detail},
                        upsert=True
                    ))
                else:
                    crawl_bulk_operations.append(UpdateOne(
                        {'from_site': sku_detail['from_site'], 'show_product_id':sku_detail['show_product_id'], 'sku_flag': sku_detail['sku_flag']},
                        {'$set': sku_detail}
                    ))

                    shop_bulk_operations.append(UpdateOne(
                        {'from_site': sku_detail['from_site'], 'show_product_id':sku_detail['show_product_id'], 'sku_flag': sku_detail['sku_flag']},
                        {'$set': sku_detail}
                    ))

        self.db['skus'].bulk_write(crawl_bulk_operations)
        self.shop_db['skus'].bulk_write(shop_bulk_operations)

        return min_list_price, min_current_price

    """
    def process_skus_gilt(self, skus, show_product_id, from_site):

        pass_show_product_id = str(os.environ.get('single_item_show_product_id'))

        '''统一下架'''
        crawl_bulk_operations = []
        shop_bulk_operations = []

        crawl_bulk_operations.append(UpdateMany({'from_site': from_site, 'show_product_id': show_product_id}, {'$set': {'is_outof_stock': True, 'show_product_id': show_product_id}}))
        shop_bulk_operations.append(UpdateMany({'from_site': from_site, 'show_product_id': show_product_id}, {'$set': {'is_outof_stock': True, 'show_product_id': show_product_id}}))

        min_list_price = None
        min_current_price = None

        for item in skus:
            sku_detail = {
                'scan_time': int(time.time()),
                'scan_date': time.strftime('%Y-%m-%d',time.localtime(time.time())),
                'show_product_id': str(item.get('show_product_id')),
                'from_site': item.get('from_site'),
                'id': item.get('id'),
                'list_price': handle_price(str(item.get('list_price'))),
                'current_price': handle_price(str(item.get('current_price'))),
                'color': item.get('color'),
                'size_num': item.get('size_num')
            }

            float_list_price = float(sku_detail['list_price'])
            if not min_list_price or min_list_price > float_list_price:
                min_list_price = float_list_price

            float_current_price = float(sku_detail['current_price'])
            if not min_current_price or min_current_price > float_current_price:
                min_current_price = float_current_price

            for key in sku_detail.keys():
                if not sku_detail[key]:
                    del sku_detail[key]
                else:
                    if type(sku_detail[key]) == str:
                        sku_detail[key] = sku_detail[key].strip()

            if 'is_outof_stock' in item.keys():
                sku_detail['is_outof_stock'] = item.get('is_outof_stock')
            else:
                sku_detail['is_outof_stock'] = False

            sku_size = item.get('size')
            if type(sku_size) == dict:
                for key in sku_size:
                    sku_detail[key] = sku_size[key]
            else:
                sku_detail['size'] = sku_size

            if 'quantity' in item.keys():
                sku_detail['quantity'] = item.get('quantity')

            sku_flag = str(sku_detail['id'])
            sku_flag = "".join(sku_flag.split())
            sku_flag = sku_flag.lower()
            spaces = ['\n', '\t', '\r']
            for s in spaces:
                if s in sku_flag:
                    sku_flag = re.sub(s, '', sku_flag)
            sku_detail['sku_flag'] = sku_flag

            sku_mongo = self.shop_db['skus'].find_one({'from_site': sku_detail['from_site'], 'show_product_id':pass_show_product_id, 'sku_flag': sku_detail['sku_flag']})

            if not sku_mongo:
                crawl_bulk_operations.append(UpdateOne(
                    {'from_site': sku_detail['from_site'], 'show_product_id': sku_detail['show_product_id'], 'sku_flag': sku_detail['sku_flag']},
                    {'$set': sku_detail},
                    upsert=True
                ))

                shop_bulk_operations.append(UpdateOne(
                    {'from_site': sku_detail['from_site'], 'show_product_id':sku_detail['show_product_id'], 'sku_flag': sku_detail['sku_flag']},
                    {'$set': sku_detail},
                    upsert=True
                ))
            else:
                crawl_bulk_operations.append(UpdateOne(
                    {'from_site': sku_detail['from_site'], 'show_product_id':pass_show_product_id, 'sku_flag': sku_detail['sku_flag']},
                    {'$set': sku_detail}
                ))

                shop_bulk_operations.append(UpdateOne(
                    {'from_site': sku_detail['from_site'], 'show_product_id':pass_show_product_id, 'sku_flag': sku_detail['sku_flag']},
                    {'$set': sku_detail}
                ))

        self.db['skus'].bulk_write(crawl_bulk_operations)
        self.shop_db['skus'].bulk_write(shop_bulk_operations)

        return min_list_price, min_current_price
    """

    def process_item(self, item, spider):

#         if os.environ.get('is_single_item') :
#             is_single_item = (os.environ.get('is_single_item') != 'False')
#         else:
#             is_single_item = False
#
#         if is_single_item and item.get('from_site') == 'fgilt' and os.environ.get('single_item_show_product_id'):
#             return self.process_item_gilt(item, spider)
        item_type = item.get('type')

        if item_type == 'color':
            color_detail = {
                'show_product_id': str(item.get('show_product_id')),
                'scan_time': int(time.time()),
                'scan_date': time.strftime('%Y-%m-%d',time.localtime(time.time())),
                'from_site': item.get('from_site'),
                'images': item.get('images'),
                'images_bak': item.get('images'),
                'name': item.get('name').strip()
            }

            color_flag = "".join(color_detail['name'].split())
            color_flag = color_flag.lower()
            color_detail['color_flag'] = color_flag

            s_name = color_detail['name'].lower().strip()
            for n in s_name:
                s_name = re.sub("  ", " ", s_name)

            color_search = self.shop_db['goods_color_info'].find_one({'name': s_name})
            if not color_search and len(color_detail['images']) > 0:
                self.shop_db['goods_color_info'].insert(
                    {"name": s_name, "num": 1, "url": color_detail['images'][0]['image']})

            if item.get('version'):
                color_detail['version'] = item.get('version')

            for i in range(len(color_detail['images'])):
                image_dic = color_detail['images'][i]
                for key in image_dic.keys():
                    key_type = type(image_dic[key])
                    if key_type == str or key_type == unicode:
                        color_detail['images'][i][key] = image_dic[key].strip()

            if item.get('cover'):
                color_detail['cover'] = item.get('cover')
                color_detail['cover_bak'] = item.get('cover')
            else:
                color_detail['cover'] = ''

            if item.get('cover_style'):
                color_detail['cover_style'] = item.get('cover_style')
            else:
                color_detail['cover_style'] = ''

            color_detail['discard'] = '0'

            need_push_queue = False
            need_re_handle_image = False

            color_mongo = self.shop_db['goods_colors'].find_one({'from_site': color_detail['from_site'], 'show_product_id':color_detail['show_product_id'], 'color_flag': color_detail['color_flag']})

            if not color_mongo:
                self.db['colors'].update_one(
                    {'from_site': color_detail['from_site'], 'show_product_id':color_detail['show_product_id'], 'color_flag': color_detail['color_flag']},
                    {'$set': color_detail},
                    upsert=True
                )

                self.shop_db['goods_colors'].update_one(
                    {'from_site': color_detail['from_site'], 'show_product_id':color_detail['show_product_id'], 'color_flag': color_detail['color_flag']},
                    {'$set': color_detail},
                    upsert=True
                )

                need_push_queue = True

            else:
                self.db['colors'].update_one(
                    {'from_site': color_detail['from_site'], 'show_product_id':color_detail['show_product_id'], 'name': color_detail['name']},
                    {'$set': color_detail}
                )

                if 'handle_image' not in color_mongo.keys() or color_mongo['handle_image'] != 2:
                    need_push_queue = True

                    self.shop_db['goods_colors'].update_one(
                        {'from_site': color_detail['from_site'], 'show_product_id':color_detail['show_product_id'], 'color_flag': color_detail['color_flag']},
                        {'$set': color_detail}
                    )
                else:
                    if len(color_mongo['images']) == 0 and len(color_detail['images']) > 0:
                        need_re_handle_image = True

                    if 'rehandle'in color_mongo.keys() and color_mongo['rehandle'] == '1':
                        need_re_handle_image = True

                    if 'images_bak' in color_mongo.keys() and color_mongo['images_bak'] != color_detail['images_bak']:
                        need_re_handle_image = True

                    if len(color_detail['cover_style']) > 0:

                        get_params_keys = ['cover_style', 'scan_date', 'scan_time', 'images_bak', 'color_flag', 'discard']

                        if need_re_handle_image:
                            get_params_keys.append('rehandle')
                            color_detail['rehandle'] = '1'

                        self.shop_db['goods_colors'].update_one(
                            {'from_site': color_detail['from_site'], 'show_product_id':color_detail['show_product_id'], 'color_flag': color_detail['color_flag']},
                            {'$set': self.get_item_params(color_detail, get_params_keys)}
                        )
                    else:

                        get_params_keys = ['scan_date', 'scan_time', 'images_bak', 'cover_bak', 'color_flag', 'discard']

                        if need_re_handle_image:
                            get_params_keys.append('rehandle')
                            color_detail['rehandle'] = '1'

                        self.shop_db['goods_colors'].update_one(
                            {'from_site': color_detail['from_site'], 'show_product_id':color_detail['show_product_id'], 'color_flag': color_detail['color_flag']},
                            {'$set': self.get_item_params(color_detail, get_params_keys)}
                        )

            if need_push_queue:
                '''将链接丢到临时的消息队列中，等待处理'''
                self.push_handle_image_to_queue('c', color_detail)
            elif need_re_handle_image:
                self.push_handle_image_to_queue('c_r', color_detail)
            else:
                self.set_md5url_redis_status('goodscolors', item.get('from_site'), 'finished: ' + color_detail['show_product_id'])

        elif item_type == 'base':

            h = HTMLParser()
            if item.get('title') is not None:
                etitle = h.unescape(item.get('title'))
            else:
                etitle = item.get('title')

            item_detail = {
                'country_id': 2, #2表示美国
                'currency': 2, #1表示人民币，2表示美元
                'scan_time': int(time.time()),
                'scan_date': time.strftime('%Y-%m-%d',time.localtime(time.time())),
                'url': item.get('url'),
                'title': etitle,
                'cover': item.get('cover'),
                'show_product_id': str(item.get('show_product_id')),
                'from_site': item.get('from_site'),
                'desc': item.get('desc'),
                'color': item.get('colors'),
                'brand': item.get('brand'),
                'product_type': item.get('product_type'),
                'category': item.get('category'),
                'sub_category': item.get('sub_category'),
                'gender': item.get('gender'),
                'list_price': item.get('list_price'),
                'current_price': item.get('current_price'),
                'size_info': item.get('size_info'),
                'begins': item.get('begins'),
                'ends': item.get('ends'),
                'sale_key': item.get('sale_key'),
                'is_sold_out': item.get('is_sold_out'),
                'good_json_url': item.get('good_json_url'),
                'size_country': item.get('country'),
                'weight': item.get('weight'),
                'groupbuy_num': item.get('groupbuy_num'),
                'linkhaitao_url': item.get('linkhaitao_url'),
                'editor_flag': item.get('editor_flag'),
                'media_url': item.get('media_url'),
                'related_items_id': item.get('related_items_id')
            }

#             if not item_detail.has_key('sale_key'):
#                 item_detail.pop('sale_key')
#                 item_detail.pop('begins')
#                 item_detail.pop('ends')
#                 item_detail.pop('is_sold_out')
#                 item_detail.pop('good_json_url')

            '''品牌文字编码处理'''
            pattern = re.compile('\&\#(\d+)\;')
            if 'brand' in item_detail.keys() and item_detail['brand'] and re.search(pattern, item_detail['brand']):
                unique_letter = chr(int(re.search(pattern, item_detail['brand']).group(1))).decode('cp1252')
                item_detail['brand'] = re.sub(pattern, unique_letter, item_detail['brand'])

            if 'brand' in item_detail.keys() and item_detail['brand'] and len(item_detail['brand'])>64:
                item_detail['brand'] = item_detail['brand'][:64]

            '''特殊爬虫'''
            if os.environ.get('linkhaitao_spider', 'False') == 'True':
                item_detail['linkhaitao'] = '1'
            else:
                item_detail['linkhaitao'] = '0'

            for special_spider in self.settings['SPECIAL_SPIDER_LIST']:
                if special_spider in spider.name:
                    item_detail['product_type_id'] = item.get('product_type_id')
                    item_detail['category_id'] = item.get('category_id')
                    break

            if item_detail['from_site'] == 'ssense':
                if item.get('size_chart'):
                    item_detail['size_chart'] = item.get('size_chart')
                if item.get('size_chart_pic'):
                    item_detail['size_chart_pic'] = item.get('size_chart_pic')

            # fgilt尺码表
            elif item_detail['from_site'] == 'fgilt' and item.get('size_chart'):
                fgilt_size_chart = item.get('size_chart')
                item_detail['size_chart'] = fgilt_size_chart['title']
                fgilt_size_chart['from_site'] = 'fgilt'
                self.shop_db['size_chart'].update_one({'title': fgilt_size_chart['title'], 'from_site': fgilt_size_chart['from_site']}, {'$set': fgilt_size_chart}, upsert = True)

            elif item_detail['from_site'] == 'macys' and item.get('size_chart'):
                macys_size_chart = item.get('size_chart')
                item_detail['size_chart'] = macys_size_chart['title']
                macys_size_chart['from_site'] = 'macys'
                self.shop_db['size_chart'].update_one({'title': macys_size_chart['title'], 'from_site': macys_size_chart['from_site']}, {'$set': macys_size_chart}, upsert = True)

            # elif item_detail['from_site'] == 'nordstrom' and item.get('size_chart'):
            #     nordstrom_size_charts = item.get('size_chart')
            #     # if len(nordstrom_size_chart)>1:
            #     item_detail['size_chart']=[]
            #     for nordstrom_size_chart in nordstrom_size_charts:
            #         item_detail['size_chart'].append(nordstrom_size_chart['title'])
            #         self.shop_db['nordstrom_size_chart'].update_one({'title': nordstrom_size_chart['title']}, {'$set': nordstrom_size_chart}, upsert = True)

            elif item_detail['from_site'] == 'forward' and item.get('size_chart'):
                forward_size_chart = item.get('size_chart')
                item_detail['size_chart'] = forward_size_chart['title']
                forward_size_chart['from_site'] = 'forward'
                self.shop_db['size_chart'].update_one({'title': forward_size_chart['title'], 'from_site': forward_size_chart['from_site']}, {'$set': forward_size_chart}, upsert = True)

            elif item_detail['from_site'] == 'luisaviaroma' and item.get('size_chart'):
                luisaviaroma_size_chart = item.get('size_chart')
                item_detail['size_chart'] = luisaviaroma_size_chart['title']
                luisaviaroma_size_chart['from_site'] = 'luisaviaroma'
                self.shop_db['size_chart'].update_one({'title': luisaviaroma_size_chart['title'], 'from_site': luisaviaroma_size_chart['from_site']}, {'$set': luisaviaroma_size_chart}, upsert = True)

            elif item.get('size_chart'):
                size_chart = item.get('size_chart')
                item_detail['size_chart'] = size_chart['title']
                size_chart['from_site'] = item_detail['from_site']
                self.shop_db['size_chart'].update_one({'title': size_chart['title'], 'from_site': size_chart['from_site']}, {'$set': size_chart}, upsert = True)

            if item.get('dimension_names'):
                item_detail['dimension_names'] = item.get('dimension_names')

            skus = item.get('skus')
            if not skus or len(skus) == 0:
                raise DropItem('empty skus')

            (min_list_price, min_current_price) = self.process_skus(skus, str(item.get('show_product_id')), item.get('from_site'))


            item_is_outof_stock = True
            for sku in skus:
                if 'is_outof_stock' in sku.keys():
                    sku_is_outof_stock = sku.get('is_outof_stock')
                else:
                    sku_is_outof_stock = False

                if sku_is_outof_stock == False:
                    item_is_outof_stock = False
                    break

            if item_is_outof_stock:
                raise DropItem('skus is all outof stock')

            if float(min_list_price) == float(min_current_price) == 0:
                raise DropItem('price is 0')

            if item_detail['from_site'] in self.currency_country_map.keys():
                item_detail['country_id'] = self.currency_country_map[item_detail['from_site']]['country_id']
                item_detail['currency'] = self.currency_country_map[item_detail['from_site']]['currency']

            '''item_detail[key]==0'''
            for key in item_detail.keys():
                if not item_detail[key] or len(str(item_detail[key])) == 0:
                    del item_detail[key]
                else:
                    key_type = type(item_detail[key])
                    if key_type == str or key_type == unicode:
                        item_detail[key] = item_detail[key].strip()
                    if key == 'gender' or key == 'product_type' or key == 'category' or key == 'sub_category':
                        item_detail[key] = item_detail[key].lower()

            if not 'desc' in item_detail.keys():
                item_detail['desc'] = ''

            if not 'list_price' in item_detail.keys():
                item_detail['list_price'] = min_list_price

            # if not 'current_price' in item_detail.keys():
            item_detail['current_price'] = min_current_price

            if 'list_price' not in item_detail.keys():
                item_detail['list_price'] = item_detail['current_price']

            item_detail['current_price'] = handle_price(str(item_detail['current_price']))
            item_detail['list_price'] = handle_price(str(item_detail['list_price']))

            '''计算折扣'''
            float_current_price = float(item_detail['current_price'])
            float_list_price = float(item_detail['list_price'])

            if float_current_price == 0:
                discount = 10
            elif float_list_price > float_current_price:
                discount = round(float_current_price/float_list_price, 3) * 10
            else:
                discount = 10

            item_detail['discount'] = discount

            '''计算CNY价格'''
            # exchange_rate = self.exchange_rate[item_detail['currency']]
            exchange_rate_map = self.item_redis_connection.hgetall('mysql:super_mammy_shop:exchange_rate')
            exchange_rate = float(exchange_rate_map[str(item_detail['currency']) + '|'])
            for country, currency in exchange_rate_map.items():
                if item_detail['from_site'] in country:
                    item_detail['currency'] = country.split('|')[0]
                    exchange_rate = float(currency)
            if exchange_rate:
                cny_price = round(float_current_price,2) * exchange_rate
                item_detail['cny_price'] = round(cny_price, 2)

            dimensions = item.get('dimensions')
            if not dimensions or len(dimensions) == 0:
                dimensions = ['size']

            if 'color' not in dimensions:
                dimensions.append('color')
            item_detail['dimensions'] = dimensions

            sizes = item.get('sizes')
            if type(sizes) == dict:
                for size_key in sizes:
                    if type(sizes[size_key]) == list:
                        item_detail[size_key] = sizes[size_key]
                    else:
                        item_detail[size_key] = [sizes[size_key]]
            else:
                item_detail['size'] = sizes

            '''处理title'''
            if 'title' in item_detail.keys():
                if type(item_detail['title']) != unicode:
                    item_detail['title'] = unicode(item_detail['title'], 'utf-8')
                doc = PyQuery(item_detail['title'])
                item_detail['title'] = doc.text()
                item_detail['low_title'] = item_detail['title'].replace(' ', '').lower()

            if type(item_detail['show_product_id']) == int:
                item_push_show_product_id = item_detail['show_product_id']
            else:
                item_push_show_product_id = item_detail['show_product_id'].encode("utf-8")

            need_push_queue = False

            item_mongo = self.shop_db['goods'].find_one({'from_site': item_detail['from_site'], 'show_product_id': item_detail['show_product_id']})

            # 商品id搜索
            if os.environ.get('parse_id', 'False') == 'True':
                make_md5 = hashlib.md5()
                make_md5.update(quote(os.environ.get('parse_id_url'), safe=''))
                url_md5 = make_md5.hexdigest()
                if item_mongo:
                    self.item_redis_connection.hset('shiji_shop_parse_id', str(item_detail['from_site']) + ':' + url_md5, str(item_mongo['_id']))
                else:
                    self.item_redis_connection.hset('shiji_shop_parse_id', str(item_detail['from_site']) + ':' + url_md5, 'item is not in database')
                    return

            if not item_mongo:
                # item_detail_new =  item_detail.copy()

                if 'sale_key' in item_detail.keys():
                    sale_key = item_detail['sale_key']
                    sale_keys = [sale_key]

                    item_detail['sale_keys'] = sale_keys
                    del item_detail['sale_key']

                    self.update_sale_show_product_ids(item_detail, sale_key)

                item_detail['sell_num'] = 0
                item_detail['status'] = 2
                '''插入商品数据库仓库'''
                self.shop_db['goods'].update_one(
                    {'from_site': item_detail['from_site'], 'show_product_id': item_detail['show_product_id']},
                    {'$set': item_detail},
                    upsert=True
                )

                # del item_detail['sell_num']
                # del item_detail['status']

                need_push_queue = True
            else:
                if 'discount' in item_detail.keys() and 'discount' in item_mongo.keys() and float(item_detail['discount']) > float(item_mongo['discount']):
                    item_detail['discount_v'] = float(item_detail['discount']) - float(item_mongo['discount'])
                else:
                    item_detail['discount_v'] = 0

                if item_mongo['status'] == 1 and 'add_time' in item_mongo.keys():
                    item_detail['status'] = 3
                elif item_mongo['status'] == 1:
                    item_detail['status'] = 2

                if 'sale_key' in item_detail.keys():
                    sale_key = item_detail['sale_key']

                    if 'sale_keys' in item_mongo.keys():
                        sale_keys = item_mongo['sale_keys']
                        if sale_key not in sale_keys:
                            sale_keys.append(sale_key)
                    else:
                        sale_keys = [sale_key]

                    del item_detail['sale_key']
                    item_detail['sale_keys'] = sale_keys

                    self.update_sale_show_product_ids(item_detail, sale_key)

                if 'handle_image' not in item_mongo.keys() or item_mongo['handle_image'] != 2:
                    need_push_queue = True

                    '''插入商品数据库仓库'''
                    self.shop_db['goods'].update_many(
                        {'from_site': item_detail['from_site'], 'show_product_id': item_detail['show_product_id']},
                        {'$set': self.get_item_params_ignore_keys(item_detail, ['title', 'desc'])}
                    )
                else:
                    '''插入商品数据库仓库'''
                    self.shop_db['goods'].update_many(
                        {'from_site': item_detail['from_site'], 'show_product_id': item_detail['show_product_id']},
                        {'$set': self.get_item_params_ignore_keys(item_detail, ['title', 'cover', 'desc'])}
                    )

                if 'status' in item_detail.keys():
                    del item_detail['status']

            '''插入爬虫数据库'''
            self.db['items'].update_many(
                {'from_site': item_detail['from_site'], 'show_product_id': item_detail['show_product_id']},
                {'$set': item_detail},
                upsert=True
            )

            '''插入item category'''
            if 'product_type' in item_detail:
                category_params = {'from_site': item_detail['from_site'], 'product_type': item_detail['product_type']}
                update_params = {'from_site': item_detail['from_site'], 'product_type': item_detail['product_type'], 'item_url': item_detail['url']}
                if 'category' in item_detail:
                    category_params['category'] = item_detail['category']
                    update_params['category'] = item_detail['category']

                if 'sub_category' in item_detail and item_detail['from_site'] in self.sub_category_sites:
                    category_params['sub_category'] = item_detail['sub_category']
                    update_params['sub_category'] = item_detail['sub_category']

                for special_spider in self.settings['SPECIAL_SPIDER_LIST']:
                    if special_spider in spider.name:
                        update_params['product_type_id'] = item.get('product_type_id')
                        update_params['category_id'] = item.get('category_id')
                        break

                self.db_category['categories'].update_one(
                    category_params,
                    {'$set': update_params},
                    upsert=True
                )

                self.shop_db_category['categories'].update_one(
                    category_params,
                    {'$set': update_params},
                    upsert=True
                )

#             if self.need_notify_redis:
#                 print 'notify'
#                 self.item_redis_connection.set('shiji_shop_crawl:goods:' + item_detail['from_site'] + ':' + item_detail['show_product_id'], 'done')
#                 print 'notify success'

            '''通知消息'''
            if not item_mongo:
                self.item_redis_connection.lpush('notify_stock_queue', json.dumps(
                    {"from_site": item_detail['from_site'], "show_product_id": item_push_show_product_id,
                     "type": "color_size"}))
            elif item_mongo and 'size' in item_detail.keys() and item_detail['size'] != item_mongo['size'] and item_detail['color'] != item_mongo['color']:
                self.item_redis_connection.lpush('notify_stock_queue', json.dumps(
                    {"from_site": item_detail['from_site'], "show_product_id": item_push_show_product_id,
                     "type": "color_size"}))
            elif item_mongo and item_detail['size'] != item_mongo['size']:
                self.item_redis_connection.lpush('notify_stock_queue', json.dumps(
                    {"from_site": item_detail['from_site'], "show_product_id": item_push_show_product_id,
                     "type": "size"}))
            elif item_mongo and item_detail['color'] != item_mongo['color']:
                self.item_redis_connection.lpush('notify_stock_queue', json.dumps(
                    {"from_site": item_detail['from_site'], "show_product_id": item_push_show_product_id,
                     "type": "color"}))

            if need_push_queue:
                '''将链接丢到临时的消息队列中，等待处理'''
                self.push_handle_image_to_queue('i', item_detail)
            else:
                self.set_md5url_redis_status('goods', item.get('from_site'), 'finished: ' + item_detail['show_product_id'])

            '''进行单item的状态设置'''
            self.handle_single_item_done(item)

        elif item_type == 'diapers_size_info':

            size_type_detail = {
                'brand_name': item.get('brand_name'),
                'size_chart_type': item.get('size_chart_type'),
                'size_type': item.get('size_type'),
            }

            size_info_detail = {
                'size_type': item.get('size_type'),
                'size_info': item.get('size_info')
            }

            self.shop_db['diapers_size_type'].update_one(
                {'brand_name': size_type_detail['brand_name'], 'size_chart_type':size_type_detail['size_chart_type']},
                {'$set': size_type_detail},
                upsert = True
            )

            self.shop_db['diapers_size_info'].update_one(
                {'size_type': size_info_detail['size_type']},
                {'$set': size_info_detail},
                upsert = True
            )
        # elif item_type == 'sale_base':
        #     item_detal['begins'] = item.get('begins')
        #     item_detail['ends'] = item.get('ends')
        #     item_detail['sale_key'] = item.get('sale_key')
        #     item_detail['is_sale'] = item.get('is_sale')

        #     self.process_base_item(item, item_detail, 'flash_goods', 'flash_items', 'categories')

        elif item_type == 'sale':
            sale_detail = {'from_site': item.get('from_site'),
                           'begins': item.get('begins'),
                           'ends': item.get('ends'),
                           'desc': item.get('desc'),
                           'image_url': item.get('image_url'),
                           'name': item.get('name'),
                           'sale_json_url': item.get('sale_json_url'),
                           'sale_key': item.get('sale_key'),
                           'sale_url': item.get('sale_url'),
                           'store': item.get('store'),
                           'scan_date': time.strftime('%Y-%m-%d', time.localtime(time.time())),
                           'scan_time': int(time.time())}
            self.shop_db['flash_sales'].update_one(
                {'from_site': sale_detail['from_site'], 'sale_key': sale_detail['sale_key']},
                {'$set': sale_detail},
                upsert=True
            )

        return item

    def handle_single_item_done(self, item):
        if os.environ.get('is_single_item'):
            is_single_item = (os.environ.get('is_single_item') != 'False')
        else:
            is_single_item = False

        if is_single_item:

            logging.warning('finish single item')
            scan_show_product_id = str(item.get('show_product_id'))

            os.environ['is_base_item_regular_end'] = 'True'
            os.environ['scan_show_product_id'] = scan_show_product_id

            need_notify_redis = (os.environ.get('item_update_notify_redis', 'False') == 'True')
            if need_notify_redis:

                # if os.environ.get('single_item_mode') == 'realtime' and os.environ.get('single_item_realtime_url'):
                #     if not scan_show_product_id:
                #         self.set_md5url_redis_status('goods', item.get('from_site'), 'failed')
                #         self.set_md5url_redis_status('goodscolors', item.get('from_site'), 'failed')

                if os.environ.get('single_item_show_product_id'):
                    show_product_id = str(os.environ.get('single_item_show_product_id'))

                    #                     if scan_show_product_id == show_product_id or item.get('from_site') == 'fgilt':
                    if scan_show_product_id == show_product_id:
                        print 'notify'
                        '''do nothing'''
                        self.item_redis_connection.set('shiji_shop_crawl:goods:' + str(item.get('from_site')) + ':' + str(item.get('show_product_id')), 'done')
                        print 'notify success'

    def get_item_params(self, item_detail, item_keys):

        result_item = {}

        item_detail_keys = item_detail.keys()

        for key in item_keys:
            if key in item_detail_keys:
                result_item[key] = item_detail[key]

        result_item['scan_date'] = item_detail['scan_date']
        result_item['scan_time'] = item_detail['scan_time']

        if 'version' in item_detail.keys():
            result_item['version'] = item_detail['version']

        return result_item

    def get_item_params_ignore_keys(self, item_detail, ignore_keys):

        result_item = {}

        item_detail_keys = item_detail.keys()

        for key in item_detail_keys:
            result_item[key] = item_detail[key]

        for ignore_key in ignore_keys:
            if ignore_key in result_item.keys():
                del result_item[ignore_key]

        return result_item

    def update_sale_show_product_ids(self, item_detail, sale_key):
        sale = self.shop_db['flash_sales'].find_one({'from_site': item_detail['from_site'], 'sale_key' : sale_key})
        if sale:
            if 'show_product_ids' in sale.keys():
                if item_detail['show_product_id'] not in sale['show_product_ids']:
                    sale['show_product_ids'].append(item_detail['show_product_id'])
            else:
                show_product_ids = [item_detail['show_product_id']]
                sale['show_product_ids'] = show_product_ids

            sale['scan_date'] = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            sale['scan_time'] = int(time.time())
            self.shop_db['flash_sales'].update_one(
                {'from_site': item_detail['from_site'], 'sale_key': sale_key},
                {'$set': sale},
            )
        else:
            logging.error(sale_key + ' not exists')

    def set_md5url_redis_status(self, type, from_site, status):
        make_md5 = hashlib.md5()
        if os.environ.get('single_item_realtime_url'):
            make_md5.update(quote(os.environ.get('single_item_realtime_url'), safe=''))
            url_md5 = make_md5.hexdigest()
            self.item_redis_connection.hset(
                'shiji_shop_single_realtime:url:' + type,  str(from_site) + ':' + url_md5, status)

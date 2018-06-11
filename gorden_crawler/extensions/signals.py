#-*-coding:utf-8-*-
"""
Send signals to Sentry

Use SENTRY_DSN setting to enable sending information
"""

import hashlib
import logging
import os
import re
import time
from urllib import quote

import redis
from pymongo import MongoClient
from pymongo.mongo_replica_set_client import MongoReplicaSetClient
from pymongo.read_preferences import ReadPreference
from scrapy import signals

from ..bee_queue.client import BeeQueueClient
from ..sizeregex.sizetransform import Batchtransform


def not_set(string):
    """ Check if a string is None or ''
    :returns: bool - True if the string is empty
    """
    if string is None:
        return True
    elif string == '':
        return True
    return False


class Signals(object):

    is_base_item_regular_end = False
    is_single_item = False
    is_header_200 = False
    is_header_404 = False
    scan_show_product_id = ''

    # Default options
    config = {
        'item_notify_redis_host': 'localhost',
        'item_notify_redis_port': '6379',
        'shop_uri': 'mongodb://localhost:27017',
        'fsync': False,
        'write_concern': 0,
        'shop_database': 'shiji_shop',
        'shop_replica_set': None,
        'size_transform_queue_redis_host': 'localhost',
        'size_transform_queue_redis_port': '6379',
    }

    def __init__(self, is_single_item=False, settings=None, **kwargs):

        self.settings = settings
        self.configure()

        if self.config['shop_replica_set'] is not None:
            shop_connection = MongoReplicaSetClient(
                self.config['shop_uri'],
                replicaSet=self.config['shop_replica_set'],
                w=self.config['write_concern'],
                fsync=self.config['fsync'],
                read_preference=ReadPreference.PRIMARY_PREFERRED)
        else:
            # Connecting to a stand alone MongoDB
            shop_connection = MongoClient(
                self.config['shop_uri'],
                fsync=self.config['fsync'],
                read_preference=ReadPreference.PRIMARY)

        self.shop_db = shop_connection[self.config['shop_database']]

    def configure(self):

        # Set all regular options
        options = [
            ('item_notify_redis_host', 'ITEM_NOTIFY_REDIS_HOST'),
            ('item_notify_redis_port', 'ITEM_NOTIFY_REDIS_PORT'),
            ('item_notify_redis_password', 'ITEM_NOTIFY_REDIS_PASSWORD'),
            ('shop_uri', 'SHOP_MONGODB_SERVER'),
            ('fsync', 'MONGODB_FSYNC'),
            ('write_concern', 'MONGODB_REPLICA_SET_W'),
            ('shop_database', 'SHOP_MONGODB_DB'),
            ('shop_replica_set', 'SHOP_MONGODB_REPLICA_SET'),
            ('size_transform_queue_redis_host', 'SIZE_TRANSFORM_QUEUE_REDIS_HOST'),
            ('size_transform_queue_redis_port', 'SIZE_TRANSFORM_QUEUE_REDIS_PORT'),
            ('size_transform_queue_redis_password', 'SIZE_TRANSFORM_QUEUE_REDIS_PASSWORD'),
        ]

        for key, setting in options:
            if not not_set(self.settings[setting]):
                self.config[key] = self.settings[setting]

    @classmethod
    def from_crawler(cls, crawler, client=None, dsn=None):

        settings = crawler.settings

        o = cls(settings=settings)

        #crawler.signals.connect(o.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.response_received, signal=signals.response_received)
        crawler.signals.connect(o.response_downloaded, signal=signals.response_downloaded)

        return o

    def response_downloaded(self, response, request, spider):
        if self.is_single_item:
            if response.status == 404:
                self.is_header_404 = True

    def response_received(self, response, request, spider):
        if self.is_single_item:
            print 'received success'
            if response.status == 200:
                self.is_header_200 = True
                logging.warning('header is 200')
            elif response.status == 404:
                self.is_header_404 = True
            else:
                logging.warning('header is ' + str(response.status))

    def spider_opened(self, spider, signal=None, sender=None, *args, **kwargs):
        if os.environ.get('is_single_item'):
            is_single_item = (os.environ.get('is_single_item') != 'False')
        else:
            is_single_item = False

        self.is_single_item = is_single_item

        '''item set'''
        self.need_notify_redis = (os.environ.get('item_update_notify_redis', 'False') == 'True')

        self.need_size_transform = (os.environ.get('need_size_transform', 'False') == 'True')

        if self.need_notify_redis or self.need_size_transform:
            if 'item_notify_redis_password' in self.config.keys():
                self.item_redis_connection = redis.Redis(host=self.config['item_notify_redis_host'], port=self.config['item_notify_redis_port'], password=self.config['item_notify_redis_password'])
            else:
                self.item_redis_connection = redis.Redis(host=self.config['item_notify_redis_host'], port=self.config['item_notify_redis_port'])

        # elif self.need_size_transform:
        #     if 'item_notify_redis_password' in self.config.keys():
        #         self.item_redis_connection = redis.Redis(host=self.config['item_notify_redis_host'], port=self.config['item_notify_redis_port'], password=self.config['item_notify_redis_password'])
        #     else:
        #         self.item_redis_connection = redis.Redis(host=self.config['item_notify_redis_host'], port=self.config['item_notify_redis_port'])

            """need_transform_flag:
                1 处理尺码尚未处理完成
                2 处理尺码且已完成"""
            if self.need_size_transform and (not self.is_single_item) and self.settings['SIZE_TRANSFORM_LIST'] and (spider.name in self.settings['SIZE_TRANSFORM_LIST']):
                self.item_redis_connection.set('size_transform:need_transform_flag:' + spider.name , 1)

        # 实时单个爬虫
        if self.is_single_item and self.need_notify_redis:
            if os.environ.get('single_item_mode') == 'realtime' and os.environ.get('single_item_realtime_url'):
                if re.findall('item_', spider.name):
                    site = re.sub('item_', '', spider.name)
                else:
                    site = spider.name
                make_MD5 = hashlib.md5()
                make_MD5.update(quote(os.environ.get('single_item_realtime_url'), safe=''))
                url_md5 = make_MD5.hexdigest()
                self.item_redis_connection.hset('shiji_shop_single_realtime:url:goods', str(site) + ':' + url_md5, 'start')
                self.item_redis_connection.hset('shiji_shop_single_realtime:url:goodscolors', str(site) + ':' + url_md5, 'start')

    def spider_closed(self, spider, reason, signal=None, sender=None, *args, **kwargs):
        if self.is_single_item and self.need_notify_redis:
            logging.warning('spider close')
            logging.warning(self.is_header_404)
            mode = os.environ.get('single_item_mode', None)
            if mode == 'realtime':
                if re.findall('item_', spider.name):
                    site = re.sub('item_', '', spider.name)
                else:
                    site = spider.name
                make_MD5 = hashlib.md5()
                make_MD5.update(quote(os.environ.get('single_item_realtime_url'), safe=''))
                url_md5 = make_MD5.hexdigest()
            '''单个爬虫更新全量商品（测试使用）'''
            if self.settings['SIZE_TRANSFORM_TEST'] and (self.settings['SIZE_TRANSFORM_TEST'] == 4 or self.settings['SIZE_TRANSFORM_TEST'] == 2):
                Batchtransform().batchtransform(spider.name, self.shop_db, self.settings['SIZE_TRANSFORM_LIST'], self.settings['SIZE_TRANSFORM_TEST'])

            if (os.environ.get('single_item_from_site') and os.environ.get('single_item_show_product_id')) or (mode == 'realtime'):
                from_site = str(os.environ.get('single_item_from_site'))
                show_product_id = str(os.environ.get('single_item_show_product_id'))

                is_base_item_regular_end = (os.environ.get('is_base_item_regular_end', 'False') == 'True')
                scan_show_product_id = os.environ.get('scan_show_product_id', '')

                if self.is_header_404:
                    if mode == 'realtime':
                        self.item_redis_connection.hset('shiji_shop_single_realtime:url:goods', str(site) + ':' + url_md5, 'failed')
                        self.item_redis_connection.hset('shiji_shop_single_realtime:url:goodscolors', str(site) + ':' + url_md5, 'failed')
                    else:
                        item_mongo = self.shop_db['goods'].find_one({'from_site': from_site, 'show_product_id': show_product_id})
                        if item_mongo:
                            self.shop_db['goods'].update_many(
                                {'from_site': from_site, 'show_product_id': show_product_id},
                                {'$set': {'status': 1, 'leave_time': int(time.time())}}
                            )
                        else:
                            pass

                        self.item_redis_connection.set('shiji_shop_crawl:goods:' + from_site + ':' + show_product_id, 'failed')
                        logging.warning('notify failed')
                        print 'notify failed'
                else:
                    if not self.is_header_200:
                        if not self.is_header_404:
                            if mode == 'realtime':
                                self.item_redis_connection.hset('shiji_shop_single_realtime:url:goods', str(site) + ':' + url_md5, 'failed')
                                self.item_redis_connection.hset('shiji_shop_single_realtime:url:goodscolors', str(site) + ':' + url_md5, 'failed')
                            else:
                                self.item_redis_connection.set('shiji_shop_crawl:goods:' + from_site + ':' + show_product_id, 'done')
                                logging.warning('notify not 200')

                    elif self.is_header_200 and mode == 'realtime' and show_product_id == 'None' and len(scan_show_product_id) == 0  :
                        self.item_redis_connection.hset('shiji_shop_single_realtime:url:goods', str(site) + ':' + url_md5, 'failed')
                        self.item_redis_connection.hset('shiji_shop_single_realtime:url:goodscolors', str(site) + ':' + url_md5, 'failed')

                    elif self.is_header_200 and (not is_base_item_regular_end or (len(scan_show_product_id) > 0 and scan_show_product_id != show_product_id)):
                        if len(scan_show_product_id) > 0:
                            logging.warning('scan product id: ' + scan_show_product_id)

                        logging.warning('params show product id: ' + show_product_id)
                        logging.warning(is_base_item_regular_end)

    #                     if is_base_item_regular_end and from_site == 'fgilt':
    #                         pass
    #                     else:
                        logging.warning('notify')
                        print 'notify'
                        '''do mongo handle'''

                        item_mongo = self.shop_db['goods'].find_one({'from_site': from_site, 'show_product_id': show_product_id})
                        if item_mongo:
                            self.shop_db['goods'].update_many(
                                {'from_site': from_site, 'show_product_id': show_product_id},
                                {'$set': {'status': 1, 'leave_time': int(time.time())}}
                            )
                        else:
                            pass

                        self.item_redis_connection.set('shiji_shop_crawl:goods:' + from_site + ':' + show_product_id, 'failed')
                        logging.warning('notify failed')
                        print 'notify failed'

            # elif os.environ.get('single_item_mode') == 'realtime' and os.environ.get('single_item_realtime_url'):





        elif self.need_size_transform:
            '''批量爬虫结束后处理尺码'''
            if self.settings['SIZE_TRANSFORM_TEST']:
                '''测试使用'''
                testFlag = self.settings['SIZE_TRANSFORM_TEST']
                if testFlag == 1:
                    Batchtransform().batchtransform(spider.name, self.shop_db, self.settings['SIZE_TRANSFORM_LIST'], testFlag)
                elif testFlag == 0:
                    pass
            elif str(os.environ.get('main_process')) == 'True':
                '''生产环境使用'''
                if 'size_transform_queue_redis_password' in self.config.keys():
                    self.size_transform_queue = BeeQueueClient('bq:size_transform:', host=self.config['size_transform_queue_redis_host'], port=self.config['size_transform_queue_redis_port'], password=self.config['size_transform_queue_redis_password'])
                else:
                    self.size_transform_queue = BeeQueueClient('bq:size_transform:', host=self.config['size_transform_queue_redis_host'], port=self.config['size_transform_queue_redis_port'])
                if str(os.environ.get('manully_upd_size')) == 'True':
                    SIZE_TRANSFORM_LIST = [spider.name]
                else:
                    SIZE_TRANSFORM_LIST = self.settings['SIZE_TRANSFORM_LIST']
                if SIZE_TRANSFORM_LIST:
                    Batchtransform().batchtransform(spider.name, self.shop_db, SIZE_TRANSFORM_LIST, self.size_transform_queue)
                if self.settings['SIZE_TRANSFORM_LIST'] and spider.name in self.settings['SIZE_TRANSFORM_LIST']:
                    self.item_redis_connection.set('size_transform:need_transform_flag:' + spider.name , 2)

    def item_scraped(self, item, response, spider, signal=None, sender=None, *args, **kwargs):
        if self.is_single_item:
            item_type = item.get('type')
            if item_type == 'base':
                self.is_base_item_regular_end = True

                self.scan_show_product_id = str(item.get('show_product_id'))

                if self.need_notify_redis:

                    if os.environ.get('single_item_show_product_id'):
                        show_product_id = str(os.environ.get('single_item_show_product_id'))

                        if self.scan_show_product_id == show_product_id:
                            print 'notify'
                            '''do nothing'''
                            self.item_redis_connection.set('shiji_shop_crawl:goods:' + str(item.get('from_site')) + ':' + str(item.get('show_product_id')), 'done')
                            print 'notify success'

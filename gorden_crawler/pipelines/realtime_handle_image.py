from ..bee_queue.client import BeeQueueClient
from ..bee_queue.bee_queue import Job

import redis
import os


class RealtimeHandleImage(object):
    config = {}

    def configure(self):
        self.config = {
            'realtime_image_handle_queue_redis_host': self.settings['REALTIME_IMAGE_HANDLE_QUEUE_REDIS_HOST'],
            'realtime_image_handle_queue_redis_port': self.settings['REALTIME_IMAGE_HANDLE_QUEUE_REDIS_PORT'],
            'realtime_image_handle_queue_redis_password': self.settings['REALTIME_IMAGE_HANDLE_QUEUE_REDIS_PASSWORD'],

            'item_notify_redis_host': self.settings['ITEM_NOTIFY_REDIS_HOST'],
            'item_notify_redis_port': self.settings['ITEM_NOTIFY_REDIS_PORT'],
            'item_notify_redis_password': self.settings['ITEM_NOTIFY_REDIS_PASSWORD']
        }

    def open_spider(self, spider):
        self.settings = spider.settings
        self.configure()
        if 'realtime_image_handle_queue_redis_password' in self.config.keys():
            self.realtime_image_handle_queue = BeeQueueClient("bq:realtime_handle_image:", host=self.config['realtime_image_handle_queue_redis_host'], port=self.config['realtime_image_handle_queue_redis_port'], password=self.config['realtime_image_handle_queue_redis_password'])
        else:
            self.realtime_image_handle_queue = BeeQueueClient("bq:realtime_handle_image:", host=self.config['realtime_image_handle_queue_redis_host'], port=self.config['realtime_image_handle_queue_redis_port'])

        if 'item_notify_redis_password' in self.config.keys():
            self.item_redis_connection = redis.Redis(host=self.config['item_notify_redis_host'], port=self.config['item_notify_redis_port'], password=self.config['item_notify_redis_password'])
        else:
            self.item_redis_connection = redis.Redis(host=self.config['item_notify_redis_host'], port=self.config['item_notify_redis_port'])

    def process_item(self, item, spider):
        for special_spider in self.settings['SPECIAL_SPIDER_LIST']:
            spider_name = spider.name
            if special_spider in spider_name:
                item_type = item.get('type')
                data = {}
                if item_type == 'color':
                    data['type'] = 'c'
                    data['from_site'] = item.get('from_site')
                    data['show_product_id'] = item.get('show_product_id')
                    if item.get('name'):
                        color_flag = "".join(item.get('name').split()).lower()
                        data['name'] = color_flag
                    self.push_to_realtime_image_queue(data, spider_name)
                elif item_type == 'base':
                    self.item_redis_connection.sadd('available:brand:artificial', item.get('brand'))
                    data['type'] = 'i'
                    data['from_site'] = item.get('from_site')
                    data['show_product_id'] = item.get('show_product_id')
                    self.push_to_realtime_image_queue(data, spider_name)
                break
        return item

    def push_to_realtime_image_queue(self, data, spider_name):
        if data['type'] == 'c':
            data = {"t": "c", 'site': data['from_site'], 'p_id': data['show_product_id'], 'c_name': data['name'], 'worker_type': 'json'}
        elif data['type'] == 'i':
            data = {"t": "i", 'site': data['from_site'], 'p_id': data['show_product_id'], 'worker_type': 'json'}

        for special_spider in self.settings['SPECIAL_SPIDER_LIST']:
            if spider_name in special_spider:
                self.realtime_image_handle_queue.pushJob(Job(data, options={"timeout": 10000, "retries": 2}))
                break

# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from ..items import BaseItem, ImageItem, SkuItem, Color
import scrapy
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from random import random
from urllib import quote
import re
import execjs
import json
import base64
import logging
from ..spiders.shiji_base import ItemSpider
from scrapy.utils.project import get_project_settings
from redis import Redis

class ItemVictoriassecretSpider(ItemSpider):
    name = "item_victoriassecret"
    allowed_domains = ["victoriassecret.com"]

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        'EXTENSIONS': {
            'gorden_crawler.extensions.signals.Signals': None,
        },
        'ITEM_PIPELINES': {
            'gorden_crawler.pipelines.mongodb.SingleMongodbPipeline': None,
            'gorden_crawler.pipelines.realtime_handle_image.RealtimeHandleImage': None
        }
    }

    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''

    start_urls = (
    )
    
    base_url = "https://www.victoriassecret.com/"

    gender = 'women'

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

    '''具体的解析规则'''
    def parse(self, response):
        
        item = {'type': 'base',
                'from_site': 'victoriassecret',
                'url': response.url}
        item = json.dumps(item)
        redis_conn = self.get_redis_connection()
        redis_conn.lpush('js_crawler_queue', self.name + ':' + base64.b64encode(response.url) + ':' + base64.b64encode(item))
        logging.warning('header: ' + str(response.status))
        return

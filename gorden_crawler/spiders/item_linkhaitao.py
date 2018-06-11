# -*- coding: utf-8 -*-
from ..items import BaseItem, ImageItem, SkuItem, Color
import os
from ..spiders.shiji_base import ItemSpider
from ..spiders.linkhaitao import LinkhaitaoSpider

class ItemLinkhaitaoSpider(ItemSpider):
    name = "item_linkhaitao"
    start_urls = []
    editor_flag = None

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 10,

        'ITEM_PIPELINES': {
            'gorden_crawler.pipelines.mongodb.SingleMongodbPipeline': 303,
            'gorden_crawler.pipelines.realtime_handle_image.RealtimeHandleImage': 305,
        }
    }

    '''具体的解析规则'''
    def parse(self, response):
        item = BaseItem()
        item['type'] = 'base'

        return LinkhaitaoSpider().handle_parse_item(response, item)


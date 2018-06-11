# -*- coding: utf-8 -*-
from ..items import BaseItem, ImageItem, SkuItem, Color
from ..spiders.shiji_base import ItemSpider
from ..spiders.shangshangsp import ShangshangspSpider

from scrapy import Request

import os


class ItemShangshangspSpider(ItemSpider):
    name = "item_shangshangsp"
    start_urls = []
    editor_flag = None

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 10,
        'COOKIES_ENABLED': True,

        'ITEM_PIPELINES': {
            'gorden_crawler.pipelines.mongodb.SingleMongodbPipeline': 303,
            'gorden_crawler.pipelines.realtime_handle_image.RealtimeHandleImage': 305,
        }
    }

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, cookies={'_u_':'nnaeri5gmdkcqhmypw7gsf444y3tafhppas7mcd5hmgxiq2zrzgte2njagxu6i7bb5ncb3emuhlxyjnqdfudj3zcv2t45tcyegpeyprd3uiwp5op3xcqr7gan4f22fqdjj6pfhtrrsgycelkcyygz7x2wwmlbe5i4izhjziqdtdxmmniwfclzv6knje3eajmqkco7422tdsnm', 'cookiecounts':1, '_i_':'rr5oyxeljh7iktqcndwjvhcaz4kq2ogfeb6gphjizgvt3mehvicok6nfftgezwiqxxoq3x6poypl6'})

    '''具体的解析规则'''
    def parse(self, response):
        item = BaseItem()
        item['type'] = 'base'

        return ShangshangspSpider().handle_parse_item(response, item)


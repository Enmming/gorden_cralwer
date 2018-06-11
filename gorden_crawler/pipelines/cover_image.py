#!/usr/bin/python
#-*-coding:utf-8-*-

import os
from scrapy import log
from scrapy.http import Request
from scrapy.contrib.pipeline.images import ImagesPipeline
from gorden_crawler.utils.select_result import list_first_item

class CoverImage(ImagesPipeline):
    """
        this is for download the  image and then complete the 
        covor_image_url field to the picture's path in the file system.
    """
    def __init__(self, store_uri, download_func=None):
        self.images_store = store_uri
        super(CoverImage,self).__init__(store_uri, download_func=None)

    def get_media_requests(self, item, info):
        if item.get('covor_image_url'):
            yield Request(item['covor_image_url'])

    def item_completed(self, results, item, info):
        if self.LOG_FAILED_RESULTS:
            msg = '%s found errors proessing %s' % (self.__class__.__name__, item)
            for ok, value in results:
                if not ok:
                    log.err(value, msg, spider=info.spider)

        image_paths = [x['path'] for ok, x in results if ok]
        image_path = list_first_item(image_paths)
        item['covor_image_url'] = os.path.join(os.path.abspath(self.images_store),image_path) if image_path else ""

        return item

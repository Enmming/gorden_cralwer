# -*- coding: utf-8 -*-
from scrapy import Spider
import os

class SizeSpider(Spider):
    name = 'size'
    
    start_urls = []
    def __init__(self, from_site=None, *args, **kwargs):
        if from_site:
            self.name = from_site
            os.environ['main_process'] = 'True'
            os.environ['need_size_transform'] = 'True'
            os.environ['manully_upd_size'] = 'True'

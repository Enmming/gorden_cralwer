# -*- coding: utf-8 -*-
import base64
import json
import logging
import re

import execjs
from redis import Redis
from scrapy import Request
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

from ..items import BaseItem, ImageItem, Color
from ..spiders.shiji_base import BaseSpider


class AmazonUsaUkSpider(BaseSpider):
    name = "amazon_usa_uk"
    allowed_domains = ["amazon.cn"]

    #正式运行的时候，start_urls为空，通过redis来喂养爬虫

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,

        'DOWNLOADER_MIDDLEWARES': {
            # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyHttpsRandomMiddleware': 100,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        },

        'ITEM_PIPELINES': {
            'gorden_crawler.pipelines.mongodb.SingleMongodbPipeline': 303,
            'gorden_crawler.pipelines.realtime_handle_image.RealtimeHandleImage': 305,
        }
    }

    base_url = 'https://www.amazon.cn'

    start_urls = [
        # 美国
        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A2029189051%2Cn%3A%212029190051%2Cn%3A2112003051&bbn=1841388071&ie=UTF8&qid=1490759058&rnid=1841388071',

        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A2029189051%2Cn%3A%212029190051%2Cn%3A2112046051&bbn=1841388071&ie=UTF8&qid=1490760164&rnid=1841388071',

        'https://www.amazon.cn/s/ref=sr_nr_n_2?fst=as%3Aoff&rh=n%3A2029189051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212029190051%2Cn%3A162854071&bbn=2029190051&ie=UTF8&qid=1490760278&rnid=2029190051',
        'https://www.amazon.cn/s/ref=sr_nr_n_3?fst=as%3Aoff&rh=n%3A2029189051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212029190051%2Cn%3A162853071&bbn=2029190051&ie=UTF8&qid=1490760278&rnid=2029190051',

        'https://www.amazon.cn/s/ref=sr_nr_n_4?fst=as%3Aoff&rh=n%3A2029189051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212029190051%2Cn%3A162416071&bbn=2029190051&ie=UTF8&qid=1490760433&rnid=2029190051',

        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152154051&bbn=2016157051&ie=UTF8&qid=1490769757&rnid=2016157051',

        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152155051&bbn=2016157051&ie=UTF8&qid=1490769757&rnid=2016157051',

        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2152156051&bbn=2152158051&ie=UTF8&qid=1490769925&rnid=2152158051',

        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2152157051&bbn=2152158051&ie=UTF8&qid=1490769925&rnid=2152158051',

        'https://www.amazon.cn/s/ref=sr_nr_n_2?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2153743051&bbn=2152158051&ie=UTF8&qid=1490769925&rnid=2152158051',

        'https://www.amazon.cn/s/ref=sr_nr_n_3?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2153777051&bbn=2152158051&ie=UTF8&qid=1490769925&rnid=2152158051',

        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A2016156051%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A100275071%2Cn%3A100276071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490779208&rnid=1841388071',

        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A2016156051%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A100275071%2Cn%3A100277071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490779291&rnid=1841388071',
        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A2016156051%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A865366051&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490779335&rnid=1841388071',

        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_0?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323884071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490776709&rnid=1323883071',

        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_1?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323885071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490776735&rnid=1323883071',
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_3?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323887071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490776735&rnid=1323883071',
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_4?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323888071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490776735&rnid=1323883071',

        # 英国
        'https://www.amazon.cn/s/ref=sr_ex_n_1?rh=n%3A1841389071%2Cn%3A2029189051%2Cn%3A%212029190051%2Cn%3A2112003051&bbn=1841389071&ie=UTF8&qid=1490781619',

        'https://www.amazon.cn/s/ref=sr_ex_n_1?rh=n%3A1841389071%2Cn%3A2029189051%2Cn%3A%212029190051%2Cn%3A2112046051&bbn=1841389071&ie=UTF8&qid=1490781643',

        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A2029189051%2Cn%3A%212112205051%2Cn%3A%212118806051%2Cn%3A%212118815051%2Cn%3A167097071%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A162853071&bbn=167097071&ie=UTF8&qid=1490781613&rnid=167097071',

        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A2029189051%2Cn%3A%212112205051%2Cn%3A%212118806051%2Cn%3A%212118815051%2Cn%3A167097071%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A162854071&bbn=167097071&ie=UTF8&qid=1490781613&rnid=167097071',

        'https://www.amazon.cn/s/ref=sr_nr_n_2?fst=as%3Aoff&rh=n%3A2029189051%2Cn%3A%212112205051%2Cn%3A%212118806051%2Cn%3A%212118815051%2Cn%3A167097071%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A162416071&bbn=167097071&ie=UTF8&qid=1490781613&rnid=167097071',

        'https://www.amazon.cn/s/ref=sr_nr_n_0?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152154051&bbn=2016157051&ie=UTF8&qid=1490781806&rnid=2016157051',

        'https://www.amazon.cn/s/ref=sr_nr_n_1?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152155051&bbn=2016157051&ie=UTF8&qid=1490781837&rnid=2016157051',

        'https://www.amazon.cn/s/ref=sr_nr_n_0?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2152156051&bbn=2152158051&ie=UTF8&qid=1490781855&rnid=2152158051',

        'https://www.amazon.cn/s/ref=sr_nr_n_1?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2152157051&bbn=2152158051&ie=UTF8&qid=1490782004&rnid=2152158051',

        'https://www.amazon.cn/s/ref=sr_nr_n_2?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2153743051&bbn=2152158051&ie=UTF8&qid=1490781855&rnid=2152158051',

        'https://www.amazon.cn/s/ref=sr_nr_n_3?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2153777051&bbn=2152158051&ie=UTF8&qid=1490781855&rnid=2152158051',
        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A100275071%2Cn%3A100276071&bbn=100275071&ie=UTF8&qid=1490782039&rnid=100275071',
        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A100275071%2Cn%3A100277071&bbn=100275071&ie=UTF8&qid=1490782039&rnid=100275071',
        'https://www.amazon.cn/s/ref=sr_nr_n_2?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A100275071%2Cn%3A100750071&bbn=100275071&ie=UTF8&qid=1490782039&rnid=100275071',
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_0?fst=as%3Aoff&rh=n%3A1841389071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323884071&bbn=1841389071&sort=popularity-rank&ie=UTF8&qid=1490782115&rnid=1323883071',
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_1?fst=as%3Aoff&rh=n%3A1841389071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323885071&bbn=1841389071&sort=popularity-rank&ie=UTF8&qid=1490782115&rnid=1323883071',
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_2?fst=as%3Aoff&rh=n%3A1841389071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323887071&bbn=1841389071&sort=popularity-rank&ie=UTF8&qid=1490782152&rnid=1323883071',
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_3?fst=as%3Aoff&rh=n%3A1841389071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323888071&bbn=1841389071&sort=popularity-rank&ie=UTF8&qid=1490782152&rnid=1323883071',
        ]

    start_urls_gender_product_type_dict = {
        # 美国
        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A2029189051%2Cn%3A%212029190051%2Cn%3A2112003051&bbn=1841388071&ie=UTF8&qid=1490759058&rnid=1841388071': {'gender': 'women', 'product_type': 'shoes'},
        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A2029189051%2Cn%3A%212029190051%2Cn%3A2112046051&bbn=1841388071&ie=UTF8&qid=1490760164&rnid=1841388071': {'gender': 'men', 'product_type': 'shoes'},
        'https://www.amazon.cn/s/ref=sr_nr_n_2?fst=as%3Aoff&rh=n%3A2029189051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212029190051%2Cn%3A162854071&bbn=2029190051&ie=UTF8&qid=1490760278&rnid=2029190051': {'gender': 'girls', 'product_type': 'shoes'},
        'https://www.amazon.cn/s/ref=sr_nr_n_3?fst=as%3Aoff&rh=n%3A2029189051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212029190051%2Cn%3A162853071&bbn=2029190051&ie=UTF8&qid=1490760278&rnid=2029190051': {'gender': 'boys', 'product_type': 'shoes'},
        'https://www.amazon.cn/s/ref=sr_nr_n_4?fst=as%3Aoff&rh=n%3A2029189051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212029190051%2Cn%3A162416071&bbn=2029190051&ie=UTF8&qid=1490760433&rnid=2029190051': {'gender': 'baby', 'product_type': 'shoes'},
        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152154051&bbn=2016157051&ie=UTF8&qid=1490769757&rnid=2016157051': {'gender': 'women', 'product_type': '女装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152155051&bbn=2016157051&ie=UTF8&qid=1490769757&rnid=2016157051': {'gender': 'men', 'product_type': '男装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2152156051&bbn=2152158051&ie=UTF8&qid=1490769925&rnid=2152158051': {'gender': 'girls', 'product_type': '女童服装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2152157051&bbn=2152158051&ie=UTF8&qid=1490769925&rnid=2152158051': {'gender': 'boys', 'product_type': '男童服装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_2?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2153743051&bbn=2152158051&ie=UTF8&qid=1490769925&rnid=2152158051': {'gender': 'girls', 'product_type': '女婴服装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_3?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA2EDK7H33M5FFG%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2153777051&bbn=2152158051&ie=UTF8&qid=1490769925&rnid=2152158051': {'gender': 'boys', 'product_type': '男婴服装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A2016156051%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A100275071%2Cn%3A100276071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490779208&rnid=1841388071': {'gender':'women', 'product_type': '单肩包、挎包、手包'},
        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A2016156051%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A100275071%2Cn%3A100277071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490779291&rnid=1841388071': {'gender':'men', 'product_type': '单肩包、挎包、手包'},
        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A2016156051%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A865366051&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490779335&rnid=1841388071': {'gender':'unisex', 'product_type': '双肩背包'},
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_0?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323884071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490776709&rnid=1323883071': {'gender': 'men', 'product_type': '腕表'},
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_1?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323885071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490776735&rnid=1323883071': {'gender': 'women', 'product_type': '腕表'},
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_3?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323887071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490776735&rnid=1323883071': {'gender': 'unisex', 'product_type': '腕表'},
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_4?fst=as%3Aoff&rh=n%3A1841388071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323888071&bbn=1841388071&sort=popularity-rank&ie=UTF8&qid=1490776735&rnid=1323883071': {'gender': 'kids-unisex', 'product_type': '腕表'},

        # 英国
        'https://www.amazon.cn/s/ref=sr_ex_n_1?rh=n%3A1841389071%2Cn%3A2029189051%2Cn%3A%212029190051%2Cn%3A2112003051&bbn=1841389071&ie=UTF8&qid=1490781619': {'gender': 'women', 'product_type': 'shoes'},
        'https://www.amazon.cn/s/ref=sr_ex_n_1?rh=n%3A1841389071%2Cn%3A2029189051%2Cn%3A%212029190051%2Cn%3A2112046051&bbn=1841389071&ie=UTF8&qid=1490781643': {'gender': 'men', 'product_type': 'shoes'},
        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A2029189051%2Cn%3A%212112205051%2Cn%3A%212118806051%2Cn%3A%212118815051%2Cn%3A167097071%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A162853071&bbn=167097071&ie=UTF8&qid=1490781613&rnid=167097071': {'gender': 'boys', 'product_type': 'shoes'},
        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A2029189051%2Cn%3A%212112205051%2Cn%3A%212118806051%2Cn%3A%212118815051%2Cn%3A167097071%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A162854071&bbn=167097071&ie=UTF8&qid=1490781613&rnid=167097071': {'gender': 'girls', 'product_type': 'shoes'},
        'https://www.amazon.cn/s/ref=sr_nr_n_2?fst=as%3Aoff&rh=n%3A2029189051%2Cn%3A%212112205051%2Cn%3A%212118806051%2Cn%3A%212118815051%2Cn%3A167097071%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A162416071&bbn=167097071&ie=UTF8&qid=1490781613&rnid=167097071': {'gender': 'baby', 'product_type': 'shoes'},
        'https://www.amazon.cn/s/ref=sr_nr_n_0?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152154051&bbn=2016157051&ie=UTF8&qid=1490781806&rnid=2016157051': {'gender': 'women', 'product_type': '女装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_1?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152155051&bbn=2016157051&ie=UTF8&qid=1490781837&rnid=2016157051': {'gender': 'men', 'product_type': '男装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_0?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2152156051&bbn=2152158051&ie=UTF8&qid=1490781855&rnid=2152158051': {'gender': 'girls', 'product_type': '女童服装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_1?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2152157051&bbn=2152158051&ie=UTF8&qid=1490782004&rnid=2152158051': {'gender': 'boys', 'product_type': '男童服装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_2?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2153743051&bbn=2152158051&ie=UTF8&qid=1490781855&rnid=2152158051': {'gender': 'girls', 'product_type': '女婴服装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_3?srs=1478512071&fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A2152158051%2Cn%3A2153777051&bbn=2152158051&ie=UTF8&qid=1490781855&rnid=2152158051': {'gender': 'boys', 'product_type': '男婴服装'},
        'https://www.amazon.cn/s/ref=sr_nr_n_0?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A100275071%2Cn%3A100276071&bbn=100275071&ie=UTF8&qid=1490782039&rnid=100275071': {'gender':'women', 'product_type': '单肩包、挎包、手包'},
        'https://www.amazon.cn/s/ref=sr_nr_n_1?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A100275071%2Cn%3A100277071&bbn=100275071&ie=UTF8&qid=1490782039&rnid=100275071': {'gender':'men', 'product_type': '单肩包、挎包、手包'},
        'https://www.amazon.cn/s/ref=sr_nr_n_2?fst=as%3Aoff&rh=n%3A2016156051%2Cp_6%3AA3TEGLC21NOO5Y%2Cn%3A%212016157051%2Cn%3A865184051%2Cn%3A100275071%2Cn%3A100750071&bbn=100275071&ie=UTF8&qid=1490782039&rnid=100275071': {'gender':'unisex', 'product_type': '双肩背包'},
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_0?fst=as%3Aoff&rh=n%3A1841389071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323884071&bbn=1841389071&sort=popularity-rank&ie=UTF8&qid=1490782115&rnid=1323883071': {'gender': 'men', 'product_type': '腕表'},
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_1?fst=as%3Aoff&rh=n%3A1841389071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323885071&bbn=1841389071&sort=popularity-rank&ie=UTF8&qid=1490782115&rnid=1323883071': {'gender': 'women', 'product_type': '腕表'},
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_2?fst=as%3Aoff&rh=n%3A1841389071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323887071&bbn=1841389071&sort=popularity-rank&ie=UTF8&qid=1490782152&rnid=1323883071': {'gender': 'unisex', 'product_type': '腕表'},
        'https://www.amazon.cn/s/ref=sr_nr_p_n_feature_four_bro_3?fst=as%3Aoff&rh=n%3A1841389071%2Cn%3A1953164051%2Cn%3A%211953165051%2Cn%3A2040033051%2Cp_n_feature_four_browse-bin%3A1323888071&bbn=1841389071&sort=popularity-rank&ie=UTF8&qid=1490782152&rnid=1323883071': {'gender': 'kids-unisex', 'product_type': '腕表'},

    }

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

    # 爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        current_url = response.url
        sel = Selector(response)

        cate_lis = sel.xpath('//div[@class="categoryRefinementsSection"]/ul/li[name(@style)="style"]')
        if len(cate_lis) > 1:
            for cate_li in cate_lis:
                if len(cate_li.xpath('./strong/text()')) > 0:
                    continue
                category = cate_li.xpath('./a/span[1]/text()').extract()[0]
                cate_url = self.base_url + cate_li.xpath('./a/@href').extract()[0]
                gender = self.start_urls_gender_product_type_dict[current_url]['gender']
                product_type = self.start_urls_gender_product_type_dict[current_url]['product_type']
                yield Request(cate_url, callback=self.parse_list, meta={"category":category, "gender":gender, "product_type":product_type})
        elif len(cate_lis) == 1:
            category = cate_lis[0].xpath('./strong/text()').extract()[0]
            gender = self.start_urls_gender_product_type_dict[current_url]['gender']
            product_type = self.start_urls_gender_product_type_dict[current_url]['product_type']
            yield Request(current_url, callback=self.parse_list, meta={"category":category, "gender":gender, "product_type":product_type}, dont_filter=True)

    def parse_list(self, response):
        category = response.meta['category']
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        sel = Selector(response)
        if len(sel.xpath('//div[@class="s-item-container"]')) == 0:
            yield Request(response.url, callback=self.parse_list, meta={"category": category, "gender": gender, "product_type": product_type}, dont_filter=True)
            logging.warning(json.dumps({"url": response.url, "category": category, "gender": gender, "product_type": product_type}))
            return
        product_divs = sel.xpath('//div[@class="s-item-container"]')
        for product_div in product_divs:
            if len(product_div.xpath('./h5')) > 0:
                continue
            item = BaseItem()
            item['from_site'] = 'amazon_usa_uk'
            item['type'] = 'base'
            item['category'] = category
            item['product_type'] = product_type
            item['gender'] = gender
            item['url'] = product_div.xpath('./div[1]//a/@href').extract()[0]
            item['cover'] = product_div.xpath('./div[1]//img[1]/@src').extract()[0]
            item['title'] = product_div.xpath('./div[2]/div[1]/a/@title').extract()[0]
            if len(product_div.xpath('./div[2]/div[2]/span[2]')) > 0:
                item['brand'] = product_div.xpath('./div[2]/div[2]/span[2]').extract()[0]
            else:
                item['brand'] = item['title'].split()[0]

            yield Request(item['url'],callback=self.parse_item,meta={"item":item})

        if len(sel.xpath('//span[@class="pagnRA"]')) > 0:
            next_url = self.base_url + sel.xpath('//span[@class="pagnRA"]/a/@href').extract()[0]
            yield Request(next_url, callback=self.parse_list, meta={"category":category, "gender":gender, "product_type":product_type})

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        if 'Correios.DoNotSend' in response.body:
            sredis_conn = self.get_redis_connection()
            item_dict = {k:v for k, v in item.items()}
            sredis_conn.lpush('amazon_usa_uk_failed', base64.b64encode(response.url) + ':' + base64.b64encode(json.dumps(item_dict)))
            logging.warning('ERROR!!!!' + response.url)
            yield Request(item['url'], callback=self.parse_item, meta={"item": item})
            return

        show_product_id_str = re.search('parentAsin\=(.+?)\&', response.body)
        if show_product_id_str:
            show_product_id = show_product_id_str.group(1)
        else:
            show_product_id = re.search('\/dp\/(.+?)\/', response.url).group(1)
        item['show_product_id'] = show_product_id

        brand = sel.xpath('//a[@id="brand"]/text()')
        if len(brand) > 0:
            item['brand'] = brand.extract()[0].strip()

        desc = sel.xpath('//div[@id="feature-bullets"]//li').extract()
        desc += sel.xpath('//div[@id="detail_bullets_id"]/table').extract()
        for s in [' ', '\t']:
            item['desc'] = ''.join(''.join(desc).split(s))
        if '<script' in item['desc']:
            item['desc'] = re.sub('(<script[\s\S]+?</script>)', '', item['desc'])
        color_details_str_1 = re.search('data\[\"colorImages\"\]\s+=\s+(.+?};)', response.body)
        colors = []
        if color_details_str_1 and len(color_details_str_1.group(1)) > 3:
            color_details_str_1 = color_details_str_1.group(1)
            context = execjs.compile('''
                var color = %s
                function getColorDetail(){
                    return color;
                }
            ''' % color_details_str_1)
            color_details = context.call('getColorDetail')

            for color_name, image_details in color_details.items():
                colorItem = Color()
                images = []
                for image_detail in image_details:
                    imageItem = ImageItem()
                    if 'hiRes' not in image_detail:
                        imageItem['image'] = image_detail['large'][:-4] + '._UL1500_.jpg'
                    else:
                        imageItem['image'] = image_detail['hiRes']
                    imageItem['thumbnail'] = image_detail['large']
                    images.append(imageItem)
                colorItem['images'] = images
                colorItem['type'] = 'color'
                colorItem['from_site'] = item['from_site']
                colorItem['show_product_id'] = item['show_product_id']
                colorItem['name'] = color_name
                colors.append(color_name)
                colorItem['cover'] = image_details[0]['thumb']
                if 'cover' not in item:
                    item['cover'] = image_details[0]['thumb']
                yield colorItem

        else:
            color_details_str_1 = re.search('ImageBlockATF\"\,\s+function\(A\)\{([\s\S]+?\};)', response.body).group(1)
            context = execjs.compile('''
                %s
                function getColorDetail(){
                    return data;
                }
            ''' % color_details_str_1)
            color_details = context.call('getColorDetail')

            colorItem = Color()
            images = []
            for image_detail in color_details['colorImages']['initial']:
                imageItem = ImageItem()
                imageItem['image'] = image_detail['hiRes']
                imageItem['thumbnail'] = image_detail['large']
                images.append(imageItem)
            colorItem['images'] = images
            colorItem['type'] = 'color'
            colorItem['from_site'] = item['from_site']
            colorItem['show_product_id'] = item['show_product_id']
            colorItem['name'] = 'One Color'
            colors = ['One Color']
            colorItem['cover'] = color_details['colorImages']['initial'][0]['thumb']
            yield colorItem

        if 'cover' not in item.keys():
            item['cover'] = colorItem['images'][0]['image']
        detail = re.search('\(\'twister\-js\-init\-dpx\-data\'\,\s+function\(\)\s+\{\s+([\s\S]+?\s+};)', response.body)
        # 单个sku情况
        if not detail:
            price = sel.xpath('//span[@id="priceblock_ourprice"]/text()').extract()[0]
            skuItem = {}
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['id'] = item['show_product_id'] + '-sku'
            skuItem['color'] = 'One Color'
            skuItem['size'] = 'One Size'
            skuItem['from_site'] = 'amazon_usa_uk'
            skuItem['list_price'] = price
            skuItem['current_price'] = price
            skuItem['is_outof_stock'] = False
            item['skus'] = [skuItem]
            item['colors'] = colors
            item['sizes'] = ['One Size']
            yield item
        else:
            # 多个sku情况
            detail = detail.group(1)
            context = execjs.compile('''
                %s
                function getDetail(){
                    return dataToReturn;
                }
            ''' % detail)
            goods_detail = context.call('getDetail')
            if 'size_name' in goods_detail['variationValues']:
                sizes = goods_detail['variationValues']['size_name']
            else:
                sizes = ['One Size']
            if 'color_name' in goods_detail['variationValues']:
                colors = goods_detail['variationValues']['color_name']
            else:
                colors = ['One Color']
            item['skus'] = []

            sku_ids = []
            for sku_id, sku_dict in goods_detail['asinVariationValues'].items():
                skuItem = {}
                skuItem['type'] = 'sku'
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['id'] = sku_id
                sku_ids.append(sku_id)
                if 'color_name' in sku_dict:
                    skuItem['color'] = colors[int(sku_dict['color_name'])]
                else:
                    skuItem['color'] = 'One Color'
                if 'size_name' in sku_dict:
                    skuItem['size'] = sizes[int(sku_dict['size_name'])]
                else:
                    skuItem['size'] = 'One Size'
                skuItem['from_site'] = 'amazon_usa_uk'

                skuItem['is_outof_stock'] = False
                item['skus'].append(skuItem)
            item['colors'] = colors
            item['sizes'] = sizes
            sku_url_surfix_str = re.search('immutableURLPrefix\"\:\"(.+?)\"\,', response.body)
            if sku_url_surfix_str:
                sku_url_surfix = sku_url_surfix_str.group(1)
                parse_sku_price_url = self.base_url + sku_url_surfix + "&psc=1&asinList=" + item['skus'][0]['id'] + "&id=" + item['skus'][0]['id']
                parse_sku_price_url_prefix = self.base_url + sku_url_surfix + "&psc=1"
                yield Request(parse_sku_price_url, callback=self.parse_price_ajax, meta={"item":item, "index":0, "parse_sku_price_url_prefix":parse_sku_price_url_prefix})

    def parse_price_ajax(self, response):
        item = response.meta['item']
        index = response.meta['index']
        parse_sku_price_url_prefix = response.meta['parse_sku_price_url_prefix']
        if re.search(r'a-size-medium a-color-price\\\">(.+?)<', response.body):
            price = re.search(r'a-size-medium a-color-price\\\">(.+?)<', response.body).group(1)
        else:
            price = '100'
            item['skus'][index]['is_outof_stock'] = True

        item['skus'][index]['list_price'] = price
        item['skus'][index]['current_price'] = price

        if index + 1 < len(item['skus']):
            index += 1
            parse_sku_price_url = parse_sku_price_url_prefix + "&asinList=" + item['skus'][index]['id'] + "&id=" + item['skus'][index]['id']
            yield Request(parse_sku_price_url, callback=self.parse_price_ajax, meta={"item":item, "index":index, "parse_sku_price_url_prefix":parse_sku_price_url_prefix})
        else:
            yield item

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
from ..spiders.amazon_usa_uk import AmazonUsaUkSpider


class AmazonDiapersSpider(BaseSpider):
    name = "amazon_diapers"
    allowed_domains = ["amazon.com"]

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

    base_url = 'https://www.amazon.com'

    start_urls = [
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_2_1_w?rh=i%3Afashion-baby-girls%2Cn%3A7141123011%2Cn%3A7147444011%2Cn%3A7628012011%2Cn%3A1044512%2Cp_6%3AA910SOE1FKRQR&bbn=7628012011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011',
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_2_2_w?rh=i%3Afashion-girls-clothing%2Cn%3A7141123011%2Cn%3A7147442011%2Cn%3A1040664%2Cp_6%3AA910SOE1FKRQR&bbn=1040664&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011',
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_2_3_w?rh=i%3Afashion-baby-boys%2Cn%3A7141123011%2Cn%3A7147444011%2Cn%3A7628013011%2Cn%3A1044510%2Cp_6%3AA910SOE1FKRQR&bbn=7628013011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011',
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_2_4_w?rh=i%3Afashion-boys-clothing%2Cn%3A7141123011%2Cn%3A7147443011%2Cn%3A1040666%2Cp_6%3AA910SOE1FKRQR&bbn=1040666&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011',
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_3_1_w?rh=i%3Afashion-baby-girls%2Cn%3A7141123011%2Cn%3A7147444011%2Cn%3A7628012011%2Cn%3A7239798011%2Cp_6%3AA910SOE1FKRQR&bbn=7239798011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011',
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_3_2_w?rh=i%3Afashion-girls-shoes%2Cn%3A7141123011%2Cn%3A7147442011%2Cn%3A679217011%2Cp_6%3AA910SOE1FKRQR&bbn=679217011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011',
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_3_3_w?rh=i%3Afashion-baby-boys%2Cn%3A7141123011%2Cn%3A7147444011%2Cn%3A7628013011%2Cn%3A7239799011%2Cp_6%3AA910SOE1FKRQR&bbn=7239799011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011',
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_3_4_w?rh=i%3Afashion-boys-shoes%2Cn%3A7141123011%2Cn%3A7147443011%2Cn%3A679182011%2Cp_6%3AA910SOE1FKRQR&bbn=679182011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011',
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_4_1_w?rh=i%3Ababy-products%2Cn%3A165796011%2Cn%3A%21165797011%2Cn%3A166764011%2Cn%3A166772011%2Cp_6%3AATVPDKIKX0DER%7CA910SOE1FKRQR&bbn=166772011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011'

        ]

    start_urls_gender_product_type_dict = {
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_2_1_w?rh=i%3Afashion-baby-girls%2Cn%3A7141123011%2Cn%3A7147444011%2Cn%3A7628012011%2Cn%3A1044512%2Cp_6%3AA910SOE1FKRQR&bbn=7628012011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011': {},
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_2_2_w?rh=i%3Afashion-girls-clothing%2Cn%3A7141123011%2Cn%3A7147442011%2Cn%3A1040664%2Cp_6%3AA910SOE1FKRQR&bbn=1040664&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011': {},
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_2_3_w?rh=i%3Afashion-baby-boys%2Cn%3A7141123011%2Cn%3A7147444011%2Cn%3A7628013011%2Cn%3A1044510%2Cp_6%3AA910SOE1FKRQR&bbn=7628013011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011': {},
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_2_4_w?rh=i%3Afashion-boys-clothing%2Cn%3A7141123011%2Cn%3A7147443011%2Cn%3A1040666%2Cp_6%3AA910SOE1FKRQR&bbn=1040666&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011': {},
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_3_1_w?rh=i%3Afashion-baby-girls%2Cn%3A7141123011%2Cn%3A7147444011%2Cn%3A7628012011%2Cn%3A7239798011%2Cp_6%3AA910SOE1FKRQR&bbn=7239798011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011': {},
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_3_2_w?rh=i%3Afashion-girls-shoes%2Cn%3A7141123011%2Cn%3A7147442011%2Cn%3A679217011%2Cp_6%3AA910SOE1FKRQR&bbn=679217011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011': {},
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_3_3_w?rh=i%3Afashion-baby-boys%2Cn%3A7141123011%2Cn%3A7147444011%2Cn%3A7628013011%2Cn%3A7239799011%2Cp_6%3AA910SOE1FKRQR&bbn=7239799011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011': {},
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_3_4_w?rh=i%3Afashion-boys-shoes%2Cn%3A7141123011%2Cn%3A7147443011%2Cn%3A679182011%2Cp_6%3AA910SOE1FKRQR&bbn=679182011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011': {},
        'https://www.amazon.com/s/ref=s9_acss_bw_ln_DiapersL_4_1_w?rh=i%3Ababy-products%2Cn%3A165796011%2Cn%3A%21165797011%2Cn%3A166764011%2Cn%3A166772011%2Cp_6%3AATVPDKIKX0DER%7CA910SOE1FKRQR&bbn=166772011&ie=UTF8&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-leftnav&pf_rd_r=BMCF2TA3A2DT9JTG6JSP&pf_rd_t=101&pf_rd_p=0ac7a0ad-c283-408c-96da-ca963f53ce72&pf_rd_i=16575122011': {}
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
        amuu = AmazonUsaUkSpider()
        return amuu.handle_parse_item(response, item)


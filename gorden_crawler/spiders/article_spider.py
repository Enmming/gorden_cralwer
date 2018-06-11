# -*- coding: utf-8 -*-
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from gorden_crawler.spiders.shiji_base import ItemSpider

from scrapy.selector import Selector
from qiniu import Auth
import re
from base64 import urlsafe_b64encode
import requests
import hashlib
import os
from collections import OrderedDict
import logging


class Article_Spider(ItemSpider):
    name = "article_spider"
    allowed_domains = ["qq.com"]

    custom_settings = {
    }

    start_urls = (
    )

    '''具体的解析规则'''

    def parse(self, response):
        if 'article_id' in os.environ.keys():
            article_id = os.environ['article_id']
        else:
            return
        sel = Selector(response)
        article_ps = sel.xpath('//div[@class="rich_media_content "]//p|//div[@class="rich_media_content "]/section')
        if len(article_ps) == 0:
            return
        article_items = OrderedDict()
        article_items['article_id'] = article_id

        bucket_name = 'qnmami-information'
        access_key = "nR4zZ4XaxesEAhPW59BZNtWOMu4aD-pnHcg28iF6",
        secret_key = "uaykXj8wnZwWT3n02XG-keUat-UOUGfbGxHKEgUr"
        q = Auth(access_key, secret_key)

        index = 0
        for article_p in article_ps:
            if len(article_p.xpath('.//img'))>0:
                if ''.join(article_p.xpath(".//text()").extract()):
                    article_items['article_item[' + str(index) + '][text_content]'] = ''.join(article_p.xpath('.//text()').extract())
                    article_items['article_item[' + str(index) + '][type]'] = 1
                    article_items['article_item[' + str(index) + '][id]'] = ''
                    index += 1
                article_items['article_item[' + str(index) + '][type]'] = 2
                article_items['article_item[' + str(index) + '][id]'] = ''
                pic_url = article_p.xpath('.//img/@data-src').extract()
                if len(pic_url) >0:
                    pic_url = pic_url[0]
                else:
                    pic_url = article_p.xpath('.//img/@src').extract()[0]
                m = hashlib.md5()
                m.update(pic_url)
                pic_url_hash = m.hexdigest()
                ff = '/fetch/' + urlsafe_b64encode(pic_url) + '/to/' + urlsafe_b64encode(bucket_name + ':article_' + pic_url_hash)
                token = q.token_of_request('http://iovip.qbox.me' + ff, content_type='application/x-www-form-urlencoded')
                token = ''.join(re.search('\(\'(.+)\',\)(.+)', token).groups())
                authorization = 'QBox ' + token
                headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': authorization}
                req = requests.post('http://iovip.qbox.me' + ff, headers=headers)
                # pic_url_qiniu = 'http://lixian.cdnqiniu01.qnmami.com/' + req.json()['key']
                pic_url_qiniu = 'http://information.cdnqiniu02.qnmami.com/' + req.json()['key']
                article_items['article_item[' + str(index) + '][image_url]'] = pic_url_qiniu
            else:
                if ''.join(article_p.xpath('.//text()').extract()) == '':
                    continue
                article_items['article_item[' + str(index) + '][text_content]'] = ''.join(article_p.xpath('.//text()').extract())
                article_items['article_item[' + str(index) + '][type]'] = 1
                article_items['article_item[' + str(index) + '][id]'] = ''
            index += 1
        req = requests.post('http://oss.qnmami.com/article/add-article-item', data=article_items)
        logging.warning(req.text)

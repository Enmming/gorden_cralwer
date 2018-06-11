# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy import Request
import re
import execjs
from gorden_crawler.spiders.shiji_base import BaseSpider
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
import copy
import json
import logging


class MybagSpider(BaseSpider):

    name = "mybag"

    base_url = "http://www.mybag.com"

    allowed_domains = ["mybag.com"]

    start_urls = [
        'http://www.mybag.com/home.dept'
    ]

    usd_suffix = 'switchcurrency=USD'

    custom_settings = {
        'DOWNLOAD_DELAY': 0.05,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        #     # 'DOWNLOADER_MIDDLEWARES': {
        #     #     # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
        #     #     'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
        #     #     'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
        #     #     'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
        #     #     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        #     # }
    }


    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)
        women_nav_divs = sel.xpath('//li[@class="nav-link nav-women"]//div[@class="constraint centered"]/div')[1:3]
        men_nav_divs = sel.xpath('//li[@class="nav-link nav-men"]//div[@class="constraint centered"]/div')[1:3]

        for women_nav_div in women_nav_divs:
            gender = 'women'
            product_type = women_nav_div.xpath('./h4/text()').extract()[0].strip()
            category_as = women_nav_div.xpath('./ul/li/a')
            for category_a in category_as:
                category = category_a.xpath('./text()').extract()[0]
                if category == 'View All':
                    continue
                else:
                    cat_url = category_a.xpath('./@href').extract()[0]
                    if self.usd_suffix not in cat_url:
                        if '?' in cat_url:
                            cat_url = cat_url + '&' + self.usd_suffix
                        else:
                            cat_url = cat_url + '?' + self.usd_suffix
                    yield Request(cat_url, callback=self.parse_list, meta={"category": category, "product_type": product_type, "gender": gender})

        for men_nav_div in men_nav_divs:
            gender = 'men'
            product_type = men_nav_div.xpath('./h4/text()').extract()[0].strip()
            category_as = men_nav_div.xpath('./ul/li/a')
            for category_a in category_as:
                category = category_a.xpath('./text()').extract()[0]
                if category == 'View All':
                    continue
                else:
                    cat_url = category_a.xpath('./@href').extract()[0]
                    if self.usd_suffix not in cat_url:
                        if '?' in cat_url:
                            cat_url = cat_url + '&' + self.usd_suffix
                        else:
                            cat_url = cat_url + '?' + self.usd_suffix
                    yield Request(cat_url, callback=self.parse_list, meta={"category": category, "product_type": product_type, "gender": gender})

    def parse_list(self, response):
        sel = Selector(response)
        current_url = response.url
        category = response.meta['category']
        product_type = response.meta['product_type']
        gender = response.meta['gender']
        product_divs_1 = sel.xpath('//div[@class="item item-health-beauty unit size-1of3 grid thg-track js-product-simple "]')
        product_divs_2 = sel.xpath('//div[@class="item item-health-beauty unit size-1of3 grid thg-track js-product-complex "]')
        product_divs = product_divs_1 + product_divs_2
        for product_div in product_divs:
            item = BaseItem()
            item['from_site'] = self.name
            item['type'] = 'base'
            item['category'] = category
            item['product_type'] = product_type
            item['gender'] = gender
            url = product_div.xpath('.//div[@data-track="product-image"]/a/@href').extract()[0]
            if '?' not in url:
                url += '?' + self.usd_suffix
            else:
                url += '&' + self.usd_suffix
            item['url'] = url
            item['cover'] = product_div.xpath('.//div[@data-track="product-image"]/a/img/@src').extract()[0]
            item['current_price'] = product_div.xpath('.//div[@class="price"]/span/text()').extract()[0]
            if len(product_div.xpath('.//div[@class="rrp"]'))>0:
                item['list_price'] = product_div.xpath('.//div[@class="rrp"]/span/text()').extract()[0]
            else:
                item['list_price'] = item['current_price']

            yield Request(url, callback=self.parse_item, meta={"item": item})

        '''分页'''
        next_a = sel.xpath('//a[@data-e2e-element="nextNavigation"]')
        if not next_a.xpath('./@disabled'):
            if 'pageNumber' in current_url:
                current_page = re.search('pageNumber=(\d+)', current_url).group(1)
                next_page = int(current_page) + 1
                next_url = re.sub('pageNumber=(\d+)', 'pageNumber=' + str(next_page), current_url)
            else:
                current_page = 1
                next_page = int(current_page) + 1
                if '?' in current_url:
                    next_url = current_url + '&pageNumber=' + str(next_page)
                else:
                    next_url = current_url + '?pageNumber=' + str(next_page)

            if self.usd_suffix not in next_url:
                if '?' in next_url:
                    next_url = next_url + '&' + self.usd_suffix
                else:
                    next_url = next_url + '?' + self.usd_suffix
            yield Request(next_url, callback=self.parse_list, meta={"category": category, "product_type": product_type, "gender": gender})

    def parse_item(self, response):
        item=response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        item['show_product_id'] = str(re.search('productID: \"(\d+)\"',response.body).group(1)).strip()
        item['brand'] = str(re.search('productBrand: \"(.+)\"',response.body).group(1)).strip()
        item['title'] = sel.xpath('.//h1[@data-track="product-title"]/text()').extract()[0].strip()
        item['desc'] = ''.join(sel.xpath('//div[@itemprop="description"]/p').extract()).strip()
        item['current_price'] = sel.xpath('//span[@class="price"]/text()').extract()[0].strip()
        list_price_search = re.search('rrp: .+\&\#36\;([\d\.]+).+',response.body)
        if list_price_search:
            item['list_price'] = list_price_search.group(1)
        else:
            item['list_price'] = item['current_price']

        images = []
        image_divs = sel.xpath('//div[@class="product-thumb-box productImageZoom__thumbnailContainer "]')
        if not image_divs:
            return
        for image_div in image_divs:
            imageItem = ImageItem()
            imageItem['thumbnail'] = image_div.xpath('./img/@src').extract()[0]
            imageItem['image'] = image_div.xpath('./parent::*/@href').extract()[0]
            images.append(imageItem)

        color_names = sel.xpath('//select[@id="opts-2"]/option[position()>1]/text()').extract()
        if len(color_names) > 1:
            return
        if not color_names:
            color_names = ['One Color']
        item['colors'] = color_names
        color = Color()
        color['type'] = 'color'
        color['from_site'] = item['from_site']
        color['show_product_id'] = item['show_product_id']
        color['images'] = images
        color['name'] = color_names[0]
        color['cover'] = images[0]['thumbnail']
        yield color

        skus = []
        sizes = sel.xpath('//select[@id="opts-1"]/option[position()>1]/text()').extract()
        if not sizes:
            sizes = ['One Size']
        item['sizes'] = sizes
        for size in sizes:
            for color_name in color_names:
                skuItem = SkuItem()
                skuItem['type'] = "sku"
                skuItem['from_site'] = item['from_site']
                skuItem['id'] = item['show_product_id'] + '-' + color_name + '-' + size
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['current_price'] = item['current_price']
                skuItem['list_price'] = item['list_price']
                skuItem['size'] = size
                skuItem['color'] = color_name
                skus.append(skuItem)
        item['skus'] = skus
        item['dimensions'] = ['size']
        yield item








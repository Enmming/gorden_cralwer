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


class PharmacyonlineSpider(BaseSpider):

    name = "pharmacyonline"

    base_url = "http://cn.pharmacyonline.com.au/"

    allowed_domains = ["pharmacyonline.com.au"]

    start_urls = [
        'http://cn.pharmacyonline.com.au/'
    ]

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
        nav_lis = sel.xpath('//ul[@class="clearfix CenterContain H-nav"]/li')[1:-1]
        for nav_li in nav_lis:
            product_type = nav_li.xpath('./a/span/text()').extract()[0]
            for cat_h2 in nav_li.xpath('./ul/li/h2'):
                category = cat_h2.xpath('./a/text()').extract()[0]
                cat_url = cat_h2.xpath('./a/@href').extract()[0]
                if u'\u5973' in category:
                    gender = 'women'
                elif u'\u7537' in category:
                    gender = 'men'
                elif u'\u5a74' in product_type:
                    gender = 'baby'
                elif u'\u7537' in product_type:
                    gender = 'men'
                elif u'\u7f8e\u5986\u4ea7\u54c1' in product_type:
                    gender = 'women'
                else:
                    gender = 'unisex'
                cat_url += '?is_in_stock=1'
                yield Request(cat_url, callback=self.parse_list, meta={"category": category, "product_type": product_type, "gender": gender})

    def parse_list(self, response):
        sel = Selector(response)
        category = response.meta['category']
        product_type = response.meta['product_type']
        gender = response.meta['gender']
        product_lis = sel.xpath('//li[@class="ProductOuter last"]')
        for product_li in product_lis:
            item = BaseItem()
            item['from_site'] = self.name
            item['type'] = 'base'
            item['category'] = category
            item['product_type'] = product_type
            item['gender'] = gender
            url = product_li.xpath('./a[@class="ProductImg"]/@href').extract()[0]
            item['url'] = url
            item['cover'] = product_li.xpath('./a[@class="ProductImg"]/img/@data-original').extract()[0]
            item['current_price'] = product_li.xpath('./div[@class="PriceContain"]/p[@class="PriceNow"]/text()').extract()[0].strip()
            item['list_price'] = product_li.xpath('./div[@class="PriceContain"]/p[@class="PriceWas"]/text()').extract()[0].strip()
            if not item['list_price']:
                item['list_price'] = item['current_price']

            yield Request(url, callback=self.parse_item, meta={"item": item})

        '''分页'''
        next_url = sel.xpath('//a[@class="next_jump"]/@href').extract()
        if next_url and next_url != response.url:
            next_url = next_url[0] + '&is_in_stock=1'
            yield Request(next_url, callback=self.parse_list, meta={"category": category, "product_type": product_type, "gender": gender})

    def parse_item(self, response):
        item=response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)

        item['show_product_id'] = re.search('(\d+)\.html', response.url).group(1)
        item['title'] = sel.xpath('//div[@class="product-name"]/h1/text()').extract()[0].strip()
        brand = re.search('brand: \'(.+)\'',response.body)
        if not brand:
            item['brand'] = 'pharmacyonline'
        else:
            item['brand'] = brand.group(1)

        img = re.search('imgUrl: \'(.+)\'',response.body).group(1)
        images = []
        imageItem = ImageItem()
        imageItem['thumbnail'] = img + '?imageMogr2/thumbnail/380x380/extent/380x380/background/d2hpdGU='
        imageItem['image'] = img
        images.append(imageItem)

        # item['cover'] = images[0]['thumbnail']

        item['colors'] = ['One Color']
        color = Color()
        color['type'] = 'color'
        color['from_site'] = item['from_site']
        color['show_product_id'] = item['show_product_id']
        color['images'] = images
        color['name'] = 'One Color'
        color['cover'] = images[0]['image'] + '?imageMogr2/thumbnail/100x100/extent/100x100/background/d2hpdGU='
        yield color

        item['desc'] = sel.xpath('//div[@class="product-collateral"]').extract()[0]
        current_price = sel.xpath('//div[@class="DetailNoDis PriceNow last_price_sing"]/span/text()')
        if len(current_price) > 0:
            item['current_price'] = current_price.extract()[0]
            item['list_price'] = item['current_price']
        else:
            item['current_price'] = sel.xpath('//div[@class="DetailPriceContain clearfix"]//div[@class="PriceNow"]/text()').extract()[0].strip()
            item['list_price'] = sel.xpath('//div[@class="DetailPriceContain clearfix"]//p[@class="PriceWas"]/text()').extract()[0].strip()

        skus = []
        item['sizes'] = ['One Size']
        skuItem = SkuItem()
        skuItem['type'] = "sku"
        skuItem['from_site'] = item['from_site']
        sku_id = sel.xpath('//div[@class="DetailSku"]/text()').extract()[0].strip()
        skuItem['id'] = re.search('(\d+)', sku_id).group(1)
        skuItem['show_product_id'] = item['show_product_id']
        skuItem['current_price'] = item['current_price']
        skuItem['list_price'] = item['list_price']
        skuItem['size'] = 'One Size'
        skuItem['color'] = 'One Color'
        skus.append(skuItem)
        item['skus'] = skus
        item['dimensions'] = ['size']
        if len(item['show_product_id']) > 6:
            product_id = item['show_product_id'][1:]
        else:
            product_id = item['show_product_id']
        stock_url = 'http://cn.pharmacyonline.com.au/pt_catalog/index/checkQty?product_id=' + product_id
        yield Request(stock_url, callback=self.parse_stock, meta={"item": item}, dont_filter=True)

    def parse_stock(self, response):
        if json.loads(response.body)['des'] == 'fail':
            return
        item = response.meta['item']
        yield item

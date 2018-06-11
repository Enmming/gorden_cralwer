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


class TiffanySpider(BaseSpider):

    name = "tiffany"

    base_url = "http://www.tiffany.com"

    allowed_domains = ["tiffany.com"]

    large_img_surffix = "&wid=960&hei=960"
    cover_img_surffix = "&wid=100&hei=100"

    start_urls = [
        'http://www.tiffany.com/jewelry/necklaces-pendants',
        'http://www.tiffany.com/jewelry/bracelets',
        'http://www.tiffany.com/jewelry/rings',
        'http://www.tiffany.com/jewelry/earrings',
        'http://www.tiffany.com/jewelry/wedding-bands',
        'http://www.tiffany.com/jewelry/tiffany-charms',
        'http://www.tiffany.com/jewelry/brooches'
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 0.05,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        'DOWNLOADER_MIDDLEWARES': {
            # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyUSAMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        response_url = response.url
        category = response_url.split('/')[-1]
        product_detail_str = re.search('<noscript>(.+</ul>)</noscript>', response.body).group(1)
        sel = Selector(text=product_detail_str)
        product_as = sel.xpath('//ul/li/a')
        for product_a in product_as:
            item = BaseItem()
            item['from_site'] = self.name
            item['type'] = 'base'
            item['category'] = category
            item['product_type'] = 'jewelry'
            item['gender'] = 'women'
            if not product_a.xpath('./@href').extract():
                continue
            url = self.base_url + product_a.xpath('./@href').extract()[0]
            item['url'] = url
            yield Request(url, callback=self.parse_item, meta={"item": item})

    def parse_item(self, response):
        item=response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        product_str = re.search('var dataLayer\s*=\s*(.+?);', response.body).group(1)
        product_json = json.loads(product_str)
        product = product_json['products'][0]

        item['brand'] = 'Tiffany'
        item['title'] = product['name']
        if not product['price']:
            return
        item['list_price'] = product['price']
        item['current_price'] = product['price']
        item['desc'] = sel.xpath('//div[@id="drawerDescription"]/div/div').extract()[0]
        item['cover'] = sel.xpath('//meta[@property="og:image"]/@content').extract()[0] + self.cover_img_surffix
        if product['stockStatus'] == 'out of stock':
            return
        skus = []
        sizes = []
        if not sel.xpath('//select[@id="ctlSkuGroupType1_selItemList"]/option'):
            item['show_product_id'] = product['sku']
            skuItem = SkuItem()
            skuItem['type'] = "sku"
            skuItem['from_site'] = item['from_site']
            skuItem['size'] = 'One Size'
            sizes = ['One Size']
            skuItem['color'] = 'One Color'
            skuItem['id'] = item['show_product_id'] + '-' + skuItem['color'] + '-' +  skuItem['size']
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['current_price'] = item['current_price']
            skuItem['list_price'] = item['list_price']
            skus.append(skuItem)
        else:
            item['show_product_id'] = product['groupSku']
            size_options = sel.xpath('//select[@id="ctlSkuGroupType1_selItemList"]/option')
            for size_option in size_options:
                skuItem = SkuItem()
                skuItem['type'] = "sku"
                skuItem['from_site'] = item['from_site']
                if not size_option.xpath('./text()').extract():
                    skuItem['size'] = 'One Size'
                else:
                    skuItem['size'] = size_option.xpath('./text()').extract()[0]
                sizes.append(skuItem['size'])
                skuItem['color'] = 'One Color'
                skuItem['id'] = item['show_product_id'] + '-' + skuItem['color'] + '-' + skuItem['size']
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['current_price'] = item['current_price']
                skuItem['list_price'] = item['list_price']
                skus.append(skuItem)

        images = []
        imageItem = ImageItem()
        imageItem['thumbnail'] = sel.xpath('//meta[@property="og:image"]/@content').extract()[0] + self.large_img_surffix
        imageItem['image'] = sel.xpath('//meta[@property="og:image"]/@content').extract()[0] + self.large_img_surffix
        images.append(imageItem)

        color = Color()
        color['type'] = 'color'
        color['from_site'] = item['from_site']
        color['show_product_id'] = item['show_product_id']
        color['images'] = images
        color['name'] = 'One Color'
        color['cover'] = item['cover']
        yield color

        item['colors'] = ['One Color']
        item['sizes'] = sizes
        item['skus'] = skus
        item['dimensions'] = ['size']
        yield item








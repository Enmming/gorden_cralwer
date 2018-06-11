# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
import json
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from random import random
from urllib import quote
import logging
import re
import execjs
import json
import requests
from gorden_crawler.spiders.shiji_base import BaseSpider


class NetAPorterSpider(BaseSpider):
    name = "netaporter"
    allowed_domains = ["net-a-porter.com"]
    gender = 'women'
    '''
    正式运行的时候，start_urls为空，通过传参数来进行，通过传递参数 -a 处理
    '''
    start_urls = [
        'https://www.net-a-porter.com/us/zh/d/Shop/Clothing/All?cm_sp=topnav-_-clothing-_-topbar&pn=1&npp=60&image_view=product&dScroll=0',
        'https://www.net-a-porter.com/us/zh/d/Shop/Sport/All_Sportswear?cm_sp=Sporter-_-LP-_-Allsportswear&pn=1&npp=60&image_view=product&dScroll=0',
        'https://www.net-a-porter.com/us/zh/d/Shop/Bags/All?cm_sp=topnav-_-bags-_-topbar&pn=1&npp=60&image_view=product&dScroll=0',
        'https://www.net-a-porter.com/us/zh/d/Shop/Accessories/All?cm_sp=topnav-_-accessories-_-topbar&pn=1&npp=60&image_view=product&dScroll=0',
        'https://www.net-a-porter.com/us/zh/d/Shop/Lingerie/All?cm_sp=topnav-_-lingerie-_-alllingerie&pn=1&npp=60&image_view=product&dScroll=0',

    ]

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,
        'DOWNLOAD_DELAY': 0.1,
        'RETRY_TIMES': 20
    }

    base_url = 'https://www.net-a-porter.com/'

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)
        if response.url == 'https://www.net-a-porter.com/us/zh/d/Shop/Sport/All_Sportswear?cm_sp=Sporter-_-LP-_-Allsportswear&pn=1&npp=60&image_view=product&dScroll=0':
            product_type = sel.xpath('//div[@id="product-list-menu"]/div[@class="product-list-title"]/h1/text()').extract()[0]
            if len(sel.xpath('//ul[@id="navLevel3-filter"]')) > 0:
                category_as = sel.xpath('//ul[@id="navLevel3-filter"]/li/a')
                for category_a in category_as:
                    category_url = sel.xpath('//ul[@id="navLevel3-filter"]/parent::*/a/@href').extract()[0]
                    if '?' in category_url:
                        category_url = category_url.replace('?', '')
                    url = self.base_url + category_url + category_a.xpath('./@href').extract()[0]
                    category = category_a.xpath('./span[@class="filter-name"]/text()').extract()[0]
                    yield Request(url, meta={'category': category, 'product_type': product_type}, callback=self.parse_list)
        else:
            product_type = sel.xpath('//div[@id="product-list-menu"]/div[@class="product-list-title"]/h1/text()').extract()[0]
            category_as = sel.xpath('//ul[@id="subnav"]/li/a')
            for category_a in category_as:
                url = self.base_url + category_a.xpath('./@href').extract()[0]
                category = category_a.xpath('./span/text()').extract()[0]
                yield Request(url, meta={'category': category, 'product_type': product_type}, callback=self.parse_subcategory)

    def parse_subcategory(self, response):
        sel = Selector(response)
        category = response.meta['category']
        product_type = response.meta['product_type']
        if len(sel.xpath('//ul[@id="navLevel3-filter"]'))>0:
            sub_category_as = sel.xpath('//ul[@id="navLevel3-filter"]/li/a')
            for sub_category_a in sub_category_as:
                category_url = sel.xpath('//ul[@id="navLevel3-filter"]/parent::*/a/@href').extract()[0]
                if '?' in category_url:
                    category_url = category_url.replace('?', '')
                sub_category_url = self.base_url + category_url+ sub_category_a.xpath('./@href').extract()[0]
                sub_category = sub_category_a.xpath('./span[@class="filter-name"]/text()').extract()[0]
                yield Request(sub_category_url, meta={'category': category, 'product_type': product_type, 'sub_category': sub_category}, callback=self.parse_list)
        else:
            yield Request(response.url, meta={'category': category, 'product_type': product_type}, callback=self.parse_list, dont_filter=True)

    def parse_list(self, response):
        sel = Selector(response)
        category = response.meta['category']
        product_type = response.meta['product_type']
        if 'sub_category' in response.meta.keys():
            sub_category = response.meta['sub_category']
        else:
            sub_category = ''

        products_lis = sel.xpath('//ul[@class="products"]/li')
        for products_li in products_lis:
            item = BaseItem()
            item['type'] = 'base'
            item['product_type'] = product_type
            item['category'] = category
            item['from_site'] = 'netaporter'
            if sub_category:
                item['sub_category'] = sub_category
            item['cover'] = products_li.xpath('./div[@class="product-image"]/a/img/@src').extract()[0]
            if 'http:' not in item['cover']:
                item['cover'] = 'http:' + item['cover']
            url = self.base_url + products_li.xpath('./div[@class="description"]/a/@href').extract()[0]
            item['url'] = url
            item['title'] = products_li.xpath('./div[@class="description"]/text()').extract()[2].strip()
            item['brand'] = products_li.xpath('./div[@class="description"]/a/span[@class="designer"]/text()').extract()[0].strip()
            item['list_price'] = products_li.xpath('./div[@class="description"]/span[@class="price "]/text()').extract()[0].strip()
            item['current_price'] = item['list_price']
            yield Request(url, callback=self.parse_item, meta={"item": item})

        total_num = sel.xpath('//span[@class="total-number-of-products"]/text()').extract()[0]
        if (int(total_num) % 60)>0:
            total_page = int(total_num) / 60 + 1
        else:
            total_page = int(total_num) / 60
        current_page_num = sel.xpath('//span[@class="pagination-page-current"]/text()').extract()[0]
        if int(current_page_num) < total_page:
            if 'pn=' in response.url:
                next_url = response.url.replace('pn='+current_page_num, 'pn='+str(int(current_page_num)+1))
            else:
                next_url = response.url + '&pn='+str(int(current_page_num)+1)
            if sub_category:
                yield Request(next_url, meta={'category': category, 'product_type': product_type, 'sub_category': sub_category}, callback=self.parse_list)
            else:
                yield Request(next_url, meta={'category': category, 'product_type': product_type}, callback=self.parse_list)

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        if len(sel.xpath('//form[@id="product-form"]//meta').extract()) > 1:
            return
        if len(sel.xpath('//div[@class="sold-out-details"]')) > 0:
            return
        item['show_product_id'] = sel.xpath('//div[@class="product-code"]/span/text()').extract()[0].strip()
        imgs = sel.xpath('//div[@class="container-imagery"]//ul[@class="thumbnails no-carousel"]/li/img/@src').extract()
        if len(imgs) == 0:
            imgs = sel.xpath('//div[@class="container-imagery"]//ul[@class="swiper-wrapper"]/li/img/@src').extract()
        images = []
        for img in imgs:
            if 'http:' not in img:
                img = 'http:' + img
            if 'xs.jpg' in img:
                img = img.replace('xs.jpg', 'pp.jpg')
            imageItem = ImageItem()
            imageItem['image'] = img
            imageItem['thumbnail'] = img.replace('pp.jpg', 'm.jpg')
            images.append(imageItem)
        colorItem = Color()
        colorItem['images'] = images
        colorItem['type'] = 'color'
        colorItem['from_site'] = item['from_site']
        colorItem['show_product_id'] = item['show_product_id']
        colorItem['name'] = 'One Color'
        colorItem['cover'] = images[0]['image'].replace('pp.jpg', 'xs.jpg')
        # colorItem['cover'] = images[0]['image'].split('_')[0] + '_sw.jpg'
        # print colorItem['cover']
        # req = requests.get(colorItem['cover'])
        # if not req.ok:
        #     colorItem['cover'] = images[0]['image'].replace('pp.jpg', 'xs.jpg')
        yield colorItem


        price = int(sel.xpath('//form[@id="product-form"]/meta/@data-price-full').extract()[0])/100
        if len(sel.xpath('//select-dropdown[@class="sku"]/@options'))>0:
            sku_str = sel.xpath('//select-dropdown[@class="sku"]/@options').extract()[0]
            skus = json.loads(sku_str)
            item['skus'] = []
            sizes = []
            for sku in skus:
                skuItem = SkuItem()
                skuItem['type'] = 'sku'
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['list_price'] = price
                skuItem['current_price'] = price
                skuItem['color'] = 'One Color'
                skuItem['size'] = sku['data']['size']
                sizes.append(sku['data']['size'])
                skuItem['id'] = sku['id']
                skuItem['from_site'] = item['from_site']
                if sku['stockLevel'] == 'In_Stock' or sku['stockLevel'] == 'Low_Stock':
                    skuItem['is_outof_stock'] = False
                else:
                    skuItem['is_outof_stock'] = True
                item['skus'].append(skuItem)
        else:
            item['skus'] = []
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['list_price'] = price
            skuItem['current_price'] = price
            skuItem['color'] = 'One Color'
            sizes = ['One Size']
            skuItem['size'] = 'One Size'
            skuItem['id'] = sel.xpath('//input [@class="sku"]/@value').extract()[0]
            stock_level = sel.xpath('//input [@class="sku"]/@data-stock').extract()[0]
            if stock_level == 'In_Stock' or stock_level == 'Low_Stock':
                skuItem['is_outof_stock'] = False
            else:
                skuItem['is_outof_stock'] = True
            skuItem['from_site'] = item['from_site']
            item['skus'].append(skuItem)
        item['gender'] = self.gender
        item['colors'] = ['One Color']
        item['sizes'] = sizes
        item['desc'] = ''
        if len(sel.xpath('//widget-show-hide[@id="accordion-1"]//ul/li')) > 0:
            item['desc'] = item['desc'] + sel.xpath('//widget-show-hide[@id="accordion-1"]//ul/li').extract()[0]
        if len(sel.xpath('//widget-show-hide[@id="accordion-2"]//ul/li')) > 0:
            item['desc'] = item['desc'] + sel.xpath('//widget-show-hide[@id="accordion-2"]//ul/li').extract()[0]
        if len(sel.xpath('//widget-show-hide[@id="accordion-2"]//p')) > 0:
            item['desc'] = item['desc'] +sel.xpath('//widget-show-hide[@id="accordion-2"]//p').extract()[0]

        product_items = sel.xpath('//widget-show-hide[@name="Editor\'s Notes"]/div[@class="show-hide-content"]/div/p/a')
        if len(product_items) > 0:
            related_items_id = []
            for product_item in product_items:
                product_id = product_item.xpath('./@href').extract()[0].split('/')[-1]
                related_items_id.append(product_id)
            if related_items_id:
                item['related_items_id'] = related_items_id

        media_url = 'https://video.net-a-porter.com/videos/productPage/' + item['show_product_id'] + '_detail.mp4'
        try:
            req = requests.head(media_url)
            if req.ok:
                item['media_url'] = media_url
        except Exception as e:
            logging.error('error media url: '+ media_url + ' error msg: ' + str(e))
        yield item



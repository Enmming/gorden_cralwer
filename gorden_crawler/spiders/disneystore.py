# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request, FormRequest
from scrapy_redis.spiders import RedisSpider
import re
from urllib import quote, unquote
import json
from gorden_crawler.utils import country
import base64

from gorden_crawler.spiders.shiji_base import BaseSpider

class DisneystoreSpider(BaseSpider):
    name = "disneystore"
    allowed_domains = ["disneystore.com"]

    custom_settings = {
        # 'DOWNLOAD_DELAY': 0.5,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        # 'DOWNLOADER_MIDDLEWARES': {
        #     #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
        #     'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
        #     'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
        #     'gorden_crawler.middlewares.proxy_ats.ProxyHttpsUSAMiddleware': 100,
        #     # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        # }
    }

    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        "https://www.disneystore.com/"
        ]

    base_url = 'https://www.disneystore.com'

    image_base_url = 'https://cdn-ssl.s7.disneystore.com/'
    cover_url_suffix = '?$yetidetail$'
    image_url_suffix = '?$yetzoom$'

    paging_base_url = 'https://www.disneystore.com/disneystore/product/category'

    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)
        nav_lis = sel.xpath('//ul[@id="topNav"]/li')
        for nav_li in nav_lis:
            gender = nav_li.xpath('./a/text()').extract()[0].strip().lower()
            if gender not in ['girls', 'boys', 'baby', 'adults']:
                continue
            if gender == 'baby':
                product_type_as = nav_li.xpath('./section/div/ul[1]/li/a')
                for product_type_a in product_type_as:
                    product_type = product_type_a.xpath('./text()').extract()[0].strip().lower()
                    product_type_url = self.base_url + product_type_a.xpath('./@href').extract()[0]
                    if 'home-decor' in product_type_url:
                        continue
                    yield Request(product_type_url, callback=self.parse_category, meta={"gender":gender, "product_type":product_type})
            else:
                product_type_as = nav_li.xpath('./section/div/ul/li[@class="flyHead"]/a')
                for product_type_a in product_type_as:
                    if product_type_a.xpath('./text()'):
                        product_type = product_type_a.xpath('./text()').extract()[0].strip().lower()
                        if product_type in ['characters', 'in the spotlight', 'entertainment', 'gift cards', 'marvel characters', 'collections', 'collectibles']:
                            continue
                        if gender == 'adults' and product_type in ['clothes for women', 'clothes for men']:
                            gender = product_type.split()[-1]
                        product_type_url = self.base_url + product_type_a.xpath('./@href').extract()[0]
                        if 'home-decor' in product_type_url:
                            continue
                        yield Request(product_type_url, callback=self.parse_category, meta={"gender":gender, "product_type":product_type})

    def parse_category(self, response):
        sel = Selector(response)
        gender = response.meta['gender']
        product_type = response.meta['product_type']

        if len(sel.xpath('//ul[@class="navList"]')) > 0:
            nav_as = sel.xpath('//ul[@class="navList"]/li/a')
            for nav_a in nav_as:
                category = nav_a.xpath('./text()').extract()[0].strip().lower()
                category_url = self.base_url + nav_a.xpath('./@href').extract()[0].strip()
                yield Request(category_url, callback=self.parse_list, meta={"gender":gender, "product_type":product_type, "category":category, 'parse_type':'parse'})    
        else:
            yield Request(response.url, callback=self.parse_list, meta={"gender":gender, "product_type":product_type, "category":product_type, 'parse_type':'parse'}, dont_filter=True)

    def parse_list(self, response):
        category = response.meta['category']
        product_type = response.meta['product_type']
        gender = response.meta['gender']
        parse_type = response.meta['parse_type']
        sel = Selector(response)
        
        if 'productDims' in response.url:
            productDims = re.search('productDims\=(.+)\&?', response.url).group(1)
        else:
            productDims = response.url.split('/')[-1] or response.url.split('/')[-2]
            if '+' in productDims:
                productDims = productDims.replace('+', '%20')

        if parse_type == 'parse':
            products = sel.xpath(".//div[@id='productTiles']/div")
            for product in products:
                item = BaseItem()
                item['from_site'] = self.name
                item['type'] = 'base'
                item['category'] = category
                item['product_type'] = product_type
                item['gender'] = gender
                item['url'] = url = self.base_url + product.xpath("./a/@href").extract()[0]
                item['cover'] = product.xpath(".//div[@class='imageHolder']/img[1]/@src").extract()[0]
                if '?' in item['cover']:
                    item['cover'] = item['cover'].split('?')[0] + self.cover_url_suffix
                if len(product.xpath("./a/@data-tealium-name")) == 0:
                    continue
                item['title'] = product.xpath("./a/@data-tealium-name").extract()[0]
                item['brand'] = 'Disney'
                yield Request(url, callback=self.parse_item, meta={"item":item})

            total_products_str = sel.xpath(".//div[@class='plNumberItems']/text()").extract()[0]
            total_pages = int(re.search('(\d+)', total_products_str).group(1)) / 96 + 1

        elif parse_type == 'ajax':
            body_json = json.loads(response.body)
            if 'fault' in body_json:
                return
            total_pages = int(body_json['productListConstants']['listFilterDefaultLimit'])
            products = body_json['Right'][0]['results']
            for product in products:
                item = BaseItem()
                item['from_site'] = self.name
                item['type'] = 'base'
                item['category'] = category
                item['product_type'] = product_type
                item['gender'] = gender
                item['url'] = url = self.base_url + product['pCanonicalURL']
                item['cover'] = self.image_base_url + product['pThumbnail']
                if '?' in item['cover']:
                    item['cover'] = item['cover'].split('?')[0] + self.cover_url_suffix
                item['title'] = product['pShortProductName']
                item['brand'] = 'Disney'
                yield Request(url, callback=self.parse_item, meta={"item":item})

        if 'offset' in response.url:
            current_offset = int(re.search('offset=(\d+)', response.url).group(1))
        else:
            current_offset = 0
        current_page = current_offset / 96 + 1

        if current_page < total_pages:
            next_offset = current_offset + 96
            next_url = self.paging_base_url + '.json?offset=' + str(next_offset) + '&priceRangeLower=&priceRangeUpper=&sortKey=' + '&productDims=' + productDims
            headers = {"Content-Type":"application/json; charset=UTF-8"}
            yield Request(next_url, callback=self.parse_list, headers=headers, meta={"gender":gender, "product_type":product_type, "category":product_type, 'parse_type':'ajax'})

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        if len(sel.xpath('//h1[@class="pageTitle"]/text()')) > 0:
            return
        if len(sel.xpath('//section[@class="productDesc"]')) > 0:
            return
        """单品s"""
        if len(sel.xpath('//div[@class="productQuickDetails"]//p[@class="productPrice sale textSale"]/span/text()')) > 0:
            item['current_price'] = sel.xpath('//div[@class="productQuickDetails"]//p[@class="productPrice sale textSale"]/span/text()').extract()[0]
            item['list_price'] = sel.xpath('//div[@class="productQuickDetails"]//p[@class="productPrice regular"]/span/text()').extract()[0]
        else:
            item['current_price'] = sel.xpath('//div[@class="productQuickDetails"]//p[@class="productPrice "]/span/text()').extract()[0]
            item['list_price'] = sel.xpath('//div[@class="productQuickDetails"]//p[@class="productPrice "]/span/text()').extract()[0]
        if '-' in item['list_price']:
            item['list_price'] = item['list_price'].split('-')[-1].strip()
        if '-' in item['current_price']:
            item['current_price'] = item['current_price'].split('-')[-1].strip()

        item['show_product_id'] = sel.xpath('//div[@class="productNumber"]/text()').extract()[0]
        if 'Item' in item['show_product_id']:
            item['show_product_id'] = re.search('(\d+)', item['show_product_id']).group(1)

        item['desc'] = sel.xpath(".//div[@class='productShortDescription']/p/text()").extract()
        if len(sel.xpath('//div[@class="longDescription"]')) > 0:
            item['desc'] = item['desc'] + sel.xpath('//div[@class="longDescription"]').extract()
        if len(sel.xpath('div[@class="productSpecs"]')) > 0:
            item['desc'] = item['desc'] + sel.xpath('div[@class="productSpecs"]').extract()
        item['desc'] = ''.join(item['desc'])

        variants_json_str = re.search('var variantsJson = (.+);', response.body).group(1)
        variants_json = json.loads(variants_json_str)

        item['skus'] = []
        item['sizes'] = []
        if not variants_json['items']:
            item['sizes'] = ['One Size']
            skuItem = {}
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['id'] = re.search('productId: \"(\d+)\"', response.body).group(1)
            skuItem['color'] = 'One Color'
            skuItem['size'] = 'One Size'
            skuItem['from_site'] = self.name
            skuItem['list_price'] = item['list_price']
            skuItem['current_price'] = item['current_price']
            skuItem['is_outof_stock'] = False
            item['skus'].append(skuItem)

        else:
            for variant_json in variants_json['items']:
                item['sizes'].append(variant_json['id'])
                skuItem = {}
                skuItem['type'] = 'sku'
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['id'] = variant_json['catEntryId']
                skuItem['color'] = 'One Color'
                skuItem['size'] = variant_json['id']
                skuItem['from_site'] = self.name
                skuItem['list_price'] = item['list_price']
                skuItem['current_price'] = variant_json['price']
                skuItem['is_outof_stock'] = not variant_json['buyable']
                item['skus'].append(skuItem)
            if 'sizeChart' in variants_json['variants'][0].keys():
                item['size_chart'] = 'https:' + variants_json['variants'][0]['sizeChart']

        img_as = sel.xpath(".//a[@class='productThumb thumbnailImage']")
        images = []
        if len(img_as) > 0:
            for img_a in img_as:
                imageItem = ImageItem()
                imageItem['image'] = img_a.xpath("./img/@src").extract()[0]
                imageItem['thumbnail'] = img_a.xpath("./img/@src").extract()[0]
                if '?' in imageItem['image']:
                    imageItem['image'] = imageItem['image'].split('?')[0] + self.image_url_suffix
                if '?' in imageItem['thumbnail']:
                    imageItem['thumbnail'] = imageItem['thumbnail'].split('?')[0] + self.cover_url_suffix
                images.append(imageItem)

        colorItem = Color()
        colorItem['type'] = 'color'
        colorItem['from_site'] = self.name
        colorItem['show_product_id'] = item['show_product_id']
        colorItem['name'] = 'One Color'
        colorItem['cover'] = images[0]['thumbnail']
        colorItem['images'] = images
        yield colorItem

        item['colors'] = ['One Color']
        if 'size_chart' in item.keys():
            yield Request(item['size_chart'], callback=self.parse_size_chart, meta={"item":item}, dont_filter=True)
        else:
            yield item

    def parse_size_chart(self, response):
        sel = Selector(response)
        item = response.meta['item']
        title = item['size_chart']
        table_heads = sel.xpath('//table[1]//tr[2]/td')
        table_bodys = sel.xpath('//table[1]//tr[position()>2]')
        chart = []
        for table_body in table_bodys:
            single_chart = {}
            for index, table_head in enumerate(table_heads):
                if len(table_head.xpath('.//text()').extract()) > 1:
                    table_head = ''.join([head.strip() for head in table_head.xpath('.//text()').extract()])
                else:
                    table_head = table_head.xpath('.//text()').extract()[0]
                single_chart[base64.encodestring(table_head)] = table_body.xpath('./td[' + str(index+1) + ']//text()').extract()[0]
            chart.append(single_chart)
        item['size_chart'] = {'from_site': item['from_site'], 'title': title, 'chart': chart}
        yield item




# -*- coding: utf-8 -*-
# from gilt.rest import GiltApiClient
from scrapy import Request
from scrapy.selector import Selector
import re
import datetime
import execjs
import logging
import json
import base64

from gorden_crawler.items import SaleBaseItem, ImageItem, SkuItem, Color, SaleItem
from gorden_crawler.spiders.shiji_base import GiltActivtiesSpider
from scrapy_redis.spiders import RedisSpider


class BaseFgiltSpider(object):
    def parse_second_item(self, response):
        baseItem = response.meta['baseItem']
        return self.parse_second_base_item(response, baseItem)

    def parse_second_base_item(self, response, baseItem):
        match = re.search(r'createConfig\("config\.product_details",([\s\S]+)\)\;\s*}\s*}\;\s*<\/script>', response.body)
        if match == None:
            return
        productDetail = match.group(1)
        # productDetail = re.search(r'\{\"brand.+\}\]\}', productDetailStr, re.S).group(0)
        context = execjs.compile('''
			var x = %s
			function getPImgs(){
				return x;
			}
		''' % productDetail)

        productDetailDict = context.call('getPImgs')
        allLooks = productDetailDict['productDetails']['product']['allLooks']
        entris = productDetailDict['skuJournal']['entries']

        defaultLook = productDetailDict['productDetails']['defaultLook']

        baseItem['cover'] = 'https:' + defaultLook['images'][0]['largeLookUrl']

        sel = Selector(response)
        baseItem['type'] = 'base'
        baseItem['title'] = sel.xpath('//h1[@class="product-name"]/text()').extract()[0]
        brand = sel.xpath('//h2[@class="brand-name"]/a/text()').extract()
        if len(brand) == 0:
            baseItem['brand'] = sel.xpath('//h2[@class="brand-name"]/span/text()').extract()[0]
        else:
            baseItem['brand'] = brand[0]
        baseItem['desc'] = sel.xpath('//section[@id="description"]').extract()[0]
        baseItem['dimensions'] = ['size', 'color']
        baseItem['from_site'] = 'fgilt'
        baseItem['product_type'] = 'gilt'

        product_id = sel.xpath('//input[@id="product-id"]/@value').extract()[0]
        baseItem['show_product_id'] = product_id

        price_section = sel.xpath('//section[@id="price"]')
        current_price = price_section.xpath('.//span[@class="product-price-sale"]/text()').extract()[0]
        if re.search(r'\-', current_price):
            baseItem['current_price'] = re.search(r'[0-9,.]+', current_price).group(0)
        else:
            baseItem['current_price'] = re.findall(r'\d.*', current_price)[0]
        list_price_str = price_section.xpath('.//div[@class="product-price-msrp"]/text()').extract()
        if len(list_price_str) == 0:
            list_price = current_price
        else:
            list_price = list_price_str[0]
        if re.search(r'\-', list_price):
            baseItem['list_price'] = re.search(r'[0-9,.]+', list_price).group(0)
        else:
            baseItem['list_price'] = re.findall(r'\d.*', list_price)[0]

        color_lis = sel.xpath('//div[@class="sku-attributes sku-attributes-swatches"]/ul[@class="sku-attribute-values"]/li')
        if len(color_lis) == 0:
            color_lis = ['one-color-li']

        colors = []
        colorAttributeMap = {}
        if 'colorAttribute' in productDetailDict['productDetails']['product'].keys():
            colorAttrs = productDetailDict['productDetails']['product']['colorAttribute']['values']
            for colorAttr in colorAttrs:
                colorAttributeMap[colorAttr['id']] = colorAttr
        else:
            colors = ['one-color']

        sizes = []
        sizeAttributeMap = {}
        if 'sizeAttribute' in productDetailDict['productDetails']['product'].keys():
            if 'secondaryName' in productDetailDict['productDetails']['product']['sizeAttribute'].keys():
                s_t = productDetailDict['productDetails']['product']['sizeAttribute']['secondaryName']
            sizeAttrs = productDetailDict['productDetails']['product']['sizeAttribute']['values']
            for sizeAttr in sizeAttrs:
                sizeAttributeMap[sizeAttr['id']] = sizeAttr['value']
                sizes.append(sizeAttr['value'])
        else:
            sizes = ['one-size']

        entryColorMap = {}
        entryLookMap = {}
        entrySkuSizeMap = {}
        entrySkuPriceMap = {}

        for entry in entris:
            if entry['type'] == 'images':
                entryColorMap[entry['savId']] = entry['images']
            if entry['type'] == 'associate_look':
                entryLookMap[entry['lookId']] = entry['savId']
            if entry['type'] == 'pricing':
                entrySkuPriceMap[entry['skuId']] = entry
            if entry['type'] == 'associate' and entry['attribute'] == 'Size':
                entrySkuSizeMap[entry['skuId']] = entry['savId']

        skus = []

        for look in allLooks:
            look_pid = look['productLookId']

            if len(colorAttributeMap) > 0:
                color_name = colorAttributeMap[entryLookMap[look_pid]]['value']
                colors.append(color_name)
                if 'swatchImageUrl' in colorAttributeMap[entryLookMap[look_pid]].keys():
                    color_cover = 'https:' + colorAttributeMap[entryLookMap[look_pid]]['swatchImageUrl']
                else:
                    color_cover = ''

                image_url_prefix = 'https:'
                images = []
                lookImages = look['images']
                for lookImage in lookImages:
                    imageItem = ImageItem()
                    imageItem['thumbnail'] = image_url_prefix + lookImage['thumbnailLookUrl']
                    imageItem['image'] = image_url_prefix + lookImage['largeLookUrl']
                    images.append(imageItem)

                colorItem = Color()
                colorItem['type'] = 'color'
                colorItem['show_product_id'] = product_id
                colorItem['from_site'] = 'fgilt'
                colorItem['name'] = color_name
                if color_cover == '':
                    color_cover = images[0]['thumbnail']
                colorItem['cover'] = color_cover
                colorItem['images'] = images

                yield colorItem
            else:
                color_name = 'one-color'

                image_url_prefix = 'https:'
                images = []
                lookImages = look['images']
                for lookImage in lookImages:
                    imageItem = ImageItem()
                    imageItem['thumbnail'] = image_url_prefix + lookImage['thumbnailLookUrl']
                    imageItem['image'] = image_url_prefix + lookImage['largeLookUrl']
                    images.append(imageItem)

                color_cover = images[0]['thumbnail']
                colorItem = Color()
                colorItem['type'] = 'color'
                colorItem['show_product_id'] = product_id
                colorItem['from_site'] = 'fgilt'
                colorItem['name'] = color_name
                colorItem['cover'] = color_cover
                colorItem['images'] = images
                yield colorItem

            lookSkus = look['skus']

            for lookSku in lookSkus:
                skuItem = SkuItem()
                skuItem['type'] = 'sku'
                skuItem['show_product_id'] = product_id
                skuItem['from_site'] = 'fgilt'
                if 's_t' in dir():
                    skuItem['s_t'] = s_t
                sku_id = lookSku['skuId']

                skuItem['id'] = sku_id

                if lookSku['inventoryStatus'] == 'SOLD_OUT':
                    skuItem['is_outof_stock'] = True
                else:
                    skuItem['is_outof_stock'] = False

                if len(sizeAttributeMap) == 0 or sku_id not in entrySkuSizeMap.keys():
                    skuItem['size'] = 'one-size'
                else:
                    skuItem['size'] = sizeAttributeMap[entrySkuSizeMap[sku_id]]
                skuItem['color'] = color_name
                skuItem['current_price'] = entrySkuPriceMap[sku_id]['salePrice']['raw']
                skuItem['list_price'] = entrySkuPriceMap[sku_id]['msrpPrice']['raw']
                skus.append(skuItem)

        baseItem['colors'] = colors
        baseItem['skus'] = skus
        baseItem['sizes'] = sizes

        '''尺码表'''
        size_chart = {}
        if len(sel.xpath('//caption[@class="display-name"]/text()')) > 0:
            size_chart_name = sel.xpath('//caption[@class="display-name"]/text()').extract()[0].strip()
            size_heads = sel.xpath('//table[@class="size-chart-data"]/thead/tr/th/text()').extract()
            size_body = sel.xpath('//table[@class="size-chart-data"]/tbody/tr')
            size_chart['title'] = size_chart_name
            size_chart['chart'] = []
            for size_data in size_body:
                chart = {}
                for index, size_head in enumerate(size_heads):
                    if len(size_data.xpath('./td[' + str(index + 1) + ']/text()')) > 0:
                        chart[base64.encodestring(size_head).strip()] = size_data.xpath('./td[' + str(index + 1) + ']/text()').extract()[0]
                    else:
                        chart[base64.encodestring(size_head).strip()] = '-'
                size_chart['chart'].append(chart)
            baseItem['size_chart'] = size_chart
        yield baseItem

    def handle_parse_item(self, response, baseItem):
        sel = Selector(response)

        response_text = response.body
        item = eval(response_text)
        show_product_id = item['id']

        baseItem['type'] = 'base'
        baseItem['show_product_id'] = show_product_id
        baseItem['title'] = item['name']
        baseItem['brand'] = item['brand']
        baseItem['good_json_url'] = item['product']

        try:
            baseItem['desc'] = item['content']['description']
        except KeyError, e:
            baseItem['desc'] = ''
        baseItem['url'] = item['url']
        baseItem['cover'] = item['image_urls']['300x400'][0]['url']
        baseItem['dimensions'] = ['size', 'color']
        # baseItem['product_type'] = self.product_type
        categories = sorted(list(set(item['categories'])))
        if len(categories) > 0:
            baseItem['product_type'] = 'gilt'
            baseItem['category'] = ','.join(categories)
        else:
            baseItem['product_type'] = 'gilt'
            baseItem['category'] = 'gilt'

        size_info = sel.xpath('//table[contains(@class, "size-chart-data")]')
        if len(size_info) > 0:
            baseItem['size_info'] = size_info.extract()[0]

        images = []
        image_urls = item['image_urls']['1080x1440']
        for image_url in image_urls:
            image_item = ImageItem()
            image = image_url['url']
            image_item['thumbnail'] = re.sub(r'1080x1440', '50x50', image)
            image_item['image'] = image
            images.append(image_item)

        skus = []
        skus_items = item['skus']
        colors = []
        sizes = []

        for sku_item in skus_items:
            msrp_price = sku_item['msrp_price']
            sale_price = sku_item['sale_price']
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['list_price'] = msrp_price
            skuItem['current_price'] = sale_price
            baseItem['list_price'] = msrp_price
            baseItem['current_price'] = sale_price
            inventory_status = sku_item['inventory_status']
            if inventory_status == 'for sale':
                skuItem['is_outof_stock'] = False
                baseItem['is_sold_out'] = False
            else:
                skuItem['is_outof_stock'] = True
                baseItem['is_sold_out'] = True
            skuItem['from_site'] = 'fgilt'
            skuItem['show_product_id'] = show_product_id

            try:
                attributes = sku_item['attributes']
                for attribute in attributes:
                    temp_name = attribute['name']
                    temp_value = attribute['value']
                    if temp_name == 'color':
                        if len(temp_value) == 0 or temp_value.isspace():
                            colors.append('one-color')
                        else:
                            colors.append(temp_value)
                    if temp_name == 'size':
                        if len(temp_value) == 0 or temp_value.isspace():
                            sizes.append('one-size')
                        else:
                            sizes.append(temp_value)
            except KeyError, e:
                pass

            if len(colors) == 0:
                colors.append('one-color')
            if len(sizes) == 0:
                sizes.append('one-size')

            baseItem['sizes'] = list(set(sizes))
            baseItem['colors'] = list(set(colors))

            for color in colors:
                colorItem = Color()
                colorItem['type'] = 'color'
                colorItem['show_product_id'] = show_product_id
                colorItem['from_site'] = self.from_site
                colorItem['images'] = images
                colorItem['cover'] = images[0]['thumbnail']
                colorItem['name'] = color

                yield colorItem
                for size in sizes:
                    skuItem['id'] = str(color) + '*' + str(size)
                    skuItem['color'] = color
                    skuItem['size'] = size
                    skus.append(skuItem)
        baseItem['skus'] = skus
        yield baseItem


class FgiltSpider(GiltActivtiesSpider, BaseFgiltSpider):
    name = "fgilt"
    from_site = 'fgilt'
    allowed_domains = ["gilt.com"]
    base_url = 'https://www.gilt.com'
    stores_gender_mapping = {
        'women': 'women',
        'men': 'men',
        'kids': 'kid-unisex',
        'home': 'unisex'
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_TIMEOUT': 40,
        'RETRY_TIMES': 20,
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyGiltMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    start_urls = [
        'https://api.gilt.com/v1/sales/men/dress-shirts-on-a-budget/detail.json?apikey=c316e4ec76c564cd35ecb2d2cc52efb3cbab3f2517191d0ef14ed9835479a553'
        # #active
        # 'https://api.gilt.com/v1/sales/women/active.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # 'https://api.gilt.com/v1/sales/men/active.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # 'https://api.gilt.com/v1/sales/kids/active.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # 'https://api.gilt.com/v1/sales/home/active.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # #upcoming
        # 'https://api.gilt.com/v1/sales/women/upcoming.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # 'https://api.gilt.com/v1/sales/men/upcoming.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # 'https://api.gilt.com/v1/sales/kids/upcoming.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b',
        # 'https://api.gilt.com/v1/sales/home/upcoming.json?apikey=6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b'
    ]
    # shiji
    # API_KEY = '6d864fd235a916550a1e5fe4e885f095ed22a6a16eb4fd3d56ad58be7e16940b'
    API_KEY = 'c316e4ec76c564cd35ecb2d2cc52efb3cbab3f2517191d0ef14ed9835479a553'
    URL_API_KEY_SUFFIX = '?apikey=' + API_KEY
    UTC_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    # def __init__(self, url):
    # 	if url:
    # 		self.start_urls = []
    # 		self.start_urls.append(url)

    def parse(self, response):
        active_sale = eval(response.body)
        begins = active_sale['begins']
        ends = active_sale['ends']
        sale_key = active_sale['sale_key']
        store = active_sale['store']
        gender = self.stores_gender_mapping[store]

        baseItem = SaleBaseItem()
        baseItem['sale_key'] = sale_key
        baseItem['gender'] = gender
        baseItem['begins'] = (datetime.datetime.strptime(begins, self.UTC_FORMAT) + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        baseItem['ends'] = (datetime.datetime.strptime(ends, self.UTC_FORMAT) + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        baseItem['from_site'] = self.from_site

        logging.warning(baseItem)
        logging.warning(store)

        if not store == 'home':
            if not active_sale.has_key('products'):
                url = active_sale['sale_url']
                logging.warning(url)
                yield Request(url, callback=self.parse_second_product, meta={'baseItem': baseItem})
            else:
                try:
                    for product_json_url in active_sale['products']:
                        product_url = product_json_url + self.URL_API_KEY_SUFFIX
                        yield Request(product_url, callback=self.parse_product_url, meta={'baseItem': baseItem})
                except KeyError, e:
                    print 'KeyError---products--' + active_sale['sale']

    def parse_product_url(self, response):
        baseItem = response.meta['baseItem']

        response_text = response.body
        item = eval(response_text)
        url = item['url']

        baseItem['url'] = url
        baseItem['title'] = item['name']
        baseItem['type'] = 'base'
        baseItem['good_json_url'] = item['product']

        categories = sorted(list(set(item['categories'])))
        if len(categories) > 0:
            baseItem['product_type'] = 'gilt'
            baseItem['category'] = ','.join(categories)
        else:
            baseItem['product_type'] = 'gilt'
            baseItem['category'] = 'gilt'

        yield Request(url, callback=self.parse_second_item, meta={'baseItem': baseItem})

    def parse_product(self, response):
        baseItem = response.meta['baseItem']

        return self.handle_parse_item(response, baseItem)

    def parse_second_product(self, response):
        baseItem = response.meta['baseItem']
        sel = Selector(response)
        sale_urls = sel.xpath('//a[@class="sale-entrance"]/@href').extract()

        for sale_url in sale_urls:
            url = self.base_url + sale_url
            yield Request(url, callback=self.parse_second_list, meta={'baseItem': baseItem})

    def parse_second_list(self, response):
        baseItem = response.meta['baseItem']
        sel = Selector(response)
        baseItem['category'] = sel.xpath('//h1[@class="page-title-sale primary"]/text()').extract()[0]
        total_items = sel.xpath('//span[@class="total-results"]/text()').extract()[0]
        total_items_str = 'q.rows=' + str(total_items)
        suffix_url = '?q.rows=45&q.start=0&country=US&currency=USD&locale=en&rule_type=DEFAULT&test_bucket_id=928874550507756949&jsKey=8XQ-rb7-Guw'
        url = response.url + re.sub(r'q.rows=\d+', total_items_str, suffix_url)
        yield Request(url, callback=self.parse_second_list_all, meta={'baseItem': baseItem})

    def parse_second_list_all(self, response):
        baseItem = response.meta['baseItem']
        sel = Selector(response)
        product_links = sel.xpath('//a[@class="product-link"]/@href').extract()
        for product_link in product_links:
            url = self.base_url + str(product_link)
            baseItem['url'] = url
            yield Request(url, callback=self.parse_second_item, meta={'baseItem': baseItem})

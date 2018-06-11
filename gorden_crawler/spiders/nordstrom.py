# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from gorden_crawler.spiders.shiji_base import BaseSpider
from scrapy.http import HtmlResponse
import re
import execjs
import copy
import demjson
import requests
import base64
import logging

# import json

class NordstromSpider(BaseSpider):
    name = "nordstrom"
    allowed_domains = ["nordstrom.com"]

    # 正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'http://shop.nordstrom.com/c/womens-clothing',
        'http://shop.nordstrom.com/c/womens-shoes',
        'http://shop.nordstrom.com/c/womens-handbags-and-wallets',
        'http://shop.nordstrom.com/c/handbags-accessories',
        'http://shop.nordstrom.com/c/mens-clothing',
        'http://shop.nordstrom.com/c/mens-shoes',
        'http://shop.nordstrom.com/c/mens-accessories',
        'http://shop.nordstrom.com/c/girls',
        'http://shop.nordstrom.com/c/toys-for-girls',
        'http://shop.nordstrom.com/c/boys',
        'http://shop.nordstrom.com/c/toys-for-boys',
        'http://shop.nordstrom.com/c/baby-girl-clothes',
        'http://shop.nordstrom.com/c/baby-boy-clothes',
        'http://shop.nordstrom.com/c/baby-toddler-accessories',
        'http://shop.nordstrom.com/c/makeup-shop',
        'http://shop.nordstrom.com/c/skincare-shop',
        'http://shop.nordstrom.com/c/womens-fragrances',
        'http://shop.nordstrom.com/c/tools-brushes',
        'http://shop.nordstrom.com/c/beauty-hair-care',
        'http://shop.nordstrom.com/c/beauty-skincare-bath-body',
        'http://shop.nordstrom.com/c/beauty-makeup-nails',
        'http://shop.nordstrom.com/c/beauty-gifts-value-sets-all',
        'http://shop.nordstrom.com/c/womens-handbags',
        'http://shop.nordstrom.com/c/all-wallets-tech-cases',
        'http://shop.nordstrom.com/c/luggage-travel'

    ]

    start_urls_map = {
        'http://shop.nordstrom.com/c/womens-clothing': {'gender': 'women', 'product_type': 'clothing'},
        'http://shop.nordstrom.com/c/womens-shoes': {'gender': 'women', 'product_type': 'shoes'},
        'http://shop.nordstrom.com/c/womens-handbags-and-wallets': {'gender': 'women', 'product_type': 'bags'},
        'http://shop.nordstrom.com/c/handbags-accessories': {'gender': 'women', 'product_type': 'accessories'},
        'http://shop.nordstrom.com/c/mens-clothing': {'gender': 'men', 'product_type': 'clothing'},
        'http://shop.nordstrom.com/c/mens-shoes': {'gender': 'men', 'product_type': 'shoes'},
        'http://shop.nordstrom.com/c/mens-accessories': {'gender': 'men', 'product_type': 'accessories'},
        'http://shop.nordstrom.com/c/girls': {'gender': 'girls', 'product_type': 'clothing'},
        'http://shop.nordstrom.com/c/toys-for-girls': {'gender': 'girls', 'product_type': 'accessories'},
        'http://shop.nordstrom.com/c/boys': {'gender': 'boys', 'product_type': 'clothing'},
        'http://shop.nordstrom.com/c/toys-for-boys': {'gender': 'boys', 'product_type': 'accessories'},
        'http://shop.nordstrom.com/c/baby-girl-clothes': {'gender': 'girls', 'product_type': 'clothing'},
        'http://shop.nordstrom.com/c/baby-boy-clothes': {'gender': 'boys', 'product_type': 'clothing'},
        'http://shop.nordstrom.com/c/baby-toddler-accessories': {'gender': 'toddler', 'product_type': 'accessories'},
        'http://shop.nordstrom.com/c/womens-handbags': {'gender': 'women', 'product_type': 'bags'},
        'http://shop.nordstrom.com/c/all-wallets-tech-cases': {'gender': 'women', 'product_type': 'bags'},
        'http://shop.nordstrom.com/c/luggage-travel': {'gender': 'women', 'product_type': 'bags'},
    }


    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOADER_MIDDLEWARES': {
              # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,'
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    base_url = 'http://shop.nordstrom.com'
    cat_list = []
    # 爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)
        current_url = response.url
        if current_url not in self.start_urls_map.keys():
            product_type = sel.xpath('//h1/text()').extract()[0]
            category_as = sel.xpath('//ul[@class="nav-list"][1]/li')
            for category_a in category_as:
                cat_url = self.base_url + category_a.xpath('./a/@href').extract()[0]
                category = category_a.xpath('./a/span/text()').extract()[0]
                if 'All' in category_a.xpath('./a/span/text()').extract()[0]:
                    continue
                yield Request(cat_url, callback=self.parse_category, meta={"gender": 'women', "product_type": product_type, "category": category})
                if 'nav-item separator' in category_a.xpath('./@class').extract()[0]:
                    break
        else:
            gender = self.start_urls_map[current_url]['gender']
            product_type = self.start_urls_map[current_url]['product_type']
            if product_type == 'bags':
                yield Request(response.url, callback=self.parse_category, meta={"gender": gender, "product_type": product_type, "category": ''}, dont_filter=True)
            elif 'baby' in response.url:
                category = product_type
                yield Request(response.url, callback=self.parse_list, meta={"gender": gender, "product_type": product_type, "category": category}, dont_filter=True)
            else:
                category_lis = sel.xpath('//ul[@class="nav-list"]/li[position()>1]')
                for category_li in category_lis:
                    category = category_li.xpath('./a/span/text()').extract()[0].strip()
                    if 'Handbags & Wallets' in category:
                        continue
                    cat_url = self.base_url + category_li.xpath('./a/@href').extract()[0].strip()
                    if category == 'Shoes':
                        product_type = 'shoes'
                    if category == 'Accessories':
                        product_type = 'accessories'
                    yield Request(cat_url, callback=self.parse_list, meta={"gender": gender, "product_type": product_type, "category": category})
                    if 'separator' in category_li.xpath('./@class').extract()[0].strip():
                        break

    def parse_category(self, response):
        sel = Selector(response)
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        category = response.meta['category']
        cat_as = sel.xpath('//ul[@class="nav-list"]/li/ul/li/ul/li/a')
        if len(cat_as) > 0:
            for cat_a in cat_as:
                cat_url = self.base_url + cat_a.xpath('./@href').extract()[0]
                yield Request(cat_url, callback=self.parse_list, meta={"gender": gender, "product_type": product_type, "category": category, "sub": True})
        else:
            cat_url = self.base_url + sel.xpath('.//li/a[@class="active-category"]/@href').extract()[0]
            yield Request(cat_url, callback=self.parse_list, meta={"gender": gender, "product_type": product_type, "category": category, "sub": True})

    def parse_list(self, response):
        sel = Selector(response)
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        category = response.meta['category']
        item = BaseItem()
        item['type'] = 'base'
        item['gender'] = gender
        item['from_site'] = 'nordstrom'
        item['product_type'] = product_type
        if not category:
            category = sel.xpath('//h1/text()').extract()[0]
        else:
            if 'sub' in response.meta.keys() :
                item['sub_category'] = sel.xpath('//h1/text()').extract()[0]
        item['category'] = category

        json_str = re.search("<script>ReactDOM\.render\(React\.createElement\(ProductResultsDesktop\,[\s]*(.+)[\s]*\)\,[\s]*document\.getElementById", response.body)

        if json_str is None:
            logging.warning(response.url + ': json empty!!')
            return
        context = execjs.compile('''
            var json = %s
            function getJson(){
                return json;
            }
        ''' % json_str.group(1))
        product_json = context.call('getJson')
        product_details = product_json['data']['ProductResult']['ProductData']

        for product_detail in product_details.values():
            item['show_product_id'] = product_detail['Id']
            item['title'] = product_detail['Title']
            # if product_detail['Media'] is not None:
            #     item['cover'] = product_detail['Media'][0]['Url']
            # else:
            #     continue
            item['brand'] = product_detail['Brand']['Label']
            onsale = False
            for price in product_detail['Prices']:
                if price['Type'] == 'Sale':
                    onsale = True
                    sale_price = price['MaxItemPrice']
                else:
                    list_price = price['MaxItemPrice']
            if onsale:
                item['list_price'] = list_price
                item['current_price'] = sale_price
            else:
                item['list_price'] = list_price
                item['current_price'] = list_price
            url = product_detail['ProductPageUrl']
            if not product_detail['Media']:
                continue
            for img_dict in product_detail['Media']:
                if img_dict['Type'] == 'MainImage':
                    item['cover'] = img_dict['Url']
            if 'http://shop.nordstrom.com/' not in url:
                url = 'http://shop.nordstrom.com/' + url
            item['url'] = url
            yield Request(url, callback=self.parse_item, meta={"item": item})

        if 'page' in str(response.url):
            current_page = re.search('page=([\d]+)', str(response.url)).group(1)
        else:
            current_page = 1
        total_str = sel.xpath('//button[@class="npr-store-mode-toggle-button"]/text()').extract()[0]
        total_goods = re.search('\(([\d]+)\)', total_str).group(1)
        if 'items' in total_goods:
            total_goods = total_goods.replace('items', '')
        last_page = int(total_goods) / 66 + 1
        next_page = int(current_page) + 1
        if int(current_page) < int(last_page):
            if 'page' in str(response.url):
                next_url = re.sub('page=[\d]+', 'page=' + str(next_page), str(response.url))
            else:
                if '?' not in response.url:
                    next_url = str(response.url) + '?page=' + str(next_page)
                else:
                    next_url = str(response.url) + '&page=' + str(next_page)
            yield Request(next_url, callback=self.parse_list, meta={'gender': gender, 'product_type': product_type, 'category': category})



            # if len(sel.xpath('//li[@class="page-arrow page-next"]')) > 0:
            #     if 'page' in response.url:
            #         next_url = re.sub('\?page=[\d]+', sel.xpath('//li[@class="page-arrow page-next"]/a/@href').extract()[0], response.url)
            #     else:
            #         next_url = response.url + sel.xpath('//li[@class="page-arrow page-next"]/a/@href').extract()[0]
            #     yield Request(next_url, callback=self.parse_list, meta={'gender': gender, 'product_type': product_type, 'category': category})

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        detail_str = re.search('<script>ReactDOM\.render\(React\.createElement\(ProductDesktop\,[\s]*(.+)[\s]*\)\,[\s]*document\.getElementById', response.body)
        if detail_str is None:
            return
        context = execjs.compile('''
            var json = %s
            function getJson(){
                return json;
            }
        ''' % detail_str.group(1))
        detail_json = context.call('getJson')
        goods_detail = detail_json['initialData']['Model']['StyleModel']
        if goods_detail['IsAvailable'] == False:
            return
        item['desc'] = goods_detail['Description']
        item['show_product_id'] = goods_detail['Id']
        item['dimensions'] = ['size', 'color']
        # if len(sel.xpath('//div[@class="size-chart"]/a/@href'))>0:
        #     item['size_info'] = sel.xpath('//div[@class="size-chart"]/a/@href').extract()[0]
        # else:
        item['size_info'] = ''
        color_details = goods_detail['StyleMedia']
        color_names = []
        color_images = {}
        image_keys = ['Zoom', 'MaxLarge', 'Large', 'Medium']

        for color_detail in color_details:
            if color_detail['ColorName'] == '':
                continue
            if color_detail['ColorName'] not in color_images.keys():
                color_images[color_detail['ColorName']]=[]
            imageItem = ImageItem()
            # imageItem['image'] = color_detail['ImageMediaUri']['Gigantic']
            # if color_detail['ImageMediaUri']['Gigantic'] == "":
            for image_key in image_keys:
                imageItem['image'] = color_detail['ImageMediaUri'][image_key]
                if not color_detail['ImageMediaUri'][image_key] or 'g.nordstromimage.com' in color_detail['ImageMediaUri'][image_key]:
                    continue
                else:
                    imageItem['image'] = color_detail['ImageMediaUri'][image_key]
                    break
            imageItem['thumbnail'] = color_detail['ImageMediaUri']['Large']
            if imageItem['thumbnail'] or 'g.nordstromimage.com' in imageItem['thumbnail']:
                imageItem['thumbnail'] = color_detail['ImageMediaUri']['Medium']
            color_images[color_detail['ColorName']].append(imageItem)
        if len(color_images) > 0:
            for color_name, images in color_images.items():
                color = Color()
                color['type'] = 'color'
                color['from_site'] = self.name
                color['show_product_id'] = item['show_product_id']
                color['images'] = images
                color['name'] = color_name
                color['cover'] = images[0]['thumbnail']
                yield color
        else:
            for color_detail in color_details:
                imageItem = ImageItem()
                for image_key in image_keys:
                    imageItem['image'] = color_detail['ImageMediaUri'][image_key]
                    if color_detail['ImageMediaUri'][image_key] == "" or 'g.nordstromimage.com' in color_detail['ImageMediaUri'][image_key]:
                        continue
                    else:
                        imageItem['image'] = color_detail['ImageMediaUri'][image_key]
                        break
                imageItem['thumbnail'] = color_detail['ImageMediaUri']['Large']
                if imageItem['thumbnail'] or 'g.nordstromimage.com' in imageItem['thumbnail']:
                    imageItem['thumbnail'] = color_detail['ImageMediaUri']['Medium']
                images = [imageItem]
            color_as = sel.xpath('//ul[@class="swatch-list"]/li/a/span/img')
            color_names = []
            for color_a in color_as:
                color = Color()
                color['type'] = 'color'
                color['from_site'] = self.name
                color['show_product_id'] = item['show_product_id']
                color_name = color_a.xpath('./@alt').extract()[0]
                if 'swatch image' in color_name:
                    color_name = color_name.replace('swatch image','')
                color['name'] = color_name.strip()
                color_names.append(color_name)
                color['images'] = images
                color['cover'] = color_a.xpath('./@src').extract()[0]
                yield color

        list_price_list = []
        sizes = []
        skus = []
        widths = []
        for item_group in goods_detail['ChoiceGroups']:
            list_price_temp = item_group['Price']['OriginalPrice']
            if '–' in list_price_temp:
                list_price_temp = list_price_temp.split('–')[1].strip()
            list_price_list.append(list_price_temp)
            if 'Size' not in item_group.keys() or item_group['Size'] is None:
                sizes = ['One Size']
                continue
            if 'Width' in item_group.keys() and item_group['Width'] is not None:
                if 'width' not in item['dimensions']:
                    item['dimensions'].append('width')
                for width_group in item_group['Width']:
                    if width_group['Value'] not in widths:
                        widths.append(width_group['Value'])
            for size_group in item_group['Size']:
                if size_group['Value'] not in sizes:
                    sizes.append(size_group['Value'])
        if widths:
            size_width = {'size': sizes, 'width': widths}
        else:
            size_width = {'size': sizes}

        sku_list_price = max(list_price_list)
        for sku_detail in goods_detail['Skus']:
            skuItem = {}
            skuItem['type'] = "sku"
            skuItem['from_site'] = self.name
            skuItem['id'] = sku_detail['Id']
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['list_price'] = sku_list_price
            skuItem['current_price'] = sku_detail['Price']
            skuItem['color'] = sku_detail['Color']
            if sku_detail['Size']:
                skuItem['size'] = {'size': sku_detail['Size']}
                if 'Width' in sku_detail.keys() and sku_detail['Width'] is not None:
                    skuItem['size']['width'] = sku_detail['Width']
            else:
                skuItem['size'] = {'size': 'One Size'}
            skus.append(skuItem)
        if len(color_images) > 0:
            item['colors'] = color_images.keys()
        else:
            item['colors'] = color_names
        item['sizes'] = size_width
        item['skus'] = skus
        # if len(sel.xpath('//div[@class="size-chart"]/a/@href'))>0:
        #     size_chart_url = sel.xpath('//div[@class="size-chart"]/a/@href').extract()[0]
        #     yield Request(size_chart_url, callback=self.parse_size_chart, meta={'item': item})
        # else:
        yield item

    # def parse_size_chart(self, response):
    #     sel = Selector(response)
    #     item = response.meta['item']
    #     final_chart_list = []
    #     if len(sel.xpath('//table[@id="size-chart-0"]'))>0:
    #         for chart_num in range(5):
    #             size_chart = {}
    #             if len(sel.xpath('//table[@id="size-chart-'+ str(chart_num) +'"]'))>0:
    #                 size_chart_name = sel.xpath('//table[@id="size-chart-'+ str(chart_num) +'"]/caption/text()').extract()[0].strip()
    #                 size_heads = sel.xpath('//table[@id="size-chart-'+ str(chart_num) +'"]/thead/tr/th/text()').extract()
    #                 size_body = sel.xpath('//table[@id="size-chart-'+ str(chart_num) +'"]/tbody[@class="unit-Centimeters"]')
    #                 size_types = sel.xpath('//table[@id="size-chart-'+ str(chart_num) +'"]/tbody[@class="unit-Centimeters"]/tr/th/text()').extract()
    #                 size_chart['title'] = size_chart_name
    #                 size_chart['chart'] = []
    #                 for head_num, size_head in enumerate(size_heads):
    #                     temp_dict={}
    #                     temp_dict[base64.encodestring('us_size').strip()] = size_head
    #                     for type_num, size_type in enumerate(size_types):
    #                         temp_dict[base64.encodestring(size_type).strip()] = size_body.xpath('./tr['+ str(type_num+1) +']/td['+ str(head_num+1) +']/text()').extract()[0]
    #                     size_chart['chart'].append(temp_dict)
    #                 final_chart_list.append(size_chart)
    #         item['size_chart'] = final_chart_list
    #         # print final_chart_list
    #         yield item
    #     else:
    #         yield item

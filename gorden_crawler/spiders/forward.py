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


# import json

class ForwardSpider(BaseSpider):
    name = "forward"
    allowed_domains = ["fwrd.com"]

    # 正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'http://www.fwrd.com/category-clothing/3699fc/',
        'http://www.fwrd.com/category-shoes/3f40a9/',
        'http://www.fwrd.com/category-bags/2df9df/',
        'http://www.fwrd.com/category-accessories/2fa629/',
        'http://www.fwrd.com/mens-category-clothing/15d48b/',
        'http://www.fwrd.com/mens-category-shoes/b05f2e/',
        'http://www.fwrd.com/mens-category-bags/6c97c1/',
        'http://www.fwrd.com/mens-category-accessories/8ad9de/',
    ]

    start_urls_map = {
        'http://www.fwrd.com/category-clothing/3699fc/': {'gender': 'women', 'product_type': 'clothing'},
        'http://www.fwrd.com/category-shoes/3f40a9/': {'gender': 'women', 'product_type': 'shoes'},
        'http://www.fwrd.com/category-bags/2df9df/': {'gender': 'women', 'product_type': 'bags'},
        'http://www.fwrd.com/category-accessories/2fa629/': {'gender': 'women', 'product_type': 'accessories'},
        'http://www.fwrd.com/mens-category-clothing/15d48b/': {'gender': 'men', 'product_type': 'clothing'},
        'http://www.fwrd.com/mens-category-shoes/b05f2e/': {'gender': 'men', 'product_type': 'shoes'},
        'http://www.fwrd.com/mens-category-bags/6c97c1/': {'gender': 'men', 'product_type': 'bags'},
        'http://www.fwrd.com/mens-category-accessories/8ad9de/': {'gender': 'men', 'product_type': 'accessories'},
    }

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield Request(url, dont_filter=True, cookies={'userLanguagePref':'en', 'path':'/', 'domain':'www.fwrd.com'})
    # 
    # def make_requests_from_url(self, url):
    #     return Request(url, dont_filter=True, cookies={'userLanguagePref':'en', 'path':'/', 'domain':'www.fwrd.com'})

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOADER_MIDDLEWARES': {
              # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,'
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyUSAMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    base_url = 'http://www.fwrd.com/'
    


    # 爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类


    def parse(self, response):
        sel = Selector(response)
        current_url = response.url
        gender = self.start_urls_map[current_url]['gender']
        product_type = self.start_urls_map[current_url]['product_type']
        category_lis = sel.xpath('//div[@class="fwd_left_navigation"]/div/ul/li[position()>1]')
        for category_li in category_lis:
            category = category_li.xpath('./a/text()').extract()[0].strip()
            cat_url = self.base_url + category_li.xpath('./a/@href').extract()[0].strip()
            yield Request(cat_url, callback=self.parse_list, meta={"gender": gender, "product_type": product_type, "category": category})

    def parse_list(self, response):
        sel = Selector(response)
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        category = response.meta['category']
        
        for item_li in sel.xpath('//li[@class="item altview_item"]'):
            item = BaseItem()
            item['type'] = 'base'
            item['gender'] = gender
            item['product_type'] = product_type
            item['category'] = category
            item['from_site'] = self.name
            item['url'] = self.base_url + item_li.xpath('./a/@href').extract()[0]
            item['cover'] = item_li.xpath('./a/div[@class="image_wrap"]/img[1]/@src').extract()[0]
            item['brand'] = item_li.xpath('./a/div[@class="info_wrap"]/div[@class="designer_brand"]/text()').extract()[0].strip()
            item['title'] = item_li.xpath('./a/div[@class="info_wrap"]/div[@class="product_name"]/text()').extract()[0].strip()
            if len(item_li.xpath('./a/div[@class="info_wrap"]/div[@class="price_box sale"]'))>0:
                list_pirce = item_li.xpath('./a/div[@class="info_wrap"]/div[@class="price_box sale"]/span[@class="price"]/text()').extract()[0].strip()
                current_price = item_li.xpath('./a/div[@class="info_wrap"]/div[@class="price_box sale"]/span[@class="discount_price"]/text()').extract()[0].strip()
            elif len(item_li.xpath('./a/div[@class="info_wrap"]/div[@class="price_box"]/span[@class="price"]/text()')) > 0:
                list_pirce = item_li.xpath('./a/div[@class="info_wrap"]/div[@class="price_box"]/span[@class="price"]/text()').extract()[0].strip()
                current_price = list_pirce
            elif len(item_li.xpath('./a/div[@class="info_wrap"]/div[@class="eagle"]/div[@class="prices sale"]'))>0:
                list_pirce = item_li.xpath('./a/div[@class="info_wrap"]/div[@class="eagle"]/div[@class="prices sale"]/span[@class="prices__retail-strikethrough"]/text()').extract()[0].strip()
                current_price = item_li.xpath('./a/div[@class="info_wrap"]/div[@class="eagle"]/div[@class="prices sale"]/span[@class="prices__markdown"]/text()').extract()[0].strip()
            else:
                list_pirce = item_li.xpath('./a/div[@class="info_wrap"]/div[@class="eagle"]/div[@class="prices"]/span/text()').extract()[0].strip()
                current_price = list_pirce
                
            if 'USD' in list_pirce:
                list_pirce = list_pirce.replace('USD', '')
            if 'USD' in current_price:
                current_price = current_price.replace('USD', '')
            url = item['url']
            yield Request(url, callback=self.parse_item, meta={'item': item})
            
        '''分页'''
        if 'pageNum' in str(response.url):
            current_page = re.search('pageNum=([\d]+)', str(response.url)).group(1)
        else:
            current_page = 1
        total_goods = sel.xpath('.//li[@class="spacer"]//span/text()').extract()[0]
        if 'Items' in total_goods:
            total_goods = total_goods.replace('Items', '')
        last_page = int(total_goods) / 96 + 1
        next_page = int(current_page) + 1
        if int(current_page) < int(last_page):
            if 'pageNum' in str(response.url):
                next_url = re.sub('pageNum=[\d]+', 'pageNum=' + str(next_page), str(response.url))
            else:
                if '?' not in response.url:
                    next_url = str(response.url) + '?pageNum=' + str(next_page)
                else:
                    next_url = str(response.url) + '&pageNum=' + str(next_page)
            yield Request(next_url, callback=self.parse_list, meta={'gender': gender, 'product_type': product_type, 'category': category}, cookies={'ckm-ctx-sf': '/'})

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        if len(sel.xpath('//div[@id="sold-out-div"]')) > 0:
            return

        if len(sel.xpath('//div[@class="price_box sale"]'))>0:
            list_pirce = sel.xpath('//div[@class="price_box sale"]/span[@class="price"]/text()').extract()[0].strip()
            current_price = sel.xpath('//div[@class="price_box sale"]/span[@class="discount_price"]/text()').extract()[0].strip()
            print 1111111111
        elif len(sel.xpath('//div[@class="price_box"]/span[@class="discount_price"]/text()')) > 0:
            list_pirce = sel.xpath('//div[@class="price_box"]/span[@class="discount_price"]/text()').extract()[0].strip()
            current_price = list_pirce
            print 2222222222222
        elif len(sel.xpath('//div[@id="tr-pdp-price--sale"]')) > 0:
            list_pirce = sel.xpath('//div[@id="tr-pdp-price--sale"]/span[@class="prices__retail-strikethrough u-margin-l--lg"]/text()').extract()[0]
            current_price = sel.xpath('//div[@id="tr-pdp-price--sale"]/span[@class="prices__markdown"]/text()').extract()[0]
            print 33333333333333
        elif len(sel.xpath('//div[@class="product_info"]/div[@class="eagle"]/div[@class="prices"]/span/text()'))>0:
            list_pirce = sel.xpath('//div[@class="product_info"]/div[@class="eagle"]/div[@class="prices"]/span/text()').extract()[0].strip()
            print list_pirce
            current_price = list_pirce
            print 444444444444444444
        else:
            return
        if 'USD' in list_pirce:
            list_pirce = list_pirce.replace('USD', '')
        if 'USD' in current_price:
            current_price = current_price.replace('USD', '')

        item['show_product_id'] = sel.xpath('//span[@id="find-your-size"]/a/@data-code').extract()[0]
        item['desc'] = sel.xpath('//div[@id="details"]/ul').extract()[0]
        item['dimensions'] = ['size', 'color']
        images = []
        image_divs = sel.xpath('.//div[@class="product-detail-image-zoom"]')
        for image_div in image_divs:
            imageItem = ImageItem()
            imageItem['image'] = image_div.xpath('./img/@src').extract()[0]
            imageItem['thumbnail'] = re.sub('fw/z', 'fw/p', imageItem['image'])
            images.append(imageItem)
        if not images:
            return
        color = Color()
        color['type'] = 'color'
        color['from_site'] = self.name
        color['show_product_id'] = item['show_product_id']
        color['images'] = images
        if len(sel.xpath('//select[@id="color-select"]'))>0:
            color_name = sel.xpath('//select[@id="color-select"]/option[1]/@value').extract()[0].strip()
            color['name'] = color_name
        else:
            color_name_ext = sel.xpath('//div[@class="color_dd"]/div[@class="title one_sizeonly"]/text()').extract()
            if color_name_ext:
                color_name = color_name_ext[0].strip()
            else:
                color_name = 'One Color'
            color['name'] = color_name
        cover = re.sub('fw/z', 'fw/c', images[0]['thumbnail'])
        color['cover'] = cover
        yield color
        
        skus = []
        sizes = []
        if len(sel.xpath('//div[@class="size_dd"]/div[@class="title one_sizeonly"]'))>0:
            skuItem = {}
            skuItem['type'] = "sku"
            skuItem['from_site'] = self.name
            size = sel.xpath('//div[@class="size_dd"]/div[@class="title one_sizeonly"]/text()').extract()[0].strip()
            skuItem['size'] = size
            sizes.append(size)
            skuItem['id'] = color_name + size
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['list_price'] = list_pirce
            skuItem['current_price'] = current_price
            skuItem['color'] = color_name
            skus.append(skuItem)
        else:
            for size_opt in sel.xpath('//select[@id="size-select"]/option[position()>1]'):
                skuItem = {}
                skuItem['type'] = "sku"
                skuItem['from_site'] = self.name
                size = size_opt.xpath('./@value').extract()[0].strip()
                skuItem['size'] = size
                sizes.append(size)
                skuItem['id'] = color_name + size
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['list_price'] = list_pirce
                skuItem['current_price'] = current_price
                skuItem['color'] = color_name
                if size_opt.xpath('./@data-is-oos').extract()[0] == 'true':
                    skuItem['is_outof_stock'] = True
                skus.append(skuItem)
        
        item['colors'] = [color_name]
        item['sizes'] = sizes
        item['skus'] = skus

        product_items = sel.xpath('//div[@id="style-with-slideshow"]/a')
        if len(product_items) > 0:
            related_items_id = []
            for product_item in product_items:
                product_id = product_item.xpath('./@href').extract()[0].split('/')[2]
                related_items_id.append(product_id)
            if related_items_id:
                item['related_items_id'] = related_items_id

        if len(sel.xpath('//a[@id="size_and_fit_link"]/@data-url'))>0:
            item['size_info'] = self.base_url + sel.xpath('//a[@id="size_and_fit_link"]/@data-url').extract()[0]
            size_chart_url = 'http://www.fwrd.com' + sel.xpath('//a[@id="size_and_fit_link"]/@data-url').extract()[0]
            yield Request(size_chart_url, callback=self.parse_size_chart, meta={'item': item}, dont_filter=True)
        else:
            item['size_info'] = ''
            yield item
        
    def parse_size_chart(self, response):
        sel = Selector(response)
        item = response.meta['item']
        size_chart = {}
        if len(sel.xpath('//table[@class="sizeguide_table"]'))>0:
            if len(sel.xpath('//table[@class="sizeguide_table"]'))>1:
                n = 1
            else:
                n = 0
            size_chart_name = response.url
            size_heads = sel.xpath('//table[@class="sizeguide_table"]')[n].xpath('./tr[1]/td[position()>1]/strong/text() | ./tr[1]/td[position()>1]/text()').extract()
            # print 'size_heads',size_heads
            size_head_one = sel.xpath('//table[@class="sizeguide_table"]')[n].xpath('./tr[1]/td[1]/strong/text() | ./tr[1]/td[1]/text()').extract()[0]
            size_body = sel.xpath('//table[@class="sizeguide_table"]')[n]
            size_types = sel.xpath('//table[@class="sizeguide_table"]')[n].xpath('./tr/td[1]/text() | ./tr/td[1]/strong/text()').extract()
            # print 'size_types', size_types
            size_chart['title'] = size_chart_name
            size_chart['chart'] = []
            for head_num, size_head in enumerate(size_heads):
                temp_dict={}
                temp_dict[base64.encodestring(size_head_one).strip()] = size_head
                for type_num, size_type in enumerate(size_types):
                    temp_dict[base64.encodestring(size_type).strip()] = size_body.xpath('./tr['+ str(type_num+1) +']/td['+ str(head_num+2) +']/text() |./tr['+ str(type_num+1) +']/td['+ str(head_num+2) +']/strong/text()').extract()[0]
                size_chart['chart'].append(temp_dict)
            # if size_chart['chart'] == []:
            #     print 'url:  ', item['url']
            #     print 'size_chart:  ', response.url
            item['size_chart'] = size_chart
        yield item        
            
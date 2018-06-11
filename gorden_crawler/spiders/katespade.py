# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from gorden_crawler.spiders.shiji_base import BaseSpider

import re
# import execjs
# import json

class KatespadeSpider(BaseSpider):
    name = "katespade"
    allowed_domains = ["katespade.com"]

    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        #'DOWNLOAD_DELAY': 1,
        'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyHttpsMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'https://www.katespade.com/handbags/view-all/',
        'https://www.katespade.com/clothing/view-all/',
        'https://www.katespade.com/shoes/view-all/',
        'https://www.katespade.com/accessories/',
        'https://www.katespade.com/sale/view-all/'
        ]

    product_type_urls_mapping = {
        'https://www.katespade.com/handbags/view-all/': {'product_type': 'handbags'},
        'https://www.katespade.com/clothing/view-all/': {'product_type': 'clothing'},
        'https://www.katespade.com/shoes/view-all/': {'product_type': 'shoes'},
        'https://www.katespade.com/accessories/': {'product_type': 'accessories'},
    }

    base_url = 'https://www.katespade.com/'
    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)
        response_url = response.url
        if response_url == 'https://www.katespade.com/sale/view-all/':
            product_type_lis = sel.xpath('//ul[@id="category-level-1"]/li')[2:]
            for product_type_li in product_type_lis:
                product_type_url = product_type_li.xpath('.//a/@href').extract()[0]
                product_type = product_type_li.xpath('.//span/text()').extract()[0]
                category = product_type
                yield Request(product_type_url, callback=self.parse_list, meta={'category':category, 'product_type': product_type})
        else:
            product_type = self.product_type_urls_mapping[response.url]['product_type']
            if product_type == 'accessories':
                category_lis = sel.xpath('//ul[@id="category-level-1"]/li')
            else:
                category_lis = sel.xpath('//ul[@id="category-level-1"]/li')[1:]
            
            for category_li in category_lis:
                category_url = category_li.xpath('.//a/@href').extract()[0]
                category = category_li.xpath('.//span/text()').extract()[0]
                yield Request(category_url, callback=self.parse_list, meta={'category':category, 'product_type': product_type})

    def parse_list(self, response):
        sel = Selector(response)
        category = response.meta['category']
        product_type = response.meta['product_type']

        items_li = sel.xpath('//ul[@id="search-result-items"]/li[contains(@class, "grid-tile")]')
        baseItem = BaseItem()
        baseItem['type'] = 'base'
        baseItem['category'] = category
        baseItem['product_type'] = product_type
        baseItem['from_site'] = self.name
        baseItem['gender'] = 'women'
        if product_type == 'clothing':
            baseItem['size_info'] = 'https://www.katespade.com/katespade-sizechart-clothing.html?format=ajax&instart_disable_injection=true'
        elif product_type == 'shoes':
            baseItem['size_info'] = 'https://www.katespade.com/katespade-sizechart-shoes.html?format=ajax&instart_disable_injection=true'
        for item_li in items_li:
            product_name_div = item_li.xpath('.//div[contains(@class, "product-name")]')
            product_image_div = item_li.xpath('.//div[contains(@class, "product-image")]')
            baseItem['cover'] = product_image_div.xpath('./a/img')[1].xpath('./@src').extract()[0]
            baseItem['title'] = product_name_div.xpath('.//a/text()').extract()[0]
            uri = product_name_div.xpath('.//a/@href').extract()[0]
            url = self.base_url[:-1] + uri if uri[0] == '/' else self.base_url + uri
            baseItem['url'] = url
            
            yield Request(url, callback=self.parse_item, meta={'baseItem': baseItem})

    def parse_item(self, response):
        item = response.meta['baseItem']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, baseItem):
        sel = Selector(response) 
#         baseItem = response.meta['baseItem']
        if len(sel.xpath('//input[@id="pid"]/@value'))>0:
            product_id = sel.xpath('//input[@id="pid"]/@value').extract()[0]
        else:
            return
        if len(sel.xpath('//p[@class="not-available-msg out-of-stock"]'))>0:
            return
        if len(sel.xpath('//span[contains(@class, "price-standard")]'))> 0:
            baseItem['list_price'] = sel.xpath('.//span[@class="price-standard"]/text()').extract()[0]
            if len(sel.xpath('.//span[@class="price-sales"]/text()'))>0:
                baseItem['current_price'] = sel.xpath('.//span[@class="price-sales"]/text()').extract()[0]
            else:
                current_price= sel.xpath('.//span[@class="price-sales range-sale-price"]/text()').extract()[0]
                if '-' in current_price:
                    current_price = re.search('-\s*\$([\d\.]+)', current_price).group(1)
                baseItem['current_price'] = current_price
        else:
            if len(sel.xpath('.//span[@class="price-sales"]/text()'))>0:
                baseItem['list_price'] = sel.xpath('.//span[@class="price-sales"]/text()').extract()[0]
                baseItem['current_price'] = baseItem['list_price']
            else:
                if len(sel.xpath('.//span[@class="price-sales"]/text()'))>0:
                    baseItem['current_price'] = sel.xpath('.//span[@class="price-sales"]/text()').extract()[0]
                else:
                    current_price= sel.xpath('.//div[@class="product-price sale"]/div/text()').extract()[0].strip()
                    if '-' in current_price:
                        current_price = re.search('-\s*\$([\d\.]+)', current_price).group(1)
                    baseItem['current_price'] = current_price
                baseItem['list_price'] = baseItem['current_price']
        
        baseItem['show_product_id'] = product_id
        baseItem['dimensions'] = ['size', 'color']
        baseItem['brand'] = 'katespade'
        desc_list = sel.xpath('//div[@class="description-details"]').extract()
        if len(desc_list) == 0:
            baseItem['desc'] = sel.xpath('//div[@class="description-details one-column"]').extract()[0]
        else:
            baseItem['desc'] = desc_list[0]
        
        sizes_tmp = sel.xpath('//ul[contains(@class, "swatches size")]/li[@class="emptyswatch"]/a/text()').re('(.+)')      
        if len(sizes_tmp) == 0:
            sizes = ['one-size'] 
        else:
            sizes = sizes_tmp  
        baseItem['sizes'] = sizes

        skus = []

        images = []
        thumbnail_lis = sel.xpath('//ul[@id="thumbnail-carousel"]/li')
        for thumbnail_li in thumbnail_lis:
            imageItem = ImageItem()            
            thumbnail = thumbnail_li.xpath('.//img[contains(@class, "productthumbnail")]/@src').extract()
            if len(thumbnail) > 0:
                imageItem['thumbnail']=thumbnail[0]
            imageItem['image'] = thumbnail_li.xpath('./a/@href').extract()[0]
            images.append(imageItem)

        color_lis = sel.xpath('//ul[contains(@class, "swatches Color clearfix")]/li')
        if len(color_lis) > 1:
            color_lis = color_lis[:-1]
        
        if len(color_lis) == 0:
            color_lis = ['one-color-li']
            baseItem['colors'] = ['one-color']

            for color_li in color_lis:
                colorItem = Color()
                colorItem['show_product_id'] = product_id
                colorItem['type'] = 'color'
                colorItem['from_site'] = 'katespade'
                colorItem['name'] = 'one-color'  
                colorItem['images'] = images
                yield colorItem

                for size in sizes:
                    skuItem = SkuItem()
                    skuItem['show_product_id'] = product_id
                    skuItem['type'] = 'sku'
                    skuItem['from_site'] = 'katespade'
                    skuItem['id'] = colorItem['name']+'-'+size
                    skuItem['current_price'] = baseItem['current_price']
                    skuItem['list_price'] = baseItem['list_price']
                    skuItem['is_outof_stock'] = False
                    skuItem['color'] = colorItem['name']
                    skuItem['size'] = size
                    skus.append(skuItem)
                    
            baseItem['skus'] = skus
            yield baseItem
        else:
            baseItem['colors'] = color_lis.xpath('.//span[@class="title"]/text()').extract() 
            
            # for color_li in color_lis:
            colorItem = Color()
            colorItem['show_product_id'] = product_id
            colorItem['type'] = 'color'
            colorItem['from_site'] = 'katespade'
            color_selected = sel.xpath('//ul[contains(@class, "swatches Color clearfix")]/li[@class="selected"]')
            if len(color_selected) == 0:
                colorItem['name'] = sel.xpath('//ul[contains(@class, "swatches Color clearfix")]/li')[0].xpath('./span[@class="title"]/text()').extract()[0]
                colorItem['cover'] = sel.xpath('//ul[contains(@class, "swatches Color clearfix")]/li')[0].xpath('./a/img/@src').extract()[0] 
            else:
                colorItem['name'] = sel.xpath('//ul[contains(@class, "swatches Color clearfix")]/li[@class="selected"]')[0].xpath('./span[@class="title"]/text()').extract()[0]
                colorItem['cover'] = sel.xpath('//ul[contains(@class, "swatches Color clearfix")]/li[@class="selected"]')[0].xpath('./a/img/@src').extract()[0] 
            colorItem['images'] = images
            yield colorItem

            for size in sizes:
                skuItem = SkuItem()
                skuItem['show_product_id'] = product_id
                skuItem['type'] = 'sku'
                skuItem['from_site'] = 'katespade'
                skuItem['id'] = colorItem['name']+'-'+size
                skuItem['current_price'] = baseItem['current_price']
                skuItem['list_price'] = baseItem['list_price']
                skuItem['is_outof_stock'] = False
                skuItem['color'] = colorItem['name']
                skuItem['size'] = size
                skus.append(skuItem)

            color_lis_not_selected = sel.xpath('//ul[contains(@class, "swatches Color clearfix")]/li[@class="emptyswatch"]')
            if len(color_lis_not_selected) == 0 or (len(color_lis_not_selected)==1 and len(color_selected) == 0):
                baseItem['skus'] = skus
                yield baseItem
            else:
                # for color_li_not_selected in color_lis_not_selected:
                color_item_url = color_lis_not_selected[0].xpath('./a/@href').extract()[0]
                
                color_data = []
                
                for color_li in color_lis_not_selected:
                    color_data.append({
                        'name': color_li.xpath('./span[@class="title"]/text()').extract()[0],
                        'cover': color_li.xpath('./a/img/@src').extract()[0], 
                        'url': color_li.xpath('./a/@href').extract()[0]
                    })
                
                index = 0
                yield Request(color_item_url, callback=self.parse_color_item, meta={'baseItem':baseItem, 'skus': skus, 'color_data': color_data, 'index':index})

    #1,'one-color'    
    #2,'one kind of color'
    #3,'above one color'

    def parse_color_item(self, response):
        sel = Selector(response)
        baseItem = response.meta['baseItem']
        skus = response.meta['skus']
        color_data = response.meta['color_data']
        index = response.meta['index']

        images = []
        thumbnail_lis = sel.xpath('//ul[@id="thumbnail-carousel"]/li')
        for thumbnail_li in thumbnail_lis:
            imageItem = ImageItem()            
            thumbnail = thumbnail_li.xpath('.//img[contains(@class, "productthumbnail")]/@src').extract()
            if len(thumbnail) > 0:
                imageItem['thumbnail']=thumbnail[0]
            imageItem['image'] = thumbnail_li.xpath('./a/@href').extract()[0]
            images.append(imageItem)

        colorItem = Color()
        colorItem['show_product_id'] = baseItem['show_product_id']
        colorItem['type'] = 'color'
        colorItem['from_site'] = 'katespade'
        colorItem['name'] = color_data[index]['name']
        colorItem['cover'] = color_data[index]['cover']
        colorItem['images'] = images
        yield colorItem

        sizes_tmp = sel.xpath('//ul[contains(@class, "swatches size")]/li[@class="emptyswatch"]/a/text()').re('(.+)')
        if len(sizes_tmp) == 0:
            sizes = ['one-size'] 
        else:
            sizes = sizes_tmp  

        for size in sizes:
            skuItem = SkuItem()
            skuItem['show_product_id'] = sel.xpath('//input[@id="pid"]/@value').extract()[0]
            skuItem['type'] = 'sku'
            skuItem['from_site'] = 'katespade'
            skuItem['id'] = colorItem['name']+'-'+size
            skuItem['current_price'] = sel.xpath('.//span[@class="price-sales"]/text()').extract()[0]
            skuItem['list_price'] = baseItem['list_price']
            skuItem['is_outof_stock'] = False
            skuItem['color'] = colorItem['name']
            skuItem['size'] = size
            skus.append(skuItem)

        index = index + 1
        if (index) == len(color_data):
            baseItem['skus'] = skus
            yield baseItem
        else:
            color_item_url = color_data[index]['url']
            yield Request(color_item_url, callback=self.parse_color_item, meta={'baseItem':baseItem, 'skus': skus, 'color_data': color_data, 'index':index})




        


# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from gorden_crawler.spiders.shiji_base import BaseSpider
from scrapy.http import HtmlResponse
from scrapy import FormRequest
from unidecode import unidecode
import re
import execjs
import copy
import demjson
import requests
import base64
import json
import unicodedata
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
# import json

class LastcallSpider(BaseSpider):
    name = "lastcall"
    allowed_domains = ["lastcall.com"]

    # 正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'http://www.lastcall.com/Hers/Womens-Apparel/cat6150001_cat000001_cat000000/c.cat',
        'http://www.lastcall.com/Hers/Shoes/cat5730006_cat000001_cat000000/c.cat',
        'http://www.lastcall.com/Hers/Jewelry/cat5730008_cat000001_cat000000/c.cat',
        'http://www.lastcall.com/Hers/Handbags/cat5730007_cat000001_cat000000/c.cat',
        'http://www.lastcall.com/Hers/Accessories/cat7780000_cat000001_cat000000/c.cat',
        'http://www.lastcall.com/His/Mens-Apparel/cat5730010_cat000002_cat000000/c.cat',
        'http://www.lastcall.com/His/Shoes/cat5920005_cat000002_cat000000/c.cat',
        'http://www.lastcall.com/His/Accessories/cat5920002_cat000002_cat000000/c.cat',
        'http://www.lastcall.com/Hers/Kids/cat5960001_cat000001_cat000000/c.cat',
    ]

    start_urls_map = {
        'http://www.lastcall.com/Hers/Womens-Apparel/cat6150001_cat000001_cat000000/c.cat': {'gender': 'women', 'product_type': 'clothing'},
        'http://www.lastcall.com/Hers/Shoes/cat5730006_cat000001_cat000000/c.cat': {'gender': 'women', 'product_type': 'shoes'},
        'http://www.lastcall.com/Hers/Jewelry/cat5730008_cat000001_cat000000/c.cat': {'gender': 'women', 'product_type': 'accessories'},
        'http://www.lastcall.com/Hers/Handbags/cat5730007_cat000001_cat000000/c.cat': {'gender': 'women', 'product_type': 'bags'},
        'http://www.lastcall.com/Hers/Accessories/cat7780000_cat000001_cat000000/c.cat': {'gender': 'women', 'product_type': 'accessories'},
        'http://www.lastcall.com/His/Mens-Apparel/cat5730010_cat000002_cat000000/c.cat': {'gender': 'men', 'product_type': 'clothing'},
        'http://www.lastcall.com/His/Shoes/cat5920005_cat000002_cat000000/c.cat': {'gender': 'men', 'product_type': 'shoes'},
        'http://www.lastcall.com/His/Accessories/cat5920002_cat000002_cat000000/c.cat': {'gender': 'men', 'product_type': 'accessories'},
        'http://www.lastcall.com/Hers/Kids/cat5960001_cat000001_cat000000/c.cat': {'gender': 'kid-unisex', 'product_type': 'clothing'},
    }


    custom_settings = {
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        'DOWNLOAD_DELAY': 0.5,
        # 'DOWNLOADER_MIDDLEWARES': {
        #       # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,'
        #     'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
        #     'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
        #     'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
        #     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        # }
    }

    base_url = 'http://www.lastcall.com'

    # 爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)
        current_url = response.url
        gender = self.start_urls_map[current_url]['gender']
        product_type = self.start_urls_map[current_url]['product_type']
        if 'Kids' in response.url:
            category = product_type
            yield Request(response.url, callback=self.parse_list, meta={"gender": gender, "product_type": product_type, "category": category}, dont_filter=True)
        else:
            category_lis = sel.xpath('//a[@id="rootcatnav"]/parent::*/ul[@class="category-menu"]/li')
            for category_li in category_lis:
                category = category_li.xpath('.//a/text()').extract()[0].strip()
                cat_url = self.base_url + category_li.xpath('.//a/@href').extract()[0].strip()
                yield Request(cat_url, callback=self.parse_list, meta={"gender": gender, "product_type": product_type, "category": category})

    def parse_list(self, response):
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        category = response.meta['category']
        if 'current_page' not in response.meta.keys():
            sel = Selector(response)
            current_page = 0
            # item = BaseItem()
            # item['type'] = 'base'
            # item['gender'] = gender
            # item['product_type'] = product_type
            # item['category'] = category
            # item['from_site'] = 'lastcall'
            # product_lis = sel.xpath('//ul[@class="category-items"]/li[@class="category-item"]')
            # for product_li in product_lis:
            #     if len(product_li.xpath('.//div[@class="product-image-frame"]/a/@href')) == 0:
            #         continue
            #     url = self.base_url + product_li.xpath('.//div[@class="product-image-frame"]/a/@href').extract()[0]
            #     item['url'] = url
            #     item['cover'] = product_li.xpath('.//div[@class="product-image-frame"]/a/img/@src').extract()[0]
            #     if len(product_li.xpath('.//figcaption[@class="product-description"]//div[@class="productdesigner OneLinkNoTx"]/text()'))>0:
            #         item['brand'] = product_li.xpath('.//figcaption[@class="product-description"]//div[@class="productdesigner OneLinkNoTx"]/text()').extract()[0].strip()
            #     else:
            #         item['brand'] = self.name
            #     item['title'] = product_li.xpath('.//figcaption[@class="product-description"]//div[@class="productname hasdesigner OneLinkNoTx"]/h2/text()').extract()[0].strip()
            #     yield Request(url, callback=self.parse_item, meta={"item": item})
            
            definitionPath = re.search('nm\.filters\.pageDefinitionPath\s*=\s*\'(.+)\'\;', response.body).group(1)
            categoryId = sel.xpath('//div[@id="endecaContent"]/@categoryid').extract()[0]
            total_goods = sel.xpath('.//span[@id="numItems"]/text()').extract()[0]
            if 'items' in total_goods:
                total_goods = total_goods.replace('items', '')
            last_page = int(total_goods) / 30 + 1
            
        else:
            definitionPath = response.meta['definitionPath']
            categoryId = response.meta['categoryId']
            prev_page = response.meta['current_page']
            current_page = prev_page + 1
            body_str = response.body
            body_str = body_str.decode('cp1252')
            # nfkd_form = unicodedata.normalize('NFKD', body_str.decode('cp1252'))
            # body_str = u"".join([c for c in body_str if not unicodedata.combining(c)])
            # print response.body
            # body_str = unidecode(body_str)
            context = execjs.compile('''
                var body_json = %s;
                function getbodyjson(){
                    return body_json;
                }
            ''' % body_str)
            body_json = context.call('getbodyjson')
            last_page = int(body_json['GenericSearchResp']['totalPages'])
            sel = Selector(text=body_json['GenericSearchResp']['productResults'])
            item = BaseItem()
            item['type'] = 'base'
            item['gender'] = gender
            item['product_type'] = product_type
            item['category'] = category
            item['from_site'] = 'lastcall'
            product_lis = sel.xpath('//ul[@class="category-items"]/li[@class="category-item"]')
            for product_li in product_lis:
                if len(product_li.xpath('.//div[@class="product-image-frame"]/a/@href')) == 0:
                    continue
                url = self.base_url + product_li.xpath('.//div[@class="product-image-frame"]/a/@href').extract()[0]
                item['url'] = url
                # item['cover'] = product_li.xpath('.//div[@class="product-image-frame"]/a/img/@src').extract()[0]
                item['cover'] = product_li.xpath('.//div[@class="product-image-frame"]/a/img/@item-url').extract()[0]
                if len(product_li.xpath('.//figcaption[@class="product-description"]//div[@class="productdesigner OneLinkNoTx"]/text()'))>0:
                    item['brand'] = product_li.xpath('.//figcaption[@class="product-description"]//div[@class="productdesigner OneLinkNoTx"]/text()').extract()[0]
                else:
                    item['brand'] = self.name
                if len(product_li.xpath('.//figcaption[@class="product-description"]//div[@class="productname hasdesigner OneLinkNoTx"]/h2/text()'))>0:
                    item['title'] = product_li.xpath('.//figcaption[@class="product-description"]//div[@class="productname hasdesigner OneLinkNoTx"]/h2/text()').extract()[0]
                yield Request(url, callback=self.parse_item, meta={"item": item})
            
        request_data = json.dumps({"GenericSearchReq":{"pageOffset":str(current_page),"pageSize":"30","definitionPath":definitionPath,"rwd":"true","categoryId":str(categoryId)}})
        request_data = ''.join(request_data.split())
        request_data_bs64 = '$b64$' + base64.encodestring(str(request_data)).strip()
        request_data_bs64 = ''.join(request_data_bs64.split())
        if int(current_page) < int(last_page):
            yield FormRequest('http://www.lastcall.com/category.service?instart_disable_injection=true', callback=self.parse_list, formdata = {'data':request_data_bs64, 'service':'getCategoryGrid'}, meta={'gender': gender, 'product_type': product_type, 'category': category, 'current_page': current_page, 'definitionPath': definitionPath, 'categoryId': categoryId}, dont_filter=True)


    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        if len(sel.xpath('//p[@class="flag-sold-out"]/text()'))>0:
            return
        elif 'static_errorpage' in response.url:
            return
        if 'title' not in item.keys():
            item['title'] = sel.xpath('//h1[@class="product-name elim-suites"]/span/text()').extract()[0].strip()
        if len(sel.xpath('//div[@id="productDetails"]//div[@itemprop="description"]//ul'))>0:
            item['desc'] = sel.xpath('//div[@id="productDetails"]//div[@itemprop="description"]//ul').extract()[0]
        product_id = sel.xpath('//input[@name="itemId"]/@value').extract()[0]
        if 'prod' in product_id:
            product_id = product_id.replace('prod', '').strip()
        item['show_product_id'] = product_id
        item['dimensions'] = ['size', 'color']
        # item['title'] = sel.xpath('//h1[@itemprop="name"]/span/text()').extract()[0].strip()
        if len(sel.xpath('//span[@class="item-price"]/text()'))>0:
            list_price = sel.xpath('//span[@class="item-price"]/text()').extract()[0].strip()
        elif len(sel.xpath('//span[@class="pos1priceDisplayStyleOverride item-price"]/text()'))>0:
            list_price = sel.xpath('//span[@class="pos1priceDisplayStyleOverride item-price"]/text()').extract()[0].strip()
        elif len(sel.xpath('//span[@class="lbl_ItemPriceSingleItem product-price"]/text()'))>0:   
            list_price = sel.xpath('//span[@class="lbl_ItemPriceSingleItem product-price"]/text()').extract()[0].strip()
        elif len(sel.xpath('//p[@class="lbl_ItemPriceSingleItem product-price"]/text()'))>0:
            list_price = sel.xpath('//p[@class="lbl_ItemPriceSingleItem product-price"]/text()').extract()[0].strip()
        elif len(sel.xpath('//span[@class="pos1override item-price"]/text()')) > 0:
            list_price = sel.xpath('//span[@class="pos1override item-price"]/text()').extract()[0].strip()
        item['list_price'] = list_price
        if len(sel.xpath('//span[@class="promo-price"]/text()'))>0:
            current_price = sel.xpath('//span[@class="promo-price"]/text()').extract()[0].strip()
        elif len(sel.xpath('//span[@class="pos1priceDisplayStyleOverride item-price"]/text()'))>0:
            current_price = sel.xpath('//span[@class="pos1priceDisplayStyleOverride item-price"]/text()').extract()[0].strip()
        elif len(sel.xpath('//span[@class="pos1override item-price"]/text()')) > 0:
            current_price = sel.xpath('//span[@class="pos1override item-price"]/text()').extract()[0].strip()
        else:
            current_price = list_price
        item['current_price'] = current_price
        
        images = []
        if len(sel.xpath('//div[@class="alt-img-wrap"]'))>0:
            imageDom = sel.xpath('//div[@class="alt-img-wrap" and @prod-id="'+ 'prod' + item["show_product_id"] +'"]')
            for dom in imageDom:
                imageItem = ImageItem()
                imageItem['image'] = dom.xpath("./img/@data-zoom-url").extract()[0]
                imageItem['thumbnail'] = dom.xpath('./img/@src').extract()[0]
                if ('images.lastcall.com' in imageItem['image'] or 'lastcall.scene7.com' in imageItem['image']) and 'http:' not in imageItem['image']:
                    imageItem['image'] = 'http:' + imageItem['image']

                if ('images.lastcall.com' in imageItem['thumbnail'] or 'lastcall.scene7.com' in imageItem['thumbnail']) and 'http:' not in imageItem['thumbnail']:
                    imageItem['thumbnail'] = 'http:' + imageItem['thumbnail']
                images.append(imageItem.copy())
        else:
            imageDom = sel.xpath('//div[@class="img-wrap" and @prod-id="'+ "prod" + item['show_product_id'] +'"]')
            for dom in imageDom:
                imageItem = ImageItem()
                imageItem['image'] = dom.xpath("./img/@data-zoom-url").extract()[0]
                if 'z.jpg' in imageItem['image']:
                    imageItem['thumbnail'] = imageItem['image'].replace('z.jpg', 'g.jpg')
                else:
                    imageItem['thumbnail'] = dom.xpath('./img/@src').extract()[0]
                if ('images.lastcall.com' in imageItem['image'] or 'lastcall.scene7.com' in imageItem['image']) and 'http:' not in imageItem['image']:
                    imageItem['image'] = 'http:' + imageItem['image']

                if ('images.lastcall.com' in imageItem['thumbnail'] or 'lastcall.scene7.com' in imageItem['thumbnail']) and 'http:' not in imageItem['thumbnail']:
                    imageItem['thumbnail'] = 'http:' + imageItem['thumbnail']
                images.append(imageItem.copy())

        yielded_coloritems = False

        color_lis = sel.xpath('//ul[@id="color-pickers"]/li')
        for color_li in color_lis:
            yielded_coloritems = True
            colorItem = Color()
            colorItem['images'] = images
            colorItem['type'] = 'color'
            colorItem['from_site'] = item['from_site']
            colorItem['show_product_id'] = item['show_product_id']
            colorItem['name'] = color_li.xpath('./@data-color-name').extract()[0]
            colorItem['cover'] = self.base_url + color_li.xpath('.//img/@src').extract()[0]
            yield colorItem

        request_skudata = json.dumps({"ProductSizeAndColor":{"productIds": "prod" + product_id}})
        request_skudata = ''.join(request_skudata.split())
        request_skudata_bs64 = '$b64$' + base64.encodestring(str(request_skudata)).strip()
        request_skudata_bs64 = ''.join(request_skudata_bs64.split())
        yield FormRequest('http://www.lastcall.com/product.service?instart_disable_injection=true', callback=self.parse_skus, formdata = {'data': request_skudata_bs64}, meta={'item':item, 'images':images, 'yielded_coloritems': yielded_coloritems}, dont_filter=True)
        
    def parse_skus(self, response):
        item = response.meta['item']
        images = response.meta['images']
        yielded_coloritems = response.meta['yielded_coloritems']
        if 'errorpage' in response.url:
            return
        body_json = json.loads(response.body)
        detail_str = body_json['ProductSizeAndColor']['productSizeAndColorJSON']
        detail_json = json.loads(detail_str)
        # if len(detail_json) >1:
        #     print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!multi skus: ', body_json['ProductSizeAndColor']['productIds'] + item['url']
        color_names = []
        sizes = []
        item['skus'] = []
        for skus_detail in detail_json:
            for sku_detail in skus_detail['skus']:
                if 'color' in sku_detail.keys():
                    if re.findall('\?.+\?false', sku_detail['color']):
                        color_name = re.sub('\?.+\?false', '', sku_detail['color'])
                        # color_name = sku_detail['color'].replace('?1?false', '').strip()
                    elif '?' in sku_detail['color']:
                        print sku_detail['color']
                        raise NameError('colorname error ' + sku_detail['color'] + ' ' + item['url'])
                    else:
                        color_name = sku_detail['color'].strip()
                else:
                    color_name = 'One Color'

                if color_name not in color_names:
                    color_names.append(color_name)
                    
                if 'size' in sku_detail.keys() and sku_detail['size']:
                    size = sku_detail['size']
                else:
                    size = 'One Size'
                if size not in sizes:
                    sizes.append(size)
                
                skuItem = SkuItem()
                skuItem['type'] = 'sku'
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['list_price'] = item['list_price']
                skuItem['current_price'] = item['current_price']
                skuItem['color'] = color_name
                skuItem['size'] = size
                skuItem['id'] = sku_detail['sku']
                skuItem['from_site'] = item['from_site']
                skuItem['is_outof_stock'] = False
                if sku_detail['status'] != 'In Stock'  and sku_detail['status'] != 'InStock':
                    print 'stock status: ', sku_detail['status']
                    # skuItem['is_outof_stock'] = True
                item['skus'].append(skuItem)

        if not yielded_coloritems:
            for color_name in color_names:
                colorItem = Color()
                colorItem['images'] = images
                colorItem['type'] = 'color'
                colorItem['from_site'] = item['from_site']
                colorItem['show_product_id'] = item['show_product_id']
                colorItem['name'] = color_name
                if not images:
                    # raise Exception('no image url: ' + item['url'])
                    return
                colorItem['cover'] = images[0]['thumbnail']
                yield colorItem
        item['sizes'] = sizes
        item['colors'] = color_names
        yield item

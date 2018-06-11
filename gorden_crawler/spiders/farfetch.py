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
import demjson
import json
from scrapy.http import FormRequest
# import httplib
# import urllib
# import urllib2
# import requests

import json


class FarfetchSpider(BaseSpider):
    name = "farfetch"
    allowed_domains = ["farfetch.com"]

    # 正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'http://www.farfetch.com/shopping/women/items.aspx',
        'http://www.farfetch.com/shopping/kids/baby-girl-clothing-6/items.aspx',
        'http://www.farfetch.com/shopping/kids/baby-boy-clothing-5/items.aspx',
        'http://www.farfetch.com/shopping/kids/girls-clothing-4/items.aspx',
        'http://www.farfetch.com/shopping/kids/boys-clothing-3/items.aspx',
        'http://www.farfetch.com/shopping/kids/baby-girl-accessories-6/items.aspx',
        'http://www.farfetch.com/shopping/kids/baby-boy-accessories-5/items.aspx',
        'http://www.farfetch.com/shopping/kids/girls-accessories-1/items.aspx',
        'http://www.farfetch.com/shopping/kids/boys-accessories-3/items.aspx',
        'http://www.farfetch.com/shopping/kids/baby-boy-shoes-5/items.aspx',
        'http://www.farfetch.com/shopping/kids/baby-girl-shoes-6/items.aspx',
        'http://www.farfetch.com/shopping/kids/girls-shoes-4/items.aspx',
        'http://www.farfetch.com/shopping/kids/boys-shoes-3/items.aspx'
    ]

    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOAD_TIMEOUT': 50,
        'RETRY_TIMES': 30,
        'DOWNLOADER_MIDDLEWARES': {
            # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyHttpsMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    gender_list = ['Men', 'Women']

    base_url = 'http://www.farfetch.com'

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, cookies={'ckm-ctx-sf': '/'})

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, cookies={'ckm-ctx-sf': '/'})

    # 爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def parse(self, response):
        sel = Selector(response)
        current_url = response.url
        if 'kids' in current_url:
            gender = 'kids'
            if 'accessories' in current_url:
                product_type = 'accessories'
            elif 'shoes' in current_url:
                product_type = 'shoes'
            elif 'clothing' in current_url:
                product_type = 'clothing'
            yield Request(current_url, callback=self.parse_category, meta={'gender': gender, 'product_type': product_type}, cookies={'ckm-ctx-sf': '/'})
        else:
            navbar_list = sel.xpath(".//nav[@class='ff-nav ff-nav-bg']")[0:2]
            for navbar in navbar_list:
                gender_str = navbar.xpath("./ul[1]/li[1]/a/text()").extract()[0]
                for g in self.gender_list:
                    if g in gender_str:
                        gender = g
                navlist = navbar.xpath(".//li[@class=' ff-has-children']")[2:8]
                for nav in navlist:
                    nav_str = nav.xpath("./a/text()").extract()[0].strip()
                    if nav_str == 'Accessories':
                        catdom = nav.xpath("./ul/li[@class='col2']")
                    elif nav_str == 'Jewelry':
                        catdom = nav.xpath("./ul/li[@class='col2']")[:3]
                    else:
                        catdom = nav.xpath("./ul/li[@class='col2']")[0]

                    if type(catdom) == type(navlist):
                        for dom in catdom:
                            if len(dom.xpath('./ul/li[@class="ff-nav-title"]').extract()) == 0:
                                continue
                            catlist = dom.xpath("./ul/li[@class='']")
                            product_type = dom.xpath("./ul/li[@class='ff-nav-title']//span/text()").extract()[0].strip()
                            if product_type == 'HOME INTERIORS':
                                continue
                            for cat in catlist:
                                category = cat.xpath("./a/text()").extract()[0].strip()
                                if not category or 'All' in category or 'Sale' in category:
                                    continue

                                url = self.base_url + cat.xpath("./a/@href").extract()[0].strip()
                                yield Request(url, callback=self.parse_list, meta={'gender': gender, 'product_type': product_type, 'category': category}, cookies={'ckm-ctx-sf': '/'})
                    else:
                        dom = catdom
                        catlist = dom.xpath("./ul/li[@class='']")
                        product_type = dom.xpath("./ul/li[@class='ff-nav-title']//span/text()").extract()[0].strip()
                        if product_type == 'HOME INTERIORS':
                            continue
                        for cat in catlist:
                            category = cat.xpath("./a/text()").extract()[0].strip()
                            if 'All' in category or 'Sale' in category:
                                continue
                            url = self.base_url + cat.xpath("./a/@href").extract()[0].strip()
                            yield Request(url, callback=self.parse_list, meta={'gender': gender, 'product_type': product_type, 'category': category}, cookies={'ckm-ctx-sf': '/'})

    def parse_category(self, response):
        sel = Selector(response)
        product_type = response.meta['product_type']
        gender = response.meta['gender']
        catlist = sel.xpath(".//ul[@class='facet-content accordion-content tree']/li[@class!='facets-clear align-right color-medium-grey js-lp-filter-clear hide']/a")
        for cat in catlist:
            cat_url = self.base_url + cat.xpath("./@href").extract()[0].strip()
            for catname in cat.xpath("./text()").extract():
                if catname.strip() != '':
                    category = catname.strip()
            if '/items.aspx' in cat_url:
                continue
            yield Request(cat_url, callback=self.parse_list, meta={'gender': gender, 'product_type': product_type, 'category': category}, cookies={'ckm-ctx-sf': '/'})

    def parse_list(self, response):
        sel = Selector(response)
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        category = response.meta['category']
        goods_jsons = re.search('window\.universal_variable\.listing[\s]*=[\s]*(.+);[\s]+</script>', response.body).group(1)
        goods_jsons = unicode(goods_jsons, errors='replace')
        if len(goods_jsons) > 0:
            context = execjs.compile('''
                var skus = %s;
                function getDetails(){
                    return skus;
                }
            ''' % goods_jsons)
            goods_details = context.call('getDetails')
        else:
            return
        items_details = goods_details['items']

        for item_detail in items_details:
            item = BaseItem()
            item['type'] = 'base'
            item['cover'] = item_detail['image_url']
            url = self.base_url + item_detail['url']
            item['url'] = url
            item['show_product_id'] = item_detail['id']
            item['brand'] = item_detail['designerName']
            item['title'] = item_detail['name']
            item['list_price'] = item_detail['unit_price']
            item['current_price'] = item_detail['unit_sale_price']
            if item_detail['color'] == "":
                item['colors'] = ["One Color"]
            else:
                item['colors'] = [item_detail['color']]
            item['gender'] = gender
            item['product_type'] = product_type
            item['category'] = category
            item['from_site'] = self.name
            yield Request(url, callback=self.parse_item, meta={'item': item}, cookies={'ckm-ctx-sf': '/'})

        if 'page' in str(response.url):
            current_page = re.search('page=([\d]+)', str(response.url)).group(1)
        else:
            current_page = 1
        total_goods = sel.xpath('.//span[@class="js-lp-pagination-total"]/text()').extract()[0]
        last_page = int(total_goods) / 180 + 1
        next_page = int(current_page) + 1
        if int(current_page) < int(last_page):
            if 'page' in str(response.url):
                next_url = re.sub('page=[\d]+', 'page=' + str(next_page), str(response.url))
            else:
                if '?' not in response.url:
                    next_url = str(response.url) + '?page=' + str(next_page)
                else:
                    next_url = str(response.url) + '&page=' + str(next_page)
            yield Request(next_url, callback=self.parse_list, meta={'gender': gender, 'product_type': product_type, 'category': category}, cookies={'ckm-ctx-sf': '/'})

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        if len(sel.xpath(".//div[@class='field mb20 mt20 detail-info-outStock']").extract()) > 0 or len(sel.xpath(".//div[@class='soldOut color-red bold h4']")) > 0:
            return
        if len(sel.xpath(".//span[@itemprop='sku']/text()")) == 0:
            return
        if 'show_product_id' not in item.keys():
            item['show_product_id'] = sel.xpath(".//span[@itemprop='sku']/text()").extract()[0]
        item['desc'] = sel.xpath(".//div[@data-tstid='Content_Composition&Care']/dl").extract()[0]
        item['dimensions'] = ['size', 'color']
        if len(sel.xpath(".//a[@data-target='.sizeGuideModal']/@href").extract()) > 0:
            item['size_info'] = self.base_url + sel.xpath(".//a[@data-target='.sizeGuideModal']/@href").extract()[0]

        product_json = re.search('window\.universal_variable\.product[\s]*=[\s]*(.+)[\s]*</script>', response.body).group(1)
        product_json = unicode(product_json, errors='replace')
        if len(product_json) > 0:
            context = execjs.compile('''
                var skus = %s;
                function getDetail(){
                    return skus;
                }
            ''' % product_json)
            goods_detail = context.call('getDetail')

            categoryId = goods_detail['categoryId']
            designerId = goods_detail['manufacturerId']
            productId = goods_detail['id']
            storeId = goods_detail['storeId']
            if goods_detail['color'] == "":
                color_name = "One Color"
            else:
                color_name = goods_detail['color']
            list_price = goods_detail['unit_price']
            current_price = goods_detail['unit_sale_price']
        else:
            return

        images = []
        image_lis = sel.xpath('.//ul[@class="sliderProduct js-sliderProduct js-sliderProductPage"]/li')
        for image_li in image_lis:
            imageItem = ImageItem()
            imageItem['image'] = image_li.xpath('./a/img/@data-zoom-image').extract()[0]
            imageItem['thumbnail'] = image_li.xpath('./a/img/@data-large').extract()[0]
            images.append(imageItem)
        if images == []:
            return
        color = Color()
        color['type'] = 'color'
        color['from_site'] = self.name
        color['show_product_id'] = item['show_product_id']
        color['images'] = images
        color['name'] = color_name
        cover = re.sub('_480\.jpg', '_70.jpg', images[0]['thumbnail'])
        color['cover'] = cover
        yield color

        # data={'categoryId': str(categoryId), 'designerId': str(designerId), 'productId': str(productId), 'storeId': str(storeId)}
        # print data
        # {'storeId': '9446', 'categoryId': '135967', 'designerId': '4981', 'productId': '11497594'}
        # # url = 'https://us-il.proxymesh.com:31280'
        # # username = 'reeves'
        # # password = '11111111'
        # # password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        # # auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        # # opener = urllib2.build_opener(auth_handler)
        # #  # urllib2.install_opener(opener)
        # # 
        # # # opener = urllib2.build_opener()
        # # opener.addheaders.append(('Cookie', 'ckm-ctx-sf=/'))
        # # sku_resp = opener.open('http://www.farfetch.com/product/GetDetailState/', urllib.urlencode(data))
        # # sku_resp_str = sku_resp.read()
        # # sku_detail_str = json.loads(sku_resp_str)['Sizes'].strip()
        # if len(sku_resp_str) > 0:
        #     context = execjs.compile('''
        #         var skus = %s;
        #         function getDetail(){
        #             return skus;
        #         }
        #     ''' % sku_resp_str)
        #     sku_detail = context.call('getDetail')
        # print sku_detail
        detail_url = 'http://www.farfetch.com/product/GetDetailState?' + 'categoryId='+ str(categoryId) + '&designerId='+ str(designerId) + '&productId='+ str(productId) + '&storeId'+ str(storeId)

        yield Request(detail_url, callback=self.parse_sku, meta={'item': item, 'color_name': color_name, 'list_price': list_price, 'current_price': current_price}, cookies={'ckm-ctx-sf': '/'}, dont_filter=True)
        
        # print FormRequest._get_body(fr)
        
        # req = requests.post('http://www.farfetch.com/product/GetDetailState',
        #                     data={'categoryId': categoryId, 'designerId': designerId, 'productId': productId,
        #                           'storeId': storeId}, cookies={'ckm-ctx-sf': '/'})
        # 
        # try:
        #     sel_size = Selector(text=req.json()['Sizes'].strip())
        # except Exception, e:
        #     print e
        #     print req.text
        
    def parse_sku(self, response):
        item = response.meta['item']
        # sel = Selector(text=json.loads(response.body)['Sizes'])
        color_name = response.meta['color_name']
        current_price = response.meta['current_price']
        list_price = response.meta['list_price']
        skus = []
        sizes = []

        body_json = json.loads(response.body)
        sku_details = body_json['SizesInformationViewModel']['AvailableSizes']
        for sku_detail in sku_details:
            skuItem = {}
            skuItem['type'] = "sku"
            skuItem['from_site'] = self.name
            skuItem['size'] = sku_detail['Description']
            sizes.append(skuItem['size'])
            skuItem['id'] = item['show_product_id'] + skuItem['size']
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['current_price'] = sku_detail['PriceInfo']['Price']
            if not skuItem['current_price']:
                skuItem['current_price'] = current_price
            skuItem['list_price'] = sku_detail['PriceInfo']['FormatedPriceWithoutPromotion']
            if not skuItem['list_price']:
                skuItem['list_price'] = list_price
            skuItem['color'] = color_name
            skus.append(skuItem)

        item['colors'] = [color_name]
        item['sizes'] = sizes
        item['skus'] = skus
        yield item


        # current_store_size_lis = sel.xpath('.//ul[@id="detailSizeDropdown"]/li[@class="js-product-selecSize-dropdown"]')
        # other_store_size_lis = sel.xpath('.//ul[@id="detailSizeDropdown"]/li[@class="js-product-selecSize-dropdown-otherStoreAvailable"]')
        # if len(current_store_size_lis) > 0:
        #     for size_li in current_store_size_lis:
        #         size = size_li.xpath('./a/div[1]/span/text()').extract()[0].strip()
        #         sizes.append(size)
        #         skuItem = {}
        #         skuItem['type'] = "sku"
        #         skuItem['from_site'] = self.name
        #         skuItem['id'] = item['show_product_id'] + size
        #         skuItem['show_product_id'] = item['show_product_id']
        #         skuItem['list_price'] = list_price
        #         skuItem['current_price'] = current_price
        #         skuItem['color'] = color_name
        #         skuItem['size'] = size
        #         skus.append(skuItem)
        #
        # if len(other_store_size_lis) > 0:
        #     for size_li in other_store_size_lis:
        #         size = size_li.xpath('./a/div/div[1]/span/text()').extract()[0].strip()
        #         sizes.append(size)
        #         skuItem = {}
        #         skuItem['type'] = "sku"
        #         skuItem['from_site'] = self.name
        #         skuItem['id'] = item['show_product_id'] + size
        #         skuItem['show_product_id'] = item['show_product_id']
        #         skuItem['list_price'] = list_price
        #         skuItem['current_price'] = current_price
        #         skuItem['color'] = color_name
        #         skuItem['size'] = size
        #         skus.append(skuItem)
        #
        # item['colors'] = [color_name]
        # item['sizes'] = sizes
        # item['skus'] = skus
        # yield item



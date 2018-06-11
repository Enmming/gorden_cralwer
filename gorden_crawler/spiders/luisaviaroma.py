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


class LuisaviaromaSpider(BaseSpider):
    name = "luisaviaroma"
    allowed_domains = ["luisaviaroma.com"]

    # 正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'https://www.luisaviaroma.com/men/catalog/clothing/lang_ZH/lineid_1',
        'https://www.luisaviaroma.com/men/catalog/bags/view+all/lang_ZH/lineid_22/catid_0',
        'https://www.luisaviaroma.com/men/catalog/shoes/view+all/lang_ZH/lineid_4/catid_0',
        'https://www.luisaviaroma.com/men/catalog/accessories/view+all/lang_ZH/lineid_3/catid_0',
        'https://www.luisaviaroma.com/men/catalog/fine+jewelry/view+all/lang_ZH/lineid_101/catid_0',
        'https://www.luisaviaroma.com/men/catalog/fashion+jewelry/view+all/lang_ZH/lineid_102/catid_0',
        'https://www.luisaviaroma.com/men/catalog/sports++_and_++lifestyle/view+all/lang_ZH/lineid_103/catid_0',
        'https://www.luisaviaroma.com/women/catalog/clothing/lang_ZH/lineid_1',
        'https://www.luisaviaroma.com/women/catalog/bags/view+all/lang_ZH/lineid_22/catid_0',
        'https://www.luisaviaroma.com/women/catalog/shoes/view+all/lang_ZH/lineid_4/catid_0',
        'https://www.luisaviaroma.com/women/catalog/accessories/view+all/lang_ZH/lineid_3/catid_0',
        'https://www.luisaviaroma.com/women/catalog/fine+jewelry/view+all/lang_ZH/lineid_101/catid_0',
        'https://www.luisaviaroma.com/women/catalog/fashion+jewelry/view+all/lang_ZH/lineid_102/catid_0',
        'https://www.luisaviaroma.com/women/catalog/sports++_and_++lifestyle/view+all/lang_ZH/lineid_103/catid_0',
        'https://www.luisaviaroma.com/kids-boys/catalog/clothing/view+all/lang_ZH/lineid_1/catid_0',
        'https://www.luisaviaroma.com/kids-boys/catalog/shoes/view+all/lang_ZH/lineid_4/catid_0',
        'https://www.luisaviaroma.com/kids-boys/catalog/accessories/view+all/lang_ZH/lineid_3/catid_0',
        'https://www.luisaviaroma.com/kids-girls/catalog/clothing/view+all/lang_ZH/lineid_1/catid_0',
        'https://www.luisaviaroma.com/kids-girls/catalog/shoes/view+all/lang_ZH/lineid_4/catid_0',
        'https://www.luisaviaroma.com/kids-girls/catalog/accessories/view+all/lang_ZH/lineid_3/catid_0',
        'https://www.luisaviaroma.com/men/sale/clothing/lang_ZH/lineid_1',
        'https://www.luisaviaroma.com/men/sale/bags/lang_ZH/lineid_22',
        'https://www.luisaviaroma.com/men/sale/shoes/lang_ZH/lineid_4',
        'https://www.luisaviaroma.com/men/sale/accessories/lang_ZH/lineid_3',
        'https://www.luisaviaroma.com/men/sale/fashion+jewelry/lang_ZH/lineid_102',
        'https://www.luisaviaroma.com/men/sale/sports++_and_++lifestyle/lang_ZH/lineid_103',
        'https://www.luisaviaroma.com/women/sale/clothing/lang_ZH/lineid_1',
        'https://www.luisaviaroma.com/women/sale/bags/lang_ZH/lineid_22',
        'https://www.luisaviaroma.com/women/sale/shoes/lang_ZH/lineid_4',
        'https://www.luisaviaroma.com/women/sale/accessories/lang_ZH/lineid_3',
        'https://www.luisaviaroma.com/women/sale/fashion+jewelry/lang_ZH/lineid_102',
        'https://www.luisaviaroma.com/women/sale/sports++_and_++lifestyle/lang_ZH/lineid_103',
        'https://www.luisaviaroma.com/kids-boys/sale/clothing/lang_ZH/lineid_1',
        'https://www.luisaviaroma.com/kids-boys/sale/shoes/lang_ZH/lineid_4',
        'https://www.luisaviaroma.com/kids-boys/sale/accessories/lang_ZH/lineid_3',
        'https://www.luisaviaroma.com/kids-girls/sale/clothing/lang_ZH/lineid_1',
        'https://www.luisaviaroma.com/kids-girls/sale/shoes/lang_ZH/lineid_4',
        'https://www.luisaviaroma.com/kids-girls/sale/accessories/lang_ZH/lineid_3'
    ]

    start_urls_map = {
        'https://www.luisaviaroma.com/kids-boys/catalog/clothing/view+all/lang_ZH/lineid_1/catid_0': {'product_type': 'clothing', 'gender': 'boys'},
        'https://www.luisaviaroma.com/kids-boys/catalog/shoes/view+all/lang_ZH/lineid_4/catid_0': {'product_type': 'shoes', 'gender': 'boys'},
        'https://www.luisaviaroma.com/kids-boys/catalog/accessories/view+all/lang_ZH/lineid_3/catid_0': {'product_type': 'accessories', 'gender': 'boys'},
        'https://www.luisaviaroma.com/kids-girls/catalog/clothing/view+all/lang_ZH/lineid_1/catid_0': {'product_type': 'clothing', 'gender': 'girls'},
        'https://www.luisaviaroma.com/kids-girls/catalog/shoes/view+all/lang_ZH/lineid_4/catid_0': {'product_type': 'shoes', 'gender': 'girls'},
        'https://www.luisaviaroma.com/kids-girls/catalog/accessories/view+all/lang_ZH/lineid_3/catid_0': {'product_type': 'accessories', 'gender': 'girls'},
        'https://www.luisaviaroma.com/men/catalog/clothing/lang_ZH/lineid_1': {'product_type': 'clothing', 'gender': 'men'},
        'https://www.luisaviaroma.com/men/catalog/bags/view+all/lang_ZH/lineid_22/catid_0': {'product_type': 'bags', 'gender': 'men'},
        'https://www.luisaviaroma.com/men/catalog/shoes/view+all/lang_ZH/lineid_4/catid_0': {'product_type': 'shoes', 'gender': 'men'},
        'https://www.luisaviaroma.com/men/catalog/accessories/view+all/lang_ZH/lineid_3/catid_0': {'product_type': 'accessories', 'gender': 'men'},
        'https://www.luisaviaroma.com/men/catalog/fine+jewelry/view+all/lang_ZH/lineid_101/catid_0': {'product_type': 'accessories', 'gender': 'men'},
        'https://www.luisaviaroma.com/men/catalog/fashion+jewelry/view+all/lang_ZH/lineid_102/catid_0': {'product_type': 'accessories', 'gender': 'men'},
        'https://www.luisaviaroma.com/men/catalog/sports++_and_++lifestyle/view+all/lang_ZH/lineid_103/catid_0': {'product_type': 'sports&lifestyle', 'gender': 'men'},
        'https://www.luisaviaroma.com/women/catalog/clothing/lang_ZH/lineid_1': {'product_type': 'clothing', 'gender': 'women'},
        'https://www.luisaviaroma.com/women/catalog/bags/view+all/lang_ZH/lineid_22/catid_0': {'product_type': 'bags', 'gender': 'women'},
        'https://www.luisaviaroma.com/women/catalog/shoes/view+all/lang_ZH/lineid_4/catid_0': {'product_type': 'shoes', 'gender': 'women'},
        'https://www.luisaviaroma.com/women/catalog/accessories/view+all/lang_ZH/lineid_3/catid_0': {'product_type': 'accessories', 'gender': 'women'},
        'https://www.luisaviaroma.com/women/catalog/fine+jewelry/view+all/lang_ZH/lineid_101/catid_0': {'product_type': 'accessories', 'gender': 'women'},
        'https://www.luisaviaroma.com/women/catalog/fashion+jewelry/view+all/lang_ZH/lineid_102/catid_0': {'product_type': 'accessories', 'gender': 'women'},
        'https://www.luisaviaroma.com/women/catalog/sports++_and_++lifestyle/view+all/lang_ZH/lineid_103/catid_0': {'product_type': 'sports&lifestyle', 'gender': 'women'},
        'https://www.luisaviaroma.com/men/sale/clothing/lang_ZH/lineid_1': {'product_type': 'clothing', 'gender': 'men'},
        'https://www.luisaviaroma.com/men/sale/bags/lang_ZH/lineid_22': {'product_type': 'bags', 'gender': 'men'},
        'https://www.luisaviaroma.com/men/sale/shoes/lang_ZH/lineid_4': {'product_type': 'shoes', 'gender': 'men'},
        'https://www.luisaviaroma.com/men/sale/accessories/lang_ZH/lineid_3': {'product_type': 'accessories', 'gender': 'men'},
        'https://www.luisaviaroma.com/men/sale/fashion+jewelry/lang_ZH/lineid_102': {'product_type': 'accessories', 'gender': 'men'},
        'https://www.luisaviaroma.com/men/sale/sports++_and_++lifestyle/lang_ZH/lineid_103': {'product_type': 'sports&lifestyle', 'gender': 'men'},
        'https://www.luisaviaroma.com/women/sale/clothing/lang_ZH/lineid_1': {'product_type': 'clothing', 'gender': 'women'},
        'https://www.luisaviaroma.com/women/sale/bags/lang_ZH/lineid_22': {'product_type': 'bags', 'gender': 'women'},
        'https://www.luisaviaroma.com/women/sale/shoes/lang_ZH/lineid_4': {'product_type': 'shoes', 'gender': 'women'},
        'https://www.luisaviaroma.com/women/sale/accessories/lang_ZH/lineid_3': {'product_type': 'accessories', 'gender': 'women'},
        'https://www.luisaviaroma.com/women/sale/fashion+jewelry/lang_ZH/lineid_102': {'product_type': 'accessories', 'gender': 'women'},
        'https://www.luisaviaroma.com/women/sale/sports++_and_++lifestyle/lang_ZH/lineid_103': {'product_type': 'sports&lifestyle', 'gender': 'women'},
        'https://www.luisaviaroma.com/kids-boys/sale/clothing/lang_ZH/lineid_1': {'product_type': 'clothing', 'gender': 'boys'},
        'https://www.luisaviaroma.com/kids-boys/sale/shoes/lang_ZH/lineid_4': {'product_type': 'shoes', 'gender': 'boys'},
        'https://www.luisaviaroma.com/kids-boys/sale/accessories/lang_ZH/lineid_3': {'product_type': 'accessories', 'gender': 'boys'},
        'https://www.luisaviaroma.com/kids-girls/sale/clothing/lang_ZH/lineid_1': {'product_type': 'clothing', 'gender': 'girls'},
        'https://www.luisaviaroma.com/kids-girls/sale/shoes/lang_ZH/lineid_4': {'product_type': 'shoes', 'gender': 'girls'},
        'https://www.luisaviaroma.com/kids-girls/sale/accessories/lang_ZH/lineid_3': {'product_type': 'accessories', 'gender': 'girls'},
    }


    custom_settings = {
        # 'DOWNLOAD_DELAY': 0.2,
        'DOWNLOAD_TIMEOUT': 20,
        'RETRY_TIMES': 20,
        'DOWNLOAD_DELAY': 0.5,
        'COOKIES_ENABLED': True,
        'DOWNLOADER_MIDDLEWARES': {
              # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,'
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyHttpsMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    base_url = 'https://www.luisaviaroma.com'
    base_image_url = 'https://images.luisaviaroma.com/'

    # 爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, cookies={'LVR_UserData': 'cty=US&curr=USD&vcurr=USD&lang=ZH&Ver=4 '})

    def parse(self, response):
        sel = Selector(response)
        current_url = response.url
        gender = self.start_urls_map[current_url]['gender']
        product_type = self.start_urls_map[current_url]['product_type']
        categories_lis = sel.xpath('//ul[@class="ul_menucat"]/li[position()>1]')
        for cat in categories_lis:
            category = cat.xpath('./a/text()').extract()[0]
            cate_url = self.base_url + cat.xpath('./a/@href').extract()[0]
            if gender == 'men' or gender == 'women':
                yield Request(cate_url, callback=self.parse_category, cookies={'LVR_UserData': 'cty=US&curr=USD&vcurr=USD&lang=ZH&Ver=4 '}, meta={'gender': gender, 'product_type': product_type, 'category': category})
            else:
                yield Request(cate_url, callback=self.parse_list, cookies={'LVR_UserData': 'cty=US&curr=USD&vcurr=USD&lang=ZH&Ver=4 '}, meta={'gender': gender, 'product_type': product_type, 'category': category})

    def parse_category(self, response):
        sel = Selector(response)
        product_type = response.meta['product_type']
        gender = response.meta['gender']
        category = response.meta['category']
        if len(sel.xpath('//li[@class="ul_menucat ul_menusubcat"]')) > 0:
            for sub_cat_a in sel.xpath('//li[@class="ul_menucat ul_menusubcat"]/a'):
                sub_cat_url = self.base_url + sub_cat_a.xpath('./@href').extract()[0]
                sub_category = sub_cat_a.xpath('./span[@class="text"]/text()').extract()[0]
                yield Request(sub_cat_url, callback=self.parse_list, cookies={'LVR_UserData': 'cty=US&curr=USD&vcurr=USD&lang=ZH&Ver=4 '}, meta={'gender': gender, 'product_type': product_type, 'category': category, 'sub_category': sub_category})
        else:
            list_url = response.url
            yield Request(list_url, callback=self.parse_list, cookies={'LVR_UserData': 'cty=US&curr=USD&vcurr=USD&lang=ZH&Ver=4 '}, meta={'gender': gender, 'product_type': product_type, 'category': category}, dont_filter=True)

    def parse_list(self, response):
        sel = Selector(response)
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        category = response.meta['category']
        item = BaseItem()
        item['type'] = 'base'
        if 'sub_category' in response.meta.keys():
            sub_category = response.meta['sub_category']
            item['sub_category'] = sub_category
        item['gender'] = gender
        item['product_type'] = product_type
        item['category'] = category
        item['from_site'] = 'luisaviaroma'
        goods_list = sel.xpath('//div[@class="article  loaded-img-article"]')
        for goods in goods_list:
            item['brand'] = goods.xpath('.//span[@class="catalog__item__brand"]/span/text()').extract()[0]
            url = self.base_url + goods.xpath('./a/@href').extract()[0]
            item['url'] = url
            item['title'] = goods.xpath('.//span[@class="catalog__item__title"]/text()').extract()[0]
            # if len(goods.xpath('.//span[@class="prz_discount"]/text()')) > 0:
            #     current_price = goods.xpath('.//span[@class="prz_discount"]/text()').extract()[0].strip()
            # else:
            #     current_price = goods.xpath('.//span[@class="catalog__item__price__info"]/span/text()').extract()[0].strip()
            # if ' ' in current_price:
            #     current_price = "".join(current_price.split())
            # if len(goods.xpath('.//span[@class="discount_container catalog__item__price__inner"]')) > 0:
            #     if len(goods.xpath('.//span[@class="discount_container catalog__item__price__inner"]/span')) > 3:
            #         list_price = goods.xpath('.//span[@class="discount_container catalog__item__price__inner"]/span[2]').extract()[0]
            #     else:
            #         list_price = goods.xpath('.//span[@class="discount_container catalog__item__price__inner"]/span[1]').extract()[0]
            #     if '-' in list_price:
            #         list_price = re.sub('-', '', list_price)
            #     list_price = list_price.strip()
            # else:
            #     list_price = current_price
            # if ' ' in list_price:
            #     list_price = "".join(list_price.split())
            #
            # item['list_price'] = list_price
            # item['current_price'] = current_price
            item['cover'] = 'https:' + goods.xpath('.//span[@class="picture__container"]/img[1]/@src').extract()[0]
            yield Request(url, callback=self.parse_item, cookies={'LVR_UserData': 'cty=US&curr=USD&vcurr=USD&lang=ZH&Ver=4 '}, meta={"item": item})

        if len(sel.xpath('//a[@class="next_page"]')) > 0:
            next_url = self.base_url + sel.xpath('//a[@class="next_page"]/@href').extract()[0]
            if 'sub_category' in response.meta.keys():
                yield Request(next_url, callback=self.parse_list, cookies={'LVR_UserData': 'cty=US&curr=USD&vcurr=USD&lang=ZH&Ver=4 '}, meta={'gender': gender, 'product_type': product_type, 'category': category, 'sub_category': sub_category})
            else:
                yield Request(next_url, callback=self.parse_list, cookies={'LVR_UserData': 'cty=US&curr=USD&vcurr=USD&lang=ZH&Ver=4 '}, meta={'gender': gender, 'product_type': product_type, 'category': category})

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        detail_json_1 = re.search('<script\s*type=\"text/javascript\">[\s]*itemResponse\s*=\s*(.+)', response.body)
        detail_json_2 = re.search('<script[\s]*type=\"text/javascript\">[\s]*menuResponse[\s]*=.+\};[\s]*itemResponse[\s]*=(.+);', response.body)

        if detail_json_1 is None and detail_json_2 is not None:
            detail_json = detail_json_2
        elif detail_json_1 is not None and detail_json_2 is None:
            detail_json = detail_json_1
        elif detail_json_1 is None and detail_json_2 is None:
            return
        
        detail_json = detail_json.group(1)
        context = execjs.compile('''
            var skus = %s;
            function getDetails(){
                return skus;
            }
        ''' % detail_json)
        goods_json = context.call('getDetails')
        
        item['desc'] = goods_json['LongDescription']
        item['dimensions'] = ['size', 'color']
        item['show_product_id'] = 'ZH-' + goods_json['ItemKey']['ItemCode']
        if len(sel.xpath('//a[@id="sp_size_naz"]/text()'))>0:
            s_t = sel.xpath('//a[@id="sp_size_naz"]/text()').extract()[0]
            if s_t == '(S/M/L)' or s_t == '(I/II/III)':
                s_t = ''
            else:
                s_t = s_t.strip() + ' '
        else:
            s_t = ''
        # if '(' in s_t or ')' in s_t:
        #     s_t = s_t.replace('(','')
        #     s_t = s_t.replace(')','')
        # item['s_t'] = s_t
        if not goods_json['Pricing']:
            return
        for pricing in goods_json['Pricing']:
            for price in pricing['Prices']:
                if price['CurrencyId'] == 'USD':
                    list_price = price['ListPrice']
                    current_price = price['FinalPrice']
        sizes = []
        skus = []
        color_id_name = {}
        for ItemAvailability in goods_json['ItemAvailability']:
            if ItemAvailability['SizeValue'] not in sizes:
                if 'A' in ItemAvailability['SizeValue']:
                    sz = s_t + ItemAvailability['SizeValue'].replace("A", "Y")
                else:
                    sz = s_t + ItemAvailability['SizeValue']
                sizes.append(sz)
                for ColorAvailability in ItemAvailability['ColorAvailability']:
                    color_id_name[ColorAvailability['VendorColorId']] = ColorAvailability['ComColorDescription']
                    skuItem = {}
                    skuItem['type'] = "sku"
                    skuItem['from_site'] = self.name
                    skuItem['id'] = ItemAvailability['SizeValue'] + '-' + ColorAvailability['ComColorDescription']
                    skuItem['show_product_id'] = item['show_product_id']
                    skuItem['list_price'] = list_price
                    skuItem['current_price'] = current_price
                    skuItem['color'] = ColorAvailability['ComColorDescription']
                    skuItem['size'] = sz
                    skus.append(skuItem)

        color_ids = color_id_name.keys()
        images_temp = []
        cover_temp = ''
        for cid in color_ids:
            images_temp = []
            cover_temp = ''
            for ItemPhotos in goods_json['ItemPhotos']:
                if ItemPhotos['VendorColorId'] == cid:
                    imageItem = ImageItem()
                    imageItem['image'] = self.base_image_url + 'Big' + ItemPhotos['Path']
                    imageItem['thumbnail'] = self.base_image_url + 'Total' + ItemPhotos['Path']
                    images_temp.append(imageItem)
                    cover_temp = imageItem['thumbnail']
            if images_temp:
                break
        if not images_temp:
            return

        for color_id, color_name in color_id_name.items():
            images = []
            cover = ''
            color = Color()
            color['type'] = 'color'
            color['from_site'] = self.name
            color['show_product_id'] = item['show_product_id']
            for ItemPhotos in goods_json['ItemPhotos']:
                if ItemPhotos['VendorColorId'] == color_id:
                    imageItem = ImageItem()
                    imageItem['image'] = self.base_image_url + 'Big' + ItemPhotos['Path']
                    imageItem['thumbnail'] = self.base_image_url + 'Total' + ItemPhotos['Path']
                    if 'item_cover' not in dir():
                        item_cover = self.base_image_url + 'Medium' + ItemPhotos['Path']
                    images.append(imageItem)
                    if cover == '':
                        cover = imageItem['thumbnail']
            if not images and images_temp and cover_temp:
                images = images_temp
                cover = cover_temp
            color['images'] = images
            color['name'] = color_name
            color['cover'] = cover
            yield color

        if ('item_cover' in dir() and 'cover' in item.keys() and 'image/gif' in item['cover']) or ('item_cover' in dir() and 'cover' not in item.keys()):
            item['cover'] = item_cover
        item['colors'] = color_id_name.values()
        item['sizes'] = sizes
        item['skus'] = skus
        size_info_url = 'https://www.luisaviaroma.com/ItemSrv.ashx?itemRequest={%22SizeChart%22:true}'
        yield Request(size_info_url, callback=self.parse_size_info, cookies={'LVR_UserData': 'cty=US&curr=USD&vcurr=USD&lang=ZH&Ver=4 '}, meta={"item": item, 'SizeChartId': goods_json['SizeChartId']}, dont_filter=True)

    def parse_size_info(self, response):
        item = response.meta['item']
        SizeChartId = response.meta['SizeChartId']
        size_info_json = re.search('itemResponse=(.+);', response.body).group(1)
        context = execjs.compile('''
            var sizeinfo = %s;
            function getSizeinfo(){
                return sizeinfo;
            }
        ''' % size_info_json)
        size_info_all = context.call('getSizeinfo')
        for size_info in size_info_all:
            if size_info[0] == SizeChartId:
                has_chart = True
                size_chart = {}
                charts = []
                size_chart['title'] = size_info[1]
                size_len = len(size_info[8][0]) - 4
                for index in range(size_len):
                    temp_dict={}
                    for chart in size_info[8]:
                        if chart[index+4]:
                            temp_dict[base64.encodestring(chart[2]).strip()] = chart[index+4]
                    if temp_dict:
                        charts.append(temp_dict)
        # for temp_dict in charts:
        #     for temp in temp_dict.values():
        #         if temp:
        #             is_empty_dict = False
        #     if 'is_empty_dict' not in dir():
        #         charts.remove(temp_dict)
        if 'has_chart' in dir() and has_chart:
            size_chart['chart'] = charts
            item['size_chart'] = size_chart
        yield item

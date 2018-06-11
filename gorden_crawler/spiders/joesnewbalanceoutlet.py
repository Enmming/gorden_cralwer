# -*- coding: utf-8 -*-
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
import re
import execjs
from gorden_crawler.spiders.shiji_base import BaseSpider
import math
import logging
import json


class JoesnewbalanceoutletBaseSpider(object):

    name = 'joesnewbalanceoutlet'

    base_url = 'https://www.joesnewbalanceoutlet.com/'

    def handle_parse_item(self, response, item):
        if 'Error' in response.url:
            return
        sel = Selector(response)
        item['category'] = sel.xpath('//section[@id="Breadcrumbs"]/nav/a[last()]/text()').extract()[0]
        show_product_id = sel.xpath('//span[@id="Sku"]/text()').extract()[-1]
        details_str = ''.join(re.search('sf\.productDetail\.init\((\{[\s\S]+?\})\)\;', response.body).group(1))
        context = execjs.compile('''
            var skus = %s;
            function getSkus(){
                return skus;
            }
        ''' % details_str)
        item['skus'] = []
        details = context.call('getSkus')
        skus_json = details['variants']
        images_json = details['images']
        images = []
        sizes = []
        width = []
        dimensions_dict = {}
        is_in_stock = False
        for children in details['children']:
            if children['c'] == show_product_id:
                color_name = children['v']
                is_in_stock = True
        if not is_in_stock:
            return 
        list_price = ''.join(sel.xpath('//div[@id="Price"]/div[@class="floatLeft productPriceInfo"]/span[@class="origPrice"]//span/text()').extract()).strip()
        current_price = ''.join(sel.xpath('//div[@id="Price"]/span[@class="floatLeft productPrice  "]/text() | //div[@id="Price"]/span[@class="floatLeft productPrice  "]/span/text()').extract()).strip()
        if not list_price:
            list_price = ''.join(sel.xpath('//div[@id="Price"]//span/text()').extract()).strip()
            current_price = list_price
        for sku_json in skus_json:
            skuItem = {}
            skuItem['type'] = 'sku'
            skuItem['id'] = sku_json['v']
            skuItem['show_product_id'] = show_product_id
            skuItem['list_price'] = list_price
            skuItem['current_price'] = current_price
            skuItem['from_site'] = item['from_site']
            skuItem['is_outof_stock'] = False
            skuItem['size'] = {}
            for sku in sku_json['a']:
                if sku['n'] == 'custom.color':
                    skuItem['color'] = sku['v']
                else:
                    if sku['n'] not in dimensions_dict.keys():
                        dimensions_dict[sku['n']] = []
                    if sku['v'] not in dimensions_dict[sku['n']]:
                        dimensions_dict[sku['n']].append(sku['v'])
                    skuItem['size'][sku['n']] = sku['v']
                # if sku['n'] == 'size':
                #     skuItem['size']['size'] = sku['v']
                #     dimensions_dict['size'].append(sku['v'])
                # if sku['n'] == 'width':
                #     skuItem['size']['width'] = sku['v']
                #     dimensions_dict['width'].append(sku['v'])
            if skuItem['size']['size'] not in sizes:
                sizes.append(skuItem['size']['size'])
            if 'width' in skuItem['size'].keys() and skuItem['size']['width'] not in width:
                width.append(skuItem['size']['width'])

            item['skus'].append(skuItem)
        for img_json in images_json:
            if img_json['c'] == show_product_id:
                imageItem = ImageItem()
                imageItem['thumbnail'] = img_json['f']
                imageItem['image'] = img_json['f'][:img_json['f'].find('?')] + '?wid=1280&hei=900'
                images.append(imageItem)

        if not images:
            return
        colorItem = Color()
        colorItem['type'] = 'color'
        colorItem['from_site'] = item['from_site']
        colorItem['show_product_id'] = show_product_id
        colorItem['images'] = images
        colorItem['cover'] = images[0]['thumbnail']
        colorItem['name'] = color_name
        yield colorItem
        item['show_product_id'] = show_product_id
        item['dimensions'] = dimensions_dict.keys()
        if len(sel.xpath('//div[@id="Description"]/p/text()')) > 0:
            item['desc'] = sel.xpath('//div[@id="Description"]/p/text()').extract()[0].strip()
        else:
            item['desc'] = ''.join(sel.xpath('//ul[@class="productFeaturesDetails"]//li').extract()).strip()
        item['colors'] = [color_name]
        item['sizes'] = dimensions_dict
        yield item



class JoesnewbalanceoutletSpider(BaseSpider, JoesnewbalanceoutletBaseSpider):
#class zappoSpider(RedisSpider):
    name = "joesnewbalanceoutlet"
    allowed_domains = ["joesnewbalanceoutlet.com"]
    brand = 'New Balance'
    '''
    正式运行的时候，start_urls为空，通过传参数来进行，通过传递参数 -a 处理
    '''


    custom_settings = {
        # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'RETRY_TIMES': 10,
        'DOWNLOAD_TIMEOUT': 200
    }

    start_urls = (
        'https://www.joesnewbalanceoutlet.com/women/shoes/running',
        'https://www.joesnewbalanceoutlet.com/women/shoes/walking',
        'https://www.joesnewbalanceoutlet.com/women/shoes/cross-training',
        'https://www.joesnewbalanceoutlet.com/women/shoes/lifestyle',
        'https://www.joesnewbalanceoutlet.com/women/shoes/tennis',
        'https://www.joesnewbalanceoutlet.com/women/shoes/golf',
        'https://www.joesnewbalanceoutlet.com/women/shoes/team-sports',
        'https://www.joesnewbalanceoutlet.com/women/clothing/performance',
        'https://www.joesnewbalanceoutlet.com/women/clothing/casual',
        'https://www.joesnewbalanceoutlet.com/women/clothing/jackets',
        'https://www.joesnewbalanceoutlet.com/women/clothing/shorts-and-skirts',
        'https://www.joesnewbalanceoutlet.com/women/clothing/pants-and-tights',
        'https://www.joesnewbalanceoutlet.com/women/clothing/sport-bras',
        'https://www.joesnewbalanceoutlet.com/women/accessories/socks',
        'https://www.joesnewbalanceoutlet.com/women/accessories/insoles',
        'https://www.joesnewbalanceoutlet.com/women/accessories/bags',
        'https://www.joesnewbalanceoutlet.com/women/accessories/hats-and-gloves',
        'https://www.joesnewbalanceoutlet.com/women/accessories/hydration',
        'https://www.joesnewbalanceoutlet.com/women/accessories/shoe-laces',
        'https://www.joesnewbalanceoutlet.com/men/shoes/running',
        'https://www.joesnewbalanceoutlet.com/men/shoes/walking',
        'https://www.joesnewbalanceoutlet.com/men/shoes/cross-training',
        'https://www.joesnewbalanceoutlet.com/men/shoes/lifestyle',
        'https://www.joesnewbalanceoutlet.com/men/shoes/tennis',
        'https://www.joesnewbalanceoutlet.com/men/shoes/golf',
        'https://www.joesnewbalanceoutlet.com/men/shoes/team-sports',
        'https://www.joesnewbalanceoutlet.com/men/clothing/performance',
        'https://www.joesnewbalanceoutlet.com/men/clothing/casual',
        'https://www.joesnewbalanceoutlet.com/men/clothing/shorts',
        'https://www.joesnewbalanceoutlet.com/men/clothing/pants-and-tights',
        'https://www.joesnewbalanceoutlet.com/men/clothing/jackets',
        'https://www.joesnewbalanceoutlet.com/men/accessories/socks',
        'https://www.joesnewbalanceoutlet.com/men/accessories/insoles',
        'https://www.joesnewbalanceoutlet.com/men/accessories/bags',
        'https://www.joesnewbalanceoutlet.com/men/accessories/hats-and-gloves',
        'https://www.joesnewbalanceoutlet.com/men/accessories/hydration',
        'https://www.joesnewbalanceoutlet.com/men/accessories/shoe-laces',
        'https://www.joesnewbalanceoutlet.com/kids/boys/grade-school-shoes',
        'https://www.joesnewbalanceoutlet.com/kids/boys/pre-school-shoes',
        'https://www.joesnewbalanceoutlet.com/kids/boys/infant-shoes',
        'https://www.joesnewbalanceoutlet.com/kids/boys/tops',
        'https://www.joesnewbalanceoutlet.com/kids/boys/bottoms',
        'https://www.joesnewbalanceoutlet.com/kids/girls/grade-school-shoes',
        'https://www.joesnewbalanceoutlet.com/kids/girls/pre-school-shoes',
        'https://www.joesnewbalanceoutlet.com/kids/girls/infant-shoes',
        'https://www.joesnewbalanceoutlet.com/kids/girls/tops',
    )

    base_url = 'https://www.joesnewbalanceoutlet.com/'

    

    '''具体的解析规则'''
    def parse_item(self, response):

#         item = BaseItem()
#         item['type'] = 'base'
#         item['show_product_id'] = '1209118'
        item = response.meta['item']

        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        return JoesnewbalanceoutletBaseSpider.handle_parse_item(self, response, item)
      
    '''
    爬虫解析入口函数，用于解析丢入的第一个请求，一般是顶级目录页
    '''

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url + '/?PageSize=500')

    def parse(self, response):
        sel = Selector(response)
        current_url_split = response.url.split('/')
        if 'kids' in response.url:
            gender = current_url_split[4]
            product_type = current_url_split[5]
        else:
            gender = current_url_split[3]
            product_type = current_url_split[4]

        prod_divs = sel.xpath('//figure/div')
        for prod_div in prod_divs:
            item = BaseItem()
            item['type'] = 'base'
            item['product_type'] = product_type
            item['gender'] = gender
            item['title'] = prod_div.xpath('./a/@title').extract()[0]
            item['brand'] = self.brand
            item['show_product_id'] = prod_div.xpath('./a/@data-productcode').extract()[0]
            item['current_price'] = prod_div.xpath('./a/@data-price').extract()[0]
            list_price = ''.join(sel.xpath('//figure[1]//div[@class="productPriceContainer"]/div[@class="origPrice"]//span/text()').extract()).strip()
            if list_price:
                item['list_price'] = list_price
            else:
                item['list_price'] = item['current_price']
            item['cover'] = prod_div.xpath('./a/img/@src').extract()[0]
            item['from_site'] = self.name
            url = self.base_url + prod_div.xpath('./a/@href').extract()[0]
            item['url'] = self.base_url + prod_div.xpath('./a/@href').extract()[0]
            yield Request(url, callback=self.parse_item, meta={"item": item})


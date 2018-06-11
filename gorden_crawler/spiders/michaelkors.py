# -*- coding: utf-8 -*-
from scrapy.selector import Selector

from ..items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request, FormRequest
import re
import execjs
from ..spiders.shiji_base import BaseSpider
from urllib import quote


class MichaelkorsSpider(BaseSpider):
    name = "michaelkors"
    allowed_domains = ["michaelkors.com"]

    #正式运行的时候，start_urls为空，通过redis来喂养爬虫

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,

        'DOWNLOADER_MIDDLEWARES': {
            # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyWeeklyRandomHttpsMiddleware': 100,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    base_url = 'https://www.michaelkors.com'
    ajax_url = 'https://www.michaelkors.com/server/data/guidedSearch'
    image_url = 'https://michaelkors.scene7.com/is/image/'
    start_urls = ['https://www.michaelkors.com/']

    # 爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)

        gender_lis = sel.xpath('//ul[@class="main-navlist"]/li')[:2]
        if len(gender_lis) > 1:
            for gender_li in gender_lis:
                gender = gender_li.xpath('./div/a/text()').extract()[0].strip()
                product_type_lis = gender_li.xpath('./div/div/div/ul[2]/li')
                for product_type_li in product_type_lis:
                    if len(product_type_li.xpath('./div/a/text()')) > 0:
                        product_type = product_type_li.xpath('./div/a/text()').extract()[0].strip()
                        if product_type == 'MICHAEL KORS COLLECTION':
                            continue
                        category_lis = product_type_li.xpath('./div/div/ul/li')[2:]
                        for category_li in category_lis:
                            category = category_li.xpath('./div/a/text()').extract()[0].strip()
                            category_url = self.ajax_url + '?stateIdentifier=_' + quote(category_li.xpath('./div/a/@href').extract()[0].strip().split('_')[-1], safe='')
                            yield Request(category_url, callback=self.parse_list, meta={"category": category, "gender": gender, "product_type": product_type})
                    else:
                        for product_type_li_2 in product_type_li.xpath('./ul/li'):
                            product_type = product_type_li_2.xpath('./div/a/text()').extract()[0]
                            category = product_type
                            category_url = self.ajax_url + '?stateIdentifier=_' + quote(product_type_li_2.xpath('./div/a/@href').extract()[0].strip().split('_')[-1], safe='')
                            yield Request(category_url, callback=self.parse_list, meta={"category": category, "gender": gender, "product_type": product_type})

    def parse_list(self, response):
        category = response.meta['category']
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        sel = Selector(response)
        context = execjs.compile('''
            var data = %s
            function getDetail(){
                return data;
            }
        ''' % response.body)
        goods_json = context.call('getDetail')
        productList = goods_json['result']['productList']

        for goods_detail in productList:
            item = BaseItem()
            item['type'] = 'base'
            item['from_site'] = 'michaelkors'
            item['show_product_id'] = goods_detail['identifier']
            item['category'] = category
            item['product_type'] = product_type
            item['gender'] = gender
            item['url'] = self.base_url + goods_detail['seoURL']
            item['cover'] = self.image_url + goods_detail['media']['mediaSet']
            item['brand'] = 'Michael Kors'
            colors = []
            for color in goods_detail['variant_options']['colors']:
                colorItem = Color()
                images = []
                image_surfixes = goods_detail['media']['alternativeImages'][0]['allSuffixes'].split(',')
                for image_surfix in image_surfixes:
                    imageItem = ImageItem()
                    imageItem['image'] = color['imageUrl'].split('_')[0] + image_surfix + '?hei=1000'
                    imageItem['thumbnail'] = color['imageUrl'].split('_')[0] + image_surfix
                    images.append(imageItem)
                colorItem['images'] = images
                colorItem['type'] = 'color'
                colorItem['from_site'] = item['from_site']
                colorItem['show_product_id'] = item['show_product_id']
                colorItem['name'] = color['colorName']
                colors.append(color['colorName'])
                colorItem['cover'] = color['imageUrl']
                yield colorItem
            item['colors'] = colors
            yield Request(item['url'], callback=self.parse_item, meta={"item": item})

        if goods_json['result']['lastProduct'] < goods_json['result']['totalProducts']:
            for pagination in goods_json['pagination']:
                if pagination['type'] == 'next':
                    next_page_surfix = pagination['stateId']
                    next_url = self.ajax_url + '?stateIdentifier=' + quote(next_page_surfix, safe='')
                    yield Request(next_url, callback=self.parse_list, meta={"category": category, "gender": gender, "product_type": product_type})

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)

        goods_str = re.search('window.__INITIAL_STATE__ = ([\s\S]+?});', response.body).group(1)
        context = execjs.compile('''
            var data = %s
            function getDetail(){
                return data;
            }
        ''' % goods_str)
        goods_json = context.call('getDetail')
        goods_detail = goods_json['pdp']['product']
        desc = '' if not goods_detail['description'] else goods_detail['description']
        item['desc'] = 'DESIGN\n' + desc + '\nDETAILS\n' + goods_detail['richTextDescription']
        item['title'] = goods_detail['displayName']
        item['show_product_id'] = goods_detail['identifier']
        colors = []
        sizes = []
        skus = []
        for sku in goods_detail['SKUs']:
            skuItem = {}
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['id'] = sku['identifier']
            skuItem['color'] = sku['variant_values']['color']['displayName']
            if skuItem['color'] not in colors:
                colors.append(skuItem['color'])
            skuItem['size'] = sku['variant_values']['size']['displayName']
            if skuItem['size'] not in sizes:
                sizes.append(skuItem['size'])
            skuItem['from_site'] = 'michaelkors'
            skuItem['list_price'] = sku['prices']['listPrice']
            skuItem['current_price'] = sku['prices']['salePrice']
            skuItem['is_outof_stock'] = False
            skus.append(skuItem)
        if 'colors' not in item.keys():
            item['colors'] = colors
        item['sizes'] = sizes
        item['skus'] = skus
        yield item



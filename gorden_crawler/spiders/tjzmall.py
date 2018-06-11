# -*- coding: utf-8 -*-
from scrapy.selector import Selector

from ..items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request, FormRequest
import re
import execjs
from ..spiders.shiji_base import BaseSpider
from urllib import quote


class TjzmallSpider(BaseSpider):
    name = "tjzmall"
    allowed_domains = ["tjzmall.com"]

    #正式运行的时候，start_urls为空，通过redis来喂养爬虫

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
    }

    base_url = 'https://me.tjzmall.com'

    start_urls = [
        'http://me.tjzmall.com/default/',
        'http://me.tjzmall.com/default/jin-kou-shi-pin/cheng-ren-nai-fen.html',
        'http://me.tjzmall.com/default/shoes.html?cat=578'

    ]

    start_urls_gender_product_type_dict = {
        'http://me.tjzmall.com/default/jin-kou-shi-pin/cheng-ren-nai-fen.html': {'gender': 'unisex', 'product_type': u'食品饮料', 'category': u'成人奶粉'},
        'http://me.tjzmall.com/default/shoes.html?cat=578': {'gender': 'women', 'product_type': u'生活用品', 'category': u'卫生巾'}
    }

    # 爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)
        if response.url in self.start_urls_gender_product_type_dict.keys():
            category = self.start_urls_gender_product_type_dict[response.url]['category']
            gender = self.start_urls_gender_product_type_dict[response.url]['gender']
            product_type = self.start_urls_gender_product_type_dict[response.url]['product_type']
            yield Request(response.url, callback=self.parse_list, meta={"category": category, "gender": gender, "product_type": product_type}, dont_filter=True)

        nav_lis = sel.xpath('//div[@class="orderDivId orderDivShow"]/dl')[1:-1]
        for nav_li in nav_lis:
            product_type_as = nav_li.xpath('./dd/ul/li/strong/a')
            for index, product_type_a in enumerate(product_type_as):
                product_type = product_type_a.xpath('./text()').extract()[0].strip()
                if product_type == '按功效':
                    continue
                category_as = nav_li.xpath('./dd/ul/li/div[' + str(index+1) + ']/a')
                for category_a in category_as:
                    if '女' in product_type:
                        gender = 'women'
                    elif '男' in product_type:
                        gender = 'men'
                    elif '宝宝' in product_type:
                        gender = 'baby'
                    elif '婴儿' in product_type:
                        gender = 'baby'
                    elif '孕妇' in product_type:
                        gender = 'women'
                    else:
                        gender = 'unisex'
                    category = product_type + category_a.xpath('./text()').extract()[0].strip()
                    category_url = category_a.xpath('./@href').extract()[0]
                    yield Request(category_url, callback=self.parse_list, meta={"category": category, "gender": gender, "product_type": product_type})

    def parse_list(self, response):
        category = response.meta['category']
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        sel = Selector(response)

        product_lis = sel.xpath('//ul[contains(@class, "products-grid")]/li')

        for goods_detail in product_lis:
            item = BaseItem()
            item['type'] = 'base'
            item['from_site'] = 'tjzmall'
            item['category'] = category
            item['product_type'] = product_type
            item['gender'] = gender
            item['url'] = goods_detail.xpath('./h2/a/@href').extract()[0]
            item['cover'] = goods_detail.xpath('./a/img/@src').extract()[0]
            item['title'] = goods_detail.xpath('./h2/a/text()').extract()[0]
            yield Request(item['url'], callback=self.parse_item, meta={"item": item})

        if len(sel.xpath('//a[@class="next i-next"]')) > 0:
            next_url = sel.xpath('//a[@class="next i-next"]/@href').extract()[0]
            yield Request(next_url, callback=self.parse_list, meta={"category": category, "gender": gender, "product_type": product_type})

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)

        item['show_product_id'] = sel.xpath('//div[@class="product-shop"]/p[4]/span[2]/text()').extract()[0]
        if sel.xpath('//div[@class="product-shop"]/p[4]/span[2]/text()').extract()[0] == '本商品不支持货到付款':
            item['show_product_id'] = sel.xpath('//div[@class="product-shop"]/p[5]/span[2]/text()').extract()[0]

        item['brand'] = re.search('品牌</td><td>(.+)</td>', response.body).group(1)
        item['desc'] = []
        if len(sel.xpath('//div[@class="short-description"]/div/text()')) > 0:
            item['desc'] = sel.xpath('//div[@class="short-description"]/div/text()').extract()
        item['desc'] += sel.xpath('//div[@class="products-param"]/table').extract()
        item['desc'] += sel.xpath('//div[@class="std"]/img').extract()
        item['desc'] = ''.join(item['desc'])
        price = sel.xpath('//div[@class="product-shop"]/p[@class="regular-price"]/span/span/text()').extract()[0]
        colorItem = Color()
        images = []
        image_lis = sel.xpath('//div[@class="product-img-box"]/div[@class="more-views"]/ul/li')
        for image_li in image_lis:
            imageItem = ImageItem()
            imageItem['image'] = image_li.xpath('./a/@href').extract()[0]
            imageItem['thumbnail'] = imageItem['image'][:(imageItem['image'].find('image') + 6)] + '320x320/' +imageItem['image'][(imageItem['image'].find('image') + 6):]
            images.append(imageItem)
            if 'cover' not in colorItem.keys():
                colorItem['cover'] = image_li.xpath('./a/img/@src').extract()[0]
        colorItem['images'] = images
        colorItem['type'] = 'color'
        colorItem['from_site'] = item['from_site']
        colorItem['show_product_id'] = item['show_product_id']
        colorItem['name'] = 'One Color'
        yield colorItem

        skuItem = {}
        skuItem['type'] = 'sku'
        skuItem['show_product_id'] = item['show_product_id']
        skuItem['id'] = item['show_product_id'] + '-sku'
        skuItem['color'] = 'One Color'
        skuItem['size'] = 'One Size'
        skuItem['from_site'] = item['from_site']
        skuItem['current_price'] = price
        skuItem['list_price'] = price
        skuItem['is_outof_stock'] = False

        item['colors'] = ['One Color']
        item['sizes'] = ['One Size']
        item['skus'] = [skuItem]
        yield item



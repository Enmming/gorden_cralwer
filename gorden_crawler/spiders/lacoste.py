# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from gorden_crawler.spiders.shiji_base import BaseSpider
import re
import execjs
import json
import copy


class LacosteBaseSpider(object):
    def handle_parse_item(self, response, itemB):

        sel = Selector(response)
        itemB['show_product_id'] = sel.xpath('//input[@id="pid"]/@value').extract()[0]
        utagStr = re.search(r'(utag_data = \{.*?\};)', response.body)

        if utagStr == None:
            if len(sel.xpath(".//*[@id='longdescription']").extract()) > 0:
                itemB['title'] = sel.xpath(".//*[@id='longdescription']/div/h3/text()").extract()[0]
                # itemB['show_product_id'] = sel.xpath(".//*[@id='longdescription']/div/span/text()").extract()[0]
                itemB['desc'] = sel.xpath(".//*[@id='longdescription']/div/p/text()").extract()[0]
            else:
                itemB['title'] = sel.xpath(".//span[@itemprop='name']/text()").extract()[0]
                # itemB['show_product_id'] = sel.xpath(".//input[@id='pmid']/@value").extract()[0]
                itemB['desc'] = ''
        else:
            context = execjs.compile('''
                %s
                function getUtag(){
                    return utag_data;
                }
            ''' % utagStr.group(0))
            
            utag = json.loads(json.dumps(context.call('getUtag')))

            if not utag:
                return

            # itemB['show_product_id'] = utag['page']['productid']
            itemB['title'] = utag['page']['pagename']
            
            if 'description' in utag['page'].keys():
                itemB['desc'] = utag['page']['description']
            else:
                itemB['desc'] = '暂无'


        if len(sel.xpath(".//*[@id='js-sku-product']//div[@class='sku-product-price']//span").extract()) > 0:
            
            if len(sel.xpath("//div[@class='sku-product-price']//span[@itemprop='price']").extract()) > 0:
                itemB['current_price'] = sel.xpath("//div[@class='sku-product-price']//span[@itemprop='price']/text()").extract()[0]
            elif len(sel.xpath("//div[@class='sku-product-price']//span[contains(@class,'price-sales')]").re('[\d\.]+')) > 0:
                itemB['current_price'] = sel.xpath("//div[@class='sku-product-price']//span[contains(@class,'price-sales')]").re('[\d\.]+')[0]
            else:
                return
            
            
            standardPrice = sel.xpath(".//*[@id='js-sku-product']//span[@class='price-standard']/text()").extract()
            if len(standardPrice) > 0:
                itemB['list_price'] = standardPrice[0][1:]
            else:
                itemB['list_price'] = itemB['current_price']
        else:
            #\t\t\r\n\t\t\t\t$61.99 - $89.50\r\n\t\t\t
            product_price = sel.xpath(".//*[@id='js-sku-product']//div[@class='sku-product-price']/div/text()").extract()[0]
            prices = re.split(' - ', product_price.strip())
            itemB['current_price'] = prices[0][1:]
            itemB['list_price'] = prices[1][1:]

        if len(sel.xpath(".//div[@data-dialog-id='dialog-size-chart']/div[@class='sizeChart']/h1/text()").extract()) > 0:
            itemB['size_info'] = sel.xpath(".//div[@data-dialog-id='dialog-size-chart']/div[@class='sizeChart']/h1/text()").extract()[0]
        elif len(sel.xpath(".//div[@data-dialog-id='dialog-size-chart']/div[@class='sizeChart']/h2/text()").extract()) > 0:
            itemB['size_info'] = sel.xpath(".//div[@data-dialog-id='dialog-size-chart']/div[@class='sizeChart']/h2/text()").extract()[0]

        # colors and sizes
        itemB['dimensions'] = ['size']
        colorsDom = sel.xpath(".//*[@id='js-sku-product']//ul[@class='product-colors swiper-wrapper sku-product-colors']/li")
        
        if len(colorsDom.extract()) > 0:
            return self.parse_colors(colorsDom,itemB)
        else:
            colorItem = Color()
            colorItem['type'] = 'color'
            colorItem['from_site'] = itemB['from_site']
            colorItem['show_product_id'] = itemB['show_product_id']
            colorItem['name'] = sel.xpath(".//input[@name='selectedColor']/@value").extract()[0] if len(sel.xpath(".//input[@name='selectedColor']/@value").extract()) > 0 else 'One Color'
            colorItem['cover'] = ''
            itemB['colors'] = [colorItem['name']]
            return self.handle_parse_itemB(response, itemB, colorItem)

    def handle_parse_itemB(self, response, itemB, colorItem):
        sel = Selector(response)
        current_price_span = sel.xpath(".//span[@itemprop='price']/text()").extract()
        if len(current_price_span) > 0:
            itemB['current_price'] = current_price_span[0]
            standardPrice = sel.xpath(".//span[@class='price-standard']/text()").extract()
            if len(standardPrice) > 0:
                itemB['list_price'] = standardPrice[0][1:]
            else:
                itemB['list_price'] = itemB['current_price']
    
            imgDom = sel.xpath(".//div[@class='galeria swiper-wrapper']/div[@class='swiper-slide']")
            images = []
            if len(imgDom.extract()) > 0:
                for dom in imgDom:
                    imageItem = ImageItem()
                    img = dom.xpath("./span/span[1]/@data-src").extract()[0]
                    imageItem['image'] = re.sub(r'sw=(\d+)&sh=(\d+)','sw=1000&sh=1000',img)
                    imageItem['thumbnail'] = re.sub(r'sw=(\d+)&sh=(\d+)','sw=350&sh=350',img)
                    if colorItem['cover'] == '':
                        colorItem['cover'] = imageItem['thumbnail']
                    images.append(imageItem)
            colorItem['images'] = images
            yield colorItem
            sizesDom = sel.xpath(".//div[@class='swatches size']//select/option[@value]")
            sizes = []
            skus = []
            if len(sizesDom.extract()) > 0:
                for dom in sizesDom:
                    if len(re.findall(r'unavailable',dom.xpath("./text()").extract()[0])):
                        continue
    
                    size = dom.xpath("./@value").extract()[0]
                    if not (size in sizes):
                        sizes.append(size)
    
                    skuItem = {}
                    skuItem['type'] = 'sku'
                    skuItem['show_product_id'] = itemB['show_product_id']
                    skuItem['id'] = colorItem['name'] + '*' + str(itemB['show_product_id'])
                    skuItem['color'] = colorItem['name']
                    skuItem['size'] = size
                    skuItem['from_site'] = colorItem['from_site']
                    skuItem['list_price'] = itemB['list_price']
                    skuItem['current_price'] = itemB['current_price']
                    skuItem['is_outof_stock'] = False
                    
                    skus.append(skuItem)
            else:
                skuItem = {}
                skuItem['type'] = 'sku'
                skuItem['show_product_id'] = itemB['show_product_id']
                skuItem['id'] = colorItem['name']+'*'+str(itemB['show_product_id'])
                skuItem['color'] = colorItem['name']
                skuItem['from_site'] = colorItem['from_site']
                skuItem['list_price'] = itemB['list_price']
                skuItem['current_price'] = itemB['current_price']
                skuItem['is_outof_stock'] = False
                skuItem['size'] = 'one-size'
                skus.append(skuItem)
                sizes.append('one-size')
            itemB['sizes'] = list(set(sizes))
            itemB['skus'] = skus
            yield itemB


    def parse_colors(self,colorsDom,itemB):

        color_item_url_mapping = {}
        color_names = []
        for dom in colorsDom:
            colorItem = Color()
            colorItem['type'] = 'color'
            colorItem['from_site'] = itemB['from_site']
            colorItem['show_product_id'] = itemB['show_product_id']
            colorItem['name'] = dom.xpath("./a/@title").extract()[0]
            color_names.append(colorItem['name'])
            style = re.findall(r'url\((http://.*)\)',dom.xpath("./a/@style").extract()[0])
            if len(style) > 0:
                colorItem['cover'] = style[0]
            else:
                colorItem['cover'] = ''

            colorUrl = dom.xpath("./a/@data-href").extract()[0]
            
            color_item_url_mapping[colorUrl] = colorItem
        itemB['colors'] = color_names
        index = 0
        # import pdb;pdb.set_trace()
        url = color_item_url_mapping.keys()[index]
        yield Request(url, callback=self.parse_item_B, meta={"item":itemB, "color_item_url_mapping": color_item_url_mapping, 'index':index})
                    
    def parse_item_B(self, response):
        index = response.meta['index']
        item = response.meta['item']
        color_item_url_mapping = response.meta['color_item_url_mapping']
        colorItem = color_item_url_mapping.values()[index]
        if index == 0:
            skus = []
            sizes = []
        else:
            skus = response.meta['skus']
            sizes = response.meta['sizes']

        sel = Selector(response)

        current_price_span = sel.xpath(".//span[@itemprop='price']/text()").extract()
        
        if len(current_price_span) > 0:
            item['current_price'] = current_price_span[0]
            standardPrice = sel.xpath(".//span[@class='price-standard']/text()").extract()
            if len(standardPrice) > 0:
                item['list_price'] = standardPrice[0][1:]
            else:
                item['list_price'] = item['current_price']
    
            imgDom = sel.xpath(".//div[@class='galeria swiper-wrapper']/div[@class='swiper-slide']")
            images = []
            if len(imgDom.extract()) > 0:
                for dom in imgDom:
                    imageItem = ImageItem()
                    img = dom.xpath("./span/span[1]/@data-src").extract()[0]
                    imageItem['image'] = re.sub(r'sw=(\d+)&sh=(\d+)','sw=1000&sh=1000',img)
                    imageItem['thumbnail'] = re.sub(r'sw=(\d+)&sh=(\d+)','sw=350&sh=350',img)
                    if colorItem['cover'] == '':
                        colorItem['cover'] = imageItem['thumbnail']
                    images.append(imageItem)
            colorItem['images'] = images
            yield colorItem
            
            sizesDom = sel.xpath(".//div[@class='swatches size']//select/option[@value]")
            
            if len(sizesDom.extract()) > 0:
                for dom in sizesDom:
                    if len(re.findall(r'unavailable',dom.xpath("./text()").extract()[0])):
                        continue
    
                    size = dom.xpath("./@value").extract()[0]
                    if not (size in sizes):
                        sizes.append(size)
    
                    skuItem = {}
                    skuItem['type'] = 'sku'
                    skuItem['show_product_id'] = item['show_product_id']
                    skuItem['id'] = colorItem['name'] + '*' + str(item['show_product_id'])
                    skuItem['color'] = colorItem['name']
                    skuItem['size'] = size
                    skuItem['from_site'] = colorItem['from_site']
                    skuItem['list_price'] = item['list_price']
                    skuItem['current_price'] = item['current_price']
                    skuItem['is_outof_stock'] = False
                    
                    skus.append(skuItem)
            else:
                skuItem = {}
                skuItem['type'] = 'sku'
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['id'] = colorItem['name']+'*'+str(item['show_product_id'])
                skuItem['color'] = colorItem['name']
                skuItem['from_site'] = colorItem['from_site']
                skuItem['list_price'] = item['list_price']
                skuItem['current_price'] = item['current_price']
                skuItem['is_outof_stock'] = False
                skuItem['size'] = 'one-size'
                skus.append(skuItem)
                sizes.append('one-size')

            index = index + 1
            if index < len(color_item_url_mapping):
                url = color_item_url_mapping.keys()[index]
                yield Request(url, callback=self.parse_item_B, meta={'item': item, 'color_item_url_mapping': color_item_url_mapping, 'index': index, 'skus':skus, 'sizes': sizes})
            else:
                item['sizes'] = list(set(sizes))
                item['skus'] = skus
                yield item


class LacosteSpider(BaseSpider,LacosteBaseSpider):
    name = "lacoste"
    allowed_domains = ["lacoste.com"]
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'http://www.lacoste.com/us/'
        ]

    base_url = 'http://www.lacoste.com'
    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)

        gender_list = ['men', 'women', 'kids']
        menu_lis = sel.xpath(".//ul[@class='links-with-sub']/li")[1:4]
        if len(menu_lis.extract()) > 0:
            for menu_li in menu_lis:
                gender = menu_li.xpath('./section/a/text()').extract()[0].strip().lower()
                product_type_lis = menu_li.xpath('./section/div/div/div[@class="menu-stories"]/ul/li')
                for product_type_li in product_type_lis:
                    product_type = product_type_li.xpath('./h3/a/text()').extract()[0].strip().lower()
                    category_lis = product_type_li.xpath('./ul/li/h4/a')
                    if product_type in ['boys', 'girls', 'baby']:
                        gender = product_type
                    for category_li in category_lis:
                        category = category_li.xpath('./text()').extract()[0].strip()
                        if category == 'New Arrivals' or category == 'Best Sellers':
                            continue
                        category_url = self.base_url + category_li.xpath('./@href').extract()[0]
                        yield Request(category_url, callback=self.parse_list, meta={"gender": gender, "category": category, "product_type": product_type})

    def parse_list(self, response):
        category = response.meta['category']
        product_type = response.meta['product_type']
        gender = response.meta['gender']

        sel = Selector(response)

        listDom = sel.xpath(".//ul[@id='search-result-items']//div[@class='before']")
        if len(listDom) > 0:
            for dom in listDom:
                url = dom.xpath('./a/@href').extract()[0]
                cover = dom.xpath('.//img/@src').extract()[0]
                # url = 'http://www.lacoste.com/us/lacoste-live/women/shoes/lacoste-live-slip-on-rene-chunky-suede-leather-sneakers/30LEW0004.html?dwvar_30LEW0004_color=2D2'
                yield Request(url,callback=self.parse_item,meta={"gender":gender, "cover":cover,"url":url, "category":category,"product_type":product_type})

            nextPageDom = sel.xpath(".//div[@class='search-result-options top-page']/div/div/ul/li[last()]/a/span")

            if len(nextPageDom.extract()) > 0 and nextPageDom.xpath("./text()").extract()[0] == 'Next Page':
                nextPageUrl = nextPageDom.xpath("./parent::*/@href").extract()[0]
                yield Request(nextPageUrl, callback=self.parse_list, meta={"gender":gender, "category":category,"product_type":product_type})


    def parse_item(self, response):
        itemB = {}
        itemB['type'] = 'base'
        itemB['from_site'] = 'lacoste'
        itemB['brand'] = 'lacoste'
        itemB['gender'] = response.meta['gender']
        itemB['cover'] = response.meta['cover']
        itemB['url'] = response.meta['url']
        itemB['category'] = response.meta['category']
        itemB['product_type'] = response.meta['product_type']

        return self.handle_parse_item(response, itemB)

    def handle_parse_item(self, response, item):

        return LacosteBaseSpider.handle_parse_item(self, response, item)

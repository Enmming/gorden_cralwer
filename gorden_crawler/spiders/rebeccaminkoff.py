# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy import Request

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color

from scrapy.utils.response import get_base_url
from gorden_crawler.spiders.shiji_base import BaseSpider
import re
import execjs
import json


class RebeccaminkoffSpider(BaseSpider):
    name = "rebeccaminkoff"
    allowed_domains = ["rebeccaminkoff.com"]
    
    '''
    正式运行的时候，start_urls为空，通过传参数来进行，通过传递参数 -a 处理
    '''
    
    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_TIMEOUT': 180
    }
    
    start_urls =[ 
        'http://www.rebeccaminkoff.com/clothing/',
        'http://www.rebeccaminkoff.com/handbags/',
        'http://www.rebeccaminkoff.com/shoes/',
        'http://www.rebeccaminkoff.com/accessories/',
    ]


    url_gender_type = {
        'http://www.rebeccaminkoff.com/clothing/':{'gender':'women', 'product_type':'clothing'},
        'http://www.rebeccaminkoff.com/handbags/':{'gender':'women', 'product_type':'bags'},
        'http://www.rebeccaminkoff.com/shoes/':{'gender':'women', 'product_type':'shoes'},
        'http://www.rebeccaminkoff.com/accessories/':{'gender':'women', 'product_type':'accessories'},
    }


    base_url = 'http://www.rebeccaminkoff.com'


    def parse(self, response):
        sel = Selector(response)
        req_url = re.sub('&p=\w', '', response.url)
        req_url = "".join(req_url.split())
        if req_url[-1] != '/':
            req_url += '/'
        gender = self.url_gender_type[req_url]['gender']
        product_type = self.url_gender_type[req_url]['product_type']


        categoryList = sel.xpath('//dl[contains(@id, "narrow-by-list")]//dd[1]//ol[contains(@class, "m-filter-item-list ")]//li')
        for cat in categoryList:
            category = cat.xpath('.//a/@title').extract()[0]
            if category != "NEW ARRIVALS" and category != "SALE":
                url = cat.xpath('.//a/@href').extract()[0]
                yield Request(url, callback = self.parse_list, meta = {"category":category, "gender":gender, "product_type":product_type} )


    def parse_list(self, response):
        sel = Selector(response)
        category = response.meta['category']
        gender = response.meta['gender']
        product_type = response.meta['product_type']

        '''
        #use for test
        url = 'http://www.rebeccaminkoff.com/pygar-top-black'
        #url = 'http://www.rebeccaminkoff.com/aria-sweater'
        #url = 'http://www.rebeccaminkoff.com/india-drawstring-holiday-black'
        #url = 'http://www.rebeccaminkoff.com/india-drawstring-holiday'
        item = BaseItem()
        item['from_site'] = 'rebeccaminkoff'
        item['url'] = url
        item['cover'] = 'cover'
        item['gender'] = gender
        item['product_type'] = product_type
        item['category'] = 'category'

        yield Request(url, callback = self.parse_item, meta = { "item":item } )
        '''

        if sel.xpath('//div[contains(@class, "pages")]//ol//li//a[contains(@class, "next i-next")]'):
            next_url =  sel.xpath('//div[contains(@class, "pages")]//ol//li//a[contains(@class, "next i-next")]/@href').extract()[0]
            #print next_url
            yield Request(next_url, callback = self.parse_list, meta = { "category":category, 'gender': gender, 'product_type': product_type })

        listArr = sel.xpath('//ul[contains(@class, "products-grid products-grid--max-3-col")]//li[contains(@class, "item")]')
        for lists in listArr:
            if lists.xpath('.//a//img/@data-src'):
                url = lists.xpath('.//a/@href').extract()[0]
                cover = lists.xpath('.//a//img/@data-src').extract()[0]

                item = BaseItem()
                item['from_site'] = 'rebeccaminkoff'
                item['url'] = url
                item['cover'] = cover
                item['gender'] = gender
                item['product_type'] = product_type
                item['category'] = category

                yield Request(url, callback = self.parse_item, meta = { "item":item } )


    def parse_item(self, response):
        item = response.meta['item']

        return self.handle_parse_item(response, item)

        
    def handle_parse_item(self, response, item):
        sel = Selector(response)
        
        outof_stock_content = sel.xpath('//div[@class="item-availability"]/span[@class="out-of-stock"]').extract()
        
        if len(outof_stock_content) > 0:
            return

        title = sel.xpath('//div[contains(@class, "product-name")]//span/text()').extract()[0]
        show_product_id = sel.xpath('//div[contains(@class, "no-display")]//input[1]/@value').extract()[0]
        desc_tmp = sel.xpath('//div[contains(@class, "tab-content")]').extract()

        item['type'] = 'base'
        item['title'] = title
        item['show_product_id'] = show_product_id
        item['brand'] = 'Rebecca Minkoff'
        if len(desc_tmp) > 1:
            item['desc'] = '%s%s' % (desc_tmp[0], desc_tmp[1])
        else :
            item['desc'] = desc_tmp[0]

        if sel.xpath('//div[contains(@class, "price-box")]//span[contains(@class, "regular-price")]'):
            item['list_price'] = sel.xpath('//span[contains(@class, "regular-price")]//span/text()').extract()[0]
            item['current_price'] = item['list_price']
        else :
            item['list_price'] = sel.xpath('//p[contains(@class, "old-price")]//span[2]/text()').extract()[0]
            item['current_price'] = sel.xpath('//p[contains(@class, "special-price")]//span[2]/text()').extract()[0]
        
        ####
        if sel.xpath('//div[contains(@class, "product-options")]'):
            jsStr = "".join(re.findall(r'<script type="text/javascript">[\s]*(var spConfig.*;)[\s]*</script>[\s]*<script type="text/javascript">[\s]*\/\/', response.body, re.S))
            strInfo = "".join(re.findall(r'({.*})', jsStr, re.S))
            strJson = json.loads(strInfo)

            attributeID = sel.xpath('//dd//div[contains(@class, "input-box")]//select/@id').extract()
            colorID = attributeID[0].replace("attribute", "")

            col_name = {}
            colors = []
            if colorID not in strJson['attributes'].keys():
                return
            for col in strJson['attributes'][colorID]['options']:
                color_id = col['id']
                name = col['label']

                color = Color()
                for productID in col['products']:
                    col_name[productID] = name

                images = []
                first_thumb = ''
                for img in strJson['swatchImages'][col['products'][0]]['galleryImages']:
                    imageItem = ImageItem()

                    imageItem['image'] = img['url']
                    imageItem['thumbnail'] = img['thumb'] 
                    images.append(imageItem)
                    
                    if len(first_thumb) == 0:
                        first_thumb = img['thumb']

                if col['swatch']['img']:
                    color['cover'] = col['swatch']['img']
                elif col['swatch']['hex']:
                    #color['cover_style'] = 'background-color: #%s;' % (col['swatch']['hex'])
                    color['cover_style'] = '#' + col['swatch']['hex']
                else:
                    color['cover'] = first_thumb

                colors.append(name)

                color['type'] = 'color'
                color['show_product_id'] = show_product_id
                color['from_site'] = 'rebeccaminkoff'
                #color['cover'] = cover
                color['images'] = images
                color['name'] = name
                yield color

            skus = []
            sizes = []
            if len(attributeID) > 1:
                sizeID = attributeID[1].replace("attribute", "")
                for skuCol in strJson['attributes'][sizeID]['options']:
                    for sku_tmp in skuCol['products']:
                        skuItem = SkuItem()
                        skuItem['type'] = 'sku'
                        skuItem['show_product_id'] = show_product_id
                        skuItem['from_site'] = "rebeccaminkoff"
                        skuItem['id'] = sku_tmp
                        skuItem['list_price'] = strJson['oldPrice']
                        skuItem['current_price'] = strJson['basePrice']
                        skuItem['size'] = skuCol['label']
                        print col_name
                        if sku_tmp not in col_name:
                            continue
                        skuItem['color'] = col_name[sku_tmp]
                        skuItem['is_outof_stock'] = False
                        #skuItem['quantity'] = ''
                        sizes.append(skuCol['label'])
                        skus.append(skuItem)
            else :
                skus = []
                sizes = ['onesize']
                skuItem = SkuItem()
                skuItem['type'] = 'sku'
                skuItem['show_product_id'] = show_product_id
                skuItem['from_site'] = 'rebeccaminkoff'
                skuItem['id'] = show_product_id
                skuItem['list_price'] = item['list_price']
                skuItem['current_price'] = item['current_price']
                skuItem['size'] = 'onesize'
                skuItem['color'] = "onecolor"
                skuItem['is_outof_stock'] = False
                skus.append(skuItem)             

            item['skus'] = skus
            item['sizes'] = list(set(sizes))
            item['colors'] = list(set(colors))   

            yield item
        else:
            images = []
            for img in sel.xpath('//ul[contains(@class, "product-image-thumbs")]//li'):
                imageItem = ImageItem()
                img_tmp = img.xpath('.//a//img/@src').extract()[0]
                imageItem['image'] = img_tmp
                imageItem['thumbnail'] = img_tmp.replace('/thumbnail/', '/thumbnail/60x90/')
                images.append(imageItem)
            
            color = Color()
            color['type'] = 'color'
            color['show_product_id'] = show_product_id
            color['from_site'] = 'rebeccaminkoff'
            color['cover'] = images[0]['thumbnail']
            color['images'] = images
            color['name'] = 'onecolor'
            yield color

            skus = []
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = show_product_id
            skuItem['from_site'] = 'rebeccaminkoff'
            skuItem['id'] = show_product_id
            skuItem['list_price'] = item['list_price']
            skuItem['current_price'] = item['current_price']
            skuItem['size'] = 'onesize'
            skuItem['color'] = "onecolor"
            skuItem['is_outof_stock'] = False
            skus.append(skuItem) 

            item['skus'] = skus
            item['sizes'] = ['onesize']
            item['colors'] = ['onecolor']

            yield item
            
            





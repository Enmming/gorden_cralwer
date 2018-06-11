# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy import Request
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy.utils.response import get_base_url
from gorden_crawler.spiders.shiji_base import BaseSpider
import json
import re


class ThecornerBaseSpider(object):

    #handle
    def handle_parse_item(self, response, item):
        sel = Selector(response)
        if not sel.xpath('//div[contains(@class, "priceUpdater")]'):
            print get_base_url(response)
            return
        if not sel.xpath('//div[contains(@class, "brandName")]/text()'):
            print get_base_url(response)
            return
        if not sel.xpath('//span[contains(@class, "price")]//span[2]'):
            print get_base_url(response)
            return
        baseItem = item
        brand = sel.xpath('//div[contains(@class, "brandName")]/text()').extract()[0]
        title = sel.xpath('//div[contains(@class, "typeSeason")]//span/text()').extract()[0]
        
        
        list_price = sel.xpath('//div[@id="itemData"]//span[contains(@class, "full price")]//span[2]/text()')
        if len(list_price) > 0:
            list_price = list_price.extract()[0]
            current_price = sel.xpath('//div[@id="itemData"]//span[contains(@class, "discounted price")]//span[2]/text()').extract()[0]
        elif len(sel.xpath('//div[@id="itemData"]//span[contains(@class, "price")]//span[2]')) > 0:            
            list_price = sel.xpath('//div[@id="itemData"]//span[contains(@class, "price")]//span[2]/text()').extract()[0]
            current_price = list_price
        else:
            return
        
        show_product_id = sel.xpath('//div[contains(@class, "productCode")]//span[2]/text()').extract()[0]
        
        baseItem['title'] = title
        baseItem['url'] = get_base_url(response)
        baseItem['brand'] = brand
        baseItem['from_site'] = 'thecorner'
        baseItem['show_product_id'] = show_product_id
        baseItem['desc'] = sel.xpath('//ul[contains(@class, "tabs")]//li[1]').extract()[0]
        baseItem['list_price'] = list_price
        baseItem['current_price'] = current_price

        if sel.xpath('//a[contains(@class, "sizeGuideLink")]'):
            baseItem['size_info'] = '%s/yTos/Plugins/ItemPlugin/RenderSizeGuide/?code10=%s&siteCode=THECORNER_US' % (self.base_url, show_product_id)
        else:
            baseItem['size_info'] = ''
        
        #no pic display
        if sel.xpath('//div[contains(@id, "alternatives")]//ul/@data-ytos-opt') and sel.xpath('//div[contains(@class, "mainImage")]/@data-ytos-opt'):
            pic_dis = 0
            thum_Json = json.loads(sel.xpath('//div[contains(@id, "alternatives")]//ul/@data-ytos-opt').extract()[0])
            thum_ext = thum_Json['options']['imageOptions']['ImageExtensionValue']
            thum_size = thum_Json['options']['imageOptions']['ImageSize']

            img_Json = json.loads(sel.xpath('//div[contains(@class, "mainImage")]/@data-ytos-opt').extract()[0])
            img_ext = img_Json['options']['imageOptions']['ImageExtensionValue']
            img_size = img_Json['options']['imageOptions']['ImageSize']

            img_box = sel.xpath('//div[contains(@id, "alternatives")]//ul//li')
        else:
            pic_dis = 1
            thum_Json = json.loads(sel.xpath('//div[contains(@id, "zoom")]/@data-ytos-opt').extract()[0])
            thum_ext = thum_Json['options']['imageOptions']['ImageExtensionValue']
            thum_size = '8'

            img_ext = thum_ext
            img_size = thum_Json['options']['imageOptions']['ImageSize']

            #img_box = thum_Json['options']['alternativeShots']
            img_box = ["f","r", "d","e","a"]
            

        images = []
        for image in img_box:
            if pic_dis == 0:
                img = image.xpath('.//img/@src').extract()[0]
                img_index = image.xpath('.//img/@data-ytos-image-shot').extract()[0]
            else:
                img = sel.xpath('//meta[@property="og:image"]/@content').extract()[0]
                img_index = image
            base_imgUrl = re.search(r'http://(.*)/(.*)/', img).group(0)
            

            images.append({"base":base_imgUrl,"index":img_index,"thum_ext":thum_ext,"thum_size":thum_size,"img_ext":img_ext,"img_size":img_size})

        color_sku_url = '%s/yTos/api/Plugins/ItemPluginApi/GetCombinations/?siteCode=THECORNER_US&code10=%s' % (self.base_url, show_product_id)
        yield Request(color_sku_url, callback=self.parse_color_sku, meta={'baseItem':baseItem, 'images':images})



    def parse_color_sku(self, response):
        baseItem = response.meta['baseItem']
        images_tmp = response.meta['images']
        jsonStr = json.loads(response.body)
        
        colors = []
        skus = []
        sizes = []
        for col in jsonStr['Colors']:
            images = []
            for img in images_tmp:
                imageItem = ImageItem()

                imageItem['thumbnail'] = '%s%s_%s_%s.%s' % (img['base'], col['Code10'], img['thum_size'], img['index'], img['thum_ext'])
                imageItem['image'] = '%s%s_%s_%s.%s' % (img['base'], col['Code10'], img['img_size'], img['index'], img['img_ext'])
                images.append(imageItem)

            color = Color()
            color['type'] = 'color'
            color['from_site'] = 'thecorner'
            color['show_product_id'] = baseItem['show_product_id']
            color['images'] = images
            color['name'] = col['Description']
            color['cover_style'] = '#' + col['Rgb']
            #color['cover_style'] = 'background-color: #%s;' % (col['Rgb'])
            colors.append(col['Description'])
            yield color

        for size in jsonStr['ModelColorSizes']:
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = baseItem['show_product_id']
            skuItem['from_site'] = 'thecorner'
            skuItem['id'] = size['Color']['Description'].encode("utf-8")+"*"+size['Size']['Description']
            skuItem['list_price'] = baseItem['list_price']
            skuItem['current_price'] = baseItem['current_price']
            skuItem['size'] = size['Size']['Description']
            skuItem['color'] = size['Color']['Description']
            skuItem['is_outof_stock'] = False
            skuItem['quantity'] = size['Quantity']
            sizes.append(size['Size']['Description'])
            skus.append(skuItem)
        
        baseItem['skus'] = skus
        baseItem['colors'] = list(set(colors))
        baseItem['sizes'] = list(set(sizes))

        yield baseItem


class ThecornerSpider(BaseSpider, ThecornerBaseSpider):   
#class ThecornerSpider(RedisSpider):
    name = "thecorner"
    allowed_domains = ["thecorner.com"]

    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        #'DOWNLOAD_DELAY': 1,
        'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
 

    #must use proxy
    start_urls = [
        #'http://www.thecorner.com/us',
        'http://www.thecorner.com/us/men/clothing/',
        'http://www.thecorner.com/us/men/shoes/',
        'http://www.thecorner.com/us/men/bags/',
        'http://www.thecorner.com/us/men/accessories/',
        'http://www.thecorner.com/us/women/clothing/',
        'http://www.thecorner.com/us/women/shoes/',
        'http://www.thecorner.com/us/women/bags/',
        'http://www.thecorner.com/us/women/accessories/',
        'http://www.thecorner.com/us/shop/nogender'
    ]

    url_gender_type = {
        'http://www.thecorner.com/us/men/clothing/':{'gender':'men', 'product_type':'clothing'},
        'http://www.thecorner.com/us/men/shoes/':{'gender':'men', 'product_type':'shoes'},
        'http://www.thecorner.com/us/men/bags/':{'gender':'men', 'product_type':'bags'},
        'http://www.thecorner.com/us/men/accessories/':{'gender':'men', 'product_type':'accessories'},
        'http://www.thecorner.com/us/women/clothing/':{'gender':'women', 'product_type':'clothing'},
        'http://www.thecorner.com/us/women/shoes/':{'gender':'women', 'product_type':'shoes'},
        'http://www.thecorner.com/us/women/bags/':{'gender':'women', 'product_type':'bags'},
        'http://www.thecorner.com/us/women/accessories/':{'gender':'women', 'product_type':'accessories'},
        'http://www.thecorner.com/us/shop/nogender':{'gender':'unisex', 'product_type':'clothing'}
    }
    


    base_url = 'http://www.thecorner.com'
    

    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类
    def parse(self, response):
        req_url = re.sub('\?page=\w', '/', response.url)
        if req_url not in self.start_urls:
            return
        sel = Selector(response)

        gender = self.url_gender_type[response.url]['gender']
        product_type = self.url_gender_type[response.url]['product_type']

        '''
        #for debug:
        url = 'http://www.thecorner.com/us/men/clothing/short-dresses'
        category = 'polo'
        yield Request(url, callback=self.parse_categories, meta={'category':category, 'gender':gender, 'product_type':product_type})
        '''
        
        categoryList = sel.xpath('//ul[contains(@class, "refinements refinementmacro")]//li//ul//li')
        for categorys in categoryList:
            category = categorys.xpath('./a//span[2]/text()').extract()[0]
            url = categorys.xpath('./a/@href').extract()[0]
            yield Request(url, callback=self.parse_categories, meta={'category':category, 'gender':gender, 'product_type':product_type})
        

    def parse_categories(self, response):
        sel = Selector(response)

        gender = response.meta['gender']
        product_type = response.meta['product_type']
        category = response.meta['category']

        items = sel.xpath('//div[contains(@class, "column-9 omega")]//ul//li//div[contains(@class, "itemContentWrapper")]')
        for item in items:
            url = item.xpath('./a/@href').extract()[0]
            #url = 'http://www.thecorner.com/us/women/leggings_cod36669708pe.html'  #use for test
            cover = item.xpath('.//a//div//img/@src').extract()[0]
            
            baseItem = BaseItem()
            baseItem['type'] = 'base'
            baseItem['cover'] = cover
            baseItem['gender'] = gender
            baseItem['product_type'] = product_type
            baseItem['category'] = category

            yield Request(url, callback=self.parse_item, meta = {'baseItem':baseItem }) 

        if sel.xpath('//div[contains(@id, "pagination")]//ul//li'):
            if sel.xpath('//div[contains(@id, "pagination")]//ul//li[contains(@class, "nextPage")]'):
                next_url = self.base_url+sel.xpath('//div[contains(@id, "pagination")]//ul//li[contains(@class, "nextPage")]//a/@href').extract()[0]
                yield Request(next_url, callback=self.parse_categories, meta={'category':category,'gender':gender, 'product_type':product_type})


    def parse_item(self, response):
        baseItem = response.meta['baseItem']
        return self.handle_parse_item(response, baseItem)

        
    def handle_parse_item(self, response, item):
        return ThecornerBaseSpider.handle_parse_item(self, response, item)

    
# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
 
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
 
from gorden_crawler.spiders.shiji_base import BaseSpider
 
import re
import execjs
# import json

class KiplingSpider(BaseSpider):
    name = "kipling"
    allowed_domains = ["kipling-usa.com","fluidretail.net"]
    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 1,
        'RETRY_TIMES': 10,
#         'DOWNLOADER_MIDDLEWARES': {
#               'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,'
#             'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
#             'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
#             'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
#             'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
#         }
    }
        #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'http://www.kipling-usa.com/',
        ]
    data_url = 'http://cdn.fluidretail.net/'
    
    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类
    def parse(self,response):
        sel = Selector(response)
        
        levelZeros = sel.xpath(".//ul[@id='navigation-menu']/li[position()>1]")
        for levelZero in levelZeros[:4]:
            product_type = levelZero.xpath("./a/text()").extract()[0]
            levelOnes = levelZero.xpath("./div/div[3]/ul/li[position()>1]")
            for levelOne in levelOnes:
                category = levelOne.xpath("./a/span/text()").extract()[0]
                url = levelOne.xpath("./a/@href").extract()[0]
                yield Request(url, callback=self.parse_list, meta={'product_type': product_type, 'category': category})
                

    def parse_list(self,response):
        sel = Selector(response)
        product_type = response.meta['product_type']
        category = response.meta['category']
        list_dom = sel.xpath(".//ul[@id='search-result-items']/li")
        if len(list_dom) > 0:
            for dom in list_dom:
                item = BaseItem()
                item['type'] = 'base'
                item['from_site'] = self.name
                item['product_type'] = product_type
                item['title'] = dom.xpath(".//a[@class='name-link']/text()").extract()[0].strip()
                item['cover'] = dom.xpath('.//div[@class="product-image"]/a[@class="thumb-link"]/img/@src').extract()[0]
                item['category'] =  category
                url = dom.xpath(".//a[@class='name-link']/@href").extract()[0]
                item['url'] = url
                yield Request(url, callback=self.parse_item, meta={"item": item})
            
    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)
    
    def handle_parse_item(self, response, item):
        sel = Selector(response)
        if len(sel.xpath('//p[@class="not-available-msg"]'))>0:
            return
        item['brand'] = 'kipling'
        item['show_product_id'] = sel.xpath(".//span[@itemprop='productID']/text()").extract()[0]
        item['brand'] = 'Kipling'
        item['gender'] = 'women'
        if len(sel.xpath(".//div[@class='description-content']/text()")) >0:
            item['desc'] = sel.xpath(".//div[@class='description-content']/text()").extract()[0]
        else:
            item['desc'] = ''
        if len(sel.xpath(".//span[@data-event-label='Full Price']/@data-event-value")) > 0:
            item['list_price'] = sel.xpath(".//span[@data-event-label='Full Price']/@data-event-value").extract()[0].strip()
            item['current_price'] = sel.xpath(".//span[@data-event-label='Full Price']/@data-event-value").extract()[0].strip()
        else:
            item['current_price'] = sel.xpath(".//span[@data-event-label='Full Minimum Price']/@data-event-value").extract()[0].strip()
            item['list_price'] = sel.xpath(".//span[@data-event-label='Full Maximum Price']/@data-event-value").extract()[0].strip()
        item['colors'] = []
        item['skus'] = []
        image_data_url = self.data_url + 'customers/c1501/' + item['show_product_id'] + '/' + item['show_product_id'] + '_pdp/js/data.js'

        colorIds = sel.xpath(".//ul[@class='swatches Color']/li/a/@data-colorid").extract()
        if len(colorIds) > 0:
            colorUrls = sel.xpath(".//li[@class='emptyswatch']/a/@href").extract()
            select_colorid = sel.xpath(".//li[@class='selected']/a/@data-colorid")
            if len(select_colorid)>0:
                colorUrls.append(sel.xpath(".//li[@class='selected']/a/@href").extract()[0] + select_colorid.extract()[0])
            yield Request(image_data_url, callback=self.handle_image_item, meta={'colorIds': colorIds, 'colorUrls':colorUrls, 'item': item})
        else:
            return
        
    def handle_image_item(self,response):
        item = response.meta['item']
        sel = Selector(response)
        colorIds = response.meta['colorIds']
        colorUrls = response.meta['colorUrls']
        image_color_dict = {}
        for colorId in colorIds:
            images=[]
            single_color_imgages = re.findall("[^\.{]*\/zoom_variation_" + colorId + "[^{]*2200\.jpg",response.body)
            if len(single_color_imgages) == 0:
                single_color_imgages = re.findall("[^\.{]*\/zoom_variation_" + colorIds[0] + "[^{]*2200\.jpg",response.body)
            for i in range(len(single_color_imgages)):
                imageItem = ImageItem()
                imageItem['image'] = self.data_url + single_color_imgages[i][1:]
                tempImage = re.sub('zoom_variation_', 'main_variation_', imageItem['image'])
                imageItem['thumbnail'] = re.sub('2192x2200', '548x550', tempImage)

                images.append(imageItem.copy())
            image_color_dict[colorId] = images
        index = 0
        
        yield Request(colorUrls[index], callback=self.handle_color_item, meta={'image_color_dict': image_color_dict, 'colorUrls': colorUrls, 'index': index, 'item': item})
        
    def handle_color_item(self,response):
        sel = Selector(response)
        item = response.meta['item']
        image_color_dict = response.meta['image_color_dict']
        colorUrls = response.meta['colorUrls']
        index = response.meta['index']
        skuItem = SkuItem()
        data_colorid = sel.xpath(".//li[@class='selected']/a/@data-colorid").extract()[0]
        images = image_color_dict[data_colorid]
        colorItem = Color()
        colorItem['images'] = images
        colorItem['type'] = 'color'
        colorItem['from_site'] = self.name
        colorItem['show_product_id'] = sel.xpath(".//span[@itemprop='productID']/text()").extract()[0]
        colorItem['name'] = sel.xpath(".//span[@class='selected-value colorValueLabel']/text()").extract()[0].strip()
        cover = sel.xpath(".//li[@class='selected']/a/@style").extract()[0]
        colorItem['cover'] = re.findall('\(.+\)',cover)[0][1:-1]
        item['colors'].append(colorItem['name'])
        
        yield colorItem
                
        skuItem['color'] = colorItem['name']
        skuItem['type'] = 'sku'
        skuItem['show_product_id'] = sel.xpath(".//span[@itemprop='productID']/text()").extract()[0]
        if len(sel.xpath(".//span[@data-event-label='Full Price']/@data-event-value")) > 0:
            skuItem['list_price'] = sel.xpath(".//span[@data-event-label='Full Price']/@data-event-value").extract()[0].strip()
            skuItem['current_price'] = sel.xpath(".//span[@data-event-label='Full Price']/@data-event-value").extract()[0].strip()
        else:
            skuItem['current_price'] = sel.xpath(".//span[@data-event-label='Full Minimum Price']/@data-event-value").extract()[0].strip()
            skuItem['list_price'] = sel.xpath(".//span[@data-event-label='Full Maximum Price']/@data-event-value").extract()[0].strip()
        skuItem['size'] = u'one size'
        skuItem['id'] = data_colorid
        skuItem['from_site'] = self.name
        sku_quantity = sel.xpath(".//select[@name='Quantity']/@data-available").extract()[0]
        if sku_quantity == 0:
            skuItem['is_outof_stock'] = True
        else:
            skuItem['is_outof_stock'] = False
        item['skus'].append(skuItem)
        item['sizes'] = [u'one size']
        index = index + 1
        if index >= len(colorUrls):
            item['colors'] = list(set(item['colors']))
            yield item
            
        else:
            yield Request(colorUrls[index], callback=self.handle_color_item, meta={'image_color_dict': image_color_dict, 'colorUrls': colorUrls, 'index': index, 'item': item})

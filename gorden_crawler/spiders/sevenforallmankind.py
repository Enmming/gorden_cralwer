# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from gorden_crawler.spiders.shiji_base import BaseSpider

import re
import execjs
from genericpath import getsize
# import json

class AllmankindSpider(BaseSpider):
    name = "sevenforallmankind"
    allowed_domians = ["7forallmankind.com"]
    
    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.5,
#         'DOWNLOADER_MIDDLEWARES': {
#             #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
#             'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
#             'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
#             'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
#             'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
         
#       RETRY_TIMES = 10
    }
    
    
    start_urls = [
        "http://www.7forallmankind.com/"
        ]
      
    base_url = 'http://www.7forallmankind.com'
    
    def parse(self,response):
        sel = Selector(response)
        navDom = sel.xpath(".//div[@class='zone zone-navigation']/article/nav/ul/li[position()<5]")
        
        for nav in navDom:
            genTitle = nav.xpath("./a/text()").extract()[0]
            genTitle = genTitle.strip().lower()
            product_type = 'clothing'
            if genTitle != 'sale':
                gender = genTitle
                if genTitle == 'kids':
                    catDom = nav.xpath("./ul/li/ul/li[position()<3]")
                    for cat in catDom:
                        category = cat.xpath("./a/text()").extract()[0]
                        category = category.strip().lower()
                        if category == 'girls':
                            gender = 'girls'
                        else:
                            gender = 'boys'
                        url = self.base_url + cat.xpath("./a/@href").extract()[0]

                        yield Request(url, callback=self.parse_list, meta={"categoryUrl":url,"category":category, "gender":gender, "product_type":product_type})
                else:
                    catDom = nav.xpath("./ul/li[4]/ul/li")
                    for cat in catDom[:-2]:
                        category = cat.xpath("./a/text()").extract()[0]
                        category = category.strip().lower()
                        if category != 'accessories':
                            url = self.base_url + cat.xpath("./a/@href").extract()[0]
                            
                            yield Request(url, callback=self.parse_list, meta={"categoryUrl":url,"category":category, "gender":gender, "product_type":product_type})
            else:
                catDom = nav.xpath("./ul/li")
                for cat in catDom:
                    gender = nav.xpath("./ul/li/a/text()").extract()[0]
                    gender = gender.strip().lower()
                    if gender != 'kids':
                        ddict = cat.xpath("./ul/li[1<position()<5]")
                    else:
                        ddict = cat.xpath("./ul/li")
                    for d in ddict:
                        category = gender + ' - ' + d.xpath("./a/text()").extract()[0]
                        url = self.base_url + d.xpath("./a/@href").extract()[0]
                        if url.find('/Contents/Item/Display') == -1:
                            yield Request(url, callback=self.parse_list, meta={"categoryUrl":url,"category":category, "gender":gender, "product_type":product_type})
                        
    def parse_list(self,response):
        category = response.meta['category']
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        categoryUrl = response.meta['categoryUrl']

        sel = Selector(response)
        
        listDom = sel.xpath(".//div[@class='col-sm-9 col-lg-10 sevn-product-list-container']/ul/li/div")
        brand = sel.xpath(".//a[@class='sevn-brand']/@title").extract()[0]
        if len(listDom.extract()) > 0:
            for dom in listDom:
                item = BaseItem()
                item['from_site'] = 'sevenforallmankind'
                item['type'] = 'base'
                item['category'] = category
                item['product_type'] = product_type
                item['gender'] = gender
                item['title'] = dom.xpath("./div[@class='os-item-summary']/a/text()").extract()[0]
                item['brand'] = brand
                item['url'] = url = self.base_url + dom.xpath("./div[@class='os-item-summary']/a/@href").extract()[0]
                
                if item['title'].strip().lower()[:4] == 'boys':
                    item['gender'] = 'boys'
                elif item['title'].strip().lower()[:4] == 'girl':
                    item['gender'] = 'girls'
                if item['url'].find('/Contents/Item/Display') == -1:
                    yield Request(item['url'], callback=self.parse_item, meta={'item': item})
            
            current_page_str = re.findall(r"\"Page\"\:\d+", response.body, re.S)    
            find_currunt_page = current_page_str[0].find(':')
            if current_page_str[0][find_currunt_page+1:] == 0:
                curruntPage = 1
            else:
                curruntPage = current_page_str[0][find_currunt_page+1:]
            
            total_count_str = re.findall(r"\"TotalCount\"\:\d+", response.body, re.S)
            find_total_count = total_count_str[0].find(':')
            totalCount = int(total_count_str[0][find_total_count+1:])
            lastPage = totalCount / 36 + 1 if totalCount % 36 > 0 else totalCount / 36
            
            if int(curruntPage) < int(lastPage):
                list_more_url = categoryUrl + '?Page=' +str(int(curruntPage) + 1)
                if list_more_url.find('/Contents/Item/Display') == -1:
                    yield Request(list_more_url, callback=self.parse_list, meta={"categoryUrl":categoryUrl, "category":category, "product_type":product_type,"gender":gender})

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)
    
      
         
    def handle_parse_item(self, response, item):
        sel = Selector(response)
        
        if 'show_product_id' not in item.keys():
            get_pid_sku_str = sel.xpath(".//div[@class='col-lg-5 sku-col']/text()").extract()[0]
            get_pid = re.findall(r"PID\:\s*\S*" , get_pid_sku_str, re.S)
            get_sku = re.findall(r"SKU\:\s*\S*" , get_pid_sku_str, re.S)
            find_product_id = get_pid[0].find(' ')
            find_sku_id = get_sku[0].find(' ')
            productId = get_pid[0][find_product_id + 1:]
            skuId = get_sku[0][find_sku_id + 1:]
            item['show_product_id'] = productId
            
        item['desc'] = sel.xpath(".//div[@data-bind='html: Description1']").extract()[0]
        item['desc'] += sel.xpath(".//div[@id='specs']/div/div").extract()[0]
        
        sizeDict = sel.xpath(".//div[@class='modal-dialog modal-lg']/div/div[2]")
        if(len(sizeDict.xpath("./div"))!=1):
            if sizeDict.xpath("./h3/text()"):
                item['size_info'] = sizeDict.xpath("./h3/text()").extract()[0]
        else:
            if item['gender'] == 'women':
                item['size_info'] = sizeDict.xpath("./div/div[1]/h3/text()").extract()[0]
            elif item['gender'] == 'men':
                item['size_info'] = sizeDict.xpath("./div/div[2]/h3/text()").extract()[0]
            else:
                item['size_info'] = sizeDict.xpath("./div/div[3]/h3/text()").extract()[0]
                
            
        
        regular_price_str = re.findall(r'MaxCost\"\:\d+\.\d+', response.body)
        
        find_Regular_Price = regular_price_str[0].find(':')
        regularPrice = regular_price_str[0][find_Regular_Price+1:]
        item['list_price'] = regularPrice
        current_price_str = re.findall(r'MinCost\"\:\d+\.\d+', response.body)
        find_Current_Price = current_price_str[0].find(':')
        currentPrice = current_price_str[0][find_Current_Price+1:]
        item['current_price'] = currentPrice
        
        skusStr = re.findall(r'var __onestop_pageData =.+\;', response.body)[0]
        if skusStr:
            context = execjs.compile('''
                var __onestop_pageData = %s;
                function getSkus(){
                    return __onestop_pageData;
                }
            ''' % skusStr[25:-1])
        skusDict = context.call('getSkus')
        
        images=[]
        imageItem1 = ImageItem()
        imageItem2 = ImageItem()
        imageItem3 = ImageItem()
        imageItem1['image'] = 'http://' + sel.xpath(".//img[@id='zoom_id']/@src").extract()[0][2:]
        imageItem1['image'] = imageItem1['image'].replace("640","960")
        imageItem1['thumbnail'] =  imageItem1['image'].replace("960","320")
        images.append(imageItem1)
        
        imageItem2['image'] = imageItem1['image'].replace('_l.','_b.')
        imageItem2['thumbnail'] = imageItem2['image'].replace("960","320")
        images.append(imageItem2)

        imageItem3['image'] = imageItem2['image'].replace('_b.', '_c.')
        imageItem3['thumbnail'] = imageItem3['image'].replace("960","320")
        images.append(imageItem3)

        
        colorItem = Color()
        colorItem['type'] = 'color'
        colorItem['from_site'] = item['from_site']
        colorItem['show_product_id'] = item['show_product_id']
        colorItem['images'] = images
        colorItem['cover'] = imageItem1['thumbnail']
        colorName = skusDict['product']['ProductColors'][0]['ColorName'].strip()
        colorItem['name'] = colorName
        yield colorItem
        
        item['cover'] = colorItem['cover']
        item['dimensions'] = ['size']
        item['sizes'] = {}
        item['colors'] = [colorName]

        skusD = skusDict['product']['ProductSizes']
        item['skus'] = []
        sizesList = []
        for sku in skusD:

            skuItem = {}
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['list_price'] = item['list_price']
            skuItem['current_price'] = item['current_price']
            skuItem['color'] = skusDict['product']['ProductColors'][0]['ColorName']
            skuItem['size'] = sku['SizeName']
            skuItem['id'] = str(int(item['show_product_id']) + sku['Id'])
            skuItem['from_site'] = item['from_site']
            if sku['StockLevel'] == 0:
                skuItem['is_outof_stock'] = True
            item['skus'].append(skuItem)
            sizesList.append(skuItem['size'])
            
        item['sizes'] = sizesList   
        yield item
    


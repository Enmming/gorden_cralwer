# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from gorden_crawler.spiders.shiji_base import BaseSpider
import copy
import re
import execjs
# import json

class SierratradingpostSpider(BaseSpider):
    name = "sierratradingpost"
    allowed_domains = ["sierratradingpost.com"]

    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.5,
#         'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
#             'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
#             'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
#             'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
#             'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
#         }
    }
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'http://www.sierratradingpost.com',
        ]

    base_url = 'http://www.sierratradingpost.com'
    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)
        navDom = sel.xpath(".//div[@class='nav-item dropdown navigation-dropdown backdrop-toggle pos-s drawer-item'][position()<3]")
        for nav in navDom:
            product_type = nav.xpath("./a/text()").extract()[0]
            categoryDom = nav.xpath("./div/div[position()<4]")
            for dom in categoryDom:
                genderTitle = dom.xpath("./a/text()").extract()[0]
                find = genderTitle.find("'s")
                if find != -1:
                    gender = genderTitle[:find].lower()
                else:
                    gender = ''
                subnavDom = dom.xpath('./div/a[@class="dropdown-item drawer-item"]')
                for cdom in subnavDom:
                    category = cdom.xpath("./text()").extract()[0]
                    category = category.strip().lower()
                    if category != 'footwear accessories':
                        url = self.base_url + cdom.xpath("./@href").extract()[0]

                        if category.find("accessories") == -1 or category.find("kids'") == -1:
                            yield Request(url, callback=self.parse_category, meta={"category":category, "gender":gender, "product_type":product_type})
                        else:
                            if category.find("boy's") != -1:
                                gender = 'boys'
                            elif category.find("girl's") != -1:
                                gender = 'girls'
                            elif category.find("infant & toddler") != -1:
                                gender = 'baby'

                            yield Request(url, callback=self.parse_list, meta={"categoryUrl":url,"category":category, "gender":gender, "product_type":product_type})
    
    def parse_category(self, response):
        category = response.meta['category']
        gender = response.meta['gender']
        product_type = response.meta['product_type']

        sel = Selector(response)
        categoryDom = sel.xpath(".//ul[@class='filterColumn']/li[1]/div/ul/li")
        if len(categoryDom.xpath('./a'))==0:
            yield Request(response.url, callback=self.parse_list, meta={"categoryUrl":response.url,"category":category, "gender":gender, "product_type":product_type}, dont_filter=True)
        else:
            for dom in categoryDom:
                subCategory = dom.xpath("./a/text()").extract()[0]
                if subCategory not in ["More Men's Accessories","More Women's Accessories","More Kids' Accessories"]: 
                    
                    if category in ['watches & accessories','jewelry & accessories',"kids' accessories"]:
                        product_type = 'accessories'
    
                    if category.find("kids'") != -1:
                        if subCategory.find("Boy's") != -1:
                            gender = 'boys'
                        elif subCategory.find("Girl's") != -1:
                            gender = 'girls'
                        elif subCategory.find("Infant & Toddler") != -1:
                            gender = 'baby'
                        else:
                            gender = 'kid-unisex'
    
                    url = self.base_url + dom.xpath("./a/@href").extract()[0]
                    yield Request(url, callback=self.parse_list, meta={"categoryUrl":url, "category":subCategory.strip().lower(), "gender":gender, "product_type":product_type})



    def parse_list(self, response):
        category = response.meta['category']
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        categoryUrl = response.meta['categoryUrl']

        sel = Selector(response)

        
        listDom = sel.xpath(".//div[@id='products']/div")
        if len(listDom.extract()) > 0:
            for dom in listDom:
                item = BaseItem()
                item['from_site'] = 'sierratradingpost'
                item['type'] = 'base'
                item['category'] = category
                item['product_type'] = product_type
                item['gender'] = gender
                item['title'] = dom.xpath("./span/@data-name").extract()[0]
                item['brand'] = dom.xpath("./span/@data-brand").extract()[0]
                item['show_product_id'] = dom.xpath("./span/@data-baseid").extract()[0]
                item['current_price'] = re.sub(r'\s', '', dom.xpath(".//span[@class='ourPrice']/text()").extract()[0])[1:]
                retailPrice = dom.xpath(".//span[@class='retailPrice']/text()").extract()[0]
                find = retailPrice.find('$')
                item['list_price'] = retailPrice[find+1:]
                item["url"] = url = self.base_url + dom.xpath("./div[@class='productTitle']/a/@href").extract()[0]

                yield Request(url, callback=self.parse_item, meta={"item": item})


            if len(sel.xpath(".//span[@class='currentPage']/text()")) == 0:
                currntePage = 1
            else:
                currntePage = sel.xpath(".//span[@class='currentPage']/text()").extract()[0]

            countStr = sel.xpath(".//span[@id='numberOfItems']/text()").extract()[0]
            countTotal = int(re.sub('[(),items]','',countStr))
            lastPage = countTotal / 24 + 1 if countTotal % 24 > 0 else countTotal / 24

            if int(currntePage) < int(lastPage):
                list_more_url = categoryUrl + str(int(currntePage)+1) + '/'
                yield Request(list_more_url, callback=self.parse_list, meta={"categoryUrl":categoryUrl, "category":category, "product_type":product_type,"gender":gender})



    def parse_item(self, response):
        item = response.meta['item']

        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)

        if 'show_product_id' not in item.keys():
            item['show_product_id'] = sel.xpath(".//input[@id='baseNo']/@value").extract()[0]
            retailPrice = re.sub(r'\s', '', sel.xpath(".//span[@class='retailPrice']/a/text()").extract()[0])
            find = retailPrice.find('$')
            item['list_price'] = retailPrice[find+1:]

        item['desc'] = sel.xpath(".//div[@id='overviewSection']/div[1]/*").extract()[0]
        if len(sel.xpath(".//div[@class='sizingChart']/table/*").extract()) > 0:
            item['desc'] += '<div><table>'
            for d in sel.xpath(".//div[@class='sizingChart']/table/*"):
                item['desc'] += d.extract()
            item['desc'] +='</table></div>'

        item['dimensions'] = []
        item['sizes'] = {}
        item['colors'] = []
        propertyDropDown = sel.xpath(".//div[@class='propertyDropDown']")
        dropDownValue = {}
        skuKey = {}
        if len(propertyDropDown.extract()):
            largeImage = sel.xpath(".//input[@id='largeImageSrcTemplate']/@value").extract()[0]
            zoomImage = sel.xpath(".//input[@id='zoomImageHrefTemplate']/@value").extract()[0]
            i = 1
            for dropDown in propertyDropDown:
                title = (sel.xpath(".//label[@id='property" + str(i) + "Label']/@title").extract()[0]).lower()
                skuKey['property'+str(i)] = title

                vk = {}
                dom = dropDown.xpath("./select/option[@value != '']")
                for d in dom:
                    k = d.xpath("./@value").extract()[0]
                    v = d.xpath("./text()").extract()[0]
                    vk[k] = v
                    if title == 'color':
                        imageItem = ImageItem()
                        colorItem = Color()
                        altImages = sel.xpath(".//a[@class='altImage']")
                        prod_images = []
                        imageItem['thumbnail'] = re.sub(r'_\d+~\d+', '_' + k + '~460', largeImage)
                        imageItem['image'] = re.sub(r'_\d+~\d+', '_' + k + '~1500', zoomImage)
                        colorItem['cover'] = re.sub(r'_\d+~\d+', '_' + k + '~220', imageItem['thumbnail'])
                        prod_images.append(imageItem.copy()) 
                        for altImage in altImages:
                            temp_image = altImage.xpath("./@href").extract()[0]
                            temp_thumbnail = altImage.xpath("./@data-image").extract()[0]
                            
                            for temp_dict in prod_images:
                                t = 0
                                if temp_dict['thumbnail'] == temp_thumbnail or imageItem['image'] == temp_image:
                                    t = -1
                                    break
                            if t!= -1:
                                imageItem['image'] = temp_image
                                imageItem['thumbnail'] = temp_thumbnail
                                prod_images.append(imageItem.copy())           
                                
                        
                        colorItem['type'] = 'color'
                        colorItem['from_site'] = item['from_site']
                        colorItem['show_product_id'] = item['show_product_id']
                        colorItem['images']= prod_images
                        colorItem['name'] = v + '(' + k + ')'
                        item['colors'].append(colorItem['name'])
                        yield colorItem
                
                dropDownValue[title] = vk
                i += 1
                if title == 'color':
                    pass
                else:    
                    item['dimensions'].append(title)
                    item['sizes'][title] = vk.values()

        if len(item['colors']) == 0:
            return

        if len(item['dimensions']) == 0:
            item['dimensions'] = ['size']

        if 'size' in item['sizes'].keys():
            pass
        else:
            item['sizes']['size'] = ['onesize']
            
        item['cover'] = imageItem['thumbnail'].replace("460","220")

        skusStr = "".join(re.findall(r'[\s]*var skus = new TAFFY\([\s]*(\[.*\])[\s]*\);', response.body, re.S))
        if skusStr:
            context = execjs.compile('''
                var skus = %s;
                function getSkus(){
                    return skus;
                }
            ''' % skusStr)
            
            skusDict = context.call('getSkus')

            item['skus'] = []
            for sku in skusDict:
                skuItem = {}
                skuItem['type'] = 'sku'
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['list_price'] = item['list_price']
                skuItem['current_price'] = sku['finalPromoPrice'][1:]
                skuItem['color'] = dropDownValue['color'][sku['property1']] + '(' +sku['property1'] + ')'
                if sku['property2'] == '':
                    skuItem['size'] = {'size':'onesize'}
                    skuItem['id'] = sku['property1']
                else:
                    skuItem['size'] = {skuKey['property2']:dropDownValue[skuKey['property2']][sku['property2']]}
                    skuItem['id'] = sku['property1'] + '*' + sku['property2']
                    if sku['property3'] != '':
                        skuItem['size'][skuKey['property3']] = dropDownValue[skuKey['property3']][sku['property3']]
                        skuItem['id'] += '*' + sku['property3']

                skuItem['from_site'] = item['from_site']
                skuItem['is_outof_stock'] = False
                if 'size' in skuItem.keys():
                    if 'size' in skuItem['size'].keys():
                        pass
                    else:
                        skuItem['size']['size'] = 'onesize'
                else:
                    skuItem['size'] = {'size':'onesize'}
                item['skus'].append(skuItem)
            yield item
                



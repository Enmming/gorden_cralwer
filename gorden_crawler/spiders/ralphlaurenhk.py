# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy import Request, FormRequest
import re
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
import datetime
from scrapy.utils.response import get_base_url
from gorden_crawler.spiders.shiji_base import BaseSpider
import execjs
import json
import urllib

class RalphlaurenhkBaseSpider(object):
    
    #handle
    def handle_parse_item(self, response, item):
        sel = Selector(response)

        catalogId = sel.xpath('//input[contains(@id, "catalogId")]/@value').extract()[0]
        storeId = sel.xpath('//input[contains(@id, "storeId")]/@value').extract()[0]
        show_product_id = sel.xpath('//input[contains(@id, "productId")]/@value').extract()[0] 
        #baseItem = response.meta['baseItem']
        baseItem = item
        baseItem['from_site'] = self.name
        baseItem['type'] = 'base'
        baseItem['title'] = sel.xpath('//div[contains(@class, "pdd_title box")]//h3/text()').extract()[0]
        baseItem['show_product_id'] = show_product_id
        baseItem['desc'] = sel.xpath('//div[contains(@class, "pdd_desc pdd_sub_item box")]').extract()[0]
        baseItem['list_price'] = sel.xpath('//p[contains(@class, "pdd_price")]//span/text()').extract()[0]
        if sel.xpath('//span[contains(@class, "promo_price")]'):
            baseItem['current_price'] = sel.xpath('//span[contains(@class, "promo_price")]/text()').extract()[0]
        else :
           baseItem['current_price'] = baseItem['list_price']

        colors = []
        skus = []
        colorNames = []
        sizes = {'size' : ['onesize']}
        
        color_coloum = sel.xpath('//ul[contains(@class, "pdd_colors_list box")]//li')
        images_coloum = sel.xpath('//div[contains(@id, "rl_pdd_cover_slider")]//ul[contains(@class, "box")]//li')
        
        
        for colors_col in color_coloum:
            color = Color()
            color['type'] = 'color'
            color['from_site'] = self.name
            color['show_product_id'] = show_product_id
            
            color['cover'] = colors_col.xpath('./a/img/@src').extract()[0]
            color['name'] = colors_col.xpath('./a/img/@alt').extract()[0]
            colorNames.append(color['name'])

            if colors_col.xpath('./a[contains(@class, "pdd_color pdd_color_picked")]//span/@onclick'):
                images = []
                
                for images_col in images_coloum:
                    imageItem = ImageItem()

                    imageItem['image'] = images_col.xpath('./img/@src').extract()[0]
                    imageItem['thumbnail'] = images_col.xpath('./img/@small').extract()[0]

                    images.append(imageItem)

                color['images'] = images
                yield color
            else :
                #print re.findall(r'\(.*?\)', clickParam)
                clickParam = colors_col.xpath('./a[contains(@class, "pdd_color")]//span/@onclick').extract()[0]
                clickParams = re.findall(r"'(.*)'", clickParam)[0].split(',')
                MFPARTNUMBER = clickParams[5].replace("'","")
                imgUrl = '%s/webapp/wcs/stores/servlet/ProductDetailFullImageView?catalogId=%s&langId=-1&storeId=%s&MFPARTNUMBER=%s' % (self.base_url,catalogId,storeId,MFPARTNUMBER)
                
                yield Request(imgUrl.encode('UTF-8'), meta={'color': color}, callback=self.parse_img) 
      
                '''
                quantityUrl = 'http://www.ralphlauren.asia/webapp/wcs/stores/servlet/ProductDetailQuantityView?catalogId=12551&langId=-1&storeId=12151'
                formdata = {
                        'SKUId': str(clickParam[2]),
                        'objectId':'',
                        'requesttype':'ajax'
                        } 
                yield FormRequest(url=sizeUrl, formdata=formdata, callback=self.parse_quantity, meta={ '': '' } )

                sizeUrl = self.base_url + '/webapp/wcs/stores/servlet/ProductDetailSizeSelectView?catalogId=12551&langId=-1&storeId=12151'
                formdata = {
                        'Id': str(clickParam[1]),
                        'SKUId': str(clickParam[2]),
                        'Color': 'Lime',
                        'ColorId': str(clickParam[5]),
                        'Size': '',
                        'InItemSppSplitChar':'@@',
                        'objectId':'',
                        'requesttype':'ajax'
                        }
                yield FormRequest(url=sizeUrl, formdata=formdata, callback=self.parse_size, meta={ 'color': color } )
                '''
        ###
        sku_coloum = sel.xpath('//select[contains(@id, "rl_pdd_size")]//option ')
        for sku_col in sku_coloum:
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = show_product_id
            skuItem['from_site'] = self.name
            skuItem['list_price'] = baseItem['list_price']
            skuItem['current_price'] = baseItem['current_price']
            skuItem['is_outof_stock'] = False
            skuItem['id'] = sel.xpath('//input[contains(@id, "selectSKUId")]/@value').extract()[0] 
            skuItem['color'] = sel.xpath('//span[contains(@class, "pdd_current_color")]/text()').extract()[0]
            #skuItem['size'] = sku_col.xpath('./option/text()').extract()[0]
            skuItem['quantity'] = sel.xpath('//select[contains(@id, "rl_pdd_qty")]//option/@value').extract()[0]
            skus.append(skuItem)

        baseItem['colors'] = colorNames
        baseItem['sizes'] = sizes
        baseItem['skus'] = skus
        baseItem['dimensions'] = ""
        baseItem['brand'] = 'ralph lauren'
        baseItem['category'] = sel.xpath('//div[contains(@class, "bread bread_bar")]//a[4]/text()').extract()[0]
        baseItem['product_type'] = sel.xpath('//div[contains(@class, "bread bread_bar")]//a[3]/text()').extract()[0]
        
        yield baseItem


    #ajax img
    def parse_img(self, response):
        sel = Selector(response)
        color = response.meta['color']
        
        images_coloum = sel.xpath('//div[contains(@id, "rl_pdd_cover_slider")]//ul[contains(@class, "box")]//li')
        images = []   
        for images_col in images_coloum:
            imageItem = ImageItem()

            imageItem['image'] = images_col.xpath('./img/@src').extract()[0]
            imageItem['thumbnail'] = images_col.xpath('./img/@small').extract()[0]

            images.append(imageItem)

        color['images'] = images
        yield color


class RalphlaurenhkSpider(BaseSpider, RalphlaurenhkBaseSpider):   
#class RalphlaurenSpider(RedisSpider):
    name = "ralphlaurenhk"
    allowed_domains = ["ralphlauren.asia"]
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
 

    start_urls = [
        'http://www.ralphlauren.asia/en/men/shop-by-category/polos-knits-66',
        'http://www.ralphlauren.asia/en/men/purple-label/new-arrival-9',
        'http://www.ralphlauren.asia/en/men/black-label/new-arrival',
        'http://www.ralphlauren.asia/en/men/polo/new-arrival-11',
        'http://www.ralphlauren.asia/en/men/rrl/new-stock',
        'http://www.ralphlauren.asia/en/men/denim-and-supply/new-arrival-15',
        'http://www.ralphlauren.asia/en/women/shop-by-category/polos-knits-68',
        'http://www.ralphlauren.asia/en/women/black-label/new-arrivals-2',
        'http://www.ralphlauren.asia/en/women/polo/new-arrivals-55',
        'http://www.ralphlauren.asia/en/women/rrl/all-apparel-19',
        'http://www.ralphlauren.asia/en/women/denim-and-supply/new-arrivals-6',
        'http://www.ralphlauren.asia/en/women/leather-goods/the-ricky-collection-18',
        'http://www.ralphlauren.asia/en/children/baby/newborn-essential-features',
        'http://www.ralphlauren.asia/en/children/boys/new-arrivals-22',
        'http://www.ralphlauren.asia/en/children/girls/new-arrivals-24',
    ]


    base_url = 'http://www.ralphlauren.asia'
    

    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类
    def parse(self, response):
        sel = Selector(response)
        category_lis = sel.xpath('//div[contains(@class, "pd_list_category")]//ul//li')
        
        '''
        url = 'http://www.ralphlauren.asia/en/men/purple-label/shirts-9'
        categoryids = '160059-160057'
        categoryId = categoryids.split('-')[0]
        parent_category_rn = categoryids.split('-')[1]
        viewtype = 3
        ajax_param = {'categoryId': categoryId, 'parent_category_rn':parent_category_rn, 'viewtype':viewtype, 'page':1 }
        yield Request(url.encode('UTF-8'), callback=self.parse_categories, meta={'ajax_param': ajax_param })
        '''
              
        for li in category_lis:
            url = li.xpath('.//a/@categoryurl').extract()[0] 
            category = li.xpath('.//a/text()').extract()[0] 
            categoryids = li.xpath('.//a/@categoryid').extract()[0] 
            viewtype = li.xpath('.//a/@viewtype').extract()[0] 
            categoryId = categoryids.split('-')[0]
            parent_category_rn = categoryids.split('-')[1]

            ajax_param = {'categoryId': categoryId, 'parent_category_rn':parent_category_rn, 'viewtype':viewtype, 'page':1 }

            yield Request(url.encode('UTF-8'), callback=self.parse_categories, meta={'ajax_param':ajax_param})
        

    def parse_categories(self, response):
        sel = Selector(response)
        ajax_param = response.meta['ajax_param']
        page = ajax_param['page']
        top_category = sel.xpath('//input[contains(@id, "search_divsion_id")]/@value').extract()[0]
        
        if int(top_category) == 122551:
            gender = "men"
        elif int(top_category) == 122552:
            gender = "women"
        elif int(top_category) == 122553:
            gender = "baby"

        item_list = sel.xpath('//div[contains(@id, "pd_list_div_Main")]//div[contains(@class, "pd_list_item")]')

        for item in item_list:
            cover = item.xpath('.//div[contains(@class, "pd_list_img")]//a//img/@src').extract()[0]
            url = item.xpath('.//div[contains(@class, "pd_list_img")]//a/@href').extract()[0]

            baseItem = BaseItem()
            baseItem['cover'] = cover
            baseItem['url'] = url
            baseItem['gender'] = gender

            yield Request(url.encode('UTF-8'), callback=self.parse_item, meta={'baseItem': baseItem})


        #next page
        pageCount = sel.xpath('.//input[contains(@id, "hidPageCount")]/@value').extract()[0] 
        
        if int(pageCount) > 2 and int(page) < int(pageCount):
            ajax_param['page'] = int(page) +1
            formdata = {
                        'pageView':'3',
                        'pageIndex': str(page),
                        'viewType': str(ajax_param['viewtype']),
                        'sortType':'',
                        'pageCount': str(pageCount),
                        'isViewAll':'0',
                        'categoryId': str(ajax_param['categoryId']),
                        'parent_category_rn': str(ajax_param['parent_category_rn']),
                        'top_category': str(top_category),
                        'facet':'',
                        'categoryIdentifier':'MNSCKNIT',
                        'currency':'HKD',
                        'clicked':'',
                        'priceFilter':'',
                        'country':'HK',
                        'objectId':'',
                        'requesttype':'ajax'
                        }

            next_url = "%s/webapp/wcs/stores/servlet/AEPCategoryMultipleGridDisplayView?pageView=image&catalogId=12551&langId=-1&shopByCategory=MNSCKNIT&storeId=12151&metaData=" % (self.base_url )

            #yield Request(url=next_url, callback=self.parse_categories, method="POST", body=urllib.urlencode(formdata),meta={ 'ajax_param': ajax_param })
            yield FormRequest(url=next_url, formdata=formdata, callback=self.parse_categories, meta={ 'ajax_param': ajax_param } )


    #item
    def parse_item(self, response):
        baseItem = response.meta['baseItem']

        return self.handle_parse_item(response, baseItem)

        
    def handle_parse_item(self, response, item):
        return RalphlaurenhkBaseSpider.handle_parse_item(self, response, item)


    
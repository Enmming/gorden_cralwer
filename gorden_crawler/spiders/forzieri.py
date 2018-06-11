# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy import Request
import re
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
import datetime
from scrapy.utils.response import get_base_url
from gorden_crawler.spiders.shiji_base import BaseSpider
from scrapy.selector import Selector
from urllib import quote

import time
import sys
reload(sys)
sys.setdefaultencoding("utf8")


class ForzieriBaseSpider(object):

    sku_ajax_str_prefix = 'http://www.forzieri.com/ajaxs/get_sku.ajax.asp?l=usa&c=usa&'
#     dept_id = ''
#     pf_id = ''

    #handle
    def handle_parse_item(self, response, item):
        sel = Selector(response)

        if not sel.xpath('//p[contains(@class, "product_code")]//span/text()').extract():
            print get_base_url(response)
            return

        product_id = sel.xpath('//p[contains(@class, "product_code")]//span/text()').extract()[0]
        title = sel.xpath('//div[@class="productTitle"]//h1/text()').extract()[0]
        
        categorys = sel.xpath('//div[@id="breadcrumbs"]//ul//li')
        desc = sel.xpath('//meta[@property="og:description"]/@content').extract()[0]
        
        baseItem = item
        baseItem['type'] = 'base'
        baseItem['title'] = title.encode("utf-8")
        baseItem['from_site'] = 'forzieri'
        show_product_id = re.search(r'^\w*\d+-\d+', product_id).group(0)
        baseItem['show_product_id'] = show_product_id
        baseItem['brand'] = sel.xpath('//div[@class="productTitle"]//p/a/text()').extract()[0]
        baseItem['desc'] = desc.encode("utf-8")

        if sel.xpath('//p[contains(@class, "size_help")]'):
            baseItem['size_info'] = '%s%s' % (sel.xpath('//p[contains(@class, "size_help")]//a/@href').extract()[0], '&layout=1')
        else:
            baseItem['size_info'] = ''

        baseItem['url'] = response.url

        #italy_url = sel.xpath('//ul[@class="fz_scroller_placeholder"]//li[7]//a/@href').extract()[0]
        us_url = sel.xpath('//ul[@class="fz_scroller_placeholder"]//li[1]//a/@href').extract()[0]
        
        yield Request(us_url, callback=self.parse_usa_goods, meta={'base_item': baseItem})
      
    def parse_usa_goods(self, response):
        sel = Selector(response)

        image_boxs = sel.xpath('//div[@id="productThumbs"]//a')
        
        baseItem = response.meta['base_item']
        
        product_id_p = sel.xpath('//p[contains(@class, "product_code")]//span/text()').extract()
        if len(product_id_p) == 0:
            return
        
        product_id = product_id_p[0]
        show_product_id = baseItem['show_product_id']

#         baseItem['sizes'] = ['onesize']
        # baseItem['colors'] = ['onecolor']
        images = []
        for image in image_boxs:
            imageItem = ImageItem()

            imageItem['image'] = image.xpath('./@data-zoom-url').extract()[0]
            imageItem['thumbnail'] = image.xpath('.//img/@src').extract()[0]
             
            images.append(imageItem)

        color_lis = sel.xpath('//div[@class="fz_scroller_placeholder container"]/ul/li')
        if len(color_lis)>0:
            baseItem['colors'] = []
            for color_li in color_lis:
                color = Color()
                color['type'] = 'color'
                color['from_site'] = 'forzieri'
                color['images'] = images
                color['show_product_id'] = show_product_id
                # if sel.xpath('//p[contains(@id, "product_variant_name")]'):
                #     color_name = sel.xpath('//p[contains(@id, "product_variant_name")]/text()').extract()[0].strip()
                # else:
                #     color_name = 'onecolor'
                color_name = color_li.xpath('./a/img/@alt').extract()[0].strip()
                color['name'] = color_name
                color['cover'] = color_li.xpath('./a/img/@src').extract()[0]
                baseItem['colors'].append(color_name)
                yield color
        else:
            color = Color()
            color['type'] = 'color'
            color['from_site'] = 'forzieri'
            color['images'] = images
            color['show_product_id'] = show_product_id
            # if sel.xpath('//p[contains(@id, "product_variant_name")]'):
            #     color_name = sel.xpath('//p[contains(@id, "product_variant_name")]/text()').extract()[0].strip()
            # else:
            #     color_name = 'onecolor'
            color['name'] = 'onecolor'
            color['cover'] = images[0]['thumbnail']

        dept_id = sel.xpath('//input[@name="dept_id"]/@value').extract()[0]
        pf_id = show_product_id
        
        skus = []
        if sel.xpath('//select[contains(@id, "variantSelect")]'):
            size_coloum = sel.xpath('//select[contains(@id, "variantSelect")]//option')
            sizes = []
            
            if size_coloum:
                for size_col in size_coloum:
                    skuItem = SkuItem()
                    skuItem['type'] = 'sku'
                    skuItem['show_product_id'] = show_product_id
                    skuItem['from_site'] = "forzieri"
                    skuItem['id'] = size_col.xpath('.//@value').extract()[0] 
                    #skuItem['list_price'] = getItalyPrice[0]
                    #skuItem['current_price'] = getItalyPrice[1]
                    skuItem['size'] = size_col.xpath('./text()').extract()[0]
                    # skuItem['color'] = color_name
                    sizes.append(size_col.xpath('./text()').extract()[0])
                    #yield skuItem
                    skus.append(skuItem)   

                if len(sizes) > 0:
                    baseItem['sizes'] = {'size' : sizes }

                index = 0   
                final_skus = []
                max_list_price = 0
                min_current_price = 0
                
                
                size_ajax_url = 'http://public.forzieri.com/v1/products/' + skus[index]['id'] + '?l=usa&c=usa&t=pv'     #self.sku_ajax_str_prefix+"dept_id="+str(dept_id)+"&pf_id="+quote(str(pf_id))+"&sku="+quote(str(skus[0]['id']))
                yield Request(size_ajax_url, callback=self.parse_sku_sold_out, meta={'dept_id': dept_id, 'pf_id': pf_id, 'baseItem':baseItem, 'skus':skus, 'index': index, 'final_skus':final_skus, 'max_list_price':max_list_price, 'min_current_price':min_current_price, 'color':color})
                
        else :
            baseItem['sizes'] = ['onesize']
            
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = show_product_id
            skuItem['from_site'] = "forzieri"
            skuItem['id'] = product_id
            skuItem['size'] = 'onesize'
            # skuItem['color'] = color_name
            skus.append(skuItem) 
            
            index = 0   
            final_skus = []
            max_list_price = 0
            min_current_price = 0
            
            
            size_ajax_url = 'http://public.forzieri.com/v1/products/' + skus[index]['id'] + '?l=usa&c=usa&t=pv'   # self.sku_ajax_str_prefix+"dept_id="+str(dept_id)+"&pf_id="+quote(str(pf_id))+"&sku="+quote(str(product_id))
            yield Request(size_ajax_url, callback=self.parse_sku_sold_out, meta={'dept_id': dept_id, 'pf_id': pf_id, 'baseItem':baseItem, 'skus':skus, 'index': index, 'final_skus':final_skus, 'max_list_price':max_list_price, 'min_current_price':min_current_price, 'color':color})  
            
    def parse_sku_sold_out(self, response):
        
        min_current_price = response.meta['min_current_price']
        max_list_price = response.meta['max_list_price']
        index = response.meta['index']
        baseItem = response.meta['baseItem']
        skus = response.meta['skus']
        color = response.meta['color']
        # us_url = response.meta['us_url']
        # color = response.meta['color']
        final_skus = response.meta['final_skus']
        dept_id= response.meta['dept_id']

        response_body_str = response.body
        response_body_false = re.sub('false', 'False', response_body_str)
        response_body_true = re.sub('true', 'True', response_body_false)
        response_body_null = re.sub('null', 'None', response_body_true)
        # import pdb;pdb.set_trace()
        ajax_sku = eval(response_body_null)
        # import pdb;pdb.set_trace()
        if 'variant_name' in ajax_sku.keys() and ajax_sku['variant_name']:
            skus[index]['color'] = ajax_sku['variant_name'].strip()
            if 'colors' not in baseItem.keys():
                baseItem['colors'] = []
                baseItem['colors'].append(ajax_sku['variant_name'].strip())
            elif ajax_sku['variant_name'].strip() not in baseItem['colors']:
                baseItem['colors'].append(ajax_sku['variant_name'].strip())
        else:
            skus[index]['color'] = 'onecolor'
            baseItem['colors'] = ['onecolor']
            
            
        if ajax_sku['in_stock'] == True:
            #yield baseItem
            skus[index]['is_outof_stock'] = False
            final_skus.append(skus[index])
        else:
            skus[index]['is_outof_stock'] = True
            final_skus.append(skus[index])

        # print len(self.final_skus)
        # yield Request(us_url.encode('UTF-8'), meta={'baseItem': baseItem, 'skus': final_skus, 'us_url':us_url, "color":color}, callback=self.parse_price)
        on_sale = ajax_sku['on_sale']
        list_price_html = ajax_sku['list_price']
        
        list_price = Selector(text=list_price_html).xpath('//span[@itemprop="price"]/@content').extract()
        
        if len(list_price) > 0:
            list_price = list_price[0]
        else:
            list_price = Selector(text=list_price_html).xpath('//meta[@itemprop="price"]/@content').extract()
            if len(list_price) > 0:
                list_price = list_price[0]
            else:
                list_price = re.search(r'[\,\d\.]+', list_price_html).group(0)

#             list_price = re.search(r'\d+', list_price_html)
        
        skus[index]['list_price'] = list_price

        if on_sale == False:
            skus[index]['current_price'] = list_price
            if max_list_price < list_price:
                max_list_price = list_price
                min_current_price = max_list_price
        else:
            print 111111
            current_price_html = ajax_sku['sale_price']
            print current_price_html
            current_price = Selector(text=current_price_html).xpath('//span[@itemprop="price"]/@content').extract()
            if len(current_price) > 0:
                current_price = current_price[0]
            else:
                current_price = Selector(text=current_price_html).xpath('//meta[@itemprop="price"]/@content').extract()
                if len(current_price) >0:
                    current_price = current_price[0]
                else:
                    current_price = re.search(r'[\,\d\.]+', current_price_html).group(0)

            print current_price
            
#                 current_price = re.search(r'\d+', current_price_html)
            skus[index]['current_price'] = current_price
            if min_current_price == 0 or min_current_price > current_price:
                min_current_price = current_price
            if max_list_price < list_price:
                max_list_price = list_price
                
        if (index+1) == len(skus):
            if len(final_skus) > 0:
                if color['name'] == 'onecolor':
                    color['name'] = baseItem['colors'][0]
                    yield color
                baseItem['list_price'] = max_list_price
                baseItem['current_price'] = min_current_price
                baseItem['skus'] = final_skus
                yield baseItem
        else:
            index = index + 1 
            if index < len(skus):   
                sku_id = skus[index]['id']
                pf_id = re.search(r'\w+\d+-\d+', sku_id).group(0)
                size_ajax_url = 'http://public.forzieri.com/v1/products/' + skus[index]['id'] + '?l=usa&c=usa&t=pv' #self.sku_ajax_str_prefix+"dept_id="+str(dept_id)+"&pf_id="+quote(str(pf_id))+"&sku="+quote(str(sku_id)) 
                yield Request(size_ajax_url, callback=self.parse_sku_sold_out, meta={'dept_id': dept_id, 'baseItem':baseItem, 'skus':skus, 'index': index, 'final_skus':final_skus, 'max_list_price':max_list_price, 'min_current_price':min_current_price, 'color':color})

#     #get italy price
#     def parse_price(self, response):

#         sel = Selector(response)
#         baseItem = response.meta['baseItem']
#         skus = response.meta['skus']
#         us_url = response.meta['us_url']
#         color = response.meta['color']

# #         list_price = 0
# #         current_price = 0
#         if sel.xpath('//span[contains(@id, "salePrice")]/span'):
#             #list_prices = sel.xpath('//span[contains(@id, "salePrice")]')
#             current_prices = sel.xpath('//span[contains(@id, "salePrice")]')
            
#             #list_price = list_prices.xpath('./span[2]/@content').extract()[0]
#             current_price = current_prices.xpath('./span[2]/@content').extract()[0]
            
#             list_price = sel.xpath('//span[contains(@id, "listPrice")]/text()').extract()[0].replace('€','')
#             m = re.match(r'(.)+,(\d{1,2}$)', list_price)
#             if m:
#                 re.sub(r',', '.', m.group(1))
#                 list_price = str(re.match(0)+re.match(1)+re.match(2))

#         if sel.xpath('//span[contains(@id, "listPrice")]/span'):
#             list_prices = sel.xpath('//span[contains(@id, "listPrice")]')
            
#             list_price = list_prices.xpath('./span[2]/@content').extract()[0]
#             current_price = list_price

#         if list_price and current_price:
#             baseItem['list_price'] = list_price
#             baseItem['current_price'] = current_price
            
#             if skus:
#                 for i in range(0, len(skus)):
#                     skus[i]['list_price'] = list_price
#                     skus[i]['current_price'] = current_price
    
#             baseItem['skus'] = skus
    
    
#             yield color
            
#             if sel.xpath('//div[@class="productTitle"]//p/a/text()'):
#                 baseItem['brand'] = sel.xpath('//div[@class="productTitle"]//p/a/text()').extract()[0]
            
#             yield baseItem
            #yield Request(us_url.encode('UTF-8'), meta={'baseItem': baseItem, "color":color}, callback=self.parse_brand) 


    #get brand
    def parse_brand(self, response):

        sel = Selector(response)
        baseItem = response.meta['baseItem']
        color = response.meta['color']
        yield color

        if sel.xpath('//div[@class="productTitle"]//p/a/text()'):
            baseItem['brand'] = sel.xpath('//div[@class="productTitle"]//p/a/text()').extract()[0]
        yield baseItem



class ForzieriSpider(BaseSpider, ForzieriBaseSpider): 
#class ForzieriSpider(RedisSpider):
    name = "forzieri"
    allowed_domains = ["forzieri.com"]
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.05,
        'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        },
        'DOWNLOAD_TIMEOUT': 30
    }

    start_urls = [
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=18',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=13',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=16',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=9',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=25',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=1',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=28',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=5',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=44',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=108',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=108&id_attributo=0027&id_valore=4',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=108&id_attributo=0027&id_valore=1',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=108&id_attributo=0027&id_valore=13',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=6',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=2',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=4',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=11',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=17',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=22',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=12',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=24',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=75&id_attributo=0022&id_valore=1',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=75&id_attributo=0022&id_valore=10',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=75&id_attributo=0022&id_valore=11',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=75&id_attributo=0022&id_valore=12',
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=75&id_attributo=0022&id_valore=16',
        'http://www.cn.forzieri.com/chn/group.asp?l=chn&c=chn&gr=312',
        'http://www.cn.forzieri.com/chn/group.asp?l=chn&c=chn&gr=313',
        'http://www.cn.forzieri.com/chn/group.asp?l=chn&c=chn&gr=314',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=33',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=888801',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=84',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=121',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=888820',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=52',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=53',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=113',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=50',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=81',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=117',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=112',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=1',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=4',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=80',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=32',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=36',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=22',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=115',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=114',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=118',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=77',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=106',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=79',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=107',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=68',
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=104',
        'http://www.cn.forzieri.com/chn/theme.asp?l=chn&c=chn&theme_id=24&dept_id=999909'
    ]


    url_gender_type = {
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=18':{'gender':'women', 'product_type':'bags', 'category':'手提包'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=13':{'gender':'women', 'product_type':'bags', 'category':'购物包'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=16':{'gender':'women', 'product_type':'bags', 'category':'肩背包'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=9':{'gender':'women', 'product_type':'bags', 'category':'手包 & 迷你包'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=25':{'gender':'women', 'product_type':'bags', 'category':'斜挎包'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=1':{'gender':'women', 'product_type':'bags', 'category':'背包'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=28':{'gender':'women', 'product_type':'bags', 'category':'动物元素'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=5':{'gender':'women', 'product_type':'bags', 'category':'桶包'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=18&id_attributo=0013&id_valore=44':{'gender':'women', 'product_type':'bags', 'category':'钱包'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=108':{'gender':'men', 'product_type':'bags', 'category':'斜挎包'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=108&id_attributo=0027&id_valore=4':{'gender':'men', 'product_type':'bags', 'category':'古典型'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=108&id_attributo=0027&id_valore=1':{'gender':'men', 'product_type':'bags', 'category':'背包'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=108&id_attributo=0027&id_valore=13':{'gender':'men', 'product_type':'bags', 'category':'购物包'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=6':{'gender':'women', 'product_type':'shoes', 'category':'凉鞋'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=2':{'gender':'women', 'product_type':'shoes', 'category':'芭蕾舞鞋'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=4':{'gender':'women', 'product_type':'shoes', 'category':'高跟鞋 & 厚底鞋'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=11':{'gender':'women', 'product_type':'shoes', 'category':'牛津穿带鞋'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=17':{'gender':'women', 'product_type':'shoes', 'category':'平台式'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=22':{'gender':'women', 'product_type':'shoes', 'category':'平底鞋'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=12':{'gender':'women', 'product_type':'shoes', 'category':'休闲鞋'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=73&id_attributo=0022&id_valore=24':{'gender':'women', 'product_type':'shoes', 'category':'帆布鞋'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=75&id_attributo=0022&id_valore=1':{'gender':'men', 'product_type':'shoes', 'category':'靴'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=75&id_attributo=0022&id_valore=10':{'gender':'men', 'product_type':'shoes', 'category':'包子鞋'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=75&id_attributo=0022&id_valore=11':{'gender':'men', 'product_type':'shoes', 'category':'牛津穿带鞋'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=75&id_attributo=0022&id_valore=12':{'gender':'men', 'product_type':'shoes', 'category':'休闲鞋'},
        'http://www.cn.forzieri.com/chn/depta.asp?l=chn&c=chn&dept_id=75&id_attributo=0022&id_valore=16':{'gender':'men', 'product_type':'shoes', 'category':'羽翼缝饰'},
        'http://www.cn.forzieri.com/chn/group.asp?l=chn&c=chn&gr=312':{'gender':'women', 'product_type':'jewelry', 'category':'高级珠宝'},
        'http://www.cn.forzieri.com/chn/group.asp?l=chn&c=chn&gr=313':{'gender':'women', 'product_type':'jewelry', 'category':'当代首饰'},
        'http://www.cn.forzieri.com/chn/group.asp?l=chn&c=chn&gr=314':{'gender':'women', 'product_type':'jewelry', 'category':'Murano玻璃'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=33':{'gender':'women', 'product_type':'jewelry', 'category':'女士腕表'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=888801':{'gender':'men', 'product_type':'jewelry', 'category':'男士首饰'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=84':{'gender':'men', 'product_type':'jewelry', 'category':'男士手表'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=121':{'gender':'men', 'product_type':'jewelry', 'category':'Fine Watches'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=888820':{'gender':'women', 'product_type':'accessories', 'category':'围巾'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=52':{'gender':'women', 'product_type':'accessories', 'category':'女士腰带'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=53':{'gender':'women', 'product_type':'accessories', 'category':'女士手套'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=113':{'gender':'women', 'product_type':'accessories', 'category':'手机袋'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=50':{'gender':'women', 'product_type':'accessories', 'category':'女帽'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=81':{'gender':'women', 'product_type':'accessories', 'category':'太阳眼镜'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=117':{'gender':'women', 'product_type':'accessories', 'category':'钥匙袋'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=112':{'gender':'women', 'product_type':'accessories', 'category':'钱包'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=1':{'gender':'men', 'product_type':'accessories', 'category':'领带'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=4':{'gender':'men', 'product_type':'accessories', 'category':'男士围巾'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=80':{'gender':'men', 'product_type':'accessories', 'category':'太阳镜'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=32':{'gender':'men', 'product_type':'accessories', 'category':'男士手套'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=36':{'gender':'men', 'product_type':'accessories', 'category':'男帽'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=22':{'gender':'men', 'product_type':'accessories', 'category':'男士皮带'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=115':{'gender':'men', 'product_type':'accessories', 'category':'钱包'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=114':{'gender':'men', 'product_type':'accessories', 'category':'手机袋'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=118':{'gender':'men', 'product_type':'accessories', 'category':'钥匙袋'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=77':{'gender':'women', 'product_type':'clothing', 'category':'夹克衫和外套'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=106':{'gender':'women', 'product_type':'clothing', 'category':'外套 & 皮草'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=79':{'gender':'men', 'product_type':'clothing', 'category':'皮革夹克'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=107':{'gender':'men', 'product_type':'clothing', 'category':'外套'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=68':{'gender':'men', 'product_type':'clothing', 'category':'衬衫'},
        'http://www.cn.forzieri.com/chn/deptd.asp?l=chn&c=chn&dept_id=104':{'gender':'men', 'product_type':'clothing', 'category':'polo衫'},
        'http://www.cn.forzieri.com/chn/theme.asp?l=chn&c=chn&theme_id=24&dept_id=999909':{'gender':'baby', 'product_type':'bags', 'category':'孩童系列'},
    }


    base_url = 'http://www.forzieri.com'
    
    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类
    test_i = 0
    
    def parse(self, response):
        sel = Selector(response)
        uri_head_lis = sel.xpath('//div[contains(@class, "product_list container")]//article')
        
#         req_url = re.sub('&page=\w', '', response.url)
#         if req_url not in self.start_urls:
#             return
        req_url = response.url
        
        if req_url in self.url_gender_type.keys():
            gender = self.url_gender_type[req_url]['gender']
            product_type = self.url_gender_type[req_url]['product_type']
            category = self.url_gender_type[req_url]['category']
        else:
            gender = response.meta['gender']
            product_type = response.meta['product_type']
            category = response.meta['category']

        for li in uri_head_lis:
            url = li.xpath('.//a[contains(@class, "thumbs")]//@href').extract()[0] 
            cover = li.xpath('.//a[contains(@class, "thumbs")]//img/@src').extract()[0] 

            item = BaseItem()
            item['from_site'] = 'forzieri'
            item['url'] = url
            item['cover'] = cover
            item['gender'] = gender
            item['product_type'] = product_type
            item['category'] = category
            
            self.test_i = self.test_i + 1
            print self.test_i
            
            yield Request(url.encode('UTF-8'), callback=self.parse_item, meta={'item':item})

        if sel.xpath('//div[contains(@class, "pagination")]//a[contains(@class, "next-page")]'):
            next_url = sel.xpath('//div[contains(@class, "pagination")]//a[contains(@class, "next-page")]/@href').extract()[0]
            
            yield Request(next_url.encode('UTF-8'), callback=self.parse, meta={'gender': gender, 'product_type': product_type, 'category':category})


    #item
    def parse_item(self, response):
        item = response.meta['item']

        return self.handle_parse_item(response, item)

        
    def handle_parse_item(self, response, item):
        return ForzieriBaseSpider.handle_parse_item(self, response, item)



       
        

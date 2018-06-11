# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
import re
import math
from gorden_crawler.spiders.shiji_base import BaseSpider
from __builtin__ import False


class BlueflySpider(BaseSpider):
    name = "bluefly"
    allowed_domains = ["bluefly.com"]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.25,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }
    
    '''
    正式运行的时候，start_urls为空，通过传参数来进行
    '''
    start_urls = (
                  'http://www.bluefly.com/kids/girls',
                  'http://www.bluefly.com/kids/boys',
                  'http://www.bluefly.com/kids/baby-nursery',
                  'http://www.bluefly.com/kids/toys',
                  'http://www.bluefly.com/men/clothing',
                  'http://www.bluefly.com/men/shoes',
                  'http://www.bluefly.com/men/men-accessories',
                  'http://www.bluefly.com/women/clothing',
                  'http://www.bluefly.com/women/shoes',
                  'http://www.bluefly.com/women/handbags-wallets/handbags',
                  'http://www.bluefly.com/women/handbags-wallets/wallets',
                  'http://www.bluefly.com/women/women-accessories',
                  'http://www.bluefly.com/women/fine-jewelry',
                  'http://www.bluefly.com/women/watches',
#         'http://www.bluefly.com/women/index',
#         'http://www.bluefly.com/women/shoes',
#         'http://www.bluefly.com/handbags/index',
#         'http://www.bluefly.com/women/women-accessories',
#         'http://www.bluefly.com/fine-jewelry/index',
#         'http://www.bluefly.com/women/fine-jewelry',
#         'http://www.bluefly.com/fine-jewelry/index',
#         'http://www.bluefly.com/women/watches',
#         'http://www.bluefly.com/men/clothing',
#         'http://www.bluefly.com/men/shoes',
#         'http://www.bluefly.com/men/men-accessories',
#         'http://www.bluefly.com/kids/baby-nursery',
#         'http://www.bluefly.com/kids/boys',
#         'http://www.bluefly.com/kids/girls',
# #         'http://www.bluefly.com/kids/boys?vl=l&ppp=48&cp=1',
#         'http://www.bluefly.com/kids/girls',
# #         'http://www.bluefly.com/kids/designer-toys',
#         'http://www.bluefly.com/kids/toys',
#         'http://www.bluefly.com/kids/toys/kids-toys-4-14-years',
#         'http://www.bluefly.com/kids/girls',
#         'http://www.bluefly.com/kids/toys',
#         'http://www.bluefly.com/kids/toys/kids-toys-4-14-years',
# #         'http://www.bluefly.com/kids/designer-toddler-boy-2t-5t?vl=l&ppp=48&cp=1',
    )
    
    url_genger_product_type_map = {
            'http://www.bluefly.com/kids/girls': {'gender': 'girls', 'product_type': 'mother-kid'},
            'http://www.bluefly.com/kids/boys': {'gender': 'boys', 'product_type': 'mother-kid'},
            'http://www.bluefly.com/kids/baby-nursery': {'gender': 'baby', 'product_type': 'mother-kid'},
            'http://www.bluefly.com/kids/toys': {'gender': 'toddler', 'product_type': 'mother-kid', 'category': 'toys'},
            'http://www.bluefly.com/men/clothing': {'gender': 'men', 'product_type': 'clothing'},
            'http://www.bluefly.com/men/shoes': {'gender': 'men', 'product_type': 'shoes'},
            'http://www.bluefly.com/men/men-accessories': {'gender': 'men', 'product_type': 'accessories'},
#             'http://www.bluefly.com/beauty/men-grooming-cologne',
            'http://www.bluefly.com/women/clothing': {'gender': 'women', 'product_type': 'clothing'},
            'http://www.bluefly.com/women/shoes': {'gender': 'women', 'product_type': 'shoes'},
            'http://www.bluefly.com/women/handbags-wallets/handbags': {'gender': 'women', 'product_type': 'handbags'},
            'http://www.bluefly.com/women/handbags-wallets/wallets': {'gender': 'women', 'product_type': 'wallets'},
            'http://www.bluefly.com/women/women-accessories': {'gender': 'women', 'product_type': 'accessories'},
#             'http://www.bluefly.com/beauty/women-beauty-fragrance',
            'http://www.bluefly.com/women/fine-jewelry': {'gender': 'women', 'product_type': 'jewelry'},
            'http://www.bluefly.com/women/watches': {'gender': 'women', 'product_type': 'watches'},
#         'http://www.bluefly.com/women/index' : {'gender': 'women', 'product_type': 'clothing'},
#         'http://www.bluefly.com/women/shoes' : {'gender': 'women', 'product_type': 'shoes'},
#         'http://www.bluefly.com/handbags/index': {'gender': 'women', 'product_type': 'handbags'},
#         'http://www.bluefly.com/women/women-accessories': {'gender': 'women', 'product_type': 'accessories'},
#         'http://www.bluefly.com/fine-jewelry/index': {'gender': 'women', 'product_type': 'jewelry'},
#         'http://www.bluefly.com/women/fine-jewelry': {'gender': 'women', 'product_type': 'jewelry'},
#         'http://www.bluefly.com/fine-jewelry/index': {'gender': 'women', 'product_type': 'jewelry'},
#         'http://www.bluefly.com/women/watches': {'gender': 'women', 'product_type': 'watches'},
#         'http://www.bluefly.com/men/clothing': {'gender': 'men', 'product_type': 'clothing'},
#         'http://www.bluefly.com/men/shoes': {'gender': 'men', 'product_type': 'shoes'},
#         'http://www.bluefly.com/men/men-accessories': {'gender': 'men', 'product_type': 'accessories'},
#         'http://www.bluefly.com/kids/baby-nursery': {'gender': 'baby', 'product_type': 'mother-kid'},
#         'http://www.bluefly.com/kids/boys': {'gender': 'boys', 'product_type': 'mother-kid'},
#         'http://www.bluefly.com/kids/girls': {'gender': 'girls', 'product_type': 'mother-kid'},
# #         'http://www.bluefly.com/kids/boys?vl=l&ppp=48&cp=1': {'gender': 'toddler', 'product_type': 'mother-kid'},
#         'http://www.bluefly.com/kids/girls': {'gender': 'toddler', 'product_type': 'mother-kid'},
#         'http://www.bluefly.com/kids/designer-toys': {'gender': 'toddler', 'product_type': 'mother-kid'},
#         'http://www.bluefly.com/kids/toys': {'gender': 'baby', 'product_type': 'mother-kid', 'category': 'toys'},
#         'http://www.bluefly.com/kids/toys/kids-toys-4-14-years': {'gender': 'kid-unisex', 'product_type': 'mother-kid', 'category': 'toys'},
# #         'http://www.bluefly.com/kids/boys?vl=l&ppp=48&cp=1': {'gender': 'toddler', 'product_type': 'mother-kid'},
#         'http://www.bluefly.com/kids/girls': {'gender': 'toddler', 'product_type': 'mother-kid'},
#         'http://www.bluefly.com/kids/designer-toys': {'gender': 'toddler', 'product_type': 'mother-kid'},
#         'http://www.bluefly.com/kids/toys': {'gender': 'baby', 'product_type': 'mother-kid', 'category': 'toys'},
#         'http://www.bluefly.com/kids/toys/kids-toys-4-14-years': {'gender': 'kid-unisex', 'product_type': 'mother-kid', 'category': 'toys'},
# #         'http://www.bluefly.com/kids/toys/designer-toddler-toys-1-3-yrs?vl=l&ppp=48&cp=1': {'gender': 'toddler', 'product_type': 'mother-kid', 'category': 'toys'},
    }
    
    base_url = 'http://www.bluefly.com'


    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def handle_parse_item(self, response, item):
        
        sel = Selector(response)
        
        if len(sel.xpath('//input[@id="waitlistSubmit"]').extract()) > 0:
            return
        if len(sel.xpath("//button[@id='add-to-cart']")) > 1:
            return
        if 'preowned' in response.url:
            return
        size_chart_url = sel.xpath('//div[@class="popover-content"]/img/@src').extract()
        if len(size_chart_url) > 0:
            size_chart_url = size_chart_url[0]
            item['size_info'] = {'size_chart_url': size_chart_url}
        
        color_li = sel.xpath('//ul[@class="product-color-list"]/li[1]')

        colorItem = Color()
        colorItem['from_site'] = self.name
        colorItem['show_product_id'] = item['show_product_id']
        colorItem['type'] = 'color'
        
        if len(color_li) > 0:
            color_name_text = color_li.xpath('./a/@data-color').extract()
            cover_text = color_li.xpath('./a/img/@src').extract()
            if len(cover_text) > 0 and len(color_name_text) > 0:
                colorItem['cover'] =  'http:' + cover_text[0]
                colorItem['name'] = color_name_text[0]
                color_name = color_name_text[0]
            else:
                cover_text = color_li.xpath('./a/div[@class="center-cropped"]/@style').re('url\(\'(.+)\'\)')
                if len(cover_text) > 0 and len(color_name_text) > 0:
                    colorItem['cover'] =  'http:' + cover_text[0]
                    colorItem['name'] = color_name_text[0]
                    color_name = color_name_text[0]
                else:
                    return
                
        elif len(sel.xpath('//span[@class="mz-productoptions-optionvalue"]/text()').extract()) > 0:
            color_name_text = sel.xpath('//span[@class="mz-productoptions-optionvalue"]/text()').extract()
            if len(color_name_text) == 0:
                return
            color_name = color_name_text[0]
            colorItem['name'] = color_name
        else:
            color_name = 'one_color'
            colorItem['name'] = color_name

                
        colorImages = []
        color_image_array = sel.xpath('//div[@id="productimages"]/img')
        if len(color_image_array) > 0:
            for color_image in color_image_array:
                if len(color_image.xpath('./@src'))>0:
                    color_image_thumb = 'http:' + color_image.xpath('./@src').extract()[0]
                else:
                    color_image_thumb = 'http:' + color_image.xpath('./@data-src').extract()[0]
                if len(color_image.xpath('./@data-zoom'))>0:
                    color_image_url = 'http:' + color_image.xpath('./@data-zoom').extract()[0]
                else:
                    color_image_url = color_image_thumb.replace('537','2160')
                    
                if 'cover' not in colorItem.keys():
                    colorItem['cover'] = color_image_thumb.replace('537','40')
                colorImages.append({
                    'thumbnail': color_image_thumb,
                    'image':  color_image_url
                })
                
            colorItem['images'] = colorImages    
            
            yield colorItem
            
        item['colors'] = [color_name]
        item['dimensions'] = ['size']
    
#             if sel.xpath('//div[@class="mz-productoptions-valuecontainer"]').extract() <= 0:
#                 item['size'] = 'One Size'
        skus = []
        sizes = []
        sku_spans = sel.xpath('//span[@class="mz-productoptions-sizebox   "] | //span[@class="mz-productoptions-sizebox   selected-box"]')
        sku_color = sel.xpath('//div[@class="mz-productoptions-optioncontainer colorList"]/div/span[@class="mz-productoptions-optionvalue"]/text()')
        if len(sku_color)>0:
            sku_color = sku_color.extract()[0]
        else:
            sku_color = 'one_color'
            
        if len(sku_spans)>0:
            for sku_span in sku_spans:
                skuItem = SkuItem()
                skuItem['type'] = 'sku'
                skuItem['from_site'] = self.name
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['id'] = item['show_product_id'] + '-' + sku_span.xpath('./@data-value').extract()[0]
                
                list_price = sel.xpath('//div[@class="mz-price is-crossedout"]/text()')
                current_price = sel.xpath('//div[@class="mz-price"]/text()')

                if len(current_price) > 0:
                    if '-' in current_price.extract()[0]:
                        current_price = current_price.re('-\s*\$(\S+)')[0]
                    else:
                        current_price = current_price.re(r'(\S+)')[0]
                elif len(sel.xpath('//div[@class="mz-price is-saleprice"]/text()')) > 0:
                    current_price = sel.xpath('//div[@class="mz-price is-saleprice"]/text()')
                    if '-' in current_price.extract()[0]:
                        current_price = current_price.re('-\s*\$(\S+)')[0]
                    else:
                        current_price = current_price.re(r'(\S+)')[0]

                if len(list_price) > 0:
                    if re.findall('Retail', list_price.extract()[0]):
                        list_price = list_price.re(r'[\d\.]+')[0]
                    else:
                        list_price = list_price.re(r'(\S+)')[0]
                else:
                    list_price = current_price
                skuItem["list_price"] = list_price
                skuItem['current_price'] = current_price
                skuItem['color'] = color_name
                skuItem['size'] = sku_span.xpath('text()').extract()[0].strip()
                skuItem['is_outof_stock'] = False
                
                sizes.append(skuItem['size'])
                skus.append(skuItem)
        else:
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['from_site'] = self.name
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['id'] = item['show_product_id']
            
            list_price = sel.xpath('//div[@class="mz-price is-crossedout"]/text()')
            current_price = sel.xpath('//div[@class="mz-price"]/text()')
            
            if len(current_price) > 0:
                current_price = current_price.re(r'(\S+)')[0]
            elif len(sel.xpath('//div[@class="mz-price is-saleprice"]/text()')) > 0:
                current_price = sel.xpath('//div[@class="mz-price is-saleprice"]/text()').re(r'(\S+)')[0]
            
            if len(list_price) > 0:
                if re.findall('Retail', list_price.extract()[0]):
                    list_price = list_price.re(r'[\d\.]+')[0]
                else:
                    list_price = list_price.re(r'(\S+)')[0]
            else:
                list_price = current_price
            
            skuItem["list_price"] = list_price
            skuItem['current_price'] = current_price
            
            skuItem['color'] = color_name
            skuItem['size'] = 'One Size'
            skuItem['is_outof_stock'] = False
            sizes.append(skuItem['size'])
            skus.append(skuItem)
        item['sizes'] = sizes
        item['skus'] = skus
        
        desc_div = sel.xpath('//div[@class="mz-productdetail-description"]/text()').extract()
        desc_lis = sel.xpath('//ul[@class="mz-productdetail-props"]/li').extract()
        if len(desc_div) > 0:
            item['desc'] = desc_div[0]
        else:
            item['desc'] = ''

        if len(desc_lis) > 0:
            item['desc'] += ''.join(desc_lis)

        yield item


    '''具体的解析规则'''
    def parse_item(self, response):
        
#         item = BaseItem()
#         item['type'] = 'base'
#         item['show_product_id'] = '1209118'
        item = response.meta['item']
        return self.handle_parse_item(response, item)
     
     
    def handle_parse_list(self, response):
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        category = response.meta['category']

        if 'sub_category' in response.meta.keys():
            sub_category = response.meta['sub_category']
        else:
            sub_category = None

        sel = Selector(response)
        lis = sel.xpath('//li[@class="mz-productlist-item"]')

        for li in lis:
            item = BaseItem()
            item['from_site'] = self.name
            item['type'] = 'base'
            item['show_product_id'] = li.xpath('@data-mz-product').extract()[0]

            cover_original_dom = li.xpath('.//img/@data-original').extract()

            if len(cover_original_dom) > 0:
                item['cover'] = 'http:' + cover_original_dom[0]
            else:
                cover_img_src = li.xpath('.//img/@src').extract()
                if len(cover_img_src) > 0:
                    item['cover'] = 'http:' + cover_img_src[0]
                else:
                    continue

            product_uri_div = li.xpath('.//div[@class="mz-productlisting-info"]/a/@href').extract()

            if len(product_uri_div) > 0:
                uri = product_uri_div[0]
            else:
                print 'hit_list_uri_empty_'+str(item['show_product_id']) + ",url = " + response.url
                continue

            item['url'] = self.base_url + uri
            item['title'] = li.xpath('.//div[@class="product-grid-name"]/text()').extract()[0].strip()
            item['brand'] = li.xpath('.//div[@class="product-grid-brand"]/text()').extract()[0].strip()
            item['gender'] = gender
            item['product_type'] = product_type
            item['category'] = category
            item['sub_category'] = sub_category

            priceBlueFlySpan = li.xpath('.//div[@class="mz-price is-saleprice"]/text()').re(r'(\S+)')
            if len(priceBlueFlySpan) > 0:
                item['current_price'] = priceBlueFlySpan[0]
            else:
                current_sale_price_div = li.xpath('.//div[@class="mz-price"]/text()').re(r'(\S+)')

                if len(current_sale_price_div) > 0:
                    item['current_price'] = current_sale_price_div[0]
                else:
                    print 'hit_list_current_price_empty_'+str(item['show_product_id'])
                    continue

            listPriceSpan = li.xpath('.//div[@class="mz-price is-crossedout"]/text()').re(r'(\S+)')
            if len(listPriceSpan) > 0:
                item['list_price'] = listPriceSpan[0]
            else:
                item['list_price'] = item['current_price']
            yield Request(item['url'], callback=self.parse_item, meta={'item': item})

        '''翻页'''
        total_dom = sel.xpath('//div[@class="page-itemcount"]/text()').re(r'\s*([\d\.]+)\s*[itemsITEMS]+\s*')
        if len(total_dom) > 0:
            total = float(total_dom[0].replace(',', ''))
            page_num = math.ceil(total / 48)
            current_page_num = int(sel.xpath('//span[@class="mz-pagenumbers-number is-current"]/text()').extract()[0])
            if current_page_num < page_num:
                current_url = response.url
                if re.search(r'startIndex', current_url):
                    url = current_url.replace('?startIndex='+ str((current_page_num-1) * 48), '?startIndex=' + str(current_page_num * 48))
                else:
                    url = current_url + "?startIndex=" + str(current_page_num * 48)
                yield Request(url, callback=self.handle_parse_list, meta={'product_type': product_type, 'gender': gender, 'category': category})
        else:
            print 'hit' + response.url

#     def parse_list(self, response):
#         print 'parse_list'
#         gender = response.meta['gender']
#         product_type = response.meta['product_type']
#         category = response.meta['category']
#
#         if 'sub_category' in response.meta.keys():
#             sub_category = response.meta['sub_category']
#         else:
#             sub_category = None
#
#         return self.handle_parse_list(response, {'gender': gender, 'product_type': product_type, 'category': category, 'sub_category': sub_category})

    def parse_category(self, response):
        product_type = response.meta['product_type']
        gender = response.meta['gender']
        category = response.meta['category']
        
        sel = Selector(response)
         
        category_divs = sel.xpath('//div[@class="mz-l-sidebaritem category-facets"]/ul/li/ul/li')
        if len(category_divs) > 0: 
            for category_div in category_divs:
                uri = category_div.xpath('./a/@href').extract()[0].strip()
                 
                url = self.base_url+uri
                 
                sub_category = category_div.xpath('./a/text()').extract()[0].strip()
                yield Request(url, callback=self.handle_parse_list, meta={'product_type': product_type, 'gender': gender, 'category': category, 'sub_category': sub_category})
        else:
            yield Request(response.url, callback=self.handle_parse_list, meta={'product_type': product_type, 'gender': gender, 'category': category}, dont_filter=True)
#             '''翻页'''
#             total_dom = sel.xpath('//div[@class="page-itemcount"]/text()').re(r'\s*([\d\.]+)\s*[itemsITEMS]+\s*')
#               
#             if len(total_dom) > 0:  
#                 total = int(total_dom[0].replace(',', ''))
#                   
#                 page_num = math.ceil(total / 48)
#                   
#                 current_page_num = int(sel.xpath('//span[@class="mz-pagenumbers-number is-current"]/text()').extract()[0])
#                   
#                 if current_page_num < page_num:
#                     current_url = response.url
#                        
#                     if re.search(r'\?startIndex=\d+$', current_url) :
#                         url = current_url.replace('\?startIndex='+ str((current_page_num-1) * 48), '?startIndex=' + str(current_page_num * 48))
#                     else:
#                         url = current_url + "?startIndex=" + str(current_page_num * 48)
#                     yield Request(url, callback=self.parse_list, meta={'product_type': product_type, 'gender': gender, 'category': category})
#             else:
#                 print 'hit' + response.url
#          
#             lis = sel.xpath('//li[@class="mz-productlist-item"]')
#               
#             for li in lis:
#                 item = BaseItem()
#                 item['from_site'] = self.name
#                 item['type'] = 'base'
#                 item['show_product_id'] = li.xpath('@data-mz-product').extract()[0]    
#                 
#                 cover_original_dom = li.xpath('.//img/@data-original').extract()
#                 
#                 if len(cover_original_dom) > 0:
#                     item['cover'] = 'http:' + cover_original_dom[0]
#                 else:
#                     cover_img_src = li.xpath('.//img/@src').extract()
#                     if len(cover_img_src) > 0:
#                         item['cover'] = 'http:' + cover_img_src[0]
#                     else:
#                         continue
#                   
#                 product_uri_div = li.xpath('.//div[@class="mz-productlisting-info"]/a/@href').extract()
#                 
#                 if len(product_uri_div) > 0:
#                     uri = product_uri_div[0]
#                 else:
#                     print 'hit_list_uri_empty_'+str(item['show_product_id']) + ",url = " + response.url
#                     continue
#                 
#                 item['url'] = self.base_url + uri
#                 item['title'] = li.xpath('.//div[@class="product-grid-name"]/text()').extract()[0].strip()
#                 item['brand'] = li.xpath('.//div[@class="product-grid-brand"]/text()').extract()[0].strip()
#                 item['gender'] = gender
#                 item['product_type'] = product_type
#                 item['category'] = category
#       
#                 priceBlueFlySpan = li.xpath('.//div[@class="mz-price is-saleprice"]/text()').re(r'(\S+)')
#                 if len(priceBlueFlySpan) > 0:
#                     item['current_price'] = priceBlueFlySpan[0]
#                 else:
#                     current_sale_price_div = li.xpath('.//div[@class="mz-price"]/text()').re(r'(\S+)')
#                     
#                     if len(current_sale_price_div) > 0:
#                         item['current_price'] = current_sale_price_div[0]
#                     else:
#                         print 'hit_list_current_price_empty_'+str(item['show_product_id'])
#                         continue;
#                       
#                 listPriceSpan = li.xpath('.//div[@class="mz-price is-crossedout"]/text()').re(r'(\S+)')
#                 if len(listPriceSpan) > 0:
#                     item['list_price'] = listPriceSpan[0]
#                 else:
#                     item['list_price'] = item['current_price']
#                 
#                 yield Request(item['url'], callback=self.parse_item, meta={'item': item})
        
    '''
    爬虫解析入口函数，用于解析丢入的第一个请求，一般是顶级目录页
    '''
    def parse(self, response):
        gender = self.url_genger_product_type_map[response.url]['gender']
        product_type = self.url_genger_product_type_map[response.url]['product_type']

        sel = Selector(response)
        if 'category' in self.url_genger_product_type_map[response.url].keys():
            
            category = self.url_genger_product_type_map[response.url]['category']

            yield Request(response.url, callback=self.handle_parse_list, meta={'product_type': product_type, 'gender': gender, 'category': category}, dont_filter=True)
#             '''翻页'''
#             total_dom = sel.xpath('//div[@class="page-itemcount"]/text()').re(r'\s*([\d\.]+)\s*[itemsITEMS]+\s*')
#               
#             if len(total_dom) > 0:
#                 total = int(total_dom[0].replace(',', ''))
#                   
#                 page_num = math.ceil(total / 48)
#                   
#                 current_page_num = int(sel.xpath('//span[@class="mz-pagenumbers-number is-current"]/text()').extract()[0])
#                   
#                 if current_page_num < page_num:
#                     current_url = response.url
#                        
#                     if re.search(r'\?startIndex=\d+$', current_url) :
#                         url = current_url.replace('\?startIndex='+ str((current_page_num-1) * 48), '?startIndex=' + str(current_page_num * 48))
#                     else:
#                         url = current_url + "?startIndex=" + str(current_page_num * 48)
#                     print 'parse,parse_list', url
#                     yield Request(url, callback=self.parse_list, meta={'product_type': product_type, 'gender': gender, 'category': category})
#             else:
#                 print 'hit' + response.url
         
#             lis = sel.xpath('//li[@class="mz-productlist-item"]')
#               
#             for li in lis:
#                 item = BaseItem()
#                 item['from_site'] = self.name
#                 item['type'] = 'base'
#                 item['show_product_id'] = li.xpath('@data-mz-product').extract()[0]    
#                 
#                 cover_original_dom = li.xpath('.//img/@data-original').extract()
#                 
#                 if len(cover_original_dom) > 0:
#                     item['cover'] = 'http:' + cover_original_dom[0]
#                 else:
#                     cover_img_src = li.xpath('.//img/@src').extract()
#                     if len(cover_img_src) > 0:
#                         item['cover'] = 'http:' + cover_img_src[0]
#                     else:
#                         continue
#                   
#                 product_uri_div = li.xpath('.//div[@class="mz-productlisting-info"]/a/@href').extract()
#                 
#                 if len(product_uri_div) > 0:
#                     uri = product_uri_div[0]
#                 else:
#                     print 'hit_list_uri_empty_'+str(item['show_product_id']) + ",url = " + response.url
#                     continue
#                 
#                 item['url'] = self.base_url + uri
#                 item['title'] = li.xpath('.//div[@class="product-grid-name"]/text()').extract()[0].strip()
#                 item['brand'] = li.xpath('.//div[@class="product-grid-brand"]/text()').extract()[0].strip()
#                 item['gender'] = gender
#                 item['product_type'] = product_type
#                 item['category'] = category
#       
#                 priceBlueFlySpan = li.xpath('.//div[@class="mz-price is-saleprice"]/text()').re(r'(\S+)')
#                 if len(priceBlueFlySpan) > 0:
#                     item['current_price'] = priceBlueFlySpan[0]
#                 else:
#                     current_sale_price_div = li.xpath('.//div[@class="mz-price"]/text()').re(r'(\S+)')
#                     
#                     if len(current_sale_price_div) > 0:
#                         item['current_price'] = current_sale_price_div[0]
#                     else:
#                         print 'hit_list_current_price_empty_'+str(item['show_product_id'])
#                         continue;
#                       
#                 listPriceSpan = li.xpath('.//div[@class="mz-price is-crossedout"]/text()').re(r'(\S+)')
#                 if len(listPriceSpan) > 0:
#                     item['list_price'] = listPriceSpan[0]
#                 else:
#                     item['list_price'] = item['current_price']
#                 
#                 yield Request(item['url'], callback=self.parse_item, meta={'item': item})
        else:
     
            category_lis = sel.xpath('//div[@class="mz-l-sidebaritem category-facets"]/ul/li/ul/li')

            for category_li in category_lis:
                uri = category_li.xpath('./a/@href').extract()[0]
                 
                url = self.base_url+uri
                 
                category = category_li.xpath('./a/text()').extract()[0].strip()
                yield Request(url, meta={'product_type': product_type, 'gender': gender, 'category': category}, callback=self.parse_category)

            category = product_type
            yield Request(response.url, callback=self.handle_parse_list, meta={'product_type': product_type, 'gender': gender, 'category': category}, dont_filter=True)

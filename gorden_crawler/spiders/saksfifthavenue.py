# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from gorden_crawler.spiders.shiji_base import BaseSpider
import logging
import re
import execjs
import json
import os

class SaksfifthavenueBaseSpider(object):

    def handle_parse_item(self, response, item):
        match = re.search(r'<script type\=\"application\/json\">({"ProductDetails".+?)<\/script>', response.body)
        print match.group(1)
        sel = Selector(response)
        if match is None:
            return
        
        context = execjs.compile('''
            var json = %s
            function getJson(){
                return json;
            }
        ''' % match.group(1))
        
        product_json = context.call('getJson')
        
        main_product = product_json['ProductDetails']['main_products'][0]
    
        item['brand'] = main_product['brand_name']['label']
        item['title'] = main_product['short_description']
        show_product_id = main_product['product_code']
        item['show_product_id'] = show_product_id
        item['desc'] = main_product['description']
        
        list_price =  main_product['price']['list_price']['usd_currency_value']
        if re.findall('\-', list_price):
            re.search('([\d\.]+)\s*\-', list_price).group(1)
        else:
            item['list_price'] = list_price
            
        sale_price = main_product['price']['sale_price']['usd_currency_value']
        if re.findall('\-', sale_price):
            re.search('([\d\.]+)\s*\-', sale_price).group(1)
        else:
            item['current_price'] = sale_price
        
        item['dimensions'] = ['size']
        skus = []
        sizes = {}
        sizes['size'] = []
        color_names = []
        
        colors = main_product['colors']['colors']
        
        handle_color_map = {}
        if len(colors) > 0:
            for color in colors:
                handle_color_map[color['id']] = color['label']
        
        handle_size_map = {}
        if len(main_product['sizes']['sizes']) == 0:
            sizes['size'].append('onesize')
        else:
            for size in main_product['sizes']['sizes']:
                handle_size_map[size['id']] = size['value']
                sizes['size'].append(size['value'])
        
        image_prefix = 'http:' + main_product['media']['images_server_url'] + main_product['media']['images_path']
        
        if len(colors) == 0:
            color_name = 'onecolor'
            color_names.append(color_name)
    
            common_images = main_product['media']['images']
            
            images = []
            
            for common_image in common_images:
                imageItem = ImageItem()
                imageItem['image'] = image_prefix + common_image + '?wid=970&hei=1293&fmt=jpg'
                imageItem['thumbnail'] = image_prefix + common_image + '?wid=396&hei=528&fmt=jpg'
                images.append(imageItem) 
            
            first_thumbnail = images[0]['thumbnail'] 
            
            colorItem = Color()
             
            colorItem['type'] = 'color'
            colorItem['from_site'] = item['from_site']
            colorItem['show_product_id'] = item['show_product_id']
            colorItem['images'] = images
            colorItem['name'] = color_name
            colorItem['cover'] = first_thumbnail
            colorItem['version'] = '1'
            yield colorItem
        else:
            common_images = main_product['media']['images']
            
            for color in colors:
                color_name = color['label']
                color_names.append(color_name)
                
                images = []
                
                imageItem = ImageItem()
                
                imageItem['image'] = image_prefix + color['colorize_image_url'] + '?wid=970&hei=1293&fmt=jpg'
                imageItem['thumbnail'] = image_prefix + color['colorize_image_url'] + '?wid=396&hei=528&fmt=jpg'
                
                images.append(imageItem)
                
                first_thumbnail = images[0]['thumbnail']
                
                for common_image in common_images:
                    
                    imageItem = ImageItem()
                    
                    imageItem['image'] = image_prefix + common_image + '?wid=970&hei=1293&fmt=jpg'
                    imageItem['thumbnail'] = image_prefix + common_image + '?wid=396&hei=528&fmt=jpg'
                        
                    images.append(imageItem) 
                
                colorItem = Color()
                 
                colorItem['type'] = 'color'
                colorItem['from_site'] = item['from_site']
                colorItem['show_product_id'] = item['show_product_id']
                colorItem['images'] = images
                colorItem['name'] = color_name
                colorItem['version'] = '1'
                if len(color['value']) > 0:
                    if re.findall('\#', color['value']):
                        colorItem['cover_style'] = color['value']
                    else:
                        cover_img_str = sel.xpath('//li[@class="product-color-options__value" and @data-colorid=' + str(color["id"]) + ']/@style').extract()
                        cover_unavi_str = sel.xpath('//li[@class="product-color-options__value product-color-options__value--unavailable" and @data-colorid=' + str(color["id"]) + ']/@style').extract()
                        cover_sel_str = sel.xpath('//li[@class="product-color-options__value product-color-options__value--selected" and @data-colorid=' + str(color["id"]) + ']/@style').extract()
                        cover_hid_str = sel.xpath('//li[@class="product-color-options__value is-hidden" and @data-colorid=' + str(color["id"]) + ']/@style').extract()
                        
                        if len(cover_img_str)>0:
                            cover_img = re.search('\((.+)\)', cover_img_str[0]).group(1)
                            colorItem['cover'] = 'http:' + cover_img
                        elif len(cover_unavi_str)>0:
                            cover_img_str = cover_unavi_str[0]
                            cover_img = re.search('\((.+)\)', cover_img_str).group(1)
                            colorItem['cover'] = 'http:' + cover_img
                        elif len(cover_sel_str)>0:
                            cover_img_str = cover_sel_str[0]
                            cover_img = re.search('\((.+)\)', cover_img_str).group(1)
                            colorItem['cover'] = 'http:' + cover_img
                        elif len(cover_hid_str)>0:
                            cover_img_str = cover_hid_str[0]
                            cover_img = re.search('\((.+)\)', cover_img_str).group(1)
                            colorItem['cover'] = 'http:' + cover_img
                        else:
                            colorItem['cover'] = first_thumbnail
                else:
                    colorItem['cover'] = first_thumbnail
                
                yield colorItem
        
        item['colors'] = color_names
        
        for sku in main_product['skus']['skus']:
            sku_id = sku['sku_id']
            if sku_id == 'DUMMY':
                continue
            
            if sku['color_id'] == -1:
                color_name = 'onecolor'
            else:
                color_name = handle_color_map[sku['color_id']]
            
            if sku['size_id'] == -1:
                size = 'onesize'
            else:
                size = handle_size_map[sku['size_id']]
        
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['from_site'] = item['from_site']
            skuItem['id'] = sku_id
            skuItem['size'] = size
            skuItem['color'] = color_name
        
            if sku['status_alias'] == 'soldout' or sku['status_alias'] == 'waitlist':
                skuItem['is_outof_stock'] = True
            else:
                skuItem['is_outof_stock'] = False
            
            if len(sku['price']['sale_price']['usd_currency_value']) > 0:
                skuItem['current_price'] = sku['price']['sale_price']['usd_currency_value']
            else:
                continue
            
            if len(sku['price']['list_price']['usd_currency_value']) > 0:
                skuItem['list_price'] = sku['price']['list_price']['usd_currency_value']
            else:
                continue
             
            skus.append(skuItem)
            
        item['sizes'] = sizes
        item['skus'] = skus
        
        if main_product['size_guide_link']['enabled'] == True:
            sizeInfo = main_product['size_guide_link']['url']
            findQ = sizeInfo.find("?")
            if findQ != -1:
                item['size_info'] = sizeInfo[:findQ]
            else: 
                item['size_info'] = sizeInfo
        
        yield item

    # def handle_parse_item(self,response,item):
    #     sel = Selector(response)
    #     if len(sel.xpath('//div[contains(@class, "main-product")]//div[contains(@class, "sold-out-message")]').extract()) > 0:
    #         return
    # 
    #     jsonStr = "".join(re.findall(r'<script type="text/javascript">[\s]*(var mlrs = .*)[\s]*</script>', response.body))
    # 
    #     if jsonStr == '':
    #         if os.environ.get('item_update_notify_redis') == 'True':
    #             logging.warning('old')
    #         
    #         detail_block = sel.xpath('//div[re:test(@class, "\s*pdp-item-container clearfix\s*$")]')
    #         
    #         item['brand'] = detail_block.xpath('.//h1[@class="brand"]/text()').extract()[0]
    #         title = detail_block.xpath('.//h2[@class="description"]/text()').extract()
    #         if len(title) > 0:
    #             item['title'] = title[0]
    #         else:
    #             item['title'] = item['brand']
    #             
    #         item['show_product_id'] = detail_block.xpath('.//h3[@class="product-code-reskin"]/text()').extract()[0]
    #         item['desc'] = detail_block.xpath('.//span[@class="pdp-reskin-detail-content"]').extract()[0]
    # 
    #         list_price = detail_block.xpath('.//span[@class="product-price"]/text()').re(r'^\s*\$([\d\.]+)')[0]
    #         
    #         sale_price = detail_block.xpath('.//span[@class="product-sale-price"]/text()').re(r'^\s*\$([\d\.]+)')
    #         if len(sale_price) > 0:
    #             current_price = sale_price[0]
    #         else:
    #             current_price = list_price
    #             
    #         item['current_price'] = current_price
    #         item['list_price'] = list_price
    #          
    #         item['dimensions'] = ['size']
    #         skus = []
    #         sizes = {}
    #         sizes['size'] = []
    #         color_names = []
    #         
    #         options = detail_block.xpath('//select[@productcode="' + item['show_product_id'] + '"]/option')
    #         
    #         if len(options) > 0:
    #             for option in options:
    #                 
    #                 sku_id = option.xpath('./@value').extract()[0]
    #                 
    #                 if sku_id == '0':
    #                     continue
    #                 
    #                 skuItem = SkuItem()
    #                 skuItem['type'] = 'sku'
    #                 skuItem['show_product_id'] = item['show_product_id']
    #                 skuItem['from_site'] = item['from_site']
    #                 skuItem['id'] = sku_id
    #                 
    #                 size = option.xpath('./@data-product-size').extract()[0]
    #                 if size == '.' or size == 'NO SIZE':
    #                     size = 'onesize'
    #                 skuItem['size'] = size
    #                 if size not in sizes['size']:
    #                     sizes['size'].append(size)
    #                     
    #                 color = option.xpath('./@data-colorname').extract()[0]
    #                 if color == 'NO COLOR':
    #                     color = 'onecolor'
    # 
    #                 skuItem['color'] = color
    #                 if color not in color_names:
    #                     color_names.append(color)
    #                 
    #                 is_outof_stock = False
    #                 wait_list = option.xpath('./@data-waitlist')
    #                 if len(wait_list) > 0:
    #                     if wait_list.extract()[0] == "true":
    #                         is_outof_stock = True
    #                 
    #                 skuItem['is_outof_stock'] = is_outof_stock
    #                 skuItem['current_price'] = item['current_price']
    #                 skuItem['list_price'] = item['list_price']
    #                 
    #                 skus.append(skuItem)
    #         else:
    #             sku_id = sel.xpath('//div[@id="pdSizeColor--MainProductqtyToBuy0"]/input[@name="ADD_CART_ITEM_ARRAY<>sku_id"]/@value').extract()[0]
    #             
    #             skuItem = SkuItem()
    #             skuItem['type'] = 'sku'
    #             skuItem['show_product_id'] = item['show_product_id']
    #             skuItem['from_site'] = item['from_site']
    #             skuItem['id'] = sku_id
    #         
    #             skuItem['size'] = 'onesize'
    #             sizes['size'].append('onesize')
    #             
    #             skuItem['color'] = 'onecolor'
    #             color_names.append('onecolor')
    #             
    #             skuItem['current_price'] = item['current_price']
    #             skuItem['list_price'] = item['list_price']
    #             skuItem['is_outof_stock'] = False
    #             
    #             skus.append(skuItem)
    #         
    #         item['skus'] = skus
    #         item['sizes'] = sizes
    #         
    #         item['colors'] = []   
    #         select_colors = detail_block.xpath('.//div[@class="product-swatches-container"]')
    #         if len(select_colors) > 0:
    #             color_lis = detail_block.xpath('.//div[@class="product-swatches-container"]//ul/li')
    #             
    #             for color_li in color_lis:
    #                 
    #                 color_div = color_li.xpath('.//div[@class="swatch-thumbnail"]')
    #                 
    #                 image_url = color_div.xpath('./@data-url').extract()[0]
    #                 color_name = color_div.xpath('./@data-color').extract()[0]
    #                 
    #                 item['colors'].append(color_name)
    #                 
    #                 imageItem = ImageItem()
    #                 imageItem['thumbnail'] = "http://image.s5a.com/is/image/" + image_url + '_247x329.jpg'
    #                 imageItem['image'] = "http://image.s5a.com/is/image/" + image_url + '_396x528.jpg'
    # 
    #                 colorItem = Color()
    #                 
    #                 colorItem['type'] = 'color'
    #                 colorItem['from_site'] = item['from_site']
    #                 colorItem['show_product_id'] = item['show_product_id']
    #                 colorItem['images'] = [imageItem]
    #                 colorItem['name'] = color_name
    #                 
    #                 color_style = color_div.xpath('./@style')
    #                 
    #                 if len(color_style) > 0:
    #                     colorItem['cover_style'] = color_style.re(r'background-color:(.+);')[0]
    #                     if '#' not in colorItem['cover_style']:
    #                         colorItem['cover_style'] = '' + colorItem['cover_style']
    #                 else:
    #                     colorItem['cover'] = imageItem['thumbnail']
    #                 
    #                 yield colorItem
    #         else:
    #             color_name = color_names[0]
    #                 
    #             item['colors'].append(color_name)
    #             
    #             imageItem = ImageItem()
    #             imageItem['thumbnail'] = "http://image.s5a.com/is/image/saks/" + item['show_product_id'] + '_247x329.jpg'
    #             imageItem['image'] = "http://image.s5a.com/is/image/saks/" + item['show_product_id'] + '_396x528.jpg'
    #             
    #             colorItem = Color()
    #                 
    #             colorItem['type'] = 'color'
    #             colorItem['from_site'] = item['from_site']
    #             colorItem['show_product_id'] = item['show_product_id']
    #             colorItem['images'] = [imageItem]
    #             colorItem['name'] = color_name
    #             colorItem['cover'] = imageItem['thumbnail']
    #             
    #             yield colorItem
    #         
    #         size_info_div = detail_block.xpath('.//div[@class="size-additional-info"]/a/@href').re(r'\'(http://.+)\',')
    #         
    #         if len(size_info_div) > 0:
    #             size_info = size_info_div[0]
    #             findQ = size_info.find("?")
    #             if findQ != -1:
    #                 item['size_info'] = size_info[:findQ]
    #             else:
    #                 item['size_info'] = size_info
    #         
    #         yield item
    #         
    #     else:
    #         context = execjs.compile('''
    #             %s
    #             function getMlrs(){
    #                 return mlrs;
    #             }
    #         ''' % jsonStr)
    #         
    #         mlrs = context.call('getMlrs')
    # 
    # 
    #         item['brand'] = mlrs['response']['body']['main_products'][0]['brand_name']['label']
    #         item['title'] = mlrs['response']['body']['main_products'][0]['short_description']
    #         if item['title'] == '':
    #             item['title'] = item['brand']
    #         item['show_product_id'] = mlrs['response']['body']['main_products'][0]['product_code']
    #         item['desc'] = mlrs['response']['body']['main_products'][0]['description']
    #         find = mlrs['response']['body']['main_products'][0]['price']['sale_price'].find(" - ")
    #         if find != -1:
    #             item['current_price'] = mlrs['response']['body']['main_products'][0]['price']['sale_price'][:find].replace("&#36;",'')
    #         else:
    #             item['current_price'] = mlrs['response']['body']['main_products'][0]['price']['sale_price'].replace("&#36;",'')
    #         
    #         find2 = mlrs['response']['body']['main_products'][0]['price']['list_price'].find(" - ")
    #         if find2 != -1:
    #             item['list_price'] = mlrs['response']['body']['main_products'][0]['price']['list_price'][find2+3:].replace("&#36;",'')
    #         else:
    #             item['list_price'] = mlrs['response']['body']['main_products'][0]['price']['list_price'].replace("&#36;",'')
    #         
    #         colors = {}
    #         item['colors'] = []
    #         if len(mlrs['response']['body']['main_products'][0]['colors']['colors']) > 0:
    #             for color in mlrs['response']['body']['main_products'][0]['colors']['colors']:
    #                 colors[color['color_id']] = color['label']
    #                 item['colors'].append(color['label'])
    #                 imageItem = ImageItem()
    #                 imageItem['thumbnail'] = "http:" + mlrs['response']['body']['main_products'][0]['media']['images_server_url'] + "is/image/" + color['colorized_image_url'] + '_247x329.jpg'
    #                 imageItem['image'] = "http:" + mlrs['response']['body']['main_products'][0]['media']['images_server_url'] + "is/image/" + color['colorized_image_url'] + '_396x528.jpg'
    # 
    #                 colorItem = Color()
    #                 colorItem['type'] = 'color'
    #                 colorItem['from_site'] = item['from_site']
    #                 colorItem['show_product_id'] = item['show_product_id']
    #                 colorItem['images'] = [imageItem]
    #                 colorItem['name'] = color['label']
    #                 if color['value'] != '':
    #                     colorItem['cover_style'] = '#' + color['value']
    #                 else:
    #                     colorItem['cover'] = imageItem['thumbnail']
    #                 
    #                 yield colorItem
    #         else:
    #             colors[-1] = 'onecolor'
    #             item['colors'].append('onecolor')
    #             imageItem = ImageItem()
    #             imageItem['thumbnail'] = "http:" + mlrs['response']['body']['main_products'][0]['media']['images_server_url'] + mlrs['response']['body']['main_products'][0]['media']['images']['product_array_image']
    #             imageItem['image'] = "http:" + mlrs['response']['body']['main_products'][0]['media']['images_server_url'] + mlrs['response']['body']['main_products'][0]['media']['images']['product_detail_image']
    # 
    #             colorItem = Color()
    #             colorItem['type'] = 'color'
    #             colorItem['from_site'] = item['from_site']
    #             colorItem['show_product_id'] = item['show_product_id']
    #             colorItem['images'] = [imageItem]
    #             colorItem['name'] = 'onecolor'
    #             yield colorItem
    # 
    #         item['dimensions'] = ['size']
    #         sizes = {}
    #         item['sizes'] = []
    #         if len(mlrs['response']['body']['main_products'][0]['sizes']['sizes']) > 0:
    #             for size in mlrs['response']['body']['main_products'][0]['sizes']['sizes']:
    #                 sizes[size['size_id']] = size['value']
    #                 item['sizes'].append(size['value'])
    #         else:
    #             sizes[-1] = 'onesize'
    #             item['sizes'].append('onesize')
    # 
    #         item['skus'] = []
    #         for sku in mlrs['response']['body']['main_products'][0]['skus']['skus']:
    #             if sku['color_id'] in colors.keys() and sku['size_id'] in sizes.keys():
    #                 skuItem = {}
    #                 skuItem['type'] = 'sku'
    #                 skuItem['show_product_id'] = item['show_product_id']
    #                 skuItem['id'] = sku['sku_id']
    #                 skuItem['list_price'] = sku['price']['list_price'].replace("&#36;",'')
    #                 skuItem['current_price'] = sku['price']['sale_price'].replace("&#36;",'')
    #                 skuItem['color'] = colors[sku['color_id']]
    #                 skuItem['size'] = sizes[sku['size_id']]
    #                 
    #                 skuItem['from_site'] = item['from_site']
    #                 skuItem['is_outof_stock'] = False if sku['status_alias'] == 'available' else True
    #                 item['skus'].append(skuItem)
    # 
    #         if mlrs['response']['body']['main_products'][0]['size_guide_link']['enabled']:
    #             sizeInfo = mlrs['response']['body']['main_products'][0]['size_guide_link']['url']
    #             findQ = sizeInfo.find("?")
    #             if findQ != -1:
    #                 item['size_info'] = sizeInfo[:findQ]
    #             else: 
    #                 item['size_info'] = sizeInfo
    #         
    #         yield item



class SaksfifthavenueSpider(BaseSpider,SaksfifthavenueBaseSpider):
    name = "saksfifthavenue"
    allowed_domains = ["saksfifthavenue.com"]

    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.5,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'http://www.saksfifthavenue.com',
        ]

    base_url = 'http://www.saksfifthavenue.com'
    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)

        navDom = sel.xpath(".//div[@class='nav']/ul/li")

        navStandard = {
            'WomensApparelNavMenu':{'gender':'women', 'product_type':'clothing'},
            'ShoesNavMenu':{'gender':'women', 'product_type':'shoes'},
            'HandbagsNavMenu':{'gender':'women', 'product_type':'bags'},
            'JewelryAccessoriesNavMenu':{'gender':'women', 'product_type':'accessories'},
            'TheMensStoreNavMenu':{'gender':'men', 'product_type':'clothing'},
            'JustKidsNavMenu':{'gender':'baby', 'product_type':'mother&baby'},
            'SaksBeautyPlaceNavMenu':{'gender':'women', 'product_type':'beauty'}
        }

        for nav in navDom:
            navId = nav.xpath("./@id").extract()[0]
            if navId in navStandard.keys():
                if navId == 'HandbagsNavMenu' or navId == 'JewelryAccessoriesNavMenu':
                    menuDom = nav.xpath(".//ul[@class='sub-menu']/li[2]/ul[1]/li")
                    for dom in menuDom:
                        category = dom.xpath("./a/text()").extract()[0]
                        if category not in ['Shop All','New Arrivals','Best Sellers']:
                            url = dom.xpath("./a/@href").extract()[0]
                            yield Request(url, callback=self.parse_list, meta={"category_url":url, "category":category, "gender":navStandard[navId]['gender'], "product_type":navStandard[navId]['product_type']})

                elif navId == 'TheMensStoreNavMenu':
                    menuDom = nav.xpath(".//ul[@class='sub-menu']/li[2]/ul[1]/li")
                    for dom in menuDom:
                        category = dom.xpath("./a/text()").extract()[0]
                        if category not in ['Shop All','New Arrivals','Best Sellers']:
                            url = dom.xpath("./a/@href").extract()[0]
                            yield Request(url, callback=self.parse_list, meta={"category_url":url, "category":category, "gender":navStandard[navId]['gender'], "product_type":'shoes'})

                    menuDom = nav.xpath(".//ul[@class='sub-menu']/li[2]/ul[2]/li")
                    for dom in menuDom:
                        category = dom.xpath("./a/text()").extract()[0]
                        if category not in ['Shop All','New Arrivals','Best Sellers']:
                            url = dom.xpath("./a/@href").extract()[0]
                            yield Request(url, callback=self.parse_list, meta={"category_url":url, "category":category, "gender":navStandard[navId]['gender'], "product_type":'accessories'})

                elif navId == 'JustKidsNavMenu':
                    menuDom = nav.xpath(".//ul[@class='sub-menu']/li[1]/ul[2]/li")
                    for dom in menuDom:
                        category = dom.xpath("./a/text()").extract()[0]
                        if category not in ['Shop All','New Arrivals','Best Sellers']:
                            url = dom.xpath("./a/@href").extract()[0]
                            gender = 'toddler' if category == 'Girls (2-6)' else 'girls'
                            yield Request(url, callback=self.parse_list, meta={"category_url":url, "category":category, "gender":gender, "product_type":navStandard[navId]['product_type']})
                    menuDom = nav.xpath(".//ul[@class='sub-menu']/li[1]/ul[3]/li")
                    for dom in menuDom:
                        category = dom.xpath("./a/text()").extract()[0]
                        if category not in ['Shop All','New Arrivals','Best Sellers']:
                            url = dom.xpath("./a/@href").extract()[0]
                            gender = 'toddler' if category == 'Boys (2-6)' else 'boys'
                            yield Request(url, callback=self.parse_list, meta={"category_url":url, "category":category, "gender":gender, "product_type":navStandard[navId]['product_type']})

                elif navId == 'SaksBeautyPlaceNavMenu':
                    menuDom = nav.xpath(".//ul[@class='sub-menu']/li[1]/ul[3]/li")
                    for dom in menuDom:
                        category = dom.xpath("./a/text()").extract()[0]
                        if category not in ['Shop All','New Arrivals','Best Sellers']:
                            url = dom.xpath("./a/@href").extract()[0]
                            gender = 'women'
                            yield Request(url, callback=self.parse_list, meta={"category_url":url, "category":category, "gender":gender, "product_type":navStandard[navId]['product_type']})
                    menuDom = nav.xpath(".//ul[@class='sub-menu']/li[2]/ul[1]/li")
                    for dom in menuDom:
                        category = dom.xpath("./a/text()").extract()[0]
                        if category not in ['Shop All','New Arrivals','Best Sellers']:
                            url = dom.xpath("./a/@href").extract()[0]
                            gender = 'men'
                            yield Request(url, callback=self.parse_list, meta={"category_url":url, "category":category, "gender":gender, "product_type":navStandard[navId]['product_type']})
                else:
                    menuDom = nav.xpath(".//ul[@class='sub-menu']/li[1]/ul[1]/li")
                    for dom in menuDom:
                        category = dom.xpath("./a/text()").extract()[0]
                        if category not in ['Shop All', 'New Arrivals', 'Best Sellers', 'Special Offers','Bag Accessories']:
                            url = dom.xpath("./a/@href").extract()[0]
                            yield Request(url, callback=self.parse_list, meta={"category_url": url, "category": category, "gender": navStandard[navId]['gender'], "product_type": navStandard[navId]['product_type']})

    def parse_list(self, response):
        category = response.meta['category']
        gender = response.meta['gender']
        product_type = response.meta['product_type']
        category_url = response.meta['category_url']
        sel = Selector(response)
        
        # if len(sel.xpath(".//div[@id='pc-top']/div[1]/span[1]/text()").extract()) == 0:
        #     return

        listDom = sel.xpath(".//*[@id='product-container']/div[@class!='pa-row-spacer' and @class!='clear']")
        if len(listDom.extract()) > 0:
            for dom in listDom:
                item = BaseItem()
                item['from_site'] = 'saksfifthavenue'
                item['type'] = 'base'
                item['category'] = category
                item['product_type'] = product_type
                item['gender'] = gender
                # item['title'] = dom.xpath("./div[@class='product-text']//p[@class='product-description']/text()").extract()[0]
                # item['brand'] = dom.xpath("./div[@class='product-text']//span[@class='product-designer-name']/text()").extract()[0]
                # item["show_product_id"] = dom.xpath("./div[@class='product-text']/a/p[1]/@productcode").extract()[0]
                # item['cover'] = dom.xpath("./div[@class='sfa-pa-product-swatches-container']/div[1]/img/@data-src").extract()[0]
                pid = dom.xpath("./div[@class='image-container-large']/a[1]/@name").extract()[0]
                item['cover'] = dom.xpath("./div[@class='image-container-large']/a[@id='image-url-" + pid +"']/img[last()]/@src").extract()[0]

                item["url"] = url = dom.xpath("./div[@class='product-text']/a/@href").extract()[0]
                
                yield Request(url, callback=self.parse_item, meta={"item": item})

            if len(sel.xpath(".//*[@id='pc-top']/ol//a[@class='page-selected']/text()")) == 0:
                currentPage = 1
            else:
                currentPage = sel.xpath(".//*[@id='pc-top']/ol//a[@class='page-selected']/text()").extract()[0]
            countStr = sel.xpath(".//div[@id='pc-top']/div[1]/span[1]/text()").extract()[0]
            countTotal = int(countStr.replace(',','').replace('.','').replace(' ',''))
            lastPage = countTotal / 60 + 1 if countTotal % 60 > 0 else countTotal / 60
            if int(currentPage) < int(lastPage):
                list_more_url = category_url + '&Nao=' + str((int(currentPage))*60)
                yield Request(list_more_url, callback=self.parse_list, meta={"category":category, "product_type":product_type,"gender":gender, "category_url":category_url})


        else:
            return

    def parse_item(self, response):
        item = response.meta['item']

        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):

        return SaksfifthavenueBaseSpider.handle_parse_item(self, response, item)
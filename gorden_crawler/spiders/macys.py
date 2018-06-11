# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
import re
from gorden_crawler.spiders.shiji_base import BaseSpider
import math
import urlparse
import json
from HTMLParser import HTMLParser
import base64

class MacysSpider(BaseSpider):
#class zappoSpider(RedisSpider):
    name = "macys"
    allowed_domains = ["macys.com"]
    
    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_TIMEOUT': 30,
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 0.01,
    }
    
    image_prefix = 'http://slimages.macysassets.com/is/image/MCY/products/'
    
    cookies = [
                {'name': 'shippingCountry','value': 'US', 'domain': '.macys.com', 'path': '/'},
                {'name': 'currency','value': 'USD', 'domain': '.macys.com', 'path': '/'}
    ]
    
    '''
    正式运行的时候，start_urls为空，通过传参数来进行，通过传递参数 -a 处理
    '''
    start_urls = (
        'http://www1.macys.com/shop/womens-clothing/womens-blazers?id=55429',
        'http://www1.macys.com/shop/womens-clothing/shop-all-lingerie?id=59459',
        'http://www1.macys.com/shop/womens-clothing/pajamas-and-robes?id=59737',
        'http://www1.macys.com/shop/womens-clothing/womens-capri-pants?id=44717',
        'http://www1.macys.com/shop/womens-clothing/womens-coats?id=269',
        'http://www1.macys.com/shop/womens-clothing/dresses?id=5449',
        'http://www1.macys.com/shop/womens-clothing/womens-jackets?id=120',
        'http://www1.macys.com/shop/womens-clothing/womens-jeans?id=3111',
        'http://www1.macys.com/shop/womens-clothing/womens-jumpsuits-rompers?id=50684',
        'http://www1.macys.com/shop/womens-clothing/leggings?id=46905',
        'http://www1.macys.com/shop/womens-clothing/maternity-clothes?id=66718',
        'http://www1.macys.com/shop/womens-clothing/womens-pants?id=157',
        'http://www1.macys.com/shop/womens-clothing/womens-shorts?id=5344',
        'http://www1.macys.com/shop/womens-clothing/womens-skirts?id=131',
        'http://www1.macys.com/shop/womens-clothing/womens-suits?id=67592',
        'http://www1.macys.com/shop/womens-clothing/womens-sweaters?id=260',
        'http://www1.macys.com/shop/womens-clothing/womens-swimwear?id=8699',
        'http://www1.macys.com/shop/womens-clothing/womens-tops?id=255',
         
        'http://www1.macys.com/shop/mens-clothing/mens-blazers-sports-coats?id=16499',
        'http://www1.macys.com/shop/mens-clothing/mens-casual-shirts?id=20627',
        'http://www1.macys.com/shop/mens-clothing/mens-jackets-coats?id=3763',
        'http://www1.macys.com/shop/mens-clothing/mens-dress-shirts?id=20635',
        'http://www1.macys.com/shop/mens-clothing/hoodies-for-men?id=25995',
        'http://www1.macys.com/shop/mens-clothing/mens-jeans?id=11221',
        'http://www1.macys.com/shop/mens-clothing/mens-pajamas?id=16295',
        'http://www1.macys.com/shop/mens-clothing/mens-pants?id=89',
        'http://www1.macys.com/shop/mens-clothing/mens-polo-shirts?id=20640',
        'http://www1.macys.com/shop/mens-clothing/mens-shirts?id=20626',
        'http://www1.macys.com/shop/mens-clothing/mens-shorts?id=3310',
        'http://www1.macys.com/shop/mens-clothing/mens-suits?id=17788',
        'http://www1.macys.com/shop/mens-clothing/mens-sweaters?id=4286',
        'http://www1.macys.com/shop/mens-clothing/mens-swimwear?id=3291',
        'http://www1.macys.com/shop/mens-clothing/mens-t-shirts?id=30423',
        'http://www1.macys.com/shop/mens-clothing/mens-tuxedos-formalwear?id=68524',
        'http://www1.macys.com/shop/mens-clothing/mens-underwear?id=57',
               
        'http://www1.macys.com/shop/mens-clothing/guys-clothing?id=60451',
        'http://www1.macys.com/shop/womens-clothing/petite-clothing?id=18579',
        'http://www1.macys.com/shop/junior-clothing?id=16904',
        'http://www1.macys.com/shop/makeup-and-perfume?id=669',
        
        'http://www1.macys.com/shop/kids-clothes/baby-clothing?id=64761',
        'http://www1.macys.com/shop/kids-clothes/girls-clothing?id=61998',
        'http://www1.macys.com/shop/kids-clothes/boys-clothing?id=61999',
         
        'http://www1.macys.com/shop/shoes/all-womens-shoes?id=56233',
        'http://www1.macys.com/shop/handbags-accessories/handbags?id=27686',
        'http://www1.macys.com/shop/handbags-accessories/accessories?id=29440',
        'http://www1.macys.com/shop/handbags-accessories/tablet-phone-cases-accessories?id=69112',
        'http://www1.macys.com/shop/jewelry/all-fine-jewelry?id=65993',
        'http://www1.macys.com/shop/jewelry/all-fashion-jewelry?id=55352',
        'http://www1.macys.com/shop/jewelry/womens-watches?id=57385',
         
        'http://www1.macys.com/shop/mens-clothing/shop-all-mens-footwear?id=55822',
        'http://www1.macys.com/shop/mens-clothing/mens-accessories?id=47665',
        'http://www1.macys.com/shop/mens-clothing/mens-backpacks-bags?id=45016',
        'http://www1.macys.com/shop/mens-clothing/mens-belts-suspenders?id=47673',
        'http://www1.macys.com/shop/makeup-and-perfume/cologne-for-men?id=30088',
        'http://www1.macys.com/shop/mens-clothing/mens-hats-gloves-scarves?id=47657',
        'http://www1.macys.com/shop/mens-clothing/mens-socks?id=18245',
        'http://www1.macys.com/shop/mens-clothing/mens-sunglasses?id=58262',
        'http://www1.macys.com/shop/mens-clothing/mens-ties-pocket-squares?id=53239',
        'http://www1.macys.com/shop/jewelry/mens-watches?id=57386',
    )
    
    url_attr_map = {
#         'http://www1.macys.com/shop/womens-clothing/womens-activewear?id=29891': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'activewear'},
        'http://www1.macys.com/shop/womens-clothing/womens-blazers?id=55429': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'blazers'},
        'http://www1.macys.com/shop/womens-clothing/shop-all-lingerie?id=59459': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'lingerie'},
        'http://www1.macys.com/shop/womens-clothing/pajamas-and-robes?id=59737': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'pajamas-and-robes'},
        'http://www1.macys.com/shop/womens-clothing/womens-capri-pants?id=44717': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'capri-pants'},
        'http://www1.macys.com/shop/womens-clothing/womens-coats?id=269': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'coats'},
        'http://www1.macys.com/shop/womens-clothing/dresses?id=5449': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'dresses'},
        'http://www1.macys.com/shop/womens-clothing/womens-jackets?id=120': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'jackets'},
        'http://www1.macys.com/shop/womens-clothing/womens-jeans?id=3111': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'jeans'},
        'http://www1.macys.com/shop/womens-clothing/womens-jumpsuits-rompers?id=50684': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'jumpsuits-rompers'},
        'http://www1.macys.com/shop/womens-clothing/leggings?id=46905': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'leggings'},
        'http://www1.macys.com/shop/womens-clothing/maternity-clothes?id=66718': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'maternity'},
        'http://www1.macys.com/shop/womens-clothing/womens-pants?id=157': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'pants'},
        'http://www1.macys.com/shop/womens-clothing/womens-shorts?id=5344': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'shorts'},
        'http://www1.macys.com/shop/womens-clothing/womens-skirts?id=131': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'skirts'},
        'http://www1.macys.com/shop/womens-clothing/womens-suits?id=67592': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'suits & suit separates'},
        'http://www1.macys.com/shop/womens-clothing/womens-sweaters?id=260': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'sweaters'},
        'http://www1.macys.com/shop/womens-clothing/womens-swimwear?id=8699': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'swimwear'},
        'http://www1.macys.com/shop/womens-clothing/womens-tops?id=255': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'tops'},
              
        'http://www1.macys.com/shop/mens-clothing/mens-blazers-sports-coats?id=16499': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'blazers-sports-coats'},
        'http://www1.macys.com/shop/mens-clothing/mens-casual-shirts?id=20627': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'mens-casual-shirts'},
        'http://www1.macys.com/shop/mens-clothing/mens-jackets-coats?id=3763': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'jackets-coats'},
        'http://www1.macys.com/shop/mens-clothing/mens-dress-shirts?id=20635': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'blazers-sports-coats'},
        'http://www1.macys.com/shop/mens-clothing/hoodies-for-men?id=25995': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'hoodies'},
        'http://www1.macys.com/shop/mens-clothing/mens-jeans?id=11221': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'jeans'},
        'http://www1.macys.com/shop/mens-clothing/mens-pajamas?id=16295': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'pajamas'},
        'http://www1.macys.com/shop/mens-clothing/mens-pants?id=89': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'pants'},
        'http://www1.macys.com/shop/mens-clothing/mens-polo-shirts?id=20640': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'polo'},
        'http://www1.macys.com/shop/mens-clothing/mens-shirts?id=20626': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'shirts'},
        'http://www1.macys.com/shop/mens-clothing/mens-shorts?id=3310': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'shorts'},
        'http://www1.macys.com/shop/mens-clothing/mens-suits?id=17788': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'suits'},
        'http://www1.macys.com/shop/mens-clothing/mens-sweaters?id=4286': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'sweaters'},
        'http://www1.macys.com/shop/mens-clothing/mens-swimwear?id=3291': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'swimwear'},
        'http://www1.macys.com/shop/mens-clothing/mens-t-shirts?id=30423': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 't-shirts'},
        'http://www1.macys.com/shop/mens-clothing/mens-tuxedos-formalwear?id=68524': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'tuxedos-formalwear'},
        'http://www1.macys.com/shop/mens-clothing/mens-underwear?id=57': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'second', 'category': 'underwear'},
              
        'http://www1.macys.com/shop/mens-clothing/guys-clothing?id=60451': {'gender': 'men', 'product_type': 'clothing', 'crawl_type': 'first'},
        'http://www1.macys.com/shop/womens-clothing/petite-clothing?id=18579': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'first'},
        'http://www1.macys.com/shop/junior-clothing?id=16904': {'gender': 'women', 'product_type': 'clothing', 'crawl_type': 'first'},
        'http://www1.macys.com/shop/makeup-and-perfume?id=669': {'gender': 'women','product_type': 'beauty', 'crawl_type': 'first', 'bold_li_seq': '2'},
        
        'http://www1.macys.com/shop/kids-clothes/baby-clothing?id=64761': {'product_type': 'motherbaby', 'crawl_type': 'first', 'gender': 'baby', 'category_key': 'KIDS_APPAREL_TYPE'},
        'http://www1.macys.com/shop/kids-clothes/girls-clothing?id=61998': {'product_type': 'motherbaby', 'crawl_type': 'first', 'gender': 'girls', 'category_key': 'KIDS_APPAREL_TYPE'},
        'http://www1.macys.com/shop/kids-clothes/boys-clothing?id=61999': {'product_type': 'motherbaby', 'crawl_type': 'first', 'gender': 'girls', 'category_key': 'KIDS_APPAREL_TYPE'},
        
        'http://www1.macys.com/shop/shoes/all-womens-shoes?id=56233': {'product_type': 'shoes', 'gender': 'women', 'crawl_type': 'second', 'category_key': 'SHOE_TYPE'},
        'http://www1.macys.com/shop/handbags-accessories/handbags?id=27686': {'gender': 'women','product_type': 'bags', 'crawl_type': 'second', 'category_key': 'HANDBAG_STYLE'},
        'http://www1.macys.com/shop/handbags-accessories/accessories?id=29440': {'gender': 'women','product_type': 'accessories', 'crawl_type': 'second', 'category_key': 'ACCESSORIES_TYPE'},
        'http://www1.macys.com/shop/handbags-accessories/tablet-phone-cases-accessories?id=69112': {'gender': 'women','product_type': 'accessories', 'crawl_type': 'second', 'category_key': 'ACCESSORIES_TYPE'},
        'http://www1.macys.com/shop/jewelry/all-fine-jewelry?id=65993': {'gender': 'women','product_type': 'accessories', 'crawl_type': 'second', 'category_key': 'JEWELRY_TYPE'},
        'http://www1.macys.com/shop/jewelry/all-fashion-jewelry?id=55352': {'gender': 'women','product_type': 'accessories', 'crawl_type': 'second', 'category_key': 'JEWELRY_TYPE'},
        'http://www1.macys.com/shop/jewelry/womens-watches?id=57385': {'gender': 'women','product_type': 'accessories', 'crawl_type': 'second', 'category': 'watches'},
        
        'http://www1.macys.com/shop/mens-clothing/shop-all-mens-footwear?id=55822': {'product_type': 'shoes', 'gender': 'men', 'crawl_type': 'second', 'category_key': 'SHOE_TYPE'},
        'http://www1.macys.com/shop/mens-clothing/mens-accessories?id=47665': {'gender': 'men','product_type': 'accessories', 'crawl_type': 'second', 'category_key': 'ACCESSORIES_TYPE'},
        'http://www1.macys.com/shop/mens-clothing/mens-backpacks-bags?id=45016': {'gender': 'men','product_type': 'bags', 'crawl_type': 'second', 'category_key': 'LUGGAGE_TYPE'},
        'http://www1.macys.com/shop/mens-clothing/mens-belts-suspenders?id=47673': {'gender': 'men','product_type': 'accessories', 'crawl_type': 'second', 'category': 'belts-suspenders'},
        'http://www1.macys.com/shop/makeup-and-perfume/cologne-for-men?id=30088': {'gender': 'men','product_type': 'beauty', 'crawl_type': 'second', 'category_key': 'BEAUTY'},
        'http://www1.macys.com/shop/mens-clothing/mens-hats-gloves-scarves?id=47657': {'gender': 'men','product_type': 'accessories', 'crawl_type': 'second', 'category_key': 'ACCESSORIES_TYPE'},
        'http://www1.macys.com/shop/mens-clothing/mens-socks?id=18245': {'gender': 'men','product_type': 'accessories', 'crawl_type': 'second', 'category': 'socks'},
        'http://www1.macys.com/shop/mens-clothing/mens-sunglasses?id=58262': {'gender': 'men','product_type': 'accessories', 'crawl_type': 'second', 'category': 'sunglasses'},
        'http://www1.macys.com/shop/mens-clothing/mens-ties-pocket-squares?id=53239': {'gender': 'men','product_type': 'accessories', 'crawl_type': 'second', 'category': 'ties-pocket-squares'},
        'http://www1.macys.com/shop/jewelry/mens-watches?id=57386': {'gender': 'men','product_type': 'accessories', 'crawl_type': 'second', 'category': 'watches'},
    }
    
    base_url = 'http://www1.macys.com'
    size_chart_pic_url = 'http://www1.macys.com/dyn_img/size_charts/'

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, cookies=self.cookies)

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, cookies=self.cookies)

    def handle_parse_item(self, response, item):
        
        '''第一种情况'''
        sel = Selector(response)
        product_json_str_dom = sel.xpath('//script[@id="productMainData"]/text()').extract()
        if len(product_json_str_dom) > 0:
            product_json_str = product_json_str_dom[0]
                
            product_json = json.loads(product_json_str)
            
            show_product_id = product_json['id']
            h = HTMLParser()
            title = h.unescape(h.unescape(product_json['title']))
            cover = product_json['imageUrl']
            desc = sel.xpath('//section[contains(@class, "product-details-content")]').extract()[0]
            brand = product_json['brandName']
            
            
            '''color handle'''
            color_covers = product_json['colorSwatchMap']
            color_primary_iamges = product_json['images']['colorwayPrimaryImages']
            
            colors = []
            color_items = {}
            color_handle_map = {}
            
            for color_name in color_primary_iamges:
                
                if color_name in color_covers.keys():
                    color_cover = self.image_prefix + color_covers[color_name]
                else:
                    color_cover = self.image_prefix + color_primary_iamges[color_name]
                
                colorItem = Color()
                    
                colorItem['type'] = 'color'
                colorItem['from_site'] = 'macys'
                colorItem['show_product_id'] = show_product_id
                colorItem['name'] = color_name
                colorItem['cover'] = color_cover
                
                images = []
                '''颜色主图片'''
                
                if color_name in product_json['images']['colorwayPrimaryImages'].keys():
                    image = self.image_prefix + product_json['images']['colorwayPrimaryImages'][color_name]
                    images.append({
                        'thumbnail': image,
                        'image': image + '?wid=1000'
                    })
                
                '''颜色附加图片'''
                color_additional_handled = False
                if color_name in product_json['images']['colorwayAdditionalImages'].keys():
                    color_additional_images_str = product_json['images']['colorwayAdditionalImages'][color_name]
                    color_additional_images = color_additional_images_str.split(',')
                    
                    for color_additional_image in color_additional_images:
                    
                        image = self.image_prefix + color_additional_image
                        images.append({
                            'thumbnail': image,
                            'image': image + '?wid=1000'
                        })
                        
                    color_additional_handled = True
                
                '''通用附加图片'''
                additional_handled = False
                if len(product_json['images']['additionalImages']) > 0:
                    additional_handled = True
                    additional_images = product_json['images']['additionalImages']
                    for additional_image in additional_images:
                    
                        image = self.image_prefix + additional_image
                        images.append({
                            'thumbnail': image,
                            'image': image + '?wid=1000'
                        })
                colorItem['images'] = images
                
                color_items[color_name] = colorItem    
                
                if color_additional_handled == True or additional_handled == True:
                    color_handle_map[color_name] = True
                else:
                    color_handle_map[color_name] = False
                    
                colors.append(color_name)
    
            for color_name in color_handle_map:
                if color_handle_map[color_name] == False:
                    selected_color_name = product_json['selectedColor']
                    
                    if selected_color_name in product_json['images']['colorwayAdditionalImages'].keys():
                        color_additional_images_str = product_json['images']['colorwayAdditionalImages'][selected_color_name]
                        color_additional_images = color_additional_images_str.split(',')
                        
                        for color_additional_image in color_additional_images:
                        
                            image = self.image_prefix + color_additional_image
                            color_items[color_name]['images'].append({
                                'thumbnail': image,
                                'image': image + '?wid=1000'
                            })
                            
            for color_item_name in color_items:
                yield color_items[color_item_name]
            
            '''color handle end'''
                
            '''handle item info begin'''
            item['title'] = title
            item['brand'] = brand
            item['cover'] = cover
            item['desc'] = desc
            item['colors'] = colors
            item['show_product_id'] = show_product_id
            
            sizes = {'size' : product_json['sizesList']}
            item['sizes'] = sizes
            if item['sizes']['size'] == []:
                item['sizes'] = ['One Size']
            item['dimensions'] = ['size']
            
            upc_list = product_json['upcMap'][show_product_id]
            
            color_price_map = {}
            for price in product_json['colorwayPricingSwatches']:
                price_map = product_json['colorwayPricingSwatches'][price]
                
                for color_name in price_map:
                    
                    color_price = price_map[color_name]
                    if color_price['onSale'] == False:
                        current_price = color_price['tieredPrice'][0]['value'][0]
                        list_price = current_price
                    else:
                        color_price_len = len(color_price['tieredPrice'])
                        current_price = color_price['tieredPrice'][color_price_len - 1]['value'][0]
                        list_price = color_price['tieredPrice'][0]['value'][0]
                    
                    color_price_map[color_name] = {'current_price': current_price, 'list_price': list_price}
            
            skuCollectionsList = []
            for sku_stock in upc_list:
                skuItem = SkuItem()
                skuItem['type'] = 'sku'
                skuItem['from_site'] = 'macys'
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['id'] = sku_stock['upcID']
                
                if len(color_price_map) == 0 or sku_stock['color'] not in color_price_map.keys():
                    skuItem["list_price"] = product_json['regularPrice']
                    skuItem['current_price'] = product_json['salePrice']
                    
                    if len(skuItem['current_price']) == 0:
                        skuItem['current_price'] = skuItem["list_price"]
                else:
                    skuItem["list_price"] = color_price_map[sku_stock['color']]['list_price']
                    skuItem['current_price'] = color_price_map[sku_stock['color']]['current_price']
                    
                
                skuItem['color'] = sku_stock['color']
                if not item['colors']:
                    item['colors'] = [skuItem['color']]
                skuItem['size'] = sku_stock['size']
                if not skuItem['size']:
                    skuItem['size'] = 'One Size'
                
                if sku_stock['isAvailable'] == "true":
                    skuItem['is_outof_stock'] = False
                else:
                    skuItem['is_outof_stock'] = True
                
                skuCollectionsList.append(skuItem)
            
            item['skus'] = skuCollectionsList
            if product_json['sizeChartMap'][show_product_id]['sizeChartCanvasId']:
                size_chart_url = self.base_url + '/shop/catalog/product/canvassizechart/json?canvasId=' + product_json['sizeChartMap'][show_product_id]['sizeChartCanvasId']
                yield Request(url=size_chart_url, meta={'item':item}, callback=self.parse_size_chart)
            elif product_json['sizeChartMap'][show_product_id]['sizeChart']:
                item['size_info'] = self.size_chart_pic_url + product_json['sizeChartMap'][show_product_id]['sizeChart']
                yield item
            elif product_json['sizeChartMap'][show_product_id]['intlSizeChart']:
                item['size_info'] = self.size_chart_pic_url + product_json['sizeChartMap'][show_product_id]['intlSizeChart']
                yield item
            else:
                item['size_info'] = ''
                yield item
        else:
            member_url_doms = sel.xpath('//div[contains(@class, "memberProducts")]')
            
            if len(member_url_doms) > 0:
                for member_url_dom in member_url_doms:
                    
                    url = member_url_dom.xpath('./@data-pdp-url').extract()[0]
                    url = self.base_url + url
                    
                    yield Request(url=url, meta={'item':item}, callback=self.parse_item)
    
    def parse_size_chart(self, response):
        
        item = response.meta['item']
        body_str = response.body
        body_str = body_str.decode('cp1252')
        size_chart_json = json.loads(body_str)
        size_chart_brand = size_chart_json['sizeChartMedia']['brandName']
        size_chart_cat = size_chart_json['sizeChartMedia']['categoryName']
        item['size_info'] = ''
        # item['size_info'] = size_chart_brand.strip() + '-' + size_chart_cat.strip()
        size_chart_data = size_chart_json['sizeChartMedia']['sizeChartData']
        us_size_chart_data = size_chart_data[0]['chartSizes']
        final_chart = []
        for us_chart_sizes in us_size_chart_data:
            temp_dict = {}
            if 'key' in us_chart_sizes.keys():
                temp_dict[base64.encodestring('us_str').strip()] = us_chart_sizes['key']
            if 'value' in us_chart_sizes.keys():
                temp_dict[base64.encodestring('us_num').strip()] = us_chart_sizes['value'][0]
            final_chart.append(temp_dict)
        
        for column in size_chart_data[0]['columns']:
            if column['name'] == "CN":
                CN_chart = True
        if 'CN_chart' in dir():
            for index, locale_size in enumerate(size_chart_data[0]['localeSizes']):
                for locale_size_value in locale_size['value']:
                    if locale_size_value['key'] == 'CN':
                        final_chart[index][base64.encodestring('CN').strip()] = locale_size_value['value']
        for index, measure_size in enumerate(size_chart_data[0]['measureSizes']):
            for k, v in measure_size['value'].items():
                if 'cm' in k:
                    final_chart[index][base64.encodestring(k).strip()] = v['CM']
                    CM_flag = True
            if 'CM_flag' not in dir():
                for k, v in measure_size['value'].items():
                    final_chart[index][base64.encodestring(k).strip()] = v[v.keys()[0]]
        macys_size_chart = {}
        macys_size_chart['title'] = size_chart_brand.strip() + '-' + size_chart_cat.strip()
        macys_size_chart['chart'] = final_chart
        item['size_chart'] = macys_size_chart
        yield item    
    
    
    '''具体的解析规则'''
    def parse_item(self, response):
        
#         item = BaseItem()
#         item['type'] = 'base'
#         item['show_product_id'] = '1209118'
        item = response.meta['item']
        
        return self.handle_parse_item(response, item)
      
    def parse_list(self, response):
        
        response_url = response.url
        meta = response.meta
        
        if 'current_page' not in response.meta.keys():
            current_page = 1
        else:
            current_page = response.meta['current_page']
        
        url_dict = urlparse.urlparse(response_url)
        
        if url_dict.path.find('/Pageindex/') > 0:
            url_path = url_dict.path
            new_url_path = re.sub(r'/Pageindex/\d+','/Pageindex/'+str(current_page + 1), url_path)
            next_url = url_dict.scheme + '://' + url_dict.netloc + new_url_path + '?' + url_dict.query
        else:
            next_url = url_dict.scheme + '://' + url_dict.netloc + url_dict.path + '/Pageindex/' + str(current_page + 1) + '?' + url_dict.query
        
        sel = Selector(response)
        
        product_count = int(sel.xpath('//span[@id="productCount"]/text()').extract()[0])
        
        page_count = math.ceil(product_count/60)
        
        lis = sel.xpath('//ul[@id="thumbnails"]/li[@class="productThumbnail borderless"]')
        
        for li in lis:
            url = li.xpath('./div/div[@class="textWrapper"]/div[@class="shortDescription"]/a/@href').extract()[0]
            url = self.base_url + url
            
            item_cover = li.xpath('./div/div[@class="fullColorOverlayOff"]/a/span/img/@src').extract()[0]
            item_title = li.xpath('./div/div[@class="fullColorOverlayOff"]/a/span/img/@title').extract()[0]
            
            h = HTMLParser()
            item_title = h.unescape(item_title)
            try:
                list_price = li.xpath('./div/div[@class="textWrapper"]/div[@class="prices"]//span[contains(@class,"first-range")]/text()').re(r'\$(.+)')[0]
                curr_price_dom = li.xpath('./div/div[@class="textWrapper"]/div[@class="prices"]//span[contains(@class,"priceSale")]/text()').re(r'\$(.+)')
            except IndexError:
                print li.extract() 
            
            if len(curr_price_dom) > 0:
                curr_price = curr_price_dom[0]
            else:
                curr_price = list_price
                
            item = BaseItem()
            item['title'] = item_title
            item['cover'] = item_cover
            item['current_price'] = curr_price
            item['list_price'] = list_price
            item['url'] = url
            item['type'] = 'base'
            item['from_site'] = 'macys'
            item['gender'] = meta['gender']
            item['product_type'] = meta['product_type']
            item['category'] = meta['category']
            
            yield Request(url, meta={'item': item}, callback=self.parse_item)
                
        if current_page < page_count:
            meta['current_page'] = current_page + 1
            
#             print response.url + ':'  + str(meta['current_page'])
            yield Request(next_url, meta=meta, callback=self.parse_list)
        
    '''
    爬虫解析入口函数，用于解析丢入的第一个请求，一般是顶级目录页
    '''
    def parse(self, response):
        
        search_key_url = None
        
        response_url = response.url
        
        if response_url not in self.url_attr_map.keys():
            all_key_urls = self.url_attr_map.keys()
            
            for key_url in all_key_urls:
                
                if response_url.find(key_url):
                    search_key_url = key_url
        else:
            search_key_url = response_url
        
        if search_key_url is None:
            return
        
        attr_map = self.url_attr_map[search_key_url]
                
        meta = {}
        
        meta['product_type'] = attr_map['product_type']
        
        if 'gender' in attr_map.keys():
            meta['gender'] = attr_map['gender']
        
        if 'category' in attr_map.keys():
            meta['category'] = attr_map['category']
        
        sel = Selector(response)
        
        if attr_map['crawl_type'] == 'first':
            
            bold_li_seq = '1'
            
            if 'bold_li_seq' in attr_map.keys():
                bold_li_seq = attr_map['bold_li_seq'] 
            
            lis = sel.xpath('//ul[@id="firstNavSubCat"]/li[@class="nav_cat_item_bold"][' + bold_li_seq + ']/ul/li')
            
            for li in lis:
            
                a_href_dom = li.xpath('./a/@href').extract()
                if len(a_href_dom) == 0:
                    continue
                
                url = a_href_dom[0]
                
                category = li.xpath('./a/text()').extract()[0]
                
                if category == 'Wear to Work':
                    continue
                elif category == 'Shop All Guys':
                    continue
                elif category == 'Activewear':
                    continue
                elif category == "All Juniors' Apparel":
                    continue
                
                meta['category'] = category
                # print url
                yield Request(url, meta=meta, callback=self.parse_list)
        else:
            if'category' not in attr_map.keys():
                category_key = attr_map['category_key']
                
                lis = sel.xpath('//li[@id="'+category_key+'"]/div[@class="listbox"]//li')
                
                for li in lis:
                    category = li.xpath('./a/@data-value').extract()[0]
                    
                    url = li.xpath('./a/@href').extract()[0]
                    
                    url = self.base_url + url
                    
                    meta['category'] = category
                    
                    yield Request(url=url, meta=meta, callback=self.parse_list)
            else:
                yield Request(url=response.url, meta=meta, callback=self.parse_list, dont_filter=True)
                    

# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy import Request
import re
import os
from gorden_crawler.spiders.shiji_base import BaseSpider
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
import copy
import execjs
import json


class Saksoff5thSpider(BaseSpider):
    name = "saksoff5th"
    allowed_domains = ["saksoff5th.com"]

    custom_settings = {
        # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.4,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    base_url = 'http://www.saksoff5th.com/'
    # 正式运行的时候，start_urls为空，通过redis来喂养爬虫

    #     start_urls = [
    #         #women
    #         # 'http://www.saksoff5th.com/womens-apparel?is_refine_request=true&alt=json&format=ajax',
    #         # 'http://www.saksoff5th.com/shoes-handbags-shoes?is_refine_request=true&alt=json&format=ajax',
    #         # 'http://www.saksoff5th.com/womens-handbags?is_refine_request=true&alt=json&format=ajax',
    #         # 'http://www.saksoff5th.com/jewelry-accessories-accessories?is_refine_request=true&alt=json&format=ajax',
    #         # 'http://www.saksoff5th.com/womens-beauty?is_refine_request=true&alt=json&format=ajax',
    #         # #men
    #         # 'http://www.saksoff5th.com/mens-apparel?is_refine_request=true&alt=json&format=ajax',
    #         # 'http://www.saksoff5th.com/mens-shoes?is_refine_request=true&alt=json&format=ajax',
    #         # 'http://www.saksoff5th.com/mens-accessories?is_refine_request=true&alt=json&format=ajax',
    #         # 'http://www.saksoff5th.com/mens-jewelry-watches?is_refine_request=true&alt=json&format=ajax',

    #     ]

    #     url_gender_map = {
    #         #women
    #         'http://www.saksoff5th.com/womens-apparel?is_refine_request=true&alt=json&format=ajax' : {'gender': 'women','product_type': 'clothing', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
    #         'http://www.saksoff5th.com/shoes-handbags-shoes?is_refine_request=true&alt=json&format=ajax' : {'gender': 'women', 'product_type': 'shoes', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
    #         'http://www.saksoff5th.com/shoes-handbags-handbags?is_refine_request=true&alt=json&format=ajax': {'gender': 'women', 'product_type': 'handbags', 'size_info': ''},
    #         'http://www.saksoff5th.com/jewelry-accessories-accessories?is_refine_request=true&alt=json&format=ajax': {'gender': 'women', 'product_type': 'accessories', 'size_info': ''},
    #         'http://www.saksoff5th.com/womens-beauty?is_refine_request=true&alt=json&format=ajax': {'gender': 'women', 'product_type': 'beauty', 'size_info': ''},
    # #         #men
    #         'http://www.saksoff5th.com/mens-apparel?is_refine_request=true&alt=json&format=ajax': {'gender': 'men', 'product_type': 'apparel', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
    #         'http://www.saksoff5th.com/mens-shoes?is_refine_request=true&alt=json&format=ajax': {'gender': 'men', 'product_type': 'shoes', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
    #         'http://www.saksoff5th.com/mens-accessories?is_refine_request=true&alt=json&format=ajax': {'gender': 'men', 'product_type': 'accessories', 'size_info': ''},
    #         'http://www.saksoff5th.com/mens-jewelry-watches?is_refine_request=true&alt=json&format=ajax': {'gender': 'men', 'product_type': 'watches', 'size_info': ''},
    #     }
    # 爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    # def parse(self, response):
    #     # response_url = response.url
    #     # gender = self.url_gender_map[response_url]['gender']
    #     # product_type = self.url_gender_map[response_url]['product_type']
    #     # size_info = self.url_gender_map[response_url]['size_info']
    #     # sel = Selector(response)
    #     # category_ul = sel.xpath('//ul[@class="o5-navigation-list-level-3"]')[0]
    #     # import pdb;pdb.set_trace()
    #     # category_lis = category_ul.xpath('./li[@class="o5-navigation-list-item-level-3"]/a')
    #     # for category_li in category_lis:
    #     #     category_url = category_li.xpath('./@href').extract()[0]+'?slot_size=15&is_refine_request=true&srule=Designer%20A%20-Z&sz=15&start=0&format=ajax'
    #     #     category = category_li.xpath('./text()').extract()[0]
    #     #     yield Request(category_url, callback=self.parse_pages, meta={'product_type': product_type, 'gender': gender, 'category': category, 'size_info':size_info})

    #     # category_url = 'http://www.saksoff5th.com/womens-apparel-dresses'+'?sz=15&start=0&srule=Designer%20A%20-Z'
    #     # category = 'dress'
    #     # yield Request(category_url, callback=self.parse_pages, meta={'product_type': product_type, 'gender': gender, 'category': category, 'size_info':size_info})
    #     response_url = response.url
    #     size_info = self.url_gender_map[response_url]['size_info']
    #     gender = self.url_gender_map[response_url]['gender']
    #     product_type_name = self.url_gender_map[response_url]['product_type']
    #     response_body_true = re.sub(r'true', 'True', response.body)
    #     response_body_false = re.sub(r'false', 'False', response_body_true)
    #     response_body_null = re.sub(r'null', 'None', response_body_false)
    #     response_body_dict = eval(response_body_null)
    #     category_refinements = response_body_dict['categoryRefinements']['values'][0:1]
    #     # import pdb;pdb.set_trace()
    #     for product_type in category_refinements:
    #         # product_type_name = product_type['name']
    #         if product_type.has_key('subCategoryRefinements'):
    #             subcategory_refinements = product_type['subCategoryRefinements']
    #             for category in subcategory_refinements:
    #                 category_name = category['name']
    #                 category_url = category['clickUrl']+'?sz=15&start=0&srule=Designer%20A%20-Z'

    #                 yield Request(category_url, callback=self.parse_pages, meta={'product_type': product_type_name, 'gender': gender, 'category': category_name, 'size_info':size_info})
    #         else:
    #             category_url = product_type['clickUrl']+'?sz=15&start=0&srule=Designer%20A%20-Z'
    #             category_name = product_type_name
    #             yield Request(category_url, callback=self.parse_pages, meta={'product_type': product_type_name, 'gender': gender, 'category': category_name, 'size_info':size_info})

#  start_urls = [
#         #men apparel
#         'http://www.saksoff5th.com/mens-apparel-suits?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-sportcoats?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-dressshirts?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-casual-shirts?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-sweaters-sweatshirts?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-jeans?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-coats-jackets?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-pants-shorts?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-polos-tees?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-swimwear?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-activewear?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-ties?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/mens-apparel-underwear-socks-sleepwear?sz=15&start=0&srule=Designer%20A%20-Z',

#         #men shoes
#         'http://www.saksoff5th.com/mens-shoes?sz=15&start=0&srule=Designer%20A%20-Z',
 
#         #men accessories
#         'http://www.saksoff5th.com/mens-accessories?sz=15&start=0&srule=Designer%20A%20-Z',
 
#         #men wateches
#         'http://www.saksoff5th.com/mens-jewelry-watches?sz=15&start=0&srule=Designer%20A%20-Z',
 
#         #women apparel
#         'http://www.saksoff5th.com/womens-apparel-dresses?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/womens-apparel-top?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/womens-apparel-sweaters?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/womens-apparel-blazers-vest?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/womens-apparel-jeans?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/womens-apparel-coats-jackets?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/womens-apparel-pants-shorts?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/womens-apparel-skirts?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/womens-apparel-swimwear-coverups?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/womens_apparel_activewear?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/womens-apparel-lingerie-and-sleepwear?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/womens-sizes14w-24w?sz=15&start=0&srule=Designer%20A%20-Z',
 
#         #women shoes
#         'http://www.saksoff5th.com/shoes-handbags-shoes-boots?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-shoes-pumps?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-shoes-flats?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-shoes-evening?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-shoes-wedges?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-shoes-sneakers?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-shoes-sandals?sz=15&start=0&srule=Designer%20A%20-Z',
 
#         #women handbags
#         'http://www.saksoff5th.com/shoes-handbags-handbags-crossbody-bags?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-handbags-totes?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-handbags-shoulder-bags?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-handbags-top-handles-satchels?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-handbags-evening?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-handbags-hobo-bags?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-handbags-clutches?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-handbags-backpacks?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-handbags-bucket-bags?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/shoes-handbags-handbags-wallets-cases?sz=15&start=0&srule=Designer%20A%20-Z',
 
#         #women jewelry
#         'http://www.saksoff5th.com/jewelry-accessories-fine-fashion-jewelry-bracelets?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-fine-fashion-jewelry-earrings?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-fine-fashion-jewelry-necklaces?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-fine-fashion-jewelry-rings?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-fine-fashion-jewelry-brooches?sz=15&start=0&srule=Designer%20A%20-Z',
 
#         #women trend jewelry
#         'http://www.saksoff5th.com/jewelry-accessories-trend-jewelry-bracelets?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-trend-jewelry-earrings?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-trend-jewelry-necklaces?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-trend-jewelry-rings?sz=15&start=0&srule=Designer%20A%20-Z',
 
#         #women watches
#         'http://www.saksoff5th.com/jewelry-accessories-watches-women?sz=15&start=0&srule=Designer%20A%20-Z',
         
#         #women accessories
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-sunglasses?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-scarves?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-belts?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-wallets-cases?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-hats?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-gloves?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-tech-mobile?sz=15&start=0&srule=Designer%20A%20-Z',
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-hair-accessories?sz=15&start=0&srule=Designer%20A%20-Z',
# #         'http://www.saksoff5th.com/jewelry-accessories-accessories-umbrellas?sz=15&start=0&srule=Designer%20A%20-Z',
 
#         #women beauty
#         'http://www.saksoff5th.com/womens-beauty?sz=15&start=0&srule=Designer%20A%20-Z',
#     ]

#     start_urls_map = {
#         #men apparel
#         'http://www.saksoff5th.com/Men/Apparel/Suits/shop/_/N-4ztf33/Ne-6ja3nn?FOLDER%3C%3Efolder_id=2534374302023839': {'product_type': 'apparel', 'category': 'Suits', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/Men/Apparel/Sportcoats/shop/_/N-4ztf4p/Ne-6ja3nn?FOLDER%3C%3Efolder_id=2534374302023897': {'product_type': 'apparel', 'category': 'Sportcoats', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/Men/Apparel/Dress-Shirts/shop/_/N-4ztf4o/Ne-6ja3nn?FOLDER%3C%3Efolder_id=2534374302023896': {'product_type': 'apparel', 'category': 'Dress Shirts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/Men/Apparel/Casual-Shirts/shop/_/N-4ztf4h/Ne-6ja3nn?FOLDER%3C%3Efolder_id=2534374302023889': {'product_type': 'apparel', 'category': 'Casual Shirts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/Men/Apparel/Polos-and-Tees/shop/_/N-4ztf2h/Ne-6ja3nn?FOLDER%3C%3Efolder_id=2534374302023817': {'product_type': 'apparel', 'category': 'Sweaters &amp; Sweatshirts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/mens-apparel-jeans?sz=15&start=0&srule=Designer%20A%20-Z': {'product_type': 'apparel', 'category': 'Jeans', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/mens-apparel-coats-jackets?sz=15&start=0&srule=Designer%20A%20-Z': {'product_type': 'apparel', 'category': 'Coats &amp; Jackets', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/mens-apparel-pants-shorts?sz=15&start=0&srule=Designer%20A%20-Z': {'product_type': 'apparel', 'category': 'Pants &amp; Shorts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/mens-apparel-polos-tees?sz=15&start=0&srule=Designer%20A%20-Z': {'product_type': 'apparel', 'category': 'Polos &amp; Tees', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/mens-apparel-swimwear?sz=15&start=0&srule=Designer%20A%20-Z': {'product_type': 'apparel', 'category': 'Swimwear', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/mens-apparel-activewear?sz=15&start=0&srule=Designer%20A%20-Z': {'product_type': 'apparel', 'category': 'Activewear', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/mens-apparel-ties?sz=15&start=0&srule=Designer%20A%20-Z': {'product_type': 'apparel', 'category': 'Ties', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         'http://www.saksoff5th.com/mens-apparel-underwear-socks-sleepwear?sz=15&start=0&srule=Designer%20A%20-Z': {'product_type': 'apparel', 'category': 'Underwear, Socks &amp; Sleepwear', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},

#         # 'http://www.saksoff5th.com/mens-apparel-suits?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Suits', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-sportcoats?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Sportcoats', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-dressshirts?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Dress Shirts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-casual-shirts?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Casual Shirts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-sweaters-sweatshirts?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Sweaters &amp; Sweatshirts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-jeans?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Jeans', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-coats-jackets?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Coats &amp; Jackets', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-pants-shorts?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Pants &amp; Shorts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-polos-tees?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Polos &amp; Tees', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-swimwear?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Swimwear', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-activewear?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Activewear', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-ties?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Ties', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},
#         # 'http://www.saksoff5th.com/mens-apparel-underwear-socks-sleepwear?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Underwear, Socks &amp; Sleepwear', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-apparel/size-guide-mens-apparel.html'},

#         #men shoes
#         'http://www.saksoff5th.com/mens-shoes?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'shoes', 'category': 'shoes', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/size-guide-mens-shoes/size-guide-mens-shoes.html'},

#         #men accessories
#         'http://www.saksoff5th.com/mens-accessories?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'accessories', 'category': 'accessories', 'gender': 'men', 'size_info': ''},

#         #men watches
#         'http://www.saksoff5th.com/mens-jewelry-watches?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'watches', 'category': 'watches', 'gender': 'men', 'size_info': ''},

#         #women apparel
#         'http://www.saksoff5th.com/womens-apparel-dresses?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'dresses', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},
#         'http://www.saksoff5th.com/womens-apparel-top?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'top', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},
#         'http://www.saksoff5th.com/womens-apparel-sweaters?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Sweaters', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},
#         'http://www.saksoff5th.com/womens-apparel-blazers-vest?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Jackets &amp; Vests', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},
#         'http://www.saksoff5th.com/womens-apparel-jeans?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Jeans', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},
#         'http://www.saksoff5th.com/womens-apparel-coats-jackets?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Coats', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},
#         'http://www.saksoff5th.com/womens-apparel-pants-shorts?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Pants, Shorts &amp; Jumpsuits', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},
#         'http://www.saksoff5th.com/womens-apparel-skirts?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Skirts', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},
#         'http://www.saksoff5th.com/womens-apparel-swimwear-coverups?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Swimwear &amp; Coverups', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},
#         'http://www.saksoff5th.com/womens_apparel_activewear?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Activewear', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},
#         'http://www.saksoff5th.com/womens-apparel-lingerie-and-sleepwear?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Lingerie &amp; Sleepwear', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},
#         'http://www.saksoff5th.com/womens-sizes14w-24w?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'Sizes 14W-24W', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-apparel/size-guide-womens-apparel.html?format=ajax'},

#         #women shoes
#         'http://www.saksoff5th.com/shoes-handbags-shoes-boots?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'shoes', 'category': 'boots', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-shoes/size-guide-womens-shoes.html'},
#         'http://www.saksoff5th.com/shoes-handbags-shoes-pumps?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'shoes', 'category': 'pumps', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-shoes/size-guide-womens-shoes.html'},
#         'http://www.saksoff5th.com/shoes-handbags-shoes-flats?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'shoes', 'category': 'flats', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-shoes/size-guide-womens-shoes.html'},
#         'http://www.saksoff5th.com/shoes-handbags-shoes-evening?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'shoes', 'category': 'evening', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-shoes/size-guide-womens-shoes.html'},
#         'http://www.saksoff5th.com/shoes-handbags-shoes-wedges?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'shoes', 'category': 'wedges', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-shoes/size-guide-womens-shoes.html'},
#         'http://www.saksoff5th.com/shoes-handbags-shoes-sneakers?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'shoes', 'category': 'sneakers', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-shoes/size-guide-womens-shoes.html'},
#         'http://www.saksoff5th.com/shoes-handbags-shoes-sandals?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'shoes', 'category': 'sandals', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/size-guide-womens-shoes/size-guide-womens-shoes.html'},

#         #women handbags
#         'http://www.saksoff5th.com/shoes-handbags-handbags-crossbody-bags?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'handbags', 'category': 'Crossbody Bags', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/shoes-handbags-handbags-totes?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'handbags', 'category': 'Totes', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/shoes-handbags-handbags-shoulder-bags?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'handbags', 'category': 'Shoulder Bags', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/shoes-handbags-handbags-top-handles-satchels?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'handbags', 'category': 'Top Handles &amp; Satchels', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/shoes-handbags-handbags-evening?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'handbags', 'category': 'Evening', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/shoes-handbags-handbags-hobo-bags?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'handbags', 'category': 'Hobo Bags', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/shoes-handbags-handbags-clutches?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'handbags', 'category': 'Clutches', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/shoes-handbags-handbags-backpacks?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'handbags', 'category': 'Backpacks', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/shoes-handbags-handbags-bucket-bags?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'handbags', 'category': 'Bucket Bags', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/shoes-handbags-handbags-wallets-cases?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'handbags', 'category': 'Wallets &amp; Cases', 'gender': 'women', 'size_info': ''},

#         #women jewelry
#         'http://www.saksoff5th.com/jewelry-accessories-fine-fashion-jewelry-bracelets?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'jewelery', 'category': 'Bracelets', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-fine-fashion-jewelry-earrings?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'jewelery', 'category': 'Earrings', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-fine-fashion-jewelry-necklaces?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'jewelery', 'category': 'Necklaces', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-fine-fashion-jewelry-rings?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'jewelery', 'category': 'Rings', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-fine-fashion-jewelry-brooches?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'jewelery', 'category': 'Brooches', 'gender': 'women', 'size_info': ''},

#         #women trend jewelry
#         'http://www.saksoff5th.com/jewelry-accessories-trend-jewelry-bracelets?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'jewelery', 'category': 'Bracelets', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-trend-jewelry-earrings?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'jewelery', 'category': 'Earrings', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-trend-jewelry-necklaces?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'jewelery', 'category': 'Necklaces', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-trend-jewelry-rings?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'jewelery', 'category': 'Rings', 'gender': 'women', 'size_info': ''},

#         #women watches
#         'http://www.saksoff5th.com/jewelry-accessories-watches-women?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'watches', 'category': 'watches', 'gender': 'women', 'size_info': ''},

#         #women accessries
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-sunglasses?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'accessries', 'category': 'sunglasses', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-scarves?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'accessries', 'category': 'scarves', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-belts?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'accessries', 'category': 'belts', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-wallets-cases?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'accessries', 'category': 'Wallets &amp; Cases', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-hats?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'accessries', 'category': 'hats', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-gloves?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'accessries', 'category': 'gloves', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-tech-mobile?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'accessries', 'category': 'Tech &amp; Mobile', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-hair-accessories?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'accessries', 'category': 'Hair Accessories', 'gender': 'women', 'size_info': ''},
#         'http://www.saksoff5th.com/jewelry-accessories-accessories-umbrellas?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'accessries', 'category': 'Umbrellas', 'gender': 'women', 'size_info': ''},


#         'http://www.saksoff5th.com/womens-beauty?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'beauty', 'category': 'beauty', 'gender': 'women', 'size_info': ''},
#     }


    start_urls = [
        #men apparel
        'http://www.saksoff5th.com/Men/Apparel/Suits/shop/_/N-4ztf33?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Sportcoats/shop/_/N-4ztf4p?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Dress-Shirts/shop/_/N-4ztf4o?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Casual-Shirts/shop/_/N-4ztf4h?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Sweaters-and-Sweatshirts/shop/_/N-4ztf20?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Jeans/shop/_/N-4ztf3r?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Coats-and-Jackets/shop/_/N-4ztf2l?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Pants-and-Shorts/shop/_/N-4ztf1z?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Polos-and-Tees/shop/_/N-4ztf2h?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Swimwear/shop/_/N-4ztf2v?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Activewear/shop/_/N-4ztf15?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Ties/shop/_/N-4ztf25?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Men/Apparel/Underwear-Socks-and-Sleepwear/shop/_/N-4zteyz?sz=15&start=0&srule=Designer%2520A%2520-Z',
        # men shoes
        'http://www.saksoff5th.com/Men/Shoes/shop/_/N-4ztf0n?sz=15&start=0&srule=Designer%2520A%2520-Z',
        
        #men accessories
        'http://www.saksoff5th.com/Men/Accessories/shop/_/N-4ztf4i?sz=15&start=0&srule=Designer%2520A%2520-Z',
        
        #men wateches
        'http://www.saksoff5th.com/Men/Jewelry-and-Watches/shop/_/N-4ztezx?sz=15&start=0&srule=Designer%2520A%2520-Z',
        
        #women apparel
        'http://www.saksoff5th.com/Women/Apparel/Dresses/shop/_/N-4ztf0a?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Women/Apparel/Tops/shop/_/N-4zteyt/Ne-6ja3nn?sz=15&start=0&srule=Designer%20A%20-Z',
        'http://www.saksoff5th.com/Women/Apparel/Sweaters/shop/_/N-4ztf3j?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Women/Apparel/Jackets-and-Vests/shop/_/N-4ztf3k?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Women/Apparel/Jeans/shop/_/N-4ztf4e?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Women/Apparel/Coats/shop/_/N-4ztf2e?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Women/Apparel/Pants-and-Jumpsuits/shop/_/N-4ztf7q?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Women/Apparel/Skirts/shop/_/N-4ztf0b?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Women/Apparel/Swimwear-and-Coverups/shop/_/N-4ztf2i?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Women/Apparel/Activewear/shop/_/N-4ztf0m?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Women/Apparel/Lingerie-and-Sleepwear/shop/_/N-4ztf2m?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Women/Apparel/Sizes-14W-24W/shop/_/N-4ztf05?sz=15&start=0&srule=Designer%2520A%2520-Z',
        
        #women shoes
        'http://www.saksoff5th.com/ShoesBags/Shoes/Boots/shop/_/N-4ztf0e?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Shoes/Pumps/shop/_/N-4ztf3n?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Shoes/Flats/shop/_/N-4ztf31?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Shoes/Evening/shop/_/N-4ztf1a?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Shoes/Wedges/shop/_/N-4ztf0s?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Shoes/Sneakers/shop/_/N-4ztf14?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Shoes/Sandals/shop/_/N-4ztf4c?sz=15&start=0&srule=Designer%2520A%2520-Z',
        
        #women handbags
        'http://www.saksoff5th.com/ShoesBags/Handbags/Crossbody-Bags/shop/_/N-4ztf3q?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Handbags/Totes/shop/_/N-4ztf2k?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Handbags/Shoulder-Bags/shop/_/N-4ztf1x?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Handbags/Top-Handles-and-Satchels/shop/_/N-4ztf1y?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Handbags/Evening/shop/_/N-4ztf1w?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Handbags/Hobo-Bags/shop/_/N-4ztf42?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Handbags/Clutches/shop/_/N-4ztf4f?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Handbags/Backpacks/shop/_/N-4ztf2j?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Handbags/Bucket-Bags/shop/_/N-4ztf4r?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/ShoesBags/Handbags/Wallets-and-Cases/shop/_/N-4ztf4g?sz=15&start=0&srule=Designer%2520A%2520-Z',
        
        #women jewelry
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Fine-Fashion-Jewelry/Bracelets/shop/_/N-4ztf2f?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Fine-Fashion-Jewelry/Earrings/shop/_/N-4ztf0g?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Fine-Fashion-Jewelry/Necklaces/shop/_/N-4ztf4d?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Fine-Fashion-Jewelry/Rings/shop/_/N-4zteyw?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Fine-Fashion-Jewelry/shop/_/N-4zteyv?sz=15&start=0&srule=Designer%2520A%2520-Z',
        
        #women trend jewelry
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Trend-Jewelry/Bracelets/shop/_/N-4ztf37?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Trend-Jewelry/Earrings/shop/_/N-4ztf0t?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Trend-Jewelry/Necklaces/shop/_/N-4ztezo?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Trend-Jewelry/Rings/shop/_/N-4ztf26?sz=15&start=0&srule=Designer%2520A%2520-Z',
        
        #women watches
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Watches/Women-s/shop/_/N-4ztezi?sz=15&start=0&srule=Designer%2520A%2520-Z',
        
        #women accessories
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Sunglasses/shop/_/N-4ztf0j?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Scarves/shop/_/N-4ztf36?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Belts/shop/_/N-4ztf2q?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Wallets-and-Cases/shop/_/N-4ztf34?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Hats/shop/_/N-4ztf3x?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Gloves/shop/_/N-4ztf3y?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Tech-and-Mobile/shop/_/N-4ztf41?sz=15&start=0&srule=Designer%2520A%2520-Z',
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Hair-Accessories/shop/_/N-4ztf48?sz=15&start=0&srule=Designer%2520A%2520-Z',
        #         'http://www.saksoff5th.com/jewelry-accessories-accessories-umbrellas?sz=15&start=0&srule=Designer%20A%20-Z',

        #women beauty
        'http://www.saksoff5th.com/Women/Beauty/shop/_/N-4ztf46?sz=15&start=0&srule=Designer%2520A%2520-Z',
    ]

    start_urls_map = {
        #men apparel
        'http://www.saksoff5th.com/Men/Apparel/Suits/shop/_/N-4ztf33?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Suits', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Sportcoats/shop/_/N-4ztf4p?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Sportcoats', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Dress-Shirts/shop/_/N-4ztf4o?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Dress Shirts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Casual-Shirts/shop/_/N-4ztf4h?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Casual Shirts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Sweaters-and-Sweatshirts/shop/_/N-4ztf20?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Sweaters &amp; Sweatshirts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Jeans/shop/_/N-4ztf3r?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Jeans', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Coats-and-Jackets/shop/_/N-4ztf2l?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Coats &amp; Jackets', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Pants-and-Shorts/shop/_/N-4ztf1z?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Pants &amp; Shorts', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Polos-and-Tees/shop/_/N-4ztf2h?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Polos &amp; Tees', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Swimwear/shop/_/N-4ztf2v?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Swimwear', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Activewear/shop/_/N-4ztf15?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Activewear', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Ties/shop/_/N-4ztf25?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Ties', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},
        'http://www.saksoff5th.com/Men/Apparel/Underwear-Socks-and-Sleepwear/shop/_/N-4zteyz?sz=15&start=0&srule=Designer%2520A%2520-Z': {'product_type': 'apparel', 'category': 'Underwear, Socks &amp; Sleepwear', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},

        #men shoes
        'http://www.saksoff5th.com/Men/Shoes/shop/_/N-4ztf0n?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'shoes', 'category': 'shoes', 'gender': 'men', 'size_info': 'http://www.saksoff5th.com/html/popups/m_sizechart.jsp'},

        #men accessories
        'http://www.saksoff5th.com/Men/Accessories/shop/_/N-4ztf4i?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'accessories', 'category': 'accessories', 'gender': 'men', 'size_info': ''},

        #men watches
        'http://www.saksoff5th.com/Men/Jewelry-and-Watches/shop/_/N-4ztezx?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'watches', 'category': 'watches', 'gender': 'men', 'size_info': ''},

        #women apparel
        'http://www.saksoff5th.com/Women/Apparel/Dresses/shop/_/N-4ztf0a?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'apparel', 'category': 'dresses', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/Women/Apparel/Tops/shop/_/N-4zteyt/Ne-6ja3nn?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'apparel', 'category': 'top', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/Women/Apparel/Sweaters/shop/_/N-4ztf3j?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'apparel', 'category': 'Sweaters', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/Women/Apparel/Jackets-and-Vests/shop/_/N-4ztf3k?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'apparel', 'category': 'Jackets &amp; Vests', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/Women/Apparel/Jeans/shop/_/N-4ztf4e?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'apparel', 'category': 'Jeans', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/Women/Apparel/Coats/shop/_/N-4ztf2e?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'apparel', 'category': 'Coats', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/Women/Apparel/Pants-and-Jumpsuits/shop/_/N-4ztf7q?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'apparel', 'category': 'Pants, Shorts &amp; Jumpsuits', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/Women/Apparel/Skirts/shop/_/N-4ztf0b?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'apparel', 'category': 'Skirts', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/Women/Apparel/Swimwear-and-Coverups/shop/_/N-4ztf2i?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'apparel', 'category': 'Swimwear &amp; Coverups', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/Women/Apparel/Activewear/shop/_/N-4ztf0m?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'apparel', 'category': 'Activewear', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/Women/Apparel/Lingerie-and-Sleepwear/shop/_/N-4ztf2m?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'apparel', 'category': 'Lingerie &amp; Sleepwear', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/Women/Apparel/Sizes-14W-24W/shop/_/N-4ztf05?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'apparel', 'category': 'Sizes 14W-24W', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},

        #women shoes
        'http://www.saksoff5th.com/ShoesBags/Shoes/Boots/shop/_/N-4ztf0e?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'shoes', 'category': 'boots', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/ShoesBags/Shoes/Pumps/shop/_/N-4ztf3n?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'shoes', 'category': 'pumps', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/ShoesBags/Shoes/Flats/shop/_/N-4ztf31?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'shoes', 'category': 'flats', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/ShoesBags/Shoes/Evening/shop/_/N-4ztf1a?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'shoes', 'category': 'evening', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/ShoesBags/Shoes/Wedges/shop/_/N-4ztf0s?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'shoes', 'category': 'wedges', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/ShoesBags/Shoes/Sneakers/shop/_/N-4ztf14?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'shoes', 'category': 'sneakers', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},
        'http://www.saksoff5th.com/ShoesBags/Shoes/Sandals/shop/_/N-4ztf4c?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'shoes', 'category': 'sandals', 'gender': 'women', 'size_info': 'http://www.saksoff5th.com/html/popups/w_sizechart.jsp'},

        #women handbags
        'http://www.saksoff5th.com/ShoesBags/Handbags/Crossbody-Bags/shop/_/N-4ztf3q?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'handbags', 'category': 'Crossbody Bags', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/ShoesBags/Handbags/Totes/shop/_/N-4ztf2k?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'handbags', 'category': 'Totes', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/ShoesBags/Handbags/Shoulder-Bags/shop/_/N-4ztf1x?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'handbags', 'category': 'Shoulder Bags', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/ShoesBags/Handbags/Top-Handles-and-Satchels/shop/_/N-4ztf1y?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'handbags', 'category': 'Top Handles &amp; Satchels', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/ShoesBags/Handbags/Evening/shop/_/N-4ztf1w?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'handbags', 'category': 'Evening', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/ShoesBags/Handbags/Hobo-Bags/shop/_/N-4ztf42?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'handbags', 'category': 'Hobo Bags', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/ShoesBags/Handbags/Clutches/shop/_/N-4ztf4f?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'handbags', 'category': 'Clutches', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/ShoesBags/Handbags/Backpacks/shop/_/N-4ztf2j?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'handbags', 'category': 'Backpacks', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/ShoesBags/Handbags/Bucket-Bags/shop/_/N-4ztf4r?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'handbags', 'category': 'Bucket Bags', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/ShoesBags/Handbags/Wallets-and-Cases/shop/_/N-4ztf4g?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'handbags', 'category': 'Wallets &amp; Cases', 'gender': 'women', 'size_info': ''},

        #women jewelry
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Fine-Fashion-Jewelry/Bracelets/shop/_/N-4ztf2f?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'jewelery', 'category': 'Bracelets', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Fine-Fashion-Jewelry/Earrings/shop/_/N-4ztf0g?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'jewelery', 'category': 'Earrings', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Fine-Fashion-Jewelry/Necklaces/shop/_/N-4ztf4d?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'jewelery', 'category': 'Necklaces', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Fine-Fashion-Jewelry/Rings/shop/_/N-4zteyw?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'jewelery', 'category': 'Rings', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Fine-Fashion-Jewelry/shop/_/N-4zteyv?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'jewelery', 'category': 'Brooches', 'gender': 'women', 'size_info': ''},

        #women trend jewelry
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Trend-Jewelry/Bracelets/shop/_/N-4ztf37?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'jewelery', 'category': 'Bracelets', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Trend-Jewelry/Earrings/shop/_/N-4ztf0t?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'jewelery', 'category': 'Earrings', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Trend-Jewelry/Necklaces/shop/_/N-4ztezo?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'jewelery', 'category': 'Necklaces', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Trend-Jewelry/Rings/shop/_/N-4ztf26?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'jewelery', 'category': 'Rings', 'gender': 'women', 'size_info': ''},

        #women watches
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Watches/Women-s/shop/_/N-4ztezi?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'watches', 'category': 'watches', 'gender': 'women', 'size_info': ''},

        #women accessries
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Sunglasses/shop/_/N-4ztf0j?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'accessries', 'category': 'sunglasses', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Scarves/shop/_/N-4ztf36?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'accessries', 'category': 'scarves', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Belts/shop/_/N-4ztf2q?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'accessries', 'category': 'belts', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Wallets-and-Cases/shop/_/N-4ztf34?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'accessries', 'category': 'Wallets &amp; Cases', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Hats/shop/_/N-4ztf3x?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'accessries', 'category': 'hats', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Gloves/shop/_/N-4ztf3y?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'accessries', 'category': 'gloves', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Tech-and-Mobile/shop/_/N-4ztf41?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'accessries', 'category': 'Tech &amp; Mobile', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/Jewelry-and-Accessories/Accessories/Hair-Accessories/shop/_/N-4ztf48?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'accessries', 'category': 'Hair Accessories', 'gender': 'women', 'size_info': ''},
        'http://www.saksoff5th.com/jewelry-accessories-accessories-umbrellas?sz=15&start=0&srule=Designer%20A%20-Z' : {'product_type': 'accessries', 'category': 'Umbrellas', 'gender': 'women', 'size_info': ''},


        'http://www.saksoff5th.com/Women/Beauty/shop/_/N-4ztf46?sz=15&start=0&srule=Designer%2520A%2520-Z' : {'product_type': 'beauty', 'category': 'beauty', 'gender': 'women', 'size_info': ''},
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        response_url = response.url
        sel = Selector(response)
        # product_type = response.meta['product_type']
        # category = response.meta['category']
        # gender = response.meta['gender']
        # size_info = response.meta['size_info']
        if re.search(r'Nao', response_url):
            Nao = response.meta['Nao']
            Nao += 60
            product_type = response.meta['product_type']
            category = response.meta['category']
            gender = response.meta['gender']
            size_info = response.meta['size_info']

        else:
            Nao = 0
            product_type = self.start_urls_map[response_url]['product_type']
            category = self.start_urls_map[response_url]['category']
            gender = self.start_urls_map[response_url]['gender']
            size_info = self.start_urls_map[response_url]['size_info']


        # m = re.search(r'product_array:[^}]+', response.body).group(0)

        # item_ids_list = eval(str(re.search(r'\[.*\]', m).group(0)))
        # for id in item_ids_list:
        #     url = self.base_url+str(id)+'.html'
        #     baseItem = BaseItem()
        #     baseItem['url'] = url
        #     baseItem['show_product_id'] = id
        #     baseItem['product_type'] = product_type
        #     baseItem['category'] = category
        #     baseItem['gender'] = gender
        #     baseItem['size_info'] = size_info
        #     yield Request(baseItem['url'], callback= self.parse_item, meta={"baseItem": baseItem})
        product_lis = sel.xpath('//div[@id="product-container"]/div[@class="pa-product-large-third  "] | //div[@id="product-container"]/div[@class="pa-product-large sfa-pa-product-with-swatches"]')
        for product_li in product_lis:
            url = product_li.xpath('./div[@class="product-text"]/a/@href').extract()[0]
            baseItem = BaseItem()
            baseItem['url'] = url
            baseItem['show_product_id'] = product_li.xpath('.//p/@productcode').extract()[0]
            baseItem['product_type'] = product_type
            baseItem['category'] = category
            baseItem['gender'] = gender
            baseItem['size_info'] = size_info
            yield Request(baseItem['url'], callback= self.parse_item, meta={"baseItem": baseItem})


        # max_page_num = sel.xpath('//div[@id="js-paging-top"]/ul/li')[-1].xpath('./ul/li/a')[-2:-1][0].xpath('./text()').extract()[0]
        # total_item_count_str = sel.xpath('//ul[@class="o5-list-horizontal o5-list-horizontal-bordered o5-pull-right"]/li')[0].xpath('./text()').extract()[0]
        total_item_count_str = sel.xpath('//span[@class="mainBoldBlackText totalRecords"]/text()').extract()[0]

        m = re.findall(r'\d+', total_item_count_str)
        total_item_count = ''.join(m)

        # if start < total_item_count:
        #     url = response_url+'?sz=15&start='+str(start*60)+'&srule=Designer%20A%20-Z'
        #     page_url = re.sub(r'start=\d+', ('start=' + str(start)), response_url)
        if Nao + 60 < int(total_item_count):
            if 'Nao' in response.url:
                page_url = re.sub(r'Nao=[\d]+', ('Nao=' + str(Nao+60)), response_url)
            else:
                page_url = re.sub(r'\?', ('?Nao=' + str(Nao+60) + '&'), response_url)
            yield Request(page_url, callback=self.parse, meta={'product_type': product_type, 'gender': gender, 'category': category, 'size_info':size_info, 'Nao': Nao})

    def parse_item(self, response):
        baseItem=response.meta['baseItem']
        return self.handle_parse_item(response, baseItem)

    def handle_parse_item(self, response, baseItem):
        sel = Selector(response)

        soldout = sel.xpath('//p[@class="product__sold-out-message"]').extract()
        err_message = sel.xpath('//div[@class="container error_message parsys"]').extract()
        complimentary_product = sel.xpath('//p[@class="product-gift-with-purchase"]')
        if len(soldout) > 0:
            return
        elif len(err_message) > 0:
            return
        elif len(complimentary_product) > 0:
            return
        # if len(sel.xpath('//header[@class="product-overview"]/h4[@class="product-overview__product-code"]/text()').extract()) > 0:
        #     show_product_id = sel.xpath('//header[@class="product-overview"]/h4[@class="product-overview__product-code"]/text()').extract()[0]
        # else:
        #     show_product_id = sel.xpath('//div[@class="fp-root"]/@data-product-id').extract()[0]

        # baseItem['show_product_id'] = show_product_id
        baseItem['type'] = 'base'
        baseItem['from_site'] = self.name
        baseItem['dimensions'] = ['size', 'color']

        brand = sel.xpath('//a[@class="product-overview__brand-link"]/text()').extract()
        if len(brand) > 0:
            baseItem['brand'] = brand[0]
        else:
            baseItem['brand'] = 'saksoff5th'

        title = sel.xpath('//h1[@class="product-overview__short-description"]/text()')
        if len(title)>0:
            baseItem['title'] = title.extract()[0]
        else:
            baseItem['title'] = self.name
        desc = sel.xpath('//section[@class="product-description"]/div/ul')
        if len(desc) == 0:
            baseItem['desc'] = baseItem['title']
        else:
            baseItem['desc'] = desc.extract()[0]

        # sizes and color_names both are list
        sizes = sel.xpath('//li[@class="product-variant-attribute-value product-variant-attribute-value--text"]/span/text()').extract()
        if ''.join(sizes) == 'NO SIZE' or sizes == []:
            sizes = sel.xpath('//select[@class="drop-down-list__select drop-down-list__select--default"]/option[position()>1]/text()').extract()
            if len(sizes) > 0:
                ss = copy.deepcopy(sizes)
                for s in ss:
                    if 'Sold Out' in s:
                        sizes.remove(s)
                if not sizes:
                    return
            else:
                sizes = ['one-size']
        color_names = sel.xpath('//li[@class="product-variant-attribute-value product-variant-attribute-value--swatch"]/span/text()').extract()
        if len(color_names) == 0:
            color_names = sel.xpath('//dd[@class="product-variant-attribute-label__selected-value"]/text()').extract()
            if len(color_names) == 0:
                color_names = ['one-color']

        baseItem['sizes'] = sizes
        baseItem['colors'] = color_names
        image_tail = '?op_usm=1.5,1,10,0&resmode=sharp&wid=1000&hei=1000&locale=en'
        thumbnail_tail = '?op_usm=1.5,1,10,0&resmode=sharp&wid=50&hei=50&locale=en'

        list_price = sel.xpath('//dl[@class="product-pricing__container product-pricing__container--previous"]/dd/span[3]/text()')
        current_price = sel.xpath('//dl[@class="product-pricing__container"]/dd/span[@itemprop="price"]/text()').extract()[0].strip()
        baseItem['current_price'] = current_price
        if len(list_price) == 0:
            baseItem['list_price'] = baseItem['current_price']
        else:
            baseItem['list_price'] = list_price.extract()[0].strip()

        goods_jsons = re.search('<script[\s]*type=\"application/json\">[\s]*(\{\"ProductDetails.+?)[\s]*</script>[\s]*</div>', response.body)
        if goods_jsons:
            goods_jsons = goods_jsons.group(1).decode('latin-1')
            context = execjs.compile('''
                var skus = %s;
                function getDetails(){
                    return skus;
                }
            ''' % goods_jsons)
            goods_details = context.call('getDetails')
        items_details = goods_details['ProductDetails']['main_products'][0]

        if len(sel.xpath('//header[@class="product-overview"]/h4[@class="product-overview__product-code"]/text()').extract()) > 0:
            show_product_id = sel.xpath('//header[@class="product-overview"]/h4[@class="product-overview__product-code"]/text()').extract()[0]
        elif len(sel.xpath('//div[@class="fp-root"]/@data-product-id')) > 0:
            show_product_id = sel.xpath('//div[@class="fp-root"]/@data-product-id').extract()[0]
        else:
            show_product_id = items_details['product_code']

        baseItem['show_product_id'] = show_product_id
        colors_json = items_details['colors']['colors']
        color_id_name_map = {}
        for color_json_temp in colors_json:
            color_id_name_map[color_json_temp['id']] = color_json_temp['label']

        sizes_json = items_details['sizes']['sizes']
        size_id_value_map = {}
        for size_json_temp in sizes_json:
            size_id_value_map[size_json_temp['id']] = size_json_temp['value']

        images_temp = []
        imgs = items_details['media']['images']
        for img in imgs:
            imageItem = ImageItem()
            image_header = 'http://image.s5a.com/is/image/saksoff5th/' + img
            imageItem['image'] = image_header+image_tail
            imageItem['thumbnail'] = image_header+thumbnail_tail
            images_temp.append(imageItem)

        color_as = sel.xpath('//li[@class="product-variant-attribute-value product-variant-attribute-value--swatch"] | //li[@class="product-variant-attribute-value product-variant-attribute-value--unavailable product-variant-attribute-value--swatch"]')
        if len(color_as) == 0:
            images = []
            image_header = 'http://image.s5a.com/is/image/saksoff5th/'+str(baseItem['show_product_id'])
            imageItem = ImageItem()
            imageItem['image'] = image_header+image_tail
            baseItem['cover'] = imageItem['image'].strip()
            imageItem['thumbnail'] = image_header+thumbnail_tail
            images.append(imageItem)

            colorItem = Color()
            colorItem['type'] = 'color'
            colorItem['from_site'] = self.name
            colorItem['show_product_id'] = baseItem['show_product_id']
            if len(sel.xpath('//dd[@class="product-variant-attribute-label__selected-value"][1]/text()')) > 0:
                colorItem['name'] = sel.xpath('//dd[@class="product-variant-attribute-label__selected-value"][1]/text()').extract()[0]
            else:
                colorItem['name'] = 'one-color'
            colorItem['images'] = images + images_temp
            colorItem['cover'] = imageItem['thumbnail']
            yield colorItem

        elif len(color_as) == 1:
            images = []
            image_header = 'http://image.s5a.com/is/image/saksoff5th/'+str(baseItem['show_product_id'])
            imageItem = ImageItem()
            imageItem['image'] = image_header+image_tail
            imageItem['thumbnail'] = image_header+thumbnail_tail
            baseItem['cover'] = imageItem['thumbnail'].strip()
            images.append(imageItem)

            colorItem = Color()
            colorItem['type'] = 'color'
            colorItem['from_site'] = self.name
            colorItem['show_product_id'] = baseItem['show_product_id']
            colorItem['name'] = color_as.xpath('./span/text()').extract()[0]
            colorItem['images'] = images + images_temp

            color_cover_style = color_as.xpath('./@style').re(r'background-color:(.+);')
            if len(color_cover_style) > 0:
                colorItem['cover_style'] = color_cover_style[0]
            else:
                colorItem['cover'] = imageItem['thumbnail']
            yield colorItem
        else:
            for color_json in colors_json:
                images = []
                image_header = 'http://image.s5a.com/is/image/saksoff5th/' + color_json['colorize_image_url']
                imageItem = ImageItem()
                imageItem['image'] = image_header+image_tail
                imageItem['thumbnail'] = image_header+thumbnail_tail
                baseItem['cover'] = imageItem['image'].strip()
                images.append(imageItem)

                colorItem = Color()
                colorItem['type'] = 'color'
                colorItem['from_site'] = self.name
                colorItem['show_product_id'] = baseItem['show_product_id']
                colorItem['name'] = color_json['label']
                colorItem['images'] = images + images_temp
                colorItem['cover'] = imageItem['thumbnail']
                if color_json['value']:
                    colorItem['cover_style'] = color_json['value']

                yield colorItem

        # color_names_copy = color_names[:]

        skus = []
        # for color_name_temp in color_names_copy:
        #     for size in sizes:
        for sku in items_details['skus']['skus']:
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = baseItem['show_product_id']
            skuItem['from_site'] = self.name
            if sku['size_id'] == -1:
                size = 'one-size'
            else:
                size = size_id_value_map[sku['size_id']]

            if color_names == ['one-color']:
                color_name = 'one-color'
            else:
                if sku['color_id'] in color_id_name_map:
                    color_name = color_id_name_map[sku['color_id']]
                else:
                    continue
            skuItem['id'] = color_name + '-' + str(size)
            skuItem['color'] = color_name
            skuItem['size']= str(size).strip()
            if sku['status_alias'] == 'available':
                skuItem['is_outof_stock'] = False
            else:
                skuItem['is_outof_stock'] = True

            sku_list_price = sku['price']['list_price']['usd_currency_value']
            if sku_list_price == 'DUMMY':
                sku_list_price = baseItem['list_price']
            sku_current_price = sku['price']['sale_price']['usd_currency_value']
            if sku_current_price == 'DUMMY':
                sku_current_price = baseItem['current_price']
            skuItem['list_price'] = sku_list_price
            skuItem['current_price'] = sku_current_price

            skus.append(skuItem)
            baseItem['skus'] = skus
        yield baseItem

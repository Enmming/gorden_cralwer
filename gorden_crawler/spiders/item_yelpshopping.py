# -*- coding: utf-8 -*-
from gorden_crawler.yelp_items import *
from scrapy.spiders import Spider
from urllib import unquote
from gorden_crawler.spiders.yelpshopping import BaseShoppingSpider
from scrapy.selector import Selector
from scrapy import Request
import re
import urlparse
import urllib

class ItemYelpshoppingSpider(Spider, BaseShoppingSpider):
    name = "item_yelpshopping"
    #allowed_domains = ["yelp.com"]

    '''
        this proxy below configuration needed when ip is banned by yelp
    '''

    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            #'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
#             'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.OpenProxyRandomMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        },

        'ITEM_PIPELINES': {
            'gorden_crawler.pipelines.yelp.YelpPipeline' :  304,
        },
        'DOWNLOAD_TIMEOUT': 30,    
        'COOKIES_ENABLED': True,
    }
    
    start_urls = [
        
    ]

    country_main_url_mapping = {
        'http://www.yelp.com' : 'UNITED STATES',
        'http://nz.yelp.com' : 'NEW ZEALAND',
        'http://zh.yelp.com.hk': 'HONG KONG',
        'http://www.yelp.com.tw': 'TAIWAN',
        'http://www.yelp.com.sg': 'SINGAPORE',
        'http://en.yelp.my': 'MALAYSIA',
        'http://en.yelp.com.ph': 'PHILIPPINES',
        'http://www.yelp.co.jp': 'JAPAN',
        'http://www.yelp.ca': 'CANADA',
        'http://www.yelp.com.au': 'AUSTRALIA',
        'http://www.yelp.at': 'AUSTRIA',
        'http://en.yelp.be': 'BELGIUM',
        'http://www.yelp.pl': 'POLAND',
        'http://www.yelp.dk': 'DANMARK',
        'http://www.yelp.de': 'DEUTSCHLAND',
        'http://www.yelp.fr': 'FRANCE', 
        'http://sv.yelp.fi': 'FINLAND',
        'http://www.yelp.nl': 'NEDERLANDS',
        'http://www.yelp.cz': 'CZECH REPUBLIC',
        'http://www.yelp.no': 'NORWAY',
        'http://www.yelp.pt': 'PORTUGAL',
        'http://www.yelp.se': 'SWEDEN',
        'http://en.yelp.ch': 'SWITZERLAND',
        'http://www.yelp.com.tr': 'TURKEY',
        'http://www.yelp.es': 'SPAIN',
        'http://www.yelp.it': 'ITALIA',
        'http://www.yelp.co.uk': 'UNITED KINGDOM',
    }
    
    country_https_mapping = []

    def __init__(self, url='', *args, **kwargs):
        super(ItemYelpshoppingSpider, self).__init__(*args, **kwargs)
    
        if url:
            url = unquote(url)
            self.start_urls = [url]

    def parse(self, response):

        sel = Selector(response)
        shoppingItem = ShoppingItem()
        response_url = response.url
        
        response_url_dict = urlparse.urlsplit(response_url)
              
        base_url = 'http://' + response_url_dict.netloc
            
        country = self.country_main_url_mapping[base_url]
        
        city = ''
        
        photo = sel.xpath('//div[@class="js-photo photo photo-2"]/div[@class="showcase-photo-box"]/a/img/@src').extract()
        if len(photo) > 0:
            shoppingItem['cover'] = photo[0]
        else:
            photo = sel.xpath('//div[@class="js-photo photo photo-1"]/div[@class="showcase-photo-box"]/a/img/@src').extract()
            if len(photo) > 0:
                shoppingItem['cover'] = photo[0]
            else:
                shoppingItem['cover'] = ''
                
        if shoppingItem['cover'] ==  'http://s3-media4.fl.yelpcdn.com/assets/srv0/yelp_styleguide/c73d296de521/assets/img/default_avatars/business_90_square.png':
            shoppingItem['cover'] = ''
        
        shop_cover = re.sub(r'ls', 'o', shoppingItem['cover'])
        shoppingItem['cover'] = shop_cover
        
#         shop_cover = sel.xpath('//div[@class="showcase-container"]//img/@src').extract()
#         if len(shop_cover) > 0:
#             if len(shop_cover) >= 2:
#                 shop_cover = shop_cover[1]
#             else:
#                 shop_cover = shop_cover[0]
#                 
#             if shop_cover == 'http://s3-media4.fl.yelpcdn.com/assets/srv0/yelp_styleguide/c73d296de521/assets/img/default_avatars/business_90_square.png':
#                 shoppingItem['cover'] = ''
#             else:
#                 print shop_cover
#                 shop_cover = re.sub(r'ls', 'o', shop_cover)
#                 shoppingItem['cover'] = shop_cover
#         else:
#             shoppingItem['cover'] = ''
            
        categories = sel.xpath('//span[@class="category-str-list"]/a/@href').extract()
        category_names = []
        categories_item_list = []
        for category_url in categories:
            match = re.match(r'^\/c\/[^/]+\/(.+)', category_url)
            
            if match:
                category = urllib.unquote(str(match.group(1))).decode('UTF-8')
                
                categoryItem = Category()
                categoryItem['from_site'] = 'yelp'
                categoryItem['crawl_url'] = response_url
                categoryItem['category'] = category
                category_names.append(category)
                categories_item_list.append(categoryItem)
            
        #categories item 
        shoppingItem['categories_item'] = categories_item_list
        shoppingItem['country'] = country
        shoppingItem['city'] = city
        # shoppingItem['area'] = area
        
        
        shoppingItem['category'] = category_names
        shoppingItem['status'] = 1

        return self.handle_parse_item(response, shoppingItem)
        

    def parse_item(self, response):
        shoppingItem = response.meta['shoppingItem']

        return self.handle_parse_item(response, shoppingItem)
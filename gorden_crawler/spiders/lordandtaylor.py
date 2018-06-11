# -*- coding: utf-8 -*-
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
import re
import execjs
from gorden_crawler.spiders.shiji_base import BaseSpider
import math
from gorden_crawler.utils import url
from gorden_crawler.utils.item_field_handler import handle_price

class LordandtaylorSpider(BaseSpider):
#class zappoSpider(RedisSpider):
    name = "lordandtaylor"
    allowed_domains = ["lordandtaylor.com"]
    
    custom_settings = {
#         'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOADER_MIDDLEWARES': {
#             'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }
    
    '''
    正式运行的时候，start_urls为空，通过传参数来进行，通过传递参数 -a 处理
    '''
    start_urls = (
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-dresses',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-tops',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-sweaters',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/plus-size-coats',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/plus-size-jackets-blazers',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-suits',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-pants',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-denim',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/plus-size-womens-jumpsuits-rompers',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-shortsskirts',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/plus-size-workout-lounge-clothes',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-swimwear',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-intimatessleep',
               
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-dresses',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-tops',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-sweaters',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/petite-coats',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/petite-jackets-blazers',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-suits',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-pants',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-denim',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/petites-womens-jumpsuits-rompers',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-shortsskirts',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/womens-petite-active-loungewear-clothing',
               
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-dresses',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-tops',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-sweaters',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-coats',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/womens-blazers-jackets',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-suiting',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-bottoms-pants',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-bottoms-denim',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-jumpsuitsrompers',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-bottoms-skirts',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-bottoms-shorts',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-activewear-loungewear',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-swimwearcoverups',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/lingerie-shapewear',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/sleepwear-robes',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/hosiery-socks',
             
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/shoes/girl',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/shoes/boy',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/shoes/baby-14418--1',  
         
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/earrings-14085--1',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/necklaces-14112--1',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/bracelets-14077--1',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/rings-14124--1',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/the-birthstone-guide',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/swiss',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/womens-watches',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/mens-watches',
             
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/girls-2-6x',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/girls-7-16',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/boys-2-7',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/boys-8-20',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/baby-girls-12-24-months',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/baby-boys-12-24-months',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/kids-accessories',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/fine-jewelry-kids',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/kids-toys-gifts',
             
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-jackets-coats',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-sportcoats-blazers',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-suits-tuxedos',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-sweaters',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-casual-button-down-shirts',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-dress-shirts',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-polos',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-tees',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-pants',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-denim-jeans',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-active',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-hoodies-sweatshirts',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-shorts-swim',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-loungewear-pajamas',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-underwear-socks',
             
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/shoes/womens-shoes',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/shoes/mens-shoes',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/handbags-13928--1',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/wallets--cases',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/fashion-jewelry',
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/accessories-14000--1',
    )
    
    need_parse_url = {
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/shoes/womens-shoes': {'gender': 'women', 'product_type': 'shoes'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/shoes/mens-shoes': {'gender': 'men', 'product_type': 'shoes'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/handbags-13928--1': {'gender': 'women', 'product_type': 'handbags'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/wallets--cases': {'gender': 'women', 'product_type': 'Wallets & Cases'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/fashion-jewelry': {'gender': 'women', 'product_type': 'Jewelry'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/accessories-14000--1': {'gender': 'women', 'product_type': 'Accessories'},
        
    }
    
    url_genger_product_type_map = {
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-dresses' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Dresses'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-tops' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Tops'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-sweaters' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Sweaters'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/plus-size-coats' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Coats'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/plus-size-jackets-blazers' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Jackets & Blazers'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-suits' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Suits & Suit Separates'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-pants' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Pants'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-denim' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Jeans'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/plus-size-womens-jumpsuits-rompers' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Jumpsuits & Rompers'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-shortsskirts' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Skirts & Shorts'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/plus-size-workout-lounge-clothes' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Activewear & Loungewear'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-swimwear' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Swimwear'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-plussize-intimatessleep' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Plus Intimates & Sleepwear'},
        
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-dresses': {'gender': 'women', 'product_type': 'clothing', 'category': 'Petltes Dresses'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-tops': {'gender': 'women', 'product_type': 'clothing', 'category': 'Petltes Tops'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-sweaters': {'gender': 'women', 'product_type': 'clothing', 'category': 'Petltes Sweaters'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/petite-coats': {'gender': 'women', 'product_type': 'clothing', 'category': 'Petltes Coats'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/petite-jackets-blazers': {'gender': 'women', 'product_type': 'clothing', 'category': 'Petltes Jackets & Blazers'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-suits': {'gender': 'women', 'product_type': 'clothing', 'category': 'Petltes Suits & Suit Separates'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-pants': {'gender': 'women', 'product_type': 'clothing', 'category': 'Petltes Pants'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-denim': {'gender': 'women', 'product_type': 'clothing', 'category': 'Petltes Jeans'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/petites-womens-jumpsuits-rompers': {'gender': 'women', 'product_type': 'clothing', 'category': 'Petltes Jumpsuits & Rompers'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-specialsizes-petites-shortsskirts': {'gender': 'women', 'product_type': 'clothing', 'category': 'Petltes Skirts & Shorts'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/womens-petite-active-loungewear-clothing': {'gender': 'women', 'product_type': 'clothing', 'category': 'Petltes Activewear & Loungewear'},
        
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-dresses' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Dresses'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-tops' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Tops'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-sweaters' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Sweaters'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-coats' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Coats'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/womens-blazers-jackets' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Jackets & Blazers'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-suiting' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Suits & Suit Separates'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-bottoms-pants' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Pants'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-bottoms-denim' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Jeans'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-jumpsuitsrompers' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Jumpsuits & Rompers'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-bottoms-skirts' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Skirts'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-bottoms-shorts' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Shorts'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-activewear-loungewear' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Activewear'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/wa-swimwearcoverups' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Swimwear'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/lingerie-shapewear' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Lingerie & Shapewear'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/sleepwear-robes' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Sleepwear & Robes'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/womens-apparel/hosiery-socks' : {'gender': 'women', 'product_type': 'clothing', 'category': 'Hosiery & Socks'},
    
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/shoes/girl' :  {'gender': 'girls', 'product_type': 'mother-kid', 'category': 'shoes'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/shoes/boy' :  {'gender': 'boys', 'product_type': 'mother-kid', 'category': 'shoes'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/shoes/baby-14418--1':  {'gender': 'baby', 'product_type': 'mother-kid', 'category': 'shoes'},  
    
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/earrings-14085--1': {'gender': 'women', 'product_type': 'Jewelry', 'category': 'Earrings'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/necklaces-14112--1': {'gender': 'women', 'product_type': 'Jewelry', 'category': 'Necklaces'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/bracelets-14077--1': {'gender': 'women', 'product_type': 'Jewelry', 'category': 'Bracelets'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/rings-14124--1': {'gender': 'women', 'product_type': 'Jewelry', 'category': 'Rings'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/the-birthstone-guide': {'gender': 'women', 'product_type': 'Jewelry', 'category': 'Birthstones'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/swiss': {'gender': 'unisex', 'product_type': 'Accessories', 'category': 'Watches'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/womens-watches': {'gender': 'women', 'product_type': 'Accessories', 'category': 'Watches'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/jewelry--accessories/mens-watches': {'gender': 'men', 'product_type': 'Accessories', 'category': 'Watches'},
        
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/girls-2-6x': {'gender': 'girls', 'product_type': 'mother-kid', 'category': 'clothing'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/girls-7-16': {'gender': 'girls', 'product_type': 'mother-kid', 'category': 'clothing'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/boys-2-7': {'gender': 'boys', 'product_type': 'mother-kid', 'category': 'clothing'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/boys-8-20': {'gender': 'boys', 'product_type': 'mother-kid', 'category': 'clothing'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/baby-girls-12-24-months': {'gender': 'baby', 'product_type': 'mother-kid', 'category': 'clothing'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/baby-boys-12-24-months': {'gender': 'baby', 'product_type': 'mother-kid', 'category': 'clothing'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/kids-accessories': {'gender': 'kid-unisex', 'product_type': 'mother-kid', 'category': 'accessories'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/fine-jewelry-kids': {'gender': 'girls', 'product_type': 'mother-kid', 'category': 'Jewelry'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/kids/kids-toys-gifts': {'gender': 'kid-unisex', 'product_type': 'mother-kid', 'category': 'Toys & Gifts'},
        
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-jackets-coats': {'gender': 'men', 'product_type': 'clothing', 'category': 'Coats & Jackets'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-sportcoats-blazers': {'gender': 'men', 'product_type': 'clothing', 'category': 'Sportcoats & Blazers'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-suits-tuxedos': {'gender': 'men', 'product_type': 'clothing', 'category': 'Suiting & Tuxedos'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-sweaters': {'gender': 'men', 'product_type': 'clothing', 'category': 'Sweaters'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-casual-button-down-shirts': {'gender': 'men', 'product_type': 'clothing', 'category': 'Casual Button Down Shirts'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-dress-shirts': {'gender': 'men', 'product_type': 'clothing', 'category': 'Dress Shirts'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-polos': {'gender': 'men', 'product_type': 'clothing', 'category': 'Polos'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-tees': {'gender': 'men', 'product_type': 'clothing', 'category': 'T-Shirts'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-pants': {'gender': 'men', 'product_type': 'clothing', 'category': 'Pants'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-denim-jeans': {'gender': 'men', 'product_type': 'clothing', 'category': 'Jeans'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-active': {'gender': 'men', 'product_type': 'clothing', 'category': 'Activewear'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-hoodies-sweatshirts': {'gender': 'men', 'product_type': 'clothing', 'category': 'Hoodies & Sweatshirts'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-shorts-swim': {'gender': 'men', 'product_type': 'clothing', 'category': 'Shorts & Swimwear'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-loungewear-pajamas': {'gender': 'men', 'product_type': 'clothing', 'category': 'Loungewear & Sleepwear'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/mens/mens-underwear-socks': {'gender': 'men', 'product_type': 'clothing', 'category': 'Underwear & Socks'},
        
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/wallets': {'gender': 'women', 'product_type': 'Wallets & Cases','category':'Wallets & Wristlets'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/tech--phone-accessories': {'gender': 'women', 'product_type': 'Wallets & Cases','category':'Tech Accessories'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/cosmetic-bags--pouches': {'gender': 'women', 'product_type': 'Wallets & Cases','category':'Cosmetic Bags'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/totes': {'gender': 'women', 'product_type': 'Wallets & Cases','category':'Totes'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/satchels': {'gender': 'women', 'product_type': 'Wallets & Cases','category':'Satchels'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/shoulder-bags': {'gender': 'women', 'product_type': 'Wallets & Cases','category':'Shoulder Bags & Hobos'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/clutches--evening': {'gender': 'women', 'product_type': 'Wallets & Cases','category':'Clutches & Evening'},
        'http://www.lordandtaylor.com/webapp/wcs/stores/servlet/en/lord-and-taylor/search/handbags/backpacks1': {'gender': 'women', 'product_type': 'Wallets & Cases','category':'Backpacks'},
        
    }
    
    base_url = 'http://www.lordandtaylor.com/'

    def handle_parse_item(self, response, item):
        
        sel = Selector(response)
        
        product_id_div = sel.xpath('//div[@id="storeCatalogEntryID"]/text()').extract()
        
        if len(product_id_div) == 0 or len(product_id_div[0].strip()) == 0 :
            return
        
        product_id = sel.xpath('//div[@id="storeCatalogEntryID"]/text()').extract()[0].strip()

        item['show_product_id'] = product_id
        
        sku_infos_str = sel.xpath('//div[@id="entitledItem_'+ product_id +'"]/text()').re(r'\[[\s\S]+\]')[0].strip()

        context = execjs.compile('''
            var sku_info = %s;
            function getSkuInfo(){
                return sku_info;
            }
        ''' % sku_infos_str)
        
        sku_infos = context.call('getSkuInfo')
        
        dimensions = set([])
        sizes = {}
        colors = []
        color_names = []
        color_name_images_map = {}
        
        color_list = sel.xpath('//ul[@class="detail_color"]/li')
        if color_list:
            for color_li in color_list:
                color_item = Color()
                color_item['show_product_id'] = product_id
                color_item['from_site'] = self.name
                color_item['type'] = 'color'
                color_item['name'] = color_li.xpath('./a//div[@class="colorName"]/span/text()').extract()[0].strip()
    
                color_names.append(color_item['name'])
                colors.append(color_item)
        else:
            color_list = sel.xpath('//div[@class="color_swatch_list"]')[:-1]
            if color_list:
                for color_li in color_list:
                    for color_l in color_li.xpath('./ul/li'):
                        c = color_l.xpath('./a/@title').extract()[0]
                        color_item = Color()
                        color_item['show_product_id'] = product_id
                        color_item['from_site'] = self.name
                        color_item['type'] = 'color'
                        color_item['name'] = c
            
                        color_names.append(color_item['name'])
                        colors.append(color_item)
            else:
                color_item = Color()
                color_item['name'] = 'one color'
                color_names.append(color_item['name'])
                colors.append(color_item)
            
                
        
        sel.xpath('//ul[@id="thumb1"]/li')
        
        skus = []
        
        for sku_info in sku_infos:
            sku_item = SkuItem()
            
            sku_id = sku_info['catentry_id']
            
            sku_item['id'] = sku_id
            sku_item['type'] = 'sku'
            sku_item['from_site'] = self.name
            sku_item['show_product_id'] = product_id
            
            attributes = sku_info['Attributes']
            sku_size = {}
            if attributes == {}:
                attributes = {'vendorcolor_one color','size_one size'}
            else:
                for tempKey in attributes.keys():
                    if tempKey.find('Size') != -1:
                        temp = 1
                        break
                    else:
                        temp = 0
                if temp == 0:
                    attributes['size_one size'] = '2'
            
            for attribute in attributes:
                
                keys = attribute.split('_')
                dimension = keys[0].lower()
                value = keys[1]
                if dimension == 'vendorcolor':
                    dimension = 'color'
                    if value not in color_name_images_map.keys():
                        
                        if 'ItemThumbnailImage' not in sku_info.keys():
                            return
                        thumbnail = sku_info['ItemThumbnailImage']
                        if not re.match(r'^http', thumbnail):
                            thumbnail = 'http:' + thumbnail
                            
                        image = sku_info['ItemImage']
                        if not re.match(r'^http', image):
                            image = 'http:' + image
                        image = image + '&wid=970&hei=1245&fit=fit,1'
                        
                        color_name_images_map[value] = {'images': [{
                            'thumbnail': thumbnail,
                            'image': image
                        }]}
                        
                        color_cover = sku_info['ItemSwatchImage2']
                        if not re.match(r'^http', color_cover):
                            color_cover = 'http:' + color_cover
                        color_name_images_map[value]['cover'] = color_cover
                    
                dimensions.add(dimension)
                    
                sku_size[dimension] = value
                
                
                if dimension != 'color':
                    if dimension not in sizes.keys():
                        sizes[dimension] = set([])
                    
                    sizes[dimension].add(value)
                    
            sku_item['size'] = sku_size
            
            if sku_info['offerPrice'] == '':
                return
            else:
                sku_item['current_price'] = sku_info['offerPrice']
                
            if sku_info['listPrice'] == '':
                return
            else:
                sku_item['list_price'] = sku_info['listPrice']
                
            sku_item['current_price'] = handle_price(sku_item['current_price'])
            sku_item['list_price'] = handle_price(sku_item['list_price'])
                 
            if  float(sku_item['list_price']) < float(sku_item['current_price']):
                sku_item['list_price'] = sku_item['current_price']
                
            if sku_info['availableQuantity']:
                sku_item['quantity'] = int(float(sku_info['availableQuantity']))
            else:
                sku_item['quantity'] = 0
            sku_item['is_outof_stock'] = sku_info['outOfStock']
            
            if 'color' not in sku_item.keys():
                sku_item['color'] = 'one color'
            elif sku_item['color'] == {}:
                sku_item['color'] = 'one color'
                 
            if 'size' not in sku_item.keys():
                sku_item['size'] = 'one size'
            elif sku_item['size'] == {}:
                sku_item['size'] = 'one size'
                
            skus.append(sku_item)
            
        for color in colors:
            if color['name'] in color_name_images_map.keys():
                color['images'] = color_name_images_map[color['name']]['images']
                color['cover'] = color_name_images_map[color['name']]['cover'] 
                yield color
        
        item['dimensions'] = list(dimensions)
        
        for size_key in sizes:
            sizes[size_key] = list(sizes[size_key])
        item['sizes'] = sizes
        item['colors'] = color_names
        
        item['skus'] = skus 
        item['desc'] = sel.xpath('//div[@id="detial_main_content"]').extract()
        if item['desc']:
            item['desc'] = item['desc'][0]
        else:
            item['desc'] = sel.xpath('//div[@class="descriptionsContent"]').extract()[0]
        
        yield item

    '''具体的解析规则'''
    def parse_item(self, response):
        
#         item = BaseItem()
#         item['type'] = 'base'
#         item['show_product_id'] = '1209118'
        item = response.meta['item']
        
        return self.handle_parse_item(response, item)
      
    def parse_list(self, response):
        
        product_type = response.meta['product_type']
        category = response.meta['category']
        gender = response.meta['gender']
        
        sel = Selector(response)
        
        lis = sel.xpath('//ul[@id="totproductsList"]/li')
        
        for li in lis:
            item = BaseItem()
            item['type'] = 'base'
            item['from_site'] = self.name
            item['product_type'] = product_type
            item['category'] = category
            item['gender'] = gender
            
            cover = li.xpath('./div[@class="pro_pic"]//img/@data-original').extract()[0]
            if not re.match(r'^http', cover):
                cover = 'http:' + cover
            
            item['cover'] = cover
            item['brand'] = li.xpath('./a[@class="tit"]/text()').extract()[0]
            item['title'] = li.xpath('./div[@class="info"]/a/text()').extract()[0].strip()
            if item['title'] == '':
                item['title'] = 'Product Title Temporarily Not Available'
                
            black_price= li.xpath('./div[@class="pro_price_black"]/text()').extract()[0].strip()
            m = re.match(r'^(\$[\d\.\,]+)\s*-\s*(\$[\d\.\,]+)', black_price)
            if m is not None:
                item['list_price'] = handle_price(m.group(2))
            else:
                item['list_price'] = handle_price(black_price)
                
            red_price = li.xpath('./div[@class="pro_price_red"]/text()').re(r'[^\$]+(.+)')
            if len(red_price) > 0:
                red_price = red_price[0].strip()
                m = re.match(r'^(\$[\d\.\,]+)\s*-\s*(\$[\d\.\,]+)', red_price)
                if m is not None:
                    item['current_price'] = handle_price(m.group(1))
                else:    
                    item['current_price'] = handle_price(red_price)
            else:
                item['current_price'] = item['list_price']
            
            url = li.xpath('.//script[@class="catEntryDisplayUrlScript"]/text()').re_first(r'categoryDisplayJS.setCatEntryDisplayURL\("(.+)"\);')  
            item['url'] = url
        
            yield Request(url, callback=self.parse_item, meta={'item': item})
    '''
    爬虫解析入口函数，用于解析丢入的第一个请求，一般是顶级目录页
    '''
    def parse(self, response):
        
        sel = Selector(response)
        
        currentUrl = response.url
        
        if currentUrl in self.need_parse_url.keys():
            '''解析'''
            gender = self.need_parse_url[currentUrl]['gender']
            product_type = self.need_parse_url[currentUrl]['product_type']
            categoryDivs = sel.xpath('//a[@class="left_cate orange"]/parent::div/following-sibling::div/div[@class="thirdM"]')
            
            for categoryDiv in categoryDivs:
                category = categoryDiv.xpath('./a[@class="left_cate2"]/text()').extract()[0]
                temp_url = categoryDiv.xpath('./a[@class="left_cate2" ]/@href').extract()[0]
                if temp_url.find('ttp://') != -1:
                    new_url = temp_url
                else:
                    new_url = self.base_url + temp_url
                yield Request(new_url, callback=self.parse, meta={'gender': gender, 'product_type': product_type, 'category': category})
        else:
            if 'gender' in response.meta.keys() and 'product_type' in response.meta.keys() and 'category' in response.meta.keys():
                gender = response.meta['gender']
                product_type = response.meta['product_type']
                category = response.meta['category']
            else:
                if response.url not in self.url_genger_product_type_map.keys():
                    return 
                
                gender = self.url_genger_product_type_map[response.url]['gender']
                product_type = self.url_genger_product_type_map[response.url]['product_type']
                category = self.url_genger_product_type_map[response.url]['category']
    
            base_ajax_url = sel.xpath('//input[@name="filterRefreshBaseURL"]/@value').extract()[0]
            
            '''翻页'''
            total_page = sel.xpath('//div[@id="list_page1"]/span/text()').re_first(r'(\d+)')
            
            total_page = float(total_page.replace(',', ''))
            page_num = int(math.ceil(total_page / 100))
            for i in range(0, page_num -1):
                ajaxUrl = url.url_values_plus(base_ajax_url, 'beginIndex', i * 100)
                yield Request(ajaxUrl, callback=self.parse_list, meta={'product_type': product_type, 'gender': gender, 'category': category})

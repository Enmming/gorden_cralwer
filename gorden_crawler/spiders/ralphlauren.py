# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy import Request, FormRequest
import re
import execjs
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color

from scrapy.utils.response import get_base_url
from gorden_crawler.spiders.shiji_base import BaseSpider


class RalphlaurenSpider(BaseSpider):
#class SixPmSpider(RedisSpider):
    name = "ralphlauren"
    allowed_domains = ["ralphlauren.com"]

    '''
    正式运行的时候，start_urls为空，通过传参数来进行，通过传递参数 -a 处理
    '''

    custom_settings = {
        # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.5,
        'RETRY_TIMES': 10,
        'DOWNLOAD_TIMEOUT': 200
    }

    start_urls =[
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760809',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2498319',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760812',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760813',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2004212',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=3351645',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=35256186',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760811',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=34560716',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2877584',

        'http://www.ralphlauren.com/family/index.jsp?categoryId=4332103',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760895',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=57940726',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=13085987',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760899',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760899',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1988976',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=13102020',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=17517136',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760962',

        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098016&cp=51960806.51960826.46098196&ab=rd_shoesaccessories&ab=ln_nodivision_cs_boots',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098026&cp=51960806.51960826.46098196&ab=rd_shoesaccessories&ab=ln_nodivision_cs_pumps',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098036&cp=51960806.51960826.46098196&ab=rd_shoesaccessories&ab=ln_nodivision_cs_sandals',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098046&cp=51960806.51960826.46098196&ab=rd_shoesaccessories&ab=ln_nodivision_cs_ballets,flats&sneakers',

        'http://www.ralphlauren.com/family/index.jsp?categoryId=52457826&cp=51960806&ab=rd_shoesaccessories.46098216&ab=ln_nodivision_cs_clutches',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=52633786&cp=51960806.51960826.46098216&ab=rd_shoesaccessories&ab=ln_nodivision_cs_crossbodybags',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=52633686&cp=51960806.51960826.46098216&ab=rd_shoesaccessories&ab=ln_nodivision_cs_hobos&shoulderbags',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=52633696&cp=51960806.51960826.46098216&ab=rd_shoesaccessories&ab=ln_nodivision_cs_tophandles&satchels',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=52633796&cp=51960806.51960826.46098216&ab=rd_shoesaccessories&ab=ln_nodivision_cs_totes',

        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098226&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_belts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097996&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_wallets&smallleathergoods',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=52457166&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_jewelry',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098376&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_sunglasses&eyewear',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=69514096&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_sleepwear&robes',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=69514806&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_socks,tights&leggings',

        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097786&cp=51960806.51960816.46097636&ab=rd_shoesaccessories&ab=ln_nodivision_cs_casual',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097796&cp=51960806.51960816.46097636&ab=rd_shoesaccessories&ab=ln_nodivision_cs_dress',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097806&cp=51960806.51960816.46097636&ab=rd_shoesaccessories&ab=ln_nodivision_cs_sneakers',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097656&cp=51960806.51960816.46097636&ab=rd_shoesaccessories&ab=ln_nodivision_cs_boots',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097396&cp=51960806.51960816&ab=rd_shoesaccessories&ab=ln_nodivision_cs_ties&pocketsquares',

        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097706&cp=51960806.51960816.46097586&ab=rd_shoesaccessories&ab=ln_nodivision_cs_travelbags',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097876&cp=51960806.51960816.46097586&ab=rd_shoesaccessories&ab=ln_nodivision_cs_totes',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097716&cp=51960806.51960816.46097586&ab=rd_shoesaccessories&ab=ln_nodivision_cs_messengers&crossbody',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097886&cp=51960806.51960816.46097586&ab=rd_shoesaccessories&ab=ln_nodivision_cs_briefcases&folios',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097896&cp=51960806.51960816.46097586&ab=rd_shoesaccessories&ab=ln_nodivision_cs_backpacks',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097406&cp=51960806.51960816&ab=rd_shoesaccessories&ab=ln_nodivision_cs_wallets&smallaccessories',

        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097316&cp=51960806.51960816&ab=rd_shoesaccessories&ab=ln_nodivision_cs_belts&braces',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097326&cp=51960806.51960816&ab=rd_shoesaccessories&ab=ln_nodivision_cs_cufflinks&jewelry',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097606&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_sunglasses',

        'http://www.ralphlauren.com/family/index.jsp?categoryId=23600576&cp=1760783.1760916&ab=ln_children_cs_tees&sweatshirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1958847&cp=1760783.1760916&ab=ln_children_cs_poloshirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1890954&cp=1760783.1760916&ab=ln_children_cs_sportshirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1890955&cp=1760783.1760916&ab=ln_children_cs_sweaters',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2462797&cp=1760783.1760916&ab=ln_children_cs_outerwear&jackets',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1767601&cp=1760783.1760916&ab=ln_children_cs_pants&shorts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1954785&cp=1760783.1760916&ab=ln_children_cs_suits&sportcoats',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1904289&cp=1760783.1760916&ab=ln_children_cs_swimwear',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=4450428&cp=1760783.1760916&ab=ln_children_cs_sleepwear',


        'http://www.ralphlauren.com/family/index.jsp?categoryId=63151986&cp=1760783.1760917.67500256&ab=rd_children_cs_outfitsforboys&cp=1760783.1760917.67500256',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=23600596&cp=1760783.1760917&ab=ln_children_cs_tees&sweatshirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1958848&cp=1760783.1760917&ab=ln_children_cs_poloshirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2124967&cp=1760783.1760917&ab=ln_children_cs_sportshirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1890958&cp=1760783.1760917&ab=ln_children_cs_sweaters',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2462796&cp=1760783.1760917&ab=ln_children_cs_outerwear&jackets',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1767605&cp=1760783.1760917&ab=ln_children_cs_pants&shorts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1954813&cp=1760783.1760917&ab=ln_children_cs_suits&sportcoats',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1904291&cp=1760783.1760917&ab=ln_children_cs_swimwear',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=32686196&cp=1760783.1760917&ab=ln_children_cs_underwear',

        'http://www.ralphlauren.com/family/index.jsp?categoryId=11855089&cp=1760783&ab=ln_children_cs_shoes',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068352&cp=1760783&ab=ln_children_cs_bags',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068354&cp=1760783&ab=ln_children_cs_ties&bowties',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068353&cp=1760783&ab=ln_children_cs_belts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068356&cp=1760783&ab=ln_children_cs_socks',

        'http://www.ralphlauren.com/family/index.jsp?categoryId=2143107&cp=1760783.1760911&ab=ln_children_cs_dresses&skirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1892952&cp=1760783.1760911&ab=ln_children_cs_outerwear&jackets',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1895475&cp=1760783.1760911&ab=ln_children_cs_tops&tees',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1961589&cp=1760783.1760911&ab=ln_children_cs_poloshirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1895476&cp=1760783.1760911&ab=ln_children_cs_sweaters',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2746382&cp=1760783.1760911&ab=ln_children_cs_pants,leggings&shorts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=4450431&cp=1760783.1760911&ab=ln_children_cs_sleepwear',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1904293&cp=1760783.1760911&ab=ln_children_cs_swimwear',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=63151996&cp=1760783.1760912.63151826&ab=rd_children_cs_outfitsforgirls&cp=1760783.1760912.63151826',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2143114&cp=1760783.1760912&ab=ln_children_cs_dresses&skirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1892953&cp=1760783.1760912&ab=ln_children_cs_outerwear&jackets',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1895477&cp=1760783.1760912&ab=ln_children_cs_tops&tees',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1961590&cp=1760783.1760912&ab=ln_children_cs_poloshirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1895478&cp=1760783.1760912&ab=ln_children_cs_sweaters',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2746384&cp=1760783.1760912&ab=ln_children_cs_pants,leggings&shorts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1904297&cp=1760783.1760912&ab=ln_children_cs_swimwear',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=11855171&cp=1760783&ab=ln_children_cs_shoes',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068346&cp=1760783&ab=ln_children_cs_bags&totes',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068347&cp=1760783&ab=ln_children_cs_belts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068348&cp=1760783&ab=ln_children_cs_jewelry&hairaccessories',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068350&cp=1760783&ab=ln_children_cs_socks&tights',


        'http://www.ralphlauren.com/family/index.jsp?categoryId=1907196&cp=2048081&ab=ln_baby_cs_outerwear',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=23600666&cp=2048081&ab=ln_baby_cs_tees&sweatshirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1988835&cp=2048081&ab=ln_baby_cs_polos',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=51185046&cp=2048081&ab=ln_baby_cs_one-pieces',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1815396&cp=2048081&ab=ln_baby_cs_outfits&giftsets',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2073387&cp=2048081&ab=ln_baby_cs_sweaters',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=18158826&cp=2048081&ab=ln_baby_cs_sportshirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1767582&cp=2048081&ab=ln_baby_cs_pants',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1882877&cp=2048081&ab=ln_baby_cs_shoes',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2249349&cp=2048081&ab=ln_baby_cs_dresses&skirts',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=51185206&cp=2048081&ab=ln_baby_cs_one-pieces',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2794258&cp=2048081&ab=ln_baby_cs_outfits&giftsets',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1767585&cp=2048081&ab=ln_baby_cs_tops',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1988868&cp=2048081&ab=ln_baby_cs_polos',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1767586&cp=2048081&ab=ln_baby_cs_pants&leggings',
        'http://www.ralphlauren.com/family/index.jsp?categoryId=3117307&cp=2048081&ab=ln_baby_cs_shoes',

    ]

    url_gender_type = {
    	'http://www.ralphlauren.com/family/index.jsp?categoryId=1760809':{'gender':'men', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2498319':{'gender':'men', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760812':{'gender':'men', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760813':{'gender':'men', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2004212':{'gender':'men', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=3351645':{'gender':'men', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=35256186':{'gender':'men', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760811':{'gender':'men', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=34560716':{'gender':'men', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2877584':{'gender':'men', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=4332103':{'gender':'women', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760895':{'gender':'women', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=57940726':{'gender':'women', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=13085987':{'gender':'women', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760899':{'gender':'women', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760899':{'gender':'women', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1988976':{'gender':'women', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=13102020':{'gender':'women', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=17517136':{'gender':'women', 'product_type':'clothing'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1760962':{'gender':'women', 'product_type':'clothing'},

        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098016&cp=51960806.51960826.46098196&ab=rd_shoesaccessories&ab=ln_nodivision_cs_boots' :{'gender':'women', 'product_type':'Shoes'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098026&cp=51960806.51960826.46098196&ab=rd_shoesaccessories&ab=ln_nodivision_cs_pumps' :{'gender':'women', 'product_type':'Shoes'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098036&cp=51960806.51960826.46098196&ab=rd_shoesaccessories&ab=ln_nodivision_cs_sandals':{'gender':'women', 'product_type':'Shoes'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098046&cp=51960806.51960826.46098196&ab=rd_shoesaccessories&ab=ln_nodivision_cs_ballets,flats&sneakers':{'gender':'women', 'product_type':'Shoes'},

        'http://www.ralphlauren.com/family/index.jsp?categoryId=52457826&cp=51960806&ab=rd_shoesaccessories.46098216&ab=ln_nodivision_cs_clutches':{'gender':'women', 'product_type':'handbags', 'category':'clutches' },
        'http://www.ralphlauren.com/family/index.jsp?categoryId=52633786&cp=51960806.51960826.46098216&ab=rd_shoesaccessories&ab=ln_nodivision_cs_crossbodybags':{'gender':'women', 'product_type':'handbags'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=52633686&cp=51960806.51960826.46098216&ab=rd_shoesaccessories&ab=ln_nodivision_cs_hobos&shoulderbags':{'gender':'women', 'product_type':'handbags'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=52633696&cp=51960806.51960826.46098216&ab=rd_shoesaccessories&ab=ln_nodivision_cs_tophandles&satchels':{'gender':'women', 'product_type':'handbags'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=52633796&cp=51960806.51960826.46098216&ab=rd_shoesaccessories&ab=ln_nodivision_cs_totes':{'gender':'women', 'product_type':'handbags'},

        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098226&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_belts': {'gender':'women', 'product_type':'accessories'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097996&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_wallets&smallleathergoods': {'gender':'women', 'product_type':'accessories'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=52457166&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_jewelry': {'gender':'women', 'product_type':'accessories'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46098376&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_sunglasses&eyewear': {'gender':'women', 'product_type':'accessories'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=69514096&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_sleepwear&robes': {'gender':'women', 'product_type':'accessories'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=69514806&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_socks,tights&leggings': {'gender':'women', 'product_type':'accessories'},

        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097786&cp=51960806.51960816.46097636&ab=rd_shoesaccessories&ab=ln_nodivision_cs_casual':{'gender':'men', 'product_type':'Shoes'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097796&cp=51960806.51960816.46097636&ab=rd_shoesaccessories&ab=ln_nodivision_cs_dress':{'gender':'men', 'product_type':'Shoes'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097806&cp=51960806.51960816.46097636&ab=rd_shoesaccessories&ab=ln_nodivision_cs_sneakers':{'gender':'men', 'product_type':'Shoes'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097656&cp=51960806.51960816.46097636&ab=rd_shoesaccessories&ab=ln_nodivision_cs_boots':{'gender':'men', 'product_type':'Shoes'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097396&cp=51960806.51960816&ab=rd_shoesaccessories&ab=ln_nodivision_cs_ties&pocketsquares':{'gender':'men', 'product_type':'accessories'},

        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097706&cp=51960806.51960816.46097586&ab=rd_shoesaccessories&ab=ln_nodivision_cs_travelbags':{'gender':'men', 'product_type':'bags'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097876&cp=51960806.51960816.46097586&ab=rd_shoesaccessories&ab=ln_nodivision_cs_totes':{'gender':'men', 'product_type':'bags'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097716&cp=51960806.51960816.46097586&ab=rd_shoesaccessories&ab=ln_nodivision_cs_messengers&crossbody':{'gender':'men', 'product_type':'bags'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097886&cp=51960806.51960816.46097586&ab=rd_shoesaccessories&ab=ln_nodivision_cs_briefcases&folios':{'gender':'men', 'product_type':'bags'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097896&cp=51960806.51960816.46097586&ab=rd_shoesaccessories&ab=ln_nodivision_cs_backpacks':{'gender':'men', 'product_type':'bags'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097406&cp=51960806.51960816&ab=rd_shoesaccessories&ab=ln_nodivision_cs_wallets&smallaccessories':{'gender':'men', 'product_type':'bags'},

        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097316&cp=51960806.51960816&ab=rd_shoesaccessories&ab=ln_nodivision_cs_belts&braces':{'gender':'men', 'product_type':'accessories'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097326&cp=51960806.51960816&ab=rd_shoesaccessories&ab=ln_nodivision_cs_cufflinks&jewelry':{'gender':'men', 'product_type':'accessories'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=46097606&cp=51960806&ab=rd_shoesaccessories&ab=ln_nodivision_cs_sunglasses':{'gender':'men', 'product_type':'accessories'},

        'http://www.ralphlauren.com/family/index.jsp?categoryId=23600576&cp=1760783.1760916&ab=ln_children_cs_tees&sweatshirts': {'gender':'boys', 'product_type': 'mother-kid', 'category': 'Tees & Sweatshirts'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1958847&cp=1760783.1760916&ab=ln_children_cs_poloshirts': {'gender':'boys', 'product_type': 'mother-kid', 'category': 'Polo Shirts'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1890954&cp=1760783.1760916&ab=ln_children_cs_sportshirts': {'gender':'boys', 'product_type': 'mother-kid', 'category': 'Sport Shirts'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1890955&cp=1760783.1760916&ab=ln_children_cs_sweaters': {'gender':'boys', 'product_type': 'mother-kid', 'category': 'Sweaters'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2462797&cp=1760783.1760916&ab=ln_children_cs_outerwear&jackets': {'gender':'boys', 'product_type': 'mother-kid', 'category': 'Outerwear & Jackets'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1767601&cp=1760783.1760916&ab=ln_children_cs_pants&shorts': {'gender':'boys', 'product_type': 'mother-kid', 'category': 'Pants & Shorts'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1954785&cp=1760783.1760916&ab=ln_children_cs_suits&sportcoats': {'gender':'boys', 'product_type': 'mother-kid', 'category': 'Suits & Sport Coats'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1904289&cp=1760783.1760916&ab=ln_children_cs_swimwear': {'gender':'boys', 'product_type': 'mother-kid', 'category': 'Swimwear'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=4450428&cp=1760783.1760916&ab=ln_children_cs_sleepwear': {'gender':'boys', 'product_type': 'mother-kid', 'category': 'Sleepwear'},


        'http://www.ralphlauren.com/family/index.jsp?categoryId=63151986&cp=1760783.1760917.67500256&ab=rd_children_cs_outfitsforboys&cp=1760783.1760917.67500256': {'category': 'Outfits for Boys', 'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=23600596&cp=1760783.1760917&ab=ln_children_cs_tees&sweatshirts': {'category': 'Tees & Sweatshirts', 'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1958848&cp=1760783.1760917&ab=ln_children_cs_poloshirts': {'category': 'Polo Shirts', 'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2124967&cp=1760783.1760917&ab=ln_children_cs_sportshirts': {'category': 'Sport Shirts', 'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1890958&cp=1760783.1760917&ab=ln_children_cs_sweaters': {'category': 'Sweaters', 'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2462796&cp=1760783.1760917&ab=ln_children_cs_outerwear&jackets': {'category': 'Outerwear & Jackets', 'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1767605&cp=1760783.1760917&ab=ln_children_cs_pants&shorts': {'category': 'Pants & Shorts', 'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1954813&cp=1760783.1760917&ab=ln_children_cs_suits&sportcoats': {'category': 'Suits & Sport Coats', 'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1904291&cp=1760783.1760917&ab=ln_children_cs_swimwear': {'category': 'Swimwear', 'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=32686196&cp=1760783.1760917&ab=ln_children_cs_underwear': {'category': 'Underwear', 'gender':'boys', 'product_type': 'mother-kid'},

        'http://www.ralphlauren.com/family/index.jsp?categoryId=11855089&cp=1760783&ab=ln_children_cs_shoes': {'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068352&cp=1760783&ab=ln_children_cs_bags': {'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068354&cp=1760783&ab=ln_children_cs_ties&bowties': {'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068353&cp=1760783&ab=ln_children_cs_belts': {'gender':'boys', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068356&cp=1760783&ab=ln_children_cs_socks': {'gender':'boys', 'product_type': 'mother-kid'},

        'http://www.ralphlauren.com/family/index.jsp?categoryId=2143107&cp=1760783.1760911&ab=ln_children_cs_dresses&skirts': {'category': 'Dresses & Skirts' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1892952&cp=1760783.1760911&ab=ln_children_cs_outerwear&jackets': {'category': 'Outerwear & Jackets' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1895475&cp=1760783.1760911&ab=ln_children_cs_tops&tees': {'category': 'Tops & Tees' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1961589&cp=1760783.1760911&ab=ln_children_cs_poloshirts': {'category': 'Polo Shirts' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1895476&cp=1760783.1760911&ab=ln_children_cs_sweaters': {'category': 'Sweaters' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2746382&cp=1760783.1760911&ab=ln_children_cs_pants,leggings&shorts': {'category': 'Pants, Leggings & Shorts' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=4450431&cp=1760783.1760911&ab=ln_children_cs_sleepwear': {'category': 'Sleepwear' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1904293&cp=1760783.1760911&ab=ln_children_cs_swimwear': {'category': 'Swimwear' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=63151996&cp=1760783.1760912.63151826&ab=rd_children_cs_outfitsforgirls&cp=1760783.1760912.63151826': {'category': 'Outfits for Girls' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2143114&cp=1760783.1760912&ab=ln_children_cs_dresses&skirts': {'category': 'Dresses & Skirts' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1892953&cp=1760783.1760912&ab=ln_children_cs_outerwear&jackets': {'category': 'Outerwear & Jackets' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1895477&cp=1760783.1760912&ab=ln_children_cs_tops&tees': {'category': 'Tops & Tees' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1961590&cp=1760783.1760912&ab=ln_children_cs_poloshirts': {'category': 'Polo Shirts' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1895478&cp=1760783.1760912&ab=ln_children_cs_sweaters': {'category': 'Sweaters' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2746384&cp=1760783.1760912&ab=ln_children_cs_pants,leggings&shorts': {'category': 'Pants, Leggings & Shorts' ,'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1904297&cp=1760783.1760912&ab=ln_children_cs_swimwear': {'category': 'Swimwear' ,'gender':'girls', 'product_type': 'mother-kid'},

        'http://www.ralphlauren.com/family/index.jsp?categoryId=11855171&cp=1760783&ab=ln_children_cs_shoes': {'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068346&cp=1760783&ab=ln_children_cs_bags&totes': {'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068347&cp=1760783&ab=ln_children_cs_belts': {'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068348&cp=1760783&ab=ln_children_cs_jewelry&hairaccessories': {'gender':'girls', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=12068350&cp=1760783&ab=ln_children_cs_socks&tights': {'gender':'girls', 'product_type': 'mother-kid'},


        'http://www.ralphlauren.com/family/index.jsp?categoryId=1907196&cp=2048081&ab=ln_baby_cs_outerwear': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=23600666&cp=2048081&ab=ln_baby_cs_tees&sweatshirts': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1988835&cp=2048081&ab=ln_baby_cs_polos': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=51185046&cp=2048081&ab=ln_baby_cs_one-pieces': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1815396&cp=2048081&ab=ln_baby_cs_outfits&giftsets': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2073387&cp=2048081&ab=ln_baby_cs_sweaters': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=18158826&cp=2048081&ab=ln_baby_cs_sportshirts': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1767582&cp=2048081&ab=ln_baby_cs_pants': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1882877&cp=2048081&ab=ln_baby_cs_shoes': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2249349&cp=2048081&ab=ln_baby_cs_dresses&skirts': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=51185206&cp=2048081&ab=ln_baby_cs_one-pieces': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=2794258&cp=2048081&ab=ln_baby_cs_outfits&giftsets': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1767585&cp=2048081&ab=ln_baby_cs_tops': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1988868&cp=2048081&ab=ln_baby_cs_polos': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=1767586&cp=2048081&ab=ln_baby_cs_pants&leggings': {'gender':'baby', 'product_type': 'mother-kid'},
        'http://www.ralphlauren.com/family/index.jsp?categoryId=3117307&cp=2048081&ab=ln_baby_cs_shoes': {'gender':'baby', 'product_type': 'mother-kid'},
    }

    base_url = 'http://www.ralphlauren.com'

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)
        req_url = response.url#re.sub('&pg=\w', '', response.url)

        response_meta_keys = response.meta.keys()
        if 'product_type' not in response_meta_keys or 'category' not in response_meta_keys or 'gender' not in response_meta_keys:

            if req_url not in self.url_gender_type.keys():
                return

            gender = self.url_gender_type[req_url]['gender']
            product_type = self.url_gender_type[req_url]['product_type']

            if 'category' not in self.url_gender_type[req_url].keys():
                if sel.xpath('//a[contains(@class, "leftnavselected")]'):
                    category = sel.xpath('//a[contains(@class, "leftnavselected")]/text()').extract()[0]
                elif req_url == 'http://www.ralphlauren.com/family/index.jsp?categoryId=46098226':
                    category = 'belts'
                else:
                    print req_url
                    return
            else:
                category = self.url_gender_type[req_url]['category']
        else:
            product_type = response.meta['product_type']
            category = response.meta['category']
            gender = response.meta['gender']

        '''
        #for test
        #url = 'http://www.ralphlauren.com/product/index.jsp?productId=62615116'
        #url = 'http://www.ralphlauren.com/product/index.jsp?productId=29102986'
        #url = 'http://www.ralphlauren.com/product/index.jsp?productId=42330166'
        url = 'http://www.ralphlauren.com/product/index.jsp?productId=4389361'
        item = BaseItem()
        item['from_site'] = 'ralphlauren'
        item['url'] = url
        item['cover'] = 'cover'
        item['gender'] = 'gender'
        item['product_type'] = 'product_type'
        item['category'] = 'category'
        yield Request(url, callback = self.parse_item, meta = { 'item':item } )
        '''


        uri_head_lis = sel.xpath('//ol[contains(@class, "products")]//li[contains(@id, "product-")]')
        for li in uri_head_lis:
            url = self.base_url + li.xpath('.//a/@href').extract()[0]
            cover = li.xpath('.//div[contains(@class, "product-photo")]//div[1]//a//img/@src').extract()[0]

            item = BaseItem()
            item['from_site'] = 'ralphlauren'
            item['url'] = url
            item['cover'] = cover
            item['gender'] = gender
            item['product_type'] = product_type
            item['category'] = category
            yield Request(url, callback = self.parse_item, meta = { 'item':item } )

        if sel.xpath('//a[contains(@class, "results next-page")]'):
            next_url = sel.xpath('//a[contains(@class, "results next-page")]/@href').extract()[0]
            real_next_url = '%s%s' % (self.base_url, next_url.replace('..', ''))
            yield Request(real_next_url, callback = self.parse, meta={'product_type': product_type, 'category': category, 'gender': gender})



    #item
    def parse_item(self, response):
        item = response.meta['item']

        return self.handle_parse_item(response, item)


    def handle_parse_item(self, response, item):
        sel = Selector(response)

        if not sel.xpath('//h1[contains(@class, "prod-title")]'):
            print get_base_url(response)
            return

        if sel.xpath('//font[@class="prodError"]'):
            return

        show_product_id = sel.xpath('//span[contains(@class, "style-num")]/text()').extract()[0]
        baseItem = item
        baseItem['type'] = 'base'
        baseItem['url'] = get_base_url(response)
        baseItem['title'] = sel.xpath('//h1[contains(@class, "prod-title")]/text()').extract()[0]
        baseItem['cover'] = item['cover']

        if sel.xpath('//span[contains(@itemprop, "offers")]//span[contains(@class, "sale-price")]'):
            if sel.xpath('//span[contains(@itemprop, "offers")]//span[contains(@class, "sale-price")]//span[2]'):
                baseItem['current_price'] = sel.xpath('//span[contains(@itemprop, "offers")]//span[contains(@class, "sale-price")]//span[2]/text()').extract()[0]
            else:
                baseItem['current_price'] = sel.xpath('//span[contains(@itemprop, "offers")]//span[contains(@class, "sale-price")]//span/text()').extract()[0]
        elif sel.xpath('//span[contains(@class, "reg-price")]//span[contains(@itemprop, "price")]'):
            #baseItem['current_price'] = sel.xpath('//span[contains(@itemprop, "price")]/text()').extract()[0]
            baseItem['current_price'] = sel.xpath('//span[contains(@class, "reg-price")]//span[contains(@itemprop, "price")]/text()').extract()[0]
        elif sel.xpath('//span[contains(@class, "reg-price")]//span[contains(@itemprop, "highPrice")]'):
            baseItem['current_price'] = sel.xpath('//span[contains(@class, "reg-price")]//span[contains(@itemprop, "highPrice")]/text()').extract()[0]
        else :
            return

        if sel.xpath('//span[contains(@class, "reg-price is-sale")]'):
            list_pri = sel.xpath('//span[contains(@class, "reg-price is-sale")]/text()').extract()[0]
            if list_pri.find('-') == -1:
                baseItem['list_price'] = list_pri
            else:
                baseItem['list_price'] = list_pri.split("-")[1]

        else:
            baseItem['list_price'] = baseItem['current_price']

        baseItem['show_product_id'] = show_product_id
        baseItem['desc'] = sel.xpath('//div[contains(@class, "detail")]//ul').extract()[0]
        baseItem['brand'] = 'Ralph Lauren'
        baseItem['from_site'] = 'ralphlauren'
        baseItem['product_type'] = item['product_type']
        baseItem['category'] = item['category']
        #baseItem['sub_category'] =
        baseItem['gender'] = item['gender']

        if sel.xpath('//a[contains(@id, "sizechart")]'):
            baseItem['size_info'] = '%s%s' % (self.base_url, sel.xpath('//a[contains(@id, "sizechart")]/@href').extract()[0] )
        else:
            baseItem['size_info'] = ''

        #jsStr = ",".join(re.findall(r'itemMap.*[\s]=[\s]*({[^}]+}[\s]*);', response.body))

        ####
        jsStr2 = "".join(re.findall(r'<script>[\s]*(var isTablet.*;)[\s]*</script>[\s]*<div class="prod-utility">', response.body, re.S))
        strinfo = re.compile('var isTablet.*;')
        imgStr = strinfo.sub('var altImages = new Array();var Scene7Map = new Array();', jsStr2)
        #print imgStr
        context2 = execjs.compile('''
            %s
            function getImages(){
                return orderedImageMap_0;
            }
            function getImages2(){
                var imageArr = new Array()
                for (i in altImages){
                    for (j in altImages[i]) {
                        altImages[i][j]["cId"] = i
                    }
                    imageArr.push(altImages[i])
                }
                return imageArr;
            }
            function getScene7Map(){
                var Scene7Maps = new Array();
                var cIds = new Array();
                for (i in Scene7Map){
                    if (i.toString().indexOf("c") != -1 ){
                        cId = i.toString().substr(1, i.length-1)
                        cIds.push(cId)
                    }
                }

                for (ii in Scene7Map){
                    for (jj in cIds) {
                        s7Index = "s7" + cIds[jj]
                        if (ii == s7Index) {
                            Scene7Maps.push({ "cId":cIds[jj], "cValue":Scene7Map[ii]})
                        }

                    }
                }
                return Scene7Maps
            }
        ''' % imgStr.decode('cp1252').encode('utf-8') )

        getImages = context2.call('getImages')
        getImages2 = context2.call('getImages2')
        Scene7Map = context2.call('getScene7Map')

        imgsArr = []
        for imgTmp in getImages:
            imgsArr_tmp = []

            #replace pic
            for STmp in Scene7Map:
                if STmp['cId'] == imgTmp['cId']:
                    imgTmp['v400'] = 'http://s7d2.scene7.com/is/image/PoloGSI/%s?$flyout_main$&cropN=0.12,0,0.7993,1&iv=fLNd_3&wid=1410&hei=1770&fit=fit,1' % (STmp['cValue'])
            imgsArr_tmp.append({"image":imgTmp['v400'],  "thumbnail": imgTmp['x50']})

            #video
            if 'vid' in imgTmp.keys():
                item['media_url'] = 'http://s7d2.scene7.com/is/content/PoloGSI/' + imgTmp['vid']

            for imgTmp2 in getImages2:
                for imgTmp22 in imgTmp2:
                    if imgTmp['cId'] == imgTmp22['cId']:
                        if imgTmp22['t940'] == '' and imgTmp22['x50'] != '':
                            imgTmp22['t940'] = imgTmp22['x50'].replace('_t50','_t940')
                        elif imgTmp22['t940'] != '' and imgTmp22['x50'] == '':
                            imgTmp22['x50'] = imgTmp22['t940'].replace('_t940','_t50')
                        imgsArr_tmp.append({"image":imgTmp22['t940'],  "thumbnail": imgTmp22['x50']})

            imgsArr.append( {"cId": imgTmp['cId'], "pics": imgsArr_tmp} )

        color_col = sel.xpath('//ul[contains(@id, "color-swatches")]//li')
        for colors in color_col:
            color_id = colors.xpath('./@data-value').extract()[0]
            cover = colors.xpath('.//img/@src').extract()[0]
            name = colors.xpath('.//img/@title').extract()[0]

            images = []
            for img in imgsArr:
                if img['cId'] == color_id:
                    images = img['pics']

            color = Color()
            color['type'] = 'color'
            color['show_product_id'] = show_product_id
            color['from_site'] = 'ralphlauren'
            color['cover'] = cover
            color['images'] = images
            color['name'] = name
            yield color


        ####
        jsStr1 = "".join(re.findall(r'<script>[\s]*(var itemMap.*;)[\s]*</script>[\s]*<!--previousURL', response.body, re.S))
        context1 = execjs.compile('''
            %s
            function getItemMaps(){
                return itemMap;
            }
        ''' % jsStr1.decode('cp1252').encode('utf-8'))


        skus = []
        sizes = []
        colors = []
        getItemMaps = context1.call('getItemMaps')
        for ItemMaps in getItemMaps:
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = show_product_id
            skuItem['from_site'] = 'ralphlauren'
            #skuItem['id'] = show_product_id + '-' +ItemMaps['sDesc']
            skuItem['id'] = ItemMaps['sku']
            skuItem['list_price'] = baseItem['list_price']
            skuItem['current_price'] = ItemMaps['price']
            skuItem['size'] = ItemMaps['sDesc']
            skuItem['color'] = ItemMaps['cDesc']
            if ItemMaps['avail'] == "OUT_OF_STOCK":
                skuItem['is_outof_stock'] = True
            else:
                skuItem['is_outof_stock'] = False
            skuItem['quantity'] = ItemMaps['quantityOnHand']
            sizes.append(ItemMaps['sDesc'])
            skus.append(skuItem)
            colors.append(ItemMaps['cDesc'])

        baseItem['skus'] = skus
        baseItem['sizes'] = list(set(sizes))
        baseItem['colors'] = list(set(colors))

        yield baseItem

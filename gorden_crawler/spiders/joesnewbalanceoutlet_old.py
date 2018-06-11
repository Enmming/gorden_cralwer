# -*- coding: utf-8 -*-
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
import re
import execjs
from gorden_crawler.spiders.shiji_base import BaseSpider
import math

class JoesnewbalanceoutletBaseSpider(object):
    
    name = 'joesnewbalanceoutlet'
    
    base_url = 'http://www.joesnewbalanceoutlet.com/'
    
    def handle_parse_item(self, response, item):
        
        sel = Selector(response)
        
        addToCardFrom = sel.xpath('//form[@name="addToCart"]').extract()
        
        if len(addToCardFrom) == 0:
            return
        else:
            if re.search(r'SOLD OUT',addToCardFrom[0]):
                return
        
        if 'list_price' not in item.keys():
            price_p = sel.xpath('//div[1]/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/table[1]/tr/td[1]/table/tr/td/p[last()]')
            
            current_price = price_p.xpath('font[1]/text()').re(r'Now:\s*\$([\d.]+)')
            
            if len(current_price) > 0:
                current_price = current_price[0]
            else:
                if len(price_p.xpath('font[1]/text()').re(r'Sale:\s*\$([\d.]+)')) > 0:
                    current_price = price_p.xpath('font[1]/text()').re(r'Sale:\s*\$([\d\.]+)')[0]
                else:
                    current_price = sel.xpath('//div[1]/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/table[1]/tr/td[1]/table/tr/td/font[1]/text()').extract()[0]
                    if 'Sale:' in current_price:
                        current_price = current_price.replace('Sale:', '')
                    elif 'Today:' in current_price:
                        current_price = current_price.replace('Today:', '')

            list_price_p = price_p.xpath('font[@class="strike"]/font/text()').extract()
            
            if len(list_price_p) > 0:
                list_price = list_price_p[0].strip()
            else:
                price_p_html = price_p.extract()[0]
                list_price_match = re.search(r'Orig:\s*\$([\d\.]+)', price_p_html)
                if list_price_match is None:
                    list_price = sel.xpath('//div[1]/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/table[1]/tr/td[1]/table/tr/td/font[2]/text()').re(r'Orig:\s*\$([\d\.]+)')[0]
                else:    
                    list_price = re.search(r'Orig:\s*\$([\d\.]+)', price_p_html).group(1).strip()

            
            item['list_price'] = list_price
            item['current_price'] = current_price
        
        brand = sel.xpath('//div/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/table[1]/tr/td[1]/table/tr/td/div/a/text()')
        if len(brand) > 0:
            brand = brand.re(r'About the\s*(.+)\s+Brand$')[0]
        else:
            brand = 'New Balance'
        
        description = sel.xpath('//div[1]/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/div[1]/table/tr[1]/td/text()').extract()
        
        if len(description) > 0 :
            description = '<div>' + description[0] + '</div>'
        elif len(sel.xpath('//div[1]/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/div[1]/table/tr[1]/td/p/text()').extract()) > 0:
            description = '<div>' + sel.xpath('//div[1]/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/div[1]/table/tr[1]/td/p/text()').extract()[0] + '</div>'
        else:
            description = ''
        
        description2 = sel.xpath('//div[1]/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/div[2]/table/tr[1]/td/ul').extract()
        
        if len(description2) > 0:
            description = '<div>' + description2[0] + '</div>'
        
        if len(description) == 0:
            description = '暂无'
        
        style_category_font = sel.xpath('//div[1]/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/table[1]/tr/td[1]/table/tr/td/p[1]/font[last()]/text()')
        show_product_id = style_category_font.re(r'Style:\s*(.+)')[0]
        category = style_category_font.extract()[1]
        
        select_options = sel.xpath('//div[1]/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/table[1]/tr/td[3]/form/table[1]/tr[2]/td/select/option')
        
        sizes = []
        skus = []
        for select_option in select_options:
            if select_option.xpath('@value').extract_first() == 'select':
                continue
            
            size = select_option.xpath('text()').extract_first()
            size = size.replace(u'\xa0', '').encode('utf-8')
            
            sku_item = SkuItem()
            
            id = select_option.xpath('@value')
            if len(id) > 0:
                id = id.extract()[0]
            else:
                id = size
            
            sku_item['type'] = 'sku'
            sku_item['show_product_id'] = show_product_id
            sku_item['from_site'] = item['from_site']
            sku_item['id'] = id
            sku_item['list_price'] = item['list_price']
            sku_item['current_price'] = item['current_price']
            sku_item['size'] = size
            sku_item['color'] = 'onecolor'
            sku_item['is_outof_stock'] = False
            
            sizes.append(size)
            skus.append(sku_item)
            
        item['skus'] = skus
        item['sizes'] = {'size': sizes}
        item['dimensions'] = ['size']
        item['colors'] = ['onecolor']

        item['brand'] = brand
        item['desc'] = description
        item['show_product_id'] = show_product_id
        if 'category' not in item.keys():
            item['category'] = category 
        
        yield item
        
        color_url = self.base_url + 'larger_view.asp?style=' + show_product_id
        
        yield Request(color_url, callback=self.parse_color, meta={'item': item})

    def parse_color(self, response):
        
        item = response.meta['item']
        
        sel = Selector(response)
        
        color_images = sel.xpath('//div[@id="largerViewContainer"]/table[3]/tr[2]/td/a')
        
        images = []
        
        cover = ''
        
        if len(color_images) > 0:
            for color_image in color_images:
                image_id = color_image.xpath('@onmouseover').re(r'AltView\(\'([\d]+)\'\,')[0]
    
                thumbnail = self.base_url.strip('/') + color_image.xpath('img/@src').extract()[0]
                
                if image_id == '0':
                    image = self.base_url + 'products/' + item['show_product_id'] + '_xl.jpg'
                    cover = thumbnail
                else:
                    image = self.base_url + 'products/alt_views/' + item['show_product_id'] + '_alt' + image_id + '.jpg';
    
                images.append({
                    'image': image,
                    'thumbnail': thumbnail
                }) 
        else:
            images = [{
                'image': self.base_url + 'products/' + item['show_product_id'] + '_xl.jpg',
                'thumbnail': self.base_url + 'products/' + item['show_product_id'] + '_xs.jpg'
            }]
            cover = self.base_url + 'products/' + item['show_product_id'] + '_xs.jpg'
            
        image_item = Color()
        
        image_item['show_product_id'] = item['show_product_id']
        image_item['from_site'] = item['from_site']
        image_item['type'] = 'color'
        image_item['cover'] = cover
        image_item['name'] = 'onecolor'
        image_item['images'] = images
           
        yield image_item
    

class JoesnewbalanceoutletSpider(BaseSpider, JoesnewbalanceoutletBaseSpider):
#class zappoSpider(RedisSpider):
    # name = "joesnewbalanceoutlet"
    allowed_domains = ["joesnewbalanceoutlet.com"]
    
    '''
    正式运行的时候，start_urls为空，通过传参数来进行，通过传递参数 -a 处理
    '''


    custom_settings = {
        # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'RETRY_TIMES': 10,
        'DOWNLOAD_TIMEOUT': 200
    }

    start_urls = (
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wrun',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wwalk',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wx',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wretro',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=woutdoor',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wcourt',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wcasual&subcat=casuals',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wcasual&subcat=dress',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wcasual&subcat=slipon',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wcasual&subcat=boots',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wsandals',
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wteam',
        
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wtops&subcat=long%20sleeve',
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wtops&subcat=short%20sleeve',
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wtops&subcat=sleeveless',
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wcas&subcat=long%20sleeve',
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wcas&subcat=short%20sleeve',
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wcas&subcat=sleeveless',
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wjv',
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wshorts&subcat=shorts',
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wshorts&subcat=skirts',
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wpt',
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wsb',
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wanue',
        
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mrun',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mwalk',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mx',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mretro',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=moutdoor',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mteam',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mcourt',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mgolf',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mcasual&subcat=casuals',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mcasual&subcat=dress',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mcasual&subcat=slipon',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mcasual&subcat=boots',
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=msandals',
        
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mtops&subcat=long%20sleeve',
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mtops&subcat=short%20sleeve',
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mtops&subcat=sleeveless',
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mcas&subcat=long%20sleeve',
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mcas&subcat=short%20sleeve',
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mshorts',
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mpt',
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mjv',
        
        'http://www.joesnewbalanceoutlet.com/cat_kid_shoes.htm?category=kids&subcat=boys', 
        'http://www.joesnewbalanceoutlet.com/cat_kid_shoes.htm?category=kids&subcat=girls',
        'http://www.joesnewbalanceoutlet.com/cat_kid_shoes.htm?category=pre&subcat=boys',
        'http://www.joesnewbalanceoutlet.com/cat_kid_shoes.htm?category=pre&subcat=girls',
        'http://www.joesnewbalanceoutlet.com/cat_kid_shoes.htm?category=infant'
    )
    
    url_genger_product_type_map = {
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm': {'gender': 'women', 'product_type': 'shoes', 'prefix': "Women's"},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm': {'gender': 'women', 'product_type': 'shoes', 'prefix': "Men's"},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wrun': {'gender': 'women', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wwalk': {'gender': 'women', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wx': {'gender': 'women', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wretro': {'gender': 'women', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=woutdoor': {'gender': 'women', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wcourt': {'gender': 'women', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wcasual&subcat=casuals': {'gender': 'women', 'product_type': 'shoes', 'category': 'Casuals'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wcasual&subcat=dress': {'gender': 'women', 'product_type': 'shoes', 'category': 'Dress'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wcasual&subcat=slipon': {'gender': 'women', 'product_type': 'shoes', 'category': 'Slip-On'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wcasual&subcat=boots': {'gender': 'women', 'product_type': 'shoes', 'category': 'Boots'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wsandals': {'gender': 'women', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_shoes.htm?category=wteam': {'gender': 'women', 'product_type': 'shoes'},
        
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wtops&subcat=long%20sleeve': {'gender': 'women', 'product_type': 'Apparel', 'category': 'Performance Tops Long Sleeve'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wtops&subcat=short%20sleeve': {'gender': 'women', 'product_type': 'Apparel', 'category': 'Performance Tops Short Sleeve'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wtops&subcat=sleeveless': {'gender': 'women', 'product_type': 'Apparel', 'category': 'Performance Tops Sleeveless'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wcas&subcat=long%20sleeve': {'gender': 'women', 'product_type': 'Apparel', 'category': 'Casual Tops Long Sleeve'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wcas&subcat=short%20sleeve': {'gender': 'women', 'product_type': 'Apparel', 'category': 'Casual Tops Short Sleeve'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wcas&subcat=sleeveless': {'gender': 'women', 'product_type': 'Apparel', 'category': 'Casual Tops Sleeveless'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wjv': {'gender': 'women', 'product_type': 'Apparel'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wshorts&subcat=shorts': {'gender': 'women', 'product_type': 'Apparel', 'category': 'Shorts'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wshorts&subcat=skirts': {'gender': 'women', 'product_type': 'Apparel', 'category': 'Skirts'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wpt': {'gender': 'women', 'product_type': 'Apparel'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wsb': {'gender': 'women', 'product_type': 'Apparel'},
        'http://www.joesnewbalanceoutlet.com/cat_womens_apparel.htm?category=app_wanue': {'gender': 'women', 'product_type': 'Apparel'},
        
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mrun': {'gender': 'men', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mwalk': {'gender': 'men', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mx': {'gender': 'men', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mretro': {'gender': 'men', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=moutdoor': {'gender': 'men', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mteam': {'gender': 'men', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mcourt': {'gender': 'men', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mgolf': {'gender': 'men', 'product_type': 'shoes'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mcasual&subcat=casuals': {'gender': 'men', 'product_type': 'shoes', 'category': 'Casuals'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mcasual&subcat=dress': {'gender': 'men', 'product_type': 'shoes', 'category': 'Dress'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mcasual&subcat=slipon': {'gender': 'men', 'product_type': 'shoes', 'category': 'Slip-On'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=mcasual&subcat=boots': {'gender': 'men', 'product_type': 'shoes', 'category': 'Boots'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_shoes.htm?category=msandals': {'gender': 'men', 'product_type': 'shoes'},
        
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mtops&subcat=long%20sleeve': {'gender': 'men', 'product_type': 'Apparel', 'category': 'Performance Tops Long Sleeve'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mtops&subcat=short%20sleeve': {'gender': 'men', 'product_type': 'Apparel', 'category': 'Performance Tops Short Sleeve'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mtops&subcat=sleeveless': {'gender': 'men', 'product_type': 'Apparel', 'category': 'Performance Tops Sleeveless'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mcas&subcat=long%20sleeve': {'gender': 'men', 'product_type': 'Apparel', 'category': 'Casual Tops Long Sleeve'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mcas&subcat=short%20sleeve': {'gender': 'men', 'product_type': 'Apparel', 'category': 'Casual Tops Short Sleeve'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mshorts': {'gender': 'men', 'product_type': 'Apparel'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mpt': {'gender': 'men', 'product_type': 'Apparel'},
        'http://www.joesnewbalanceoutlet.com/cat_mens_apparel.htm?category=app_mjv': {'gender': 'men', 'product_type': 'Apparel'},
        
        'http://www.joesnewbalanceoutlet.com/cat_kid_shoes.htm?category=kids&subcat=boys': {'gender': 'boys', 'product_type': 'shoes', 'category': 'Grade School'}, 
        'http://www.joesnewbalanceoutlet.com/cat_kid_shoes.htm?category=kids&subcat=girls': {'gender': 'girls', 'product_type': 'shoes', 'category': 'Grade School'},
        'http://www.joesnewbalanceoutlet.com/cat_kid_shoes.htm?category=pre&subcat=boys': {'gender': 'boys', 'product_type': 'shoes', 'category': 'Pre School'},
        'http://www.joesnewbalanceoutlet.com/cat_kid_shoes.htm?category=pre&subcat=girls': {'gender': 'girls', 'product_type': 'shoes', 'category': 'Pre School'},
        'http://www.joesnewbalanceoutlet.com/cat_kid_shoes.htm?category=infant': {'gender': 'baby', 'product_type': 'shoes'}
        
    }
    
    base_url = 'http://www.joesnewbalanceoutlet.com/'

    

    '''具体的解析规则'''
    def parse_item(self, response):
        
#         item = BaseItem()
#         item['type'] = 'base'
#         item['show_product_id'] = '1209118'
        item = response.meta['item']
        
        return self.handle_parse_item(response, item)
     
    def handle_parse_item(self, response, item):
        return JoesnewbalanceoutletBaseSpider.handle_parse_item(self, response, item) 
      
    '''
    爬虫解析入口函数，用于解析丢入的第一个请求，一般是顶级目录页
    '''
    def parse(self, response):
        
        sel = Selector(response)
        
        meta_keys = response.meta.keys()
        
        current_url = response.url
        
        if 'gender' in meta_keys and 'product_type' in meta_keys:
            gender = response.meta['gender']
            product_type = response.meta['product_type']
        elif current_url in self.url_genger_product_type_map.keys():
            gender = self.url_genger_product_type_map[current_url]['gender']
            product_type = self.url_genger_product_type_map[current_url]['product_type']
        else:
            print current_url + ' missing'
        
        table_num = 4
        
        for table_num in range(4, 8):
            row = sel.xpath('//div[1]/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/table[' + str(table_num) +']')
        
            if len(row) > 0:
                if len(row.xpath('tr')) > 1:
                    break
                
                item_tables = row.xpath('tr/td/table')
                
                for item_table in item_tables:
                    td_a = item_table.xpath('tr[1]/td/table/tr/td/a')
                    url = self.base_url + td_a.xpath('@href').extract()[0]
                    cover = self.base_url + td_a.xpath('img/@src').extract()[0]
                    
                    title = item_table.xpath('tr[2]/td/a/text()').extract()[0]
                    
                    current_price = item_table.xpath('tr[2]/td/font[@class="price"]/text()').re(r'Now:\s*\$([\d.]+)')
                    if len(current_price) > 0:
                        current_price = current_price[0]
                    else:
                        current_price = item_table.xpath('tr[2]/td/font[@class="price"]/text()').re(r'Sale:\s*\$([\d.]+)')[0]
                    
                    list_price = item_table.xpath('tr[2]/td/font[@class="price"]/following-sibling::*').re(r'Orig:\s*\$([\d.]+)')[0]
                    
                    item = BaseItem()
                    item['type'] = 'base'
                    item['from_site'] = 'joesnewbalanceoutlet'#self.name
                    item['title'] = title
                    item['url'] = url
                    item['cover'] = cover
                    item['current_price'] = current_price
                    item['list_price'] = list_price
                    item['gender'] = gender
                    item['product_type'] = product_type
                    
                    yield Request(url, callback=self.parse_item, meta={'item': item})
            else:
                break
        
        next_page = sel.xpath('//div[1]/div/div/table/tr[2]/td/table[3]/tr/td[2]/table[3]/tr/td[2]/table[last()]/tr[2]/td[3]/strong/a/@href').extract()
        
        if len(next_page) > 0:
            
            next_uri = next_page[0]
            
            next_url = self.base_url + next_uri
            
            yield Request(next_url, callback=self.parse, meta={'gender': gender, 'product_type': product_type})

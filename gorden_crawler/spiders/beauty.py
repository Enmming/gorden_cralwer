# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy import Request
import re
from gorden_crawler.spiders.shiji_base import BaseSpider
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color

class BeautySpider(BaseSpider):
    name = "beauty"
    
    base_url = "http://www.beauty.com"
    
    allowed_domains = ["beauty.com"]
    start_urls = [
#           'http://www.beauty.com/skin-care/face/qxg298231-0'
        'http://www.beauty.com/skin-care/qxg12873-0',
        'http://www.beauty.com/makeup/qxg12871-0',
        'http://www.beauty.com/fragrance/qxg12872-0',
        'http://www.beauty.com/bath-body/qxg12874-0',
        'http://www.beauty.com/hair-care/qxg12875-0'
    ]

    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_TIMEOUT': 180,
        #'DOWNLOAD_DELAY': 0.25,
    }

    #product_type is category actually
    product_type_url_mapping = {
        'http://www.beauty.com/skin-care/qxg12873-0' : {'product_type' : 'skin-care'},
        'http://www.beauty.com/makeup/qxg12871-0' : {'product_type' : 'makeup'},
        'http://www.beauty.com/fragrance/qxg12872-0' : {'product_type' : 'fragrance'},
        'http://www.beauty.com/bath-body/qxg12874-0' : {'product_type' : 'bath-body'},
        'http://www.beauty.com/hair-care/qxg12875-0' : {'product_type' : 'hair-care'}
       }

    def parse(self, response):
        product_type = self.product_type_url_mapping[response.url]['product_type']
        sel = Selector(response)
        category_a_list = sel.xpath('//div[@id="Categories-collapse"]//a')
        
        for category_a in category_a_list:
            category_url = self.base_url + category_a.xpath('./@href').extract()[0]
            temp_product_type =product_type +'*'+ category_a.xpath('./h2/text()').extract()[0]
#             if category == 'ULTIMATE SALE':
#                 category = 'tools-and-accessories'
            yield Request(category_url, callback=self.parse_category, meta={'product_type': temp_product_type})

    def parse_category(self, response):
        # import pdb;pdb.set_trace()
        sel = Selector(response)
        response_url = response.url
        # product_type = response.meta['product_type']
        product_type = response.meta['product_type']

        category_lis = sel.xpath('//div[@id="Categories-collapse"]//li')
        for category_li in category_lis:
            url = self.base_url + category_li.xpath('./a/@href').extract()[0]
            category = category_li.xpath('./a/h2/text()').extract()[0]
            yield Request(url, callback=self.parse_category_next, meta={'product_type': product_type, 'category': category})

    def parse_category_next(self, response):
        product_type = response.meta['product_type']
        category = response.meta['category']

        sel = Selector(response)

        if 'For Men' in product_type:
            gender = 'men'
        else:
            gender = 'women'
        
        product_divs = sel.xpath('//div[@class="flex-box-3 item"]/div[contains(@class,"itemGridbty")]')
        for product_div in product_divs:
            baseItem = BaseItem()
            baseItem['type'] = 'base'
            baseItem['from_site'] = self.name
            baseItem['product_type'] = product_type
            baseItem['category'] = category
            baseItem['gender'] = gender
            
            url = self.base_url + product_div.xpath('.//a[@class="oesLink"]/@href').extract()[0]
            baseItem['url'] = url 
            baseItem['cover'] = product_div.xpath('.//img/@src').extract()[0]
            brand_title_span = product_div.xpath('.//a[@class="oesLink"]/span/text()').extract()
            baseItem['brand'] = brand_title_span[0]
            baseItem['title'] = brand_title_span[1]
            current_price = product_div.xpath('.//td[@id="priceTd"]//span[@itemprop="price"]/text()')
            if len(current_price) > 0:
                baseItem['current_price'] = current_price.extract()[0]
            else:
                baseItem['current_price'] = product_div.xpath('.//td[@id="priceTd"]//span[@itemprop="highPrice"]/text()').extract()[0]
            list_price = product_div.xpath('.//td[@id="priceTd"]//span[@itemprop="PListRegularPrice"]/text()')
            if len(list_price) > 0:
                list_price_num = list_price.extract()[0]
                m = re.search(r'$\d+\.\d+', list_price_num)
                if m:
                    baseItem['list_price'] = m.group(0)
            else:
                baseItem['list_price'] = baseItem['current_price']
            show_product_id = product_div.xpath('./div')[-1].xpath('./@id').extract()[0]
            m = re.search(r'\d+', show_product_id)
            if m:
                baseItem['show_product_id'] = m.group(0)
   
            yield Request(url, callback=self.parse_item, meta={'baseItem': baseItem})

        next_page = sel.xpath('//div[@class="paginationDiv"]//a[@class="nextpage"]')
        if len(next_page) > 0:
            
            next_page_url = self.base_url + next_page.xpath('@href').extract()[0]
            
            # print sel.xpath('//div[@class="paginationDiv"]//div[@class="PaginationActiveLink"]/text()').extract()[0]
            # import pdb;pdb.set_trace()
            yield Request(next_page_url, callback=self.parse_category_next, meta={'product_type' : product_type, 'category': category})

#         max_page = sel.xpath('//div[contains(@class, "PaginationInactiveLink")]/a/text()')
#         if len(max_page) > 0:
#             max_page_num = int(max_page.extract()[0])
#             active_link_num = int(sel.xpath('//div[contains(@class, "PaginationActiveLink")]/text()').extract()[0])
#             if active_link_num == 1:
#                 to_crawled_page = 2
#             else:
#                 to_crawled_page = response.meta['to_crawled_page']
#                 to_crawled_page = to_crawled_page + 1
#             if to_crawled_page <= max_page_num:
#                 m = re.search(r'catid=\d{6}', response.body)
#                 if m :
#                     catid = m.group(0)
#                     index = (to_crawled_page - 1) * 18
#                     page_uri_suffix = '/templates/gn/default.asp?Nao=' + str(index) + '&' + str(catid) + '&ipp=18'
#                     to_crawled_page_url = self.base_url + page_uri_suffix
#                     yield Request(to_crawled_page_url, callback=self.parse_category, meta={'to_crawled_page' : to_crawled_page, 'product_type' : product_type, 'category' : category})

    def parse_item(self, response):
        baseItem = response.meta['baseItem']
        return self.handle_parse_item(response, baseItem)

    def parse_color_item(self, response):
        sel = Selector(response)
        
        index = response.meta['index']
        color_urls = response.meta['color_urls']
        baseItem = response.meta['baseItem']
        
        colorItem = Color()
        colorItem['type'] = 'color'
        colorItem['show_product_id'] = baseItem['show_product_id']
        colorItem['from_site'] = self.name
        colorItem['name'] = color_urls[index]['color_name']
        colorItem['cover'] = color_urls[index]['color_cover']
        
        images = []
        
        imageItem = ImageItem()
        image_url = sel.xpath('//meta[@property="og:image"]/@content').extract()[0]
            
        imageItem['image'] = re.sub(r'wid=\d+&hei=\d+', 'wid=1000&hei=1000', image_url)
        imageItem['thumbnail'] = re.sub(r'wid=\d+&hei=\d+', 'wid=50&hei=50', image_url)
        
        images.append(imageItem)
        
        image_url2 = sel.xpath('//div[@id="productSwatch"]/img/@src').extract()[0]

        imageItem = ImageItem()
        imageItem['image'] = re.sub(r'wid=\d+&hei=\d+', 'wid=1000&hei=1000', image_url2)
        imageItem['thumbnail'] = re.sub(r'wid=\d+&hei=\d+', 'wid=50&hei=50', image_url2)
        
        images.append(imageItem)
        
        colorItem['images'] = images
            
        yield colorItem
        
        skus = response.meta['skus']
        skuItem = SkuItem()
        skuItem['type'] = 'sku'
        skuItem['show_product_id'] = baseItem['show_product_id']
        skuItem['from_site'] = self.name
        skuItem['current_price'] = sel.xpath('//div[@class="prodprice saleprice"]/p/span[@itemprop="price"]/text()').extract()[0]
        if len(sel.xpath('//div[@class="prodprice saleprice"]/p/span[@class="basePrice"]/text()').extract()) > 0:
            skuItem['list_price'] = sel.xpath('//div[@class="prodprice saleprice"]/p/span[@class="basePrice"]/text()').extract()[0]
        else:
            skuItem['list_price'] = skuItem['current_price']
        skuItem['is_outof_stock'] = False
        skuItem['color'] = color_urls[index]['color_name']
        skuItem['size'] = 'one-size'
        skuItem['id'] = baseItem['show_product_id']
        skus.append(skuItem)
        
        if index + 1 == len(color_urls):
            baseItem['skus'] = skus
            
            yield baseItem
        else:
            yield Request(color_urls[index+1]['url'], callback=self.parse_color_item
                          , meta={'baseItem': baseItem, 'color_urls': color_urls, 'index': index+1, 'skus': skus})

    def handle_parse_item(self, response, baseItem):
        sel = Selector(response)
        
        if len(sel.xpath('//table[@id="TblProdForkPromo"]/tr').extract()) > 0:
            baseItem['desc'] = '<table>' + sel.xpath('//table[@id="TblProdForkPromo"]/tr').extract()[0] + '</table>'
        else:
            baseItem['desc'] = ''
        
        baseItem['dimensions'] = ['size', 'color']
        baseItem['sizes'] = ['one-size']
         
        color_lis = sel.xpath('//dl[@id="color"]//li')
        
        if len(color_lis) > 0:
            
            color_urls = []
            colors = []
            for color_li in color_lis:
                
                color_item_uri = color_li.xpath('./a/@href').extract()[0]
                color_url = self.base_url + color_item_uri
                
                
                color_name = color_li.xpath('./a/div[@class="distinctionName"]/text()').extract()[0]
                
                colors.append(color_name)
                
                color_cover = color_li.xpath('./a/div/img/@src').extract()[0]
                
                color_urls.append({'url': color_url, 'color_name': color_name, 'color_cover': color_cover})
                
            baseItem['colors'] = colors
            yield Request(color_urls[0]['url'], callback=self.parse_color_item
                          , meta={'baseItem': baseItem, 'color_urls': color_urls, 'index': 0, 'skus': []})
            
        else:  
            baseItem['colors'] = ['one-color']
            
            skus = []
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = baseItem['show_product_id']
            skuItem['from_site'] = self.name
            skuItem['current_price'] = sel.xpath('//div[@class="prodprice saleprice"]/p/span[@itemprop="price"]/text()').extract()[0]
            if len(sel.xpath('//div[@class="prodprice saleprice"]/p/span[@class="basePrice"]/text()').extract()) > 0:
                skuItem['list_price'] = sel.xpath('//div[@class="prodprice saleprice"]/p/span[@class="basePrice"]/text()').extract()[0]
            else:
                skuItem['list_price'] = skuItem['current_price']
            skuItem['is_outof_stock'] = False
            skuItem['color'] = 'one-color'
            skuItem['size'] = 'one-size'
            skuItem['id'] = baseItem['show_product_id']
            skus.append(skuItem)
            imageItem = ImageItem()
            
            image_url = sel.xpath('//meta[@property="og:image"]/@content').extract()[0]
            
            imageItem['image'] = re.sub(r'wid=\d+&hei=\d+', 'wid=1000&hei=1000', image_url)
            imageItem['thumbnail'] = re.sub(r'wid=\d+&hei=\d+', 'wid=50&hei=50', image_url)
    
            images = []
            images.append(imageItem)
    
            colorItem = Color()
            colorItem['type'] = 'color'
            colorItem['show_product_id'] = baseItem['show_product_id']
            colorItem['from_site'] = self.name
            colorItem['images'] = images
            colorItem['name'] = 'one-color'
            colorItem['cover'] = imageItem['thumbnail']
            
            yield colorItem
            baseItem['skus'] = skus
            yield baseItem

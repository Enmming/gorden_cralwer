# -*- coding: utf-8 -*-
from gorden_crawler.spiders.shiji_base import BaseSpider
from scrapy.selector import Selector
from gorden_crawler.items import BaseItem, ImageItem, Color, SkuItem
from scrapy import Request
from gorden_crawler.utils.item_field_handler import handle_price
import re
import execjs
class ShopbopEastdaneCommon(BaseSpider):
    def parse_pages(self, response):
        sel = Selector(response)
        category = response.meta['category']
        product_type = response.meta['product_type']
        gender = response.meta['gender']
        category_url = response.meta['category_url']
        item_link_lis = sel.xpath('//li[contains(@class, "hproduct product")]')
        if len(item_link_lis.extract())>0 :
            for item_link_li in item_link_lis:
                item_link_uri = item_link_li.xpath('./div/a/@href').extract()[0]
                url = self.shopbop_base_url + item_link_uri
                baseItem = BaseItem()
                baseItem['type'] = 'base'
                baseItem['category'] = category
                baseItem['product_type'] = product_type
                baseItem['url'] = url
                baseItem['gender'] = gender
                baseItem['brand'] = item_link_li.xpath('.//div[@class="brand"]/text()').extract()[0]
                baseItem['title'] = item_link_li.xpath('.//div[@class="title"]/text()').extract()[0]
                baseItem['cover'] = item_link_li.xpath('.//img/@src').extract()[0]
                baseItem['list_price'] = handle_price(item_link_li.xpath('.//span[@class="retail-price"]/text()').extract()[0])
                baseItem['current_price'] = handle_price(item_link_li.xpath('.//span[@class="sale-price-low"]/text()').extract()[0])
                yield Request(url, callback=self.parse_item, meta={'baseItem' : baseItem})
        next_page_link = sel.xpath('//span[@data-at="nextPage"]/@data-next-link').extract()
        if len(next_page_link)>0 and (category_url[category] !=  next_page_link[0]):
            url = self.shopbop_base_url + next_page_link[0]
            yield Request(url, callback=self.parse_pages, meta={'category' : category, 'product_type' : product_type, 'gender' : gender, 'category_url' : category_url})

    def parse_item(self, response):
        baseItem = response.meta['baseItem']
        return self.handle_parse_item(response, baseItem)
    
    def handle_parse_item(self, response, baseItem):
        product_detail_str="".join(re.findall(r"var\s+productDetail[^;]+", response.body))
        if len(product_detail_str)>0:
            context = execjs.compile('''
                %s
                function get_product_detail(){
                    return productDetail;
                    }
            ''' % (product_detail_str))
        product_detail = context.call('get_product_detail')
        sel = Selector(response)
        product_id = sel.xpath('//div[@id="productId"]/text()').extract()[0]
        skus = []
        baseItem['from_site'] = self.name
        baseItem['show_product_id'] = product_id
        
        size_js_infos = product_detail['sizes']
        size_infos = {}
        size_values = []
        for size_id in size_js_infos:
            size_infos[size_js_infos[size_id]['sizeCode']] = size_id
            size_values.append(size_id)

        list_price = sel.xpath('//div[@id="productPrices"]//meta[@itemprop="price"]/@content').extract()[0]

        color_price_blocks = sel.xpath('//div[@id="productPrices"]//div[@class="priceBlock"]')
        color_price_mapping = {}
        for color_price_block in color_price_blocks:
            color_name = color_price_block.xpath('./span[@class="priceColors"]/text()').extract()
            
            if len(color_name) > 0:
                regular_price_span = color_price_block.xpath('./span[@class="regularPrice"]/text()').extract()
                if len(regular_price_span) > 0:
                    color_price_mapping[color_name[0]] = regular_price_span[0]
                else:
                    color_price_mapping[color_name[0]] = color_price_block.xpath('./span[@class="salePrice"]/text()').extract()[0]
        
        image_items = product_detail['colors']

        color_names = []
        for key in image_items:
            imageItems = image_items[key]['images']
            color_name = image_items[key]['colorName'].strip()
            
            color_names.append(color_name)
            
            images=[]
            tmp_images = []
            for image_key in imageItems:
                imageItem = ImageItem()
                image = imageItems[image_key]
                
                imageItem['thumbnail'] = image['thumbnail']
                imageItem['image'] = image['zoom']
                
                tmp_images.append((image['index'], imageItem))
                
            tmp_images = sorted(tmp_images, key=lambda x:x[0])

            for tmp_tuple in tmp_images:
                images.append(tmp_tuple[1])
            
            colorItem = Color()
            colorItem['type'] = 'color'
            colorItem['show_product_id'] = product_id
            colorItem['from_site'] = self.name
            colorItem['cover'] = image_items[key]['swatch']
            colorItem['name'] = color_name
            colorItem['images'] = images
            
            yield colorItem
            
            sizes = image_items[key]['sizes']
            
            for size in sizes:
                size_name = size_infos[size]
                
                skuItem = SkuItem()
                skuItem['type'] = 'sku'
                skuItem['from_site'] = self.name
                skuItem['color'] = color_name
                skuItem['show_product_id'] = product_id
                skuItem['id'] = key+"-"+size
                skuItem['size'] = size_name
                skuItem['list_price'] = list_price
                if len(color_price_mapping)>0 and color_name in color_price_mapping.keys():
#                     skuItem['current_price'] = sale_price_span.re(r'\d+.?\d*')[0]
                    skuItem['current_price'] = color_price_mapping[colorItem['name']]
                else:
                    skuItem['current_price'] = skuItem['list_price']
                skuItem['is_outof_stock'] = False
                skus.append(skuItem)

        baseItem['sizes'] = size_values
        baseItem['colors']= color_names
        baseItem['skus'] = skus
        size_fit_container = sel.xpath('//div[@id="sizeFitContainer"]')
        if len(size_fit_container)>0:
            size_fit = size_fit_container.extract()[0]
            baseItem['desc'] = '<div>'+sel.xpath('//div[@itemprop="description"]').extract()[0]+size_fit+"</div>"
        else:
            baseItem['desc'] = sel.xpath('//div[@itemprop="description"]').extract()[0]
        baseItem['dimensions'] = ['size', 'color']
        yield baseItem
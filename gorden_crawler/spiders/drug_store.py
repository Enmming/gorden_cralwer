# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
import re
from gorden_crawler.spiders.shiji_base import BaseSpider
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from unicodedata import category

class DrugStoreSpider(BaseSpider):
#class DrugStoreSpider(Spider):
    name = "drug_store"
    allowed_domains = ["drugstore.com"]
    
    start_urls = [
        'http://www.drugstore.com/medicine-and-health/qxg180610-0',
        'http://www.drugstore.com/personal-care/qxg180627-0',
        'http://www.drugstore.com/vitamins/qxg180672-0',
        'http://www.drugstore.com/diet-and-fitness/qxg180686-0'
    ]
    
    url_gender_product_type_map = {
        'http://www.drugstore.com/medicine-and-health/qxg180610-0' : {'product_type': 'medicine&health'},
        'http://www.drugstore.com/personal-care/qxg180627-0' : {'product_type': 'personal care'},
        'http://www.drugstore.com/vitamins/qxg180672-0' : {'product_type': 'vitamins'},
        'http://www.drugstore.com/diet-and-fitness/qxg180686-0' : {'product_type': 'diet&fitness'},
    }
    
    base_url='http://www.drugstore.com'

    def parse(self, response):
        sel = Selector(response)
        product_type = self.url_gender_product_type_map[response.url]['product_type']
        category_links=sel.xpath('//div[@id="refineBycategory"]/a')
#         import pdb;pdb.set_trace()
        for category_link in category_links:
            category = category_link.xpath('./h2/text()').extract()[0]
            url=self.base_url+category_link.xpath('./@href').extract()[0]
            yield Request(url, callback=self.parse_pages, meta={'product_type': product_type, 'category': category})

    def parse_pages(self, response):
        income_url = response.url
        gender='unisex'
        if income_url == "http://www.drugstore.com/personal-care/mens/qxg286961-0" or income_url == "http://www.drugstore.com/vitamins/for-men/qxg180683-0":
            gender='men'
        elif income_url == "http://www.drugstore.com/vitamins/for-children/qxg180682-0" or income_url == "http://www.drugstore.com/medicine-and-health/childrens-healthcare/qxg180623-0":
            gender="kid-unisex"
        elif income_url == "http://www.drugstore.com/vitamins/for-women/qxg180684-0":
            gender="women"
        sel = Selector(response)
        product_type = response.meta['product_type']
        category = response.meta['category']
        item_list_links=sel.xpath('//div[contains(@class, "itemGrid")]')
        #item_list_links=sel.xpath('//div[@class="prodImg"]')
        #item_list_link 代表一个商品
        if len(item_list_links)>0:
            for item_list_link in item_list_links:
                
                cover_div = item_list_link.xpath('./div[@class="prodImg"]/a/img/@src').extract()
                if len(cover_div) > 0:
                    baseItem=BaseItem()
                    baseItem['gender'] = gender
                    baseItem['product_type'] = product_type
                    baseItem['category'] = category
                    baseItem['cover']=cover_div[0]
                    brand=item_list_link.xpath('./div[@class="info"]//span[@class="name"]/text()')
                    if len(brand)>0:
                        baseItem['brand']=brand.re_first(r'([^-]+)-\s*$').strip()
                    item_list_link_uri=item_list_link.xpath('./div[@class="prodImg"]/a/@href')
                    baseItem['url']=self.base_url+item_list_link_uri.extract()[0]
                    #price_not_on_sale=item_list_link.xpath('./div[@class="pricing"]//span[@class="PlistPrice"]/text()')
                    #if len(price_not_on_sale)>0:
                    #    baseItem['list_price']=price_not_on_sale.extract()[0]
                    #    baseItem['current_price']=baseItem['list_price']
                    #elif len(item_list_link.xpath('./div[@class="pricing"]//span[@class="PlistOfferPrice"]/text()'))>0:
                    #    baseItem['list_price']=item_list_link.xpath('./div[@class="pricing"]//span[@class="PListPriceStrikeOut"]/s/text()').extract()[0]
                    #    baseItem['current_price']=item_list_link.xpath('./div[@class="pricing"]//span[@class="PlistOfferPrice"]/text()').extract()[0]
                    yield Request(baseItem['url'], callback=self.parse_item, meta={'baseItem': baseItem})
            #获取下一页url
            next_page_url=sel.xpath('//a[@class="nextpage"]/@href')
            if len(next_page_url)>0:
                next_page=self.base_url+next_page_url.extract()[0]
                yield Request(next_page, callback=self.parse_pages, meta={'product_type': product_type, 'category': category})
            

    def parse_item(self, response):
        baseItem=response.meta['baseItem']
        return self.handle_parse_item(response, baseItem)
    
    def handle_parse_item(self, response, baseItem):
        sel = Selector(response)
#         bread_crumbs=sel.xpath('//div[@id="divBreadCrumb"]/span')
#         baseItem['product_type']=
#         baseItem['category']=bread_crumbs[2].xpath('./a/text()').extract()[0]
#         import pdb;pdb.set_trace()
        product_id_re_result = re.findall(r'dtmProductId = [^;]+', response.body)
        
        if product_id_re_result and len(product_id_re_result) > 0:
            product_id_str=product_id_re_result[0]
            product_id=re.findall(r'\d+', product_id_str)[0]
            baseItem['show_product_id']=int(product_id)
            #baseItem['sub_category']=bread_crumbs[3].xpath('./a/text()').extract()[0]
            baseItem['type']='base'
            item_in_stock=sel.xpath('//div[@id="divAvailablity"]')
            if len(item_in_stock)>0:
                baseItem['title']=sel.xpath('//div[@id="divCaption"]/h1/text()').extract()[0]
                
                desc_a=sel.xpath('//table[@id="TblProdForkPromo"]//td[@class="contenttd"]').extract()
                desc_b=sel.xpath('//table[@id="TblProdForkWarnings"]//td[@class="contenttd"]').extract()
                if len(desc_a)>0:
                    baseItem['desc']=desc_a[0]
                if len(desc_b)>0:
                    baseItem['desc']=desc_b[0]
                baseItem['colors']=['onecolor']
                baseItem['sizes']=['onesize']
                baseItem['dimensions']=['size', 'color']
                baseItem['from_site']=self.name
    
                imageItem=ImageItem()
                images=[]
                imageItem['thumbnail']=sel.xpath('//div[@id="divPImage"]//img/@src').extract()[0]
                imageItem['image']=re.sub(r'300(\.\w+)', '500\\1', imageItem['thumbnail'])
                images.append(imageItem)
    
                colorItem=Color()
                colorItem['type']='color'
                colorItem['from_site']=self.name
                colorItem['show_product_id']=baseItem['show_product_id']
                colorItem['images']=images
                colorItem['cover']=imageItem['thumbnail']
                colorItem['name']='onecolor'
    #             import pdb;pdb.set_trace()
                yield colorItem
                
                skus=[]
                skuItem=SkuItem()
                skuItem['type']='sku'
                skuItem['show_product_id']=baseItem['show_product_id']
                skuItem['from_site']=self.name
                list_price=sel.xpath('//span[@id="rowMSRP"]')
                if len(list_price)>0:
                    skuItem['list_price']=list_price.xpath('./s/text()').extract()[0]
                    skuItem['current_price']=sel.xpath('//div[@id="productprice"]/span/text()').extract()[0]
                    baseItem['list_price']=skuItem['list_price']
                    baseItem['current_price']=skuItem['current_price']
                else:
                    skuItem['current_price']=sel.xpath('//div[@id="productprice"]/span/text()').extract()[0]
                    skuItem['list_price']=skuItem['current_price']
                    baseItem['list_price']=skuItem['list_price']
                    baseItem['current_price']=skuItem['current_price']
                skuItem['is_outof_stock']=False
                skuItem['color']='onecolor'
                skuItem['id']=baseItem['show_product_id']
                skuItem['size']='onesize'
                skus.append(skuItem)
                baseItem['skus']=skus
            yield baseItem
        

                    
                    
     
        
        
            

        
        
        
       
        

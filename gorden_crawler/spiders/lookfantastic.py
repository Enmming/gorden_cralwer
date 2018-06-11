# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import FormRequest

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from gorden_crawler.spiders.shiji_base import BaseSpider

import re
from ..utils.item_field_handler import handle_no_http
# import execjs
# import json

class BaseLookfantasticSpider(object):
    def handle_parse_item(self,response,item):
        sel = Selector(response)

        soldout_span = sel.xpath('//div[@class="cta-container"]//span[contains(@class, "soldout")]/text()').extract()
        
        if len(soldout_span) > 0:
            return

        # siteObjStr = "".join(re.findall(r'(var siteObj = [\s\S]*exitting = false;)', response.body))

        # context = execjs.compile('''
        #     %s
        #     function getSiteObj(){
        #         return siteObj;
        #     }
        # ''' % siteObjStr)
        
        # tmpStr = json.dumps(context.call('getSiteObj'))
        # siteObj = json.loads(tmpStr)

        # product_id = siteObj['productID']
        # product_title = siteObj['productTitle']
        # product_price = siteObj['productPrice']
        # product_brand = siteObj['productBrand']
        # product_rrp = siteObj['rrp']
        product_id = eval(re.search(r'productID:(.*),', response.body).group(1))
        # product_title = eval(re.search(r'productTitle:(.*),', response.body).group(1))
        product_price = eval(re.search(r'productPrice:(.*),', response.body).group(1))
        product_brand = eval(re.search(r'productBrand:(.*),', response.body).group(1))
        product_rrp = eval(re.search(r'rrp:(.*),', response.body).group(1))

        if len(sel.xpath(".//h1[@itemprop='name']/text()"))>0:
            product_title = sel.xpath(".//h1[@itemprop='name']/text()").extract()[0]
        else:
            current_url = response.url
            product_title = ' '.join(current_url.split('/')[3].split('-'))

        rrp_dr = re.compile(r'<[^>]+>',re.S)
        rrp = rrp_dr.sub('',product_rrp)
        rrp_prices = re.split(r': ',rrp)

        if len(sel.xpath(".//*[@id='health-beauty']//div[@itemprop='description']").extract()) > 0:
            product_desc = sel.xpath(".//*[@id='health-beauty']//div[@itemprop='description']").extract()[0]
        else:
            product_desc = ''

        if product_id:
            item['show_product_id'] = product_id
            item['title'] = product_title
            item['current_price'] = product_price.replace('&#163;','')
            item['list_price'] = rrp_prices[1].replace('&#163;','')
            item['desc'] = product_desc
            item['brand'] = product_brand
            item['dimensions'] = ['size']
            item['sizes'] = ['onesize']
            item['colors'] = ['onecolor']
            if re.findall(r'men',item['brand']):
                item['gender'] = 'men'

        else:
            return

        thumbnails = sel.xpath(".//ul[@class='product-thumbnails nav-items product-large-view-thumbs productImageZoom__thumbs']/li//div[contains(@class, 'product-thumb-box')]/img/@src").extract()
        #thumbnails = sel.xpath(".//div[@class='product-thumb-box']/img/@src").extract()
        # viewimages = sel.xpath(".//div[@class='product-thumb-box']/parent::*/@href").extract() #480*480
        viewimages = sel.xpath(".//ul[@class='product-thumbnails nav-items product-large-view-thumbs productImageZoom__thumbs']/li/a/@href").extract() #600*600
        
        images = []
        color_cover = None
        if len(thumbnails) > 0:
            imgKey = 0
            for imgVal in thumbnails:
                imageItem = ImageItem()
                imageItem['image'] = handle_no_http(viewimages[imgKey].strip())
                imageItem['thumbnail'] = handle_no_http(imgVal)
                
                if not color_cover:
                    color_cover = imageItem['thumbnail']
                    
                images.append(imageItem)
                imgKey += 1

        

        color_form = sel.xpath('//div[@class="variation-dropdowns"]/form//option/@value').extract()[1:]
        color_names = sel.xpath('//div[@class="variation-dropdowns"]/form//option/text()').extract()[1:]
        size_or_color_str = sel.xpath('//div[@class="variation-dropdowns"]/form//label/text()').extract()
        if len(size_or_color_str)>0:
            size_or_color = size_or_color_str[0]
            if len(color_form)>0 and size_or_color == 'Shade:':
                item['colors'] = color_names
                color_ajax_url = 'https://www.lookfantastic.com/variations.json?productId='+str(item['show_product_id'])
                
                color_form_value = color_form.pop(0)

                # for color_form_value in color_form:
                form_data = {'option1':str(color_form_value), 'selected':'1', 'variation1':'4'}
                # import pdb;pdb.set_trace()
                yield FormRequest(color_ajax_url, formdata=form_data, callback=self.parse_color, meta={'item':item, 'color_forms':color_form})
            elif len(color_form)>0 and size_or_color == 'Size:':
                item['sizes'] = color_names

                #pop color
                colorItem = Color()
                colorItem['type'] = 'color'
                colorItem['from_site'] = item['from_site']
                colorItem['show_product_id'] = item['show_product_id']
                colorItem['name'] = 'onecolor'
                colorItem['images'] = images   
                colorItem['cover'] = color_cover    
        
                yield colorItem

                size_ajax_url = 'https://www.lookfantastic.com/variations.json?productId='+str(item['show_product_id'])

                color_form_value = color_form.pop(0)
                # for color_form_value in color_form:
                form_data = {'option1': str(color_form_value), 'selected':'1', 'variation1': '1'}
                # import pdb;pdb.set_trace()
                yield FormRequest(size_ajax_url, formdata=form_data, callback=self.parse_size, meta={'item':item, 'color_forms':color_form})

        else:
            colorItem = Color()
            colorItem['type'] = 'color'
            colorItem['from_site'] = item['from_site']
            colorItem['show_product_id'] = product_id
            colorItem['images'] = images       
            colorItem['cover'] = color_cover
            colorItem['name'] = 'onecolor'
            yield colorItem

            item['skus'] = []
            skuItem = {}
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = product_id
            skuItem['id'] = product_id
            skuItem['list_price'] = item['list_price']
            skuItem['current_price'] = item['current_price']
            skuItem['from_site'] = item['from_site']
            skuItem['color'] = 'onecolor'
            skuItem['size'] = 'onesize'
            skuItem['is_outof_stock'] = False
            item['skus'].append(skuItem)
            # yield skuItem

            yield item
            
    def parse_color(self, response):
        item = response.meta['item']
        color_forms = response.meta['color_forms']
        # print color_forms
        colorItem = Color()
        colorItem['type'] = 'color'
        colorItem['from_site'] = item['from_site']
        colorItem['show_product_id'] = item['show_product_id']
        
        response_body = re.sub(r'null', 'None', response.body)
        color_form_response = eval(response_body)
        
        if 'images' in color_form_response.keys():
            thumbnail = color_form_response['images'][0]['name']
            if len(color_form_response['images'])<4:
                return
            image = color_form_response['images'][3]['name']
            if '/600' not in image:
                image = re.sub('/[\d]+/[\d]+', '/600/600', image)

            color_name = color_form_response['variations'][0]['options'][0]['name']
            cover_style = color_form_response['variations'][0]['options'][0]['value']
            price_str = color_form_response['price']
            m = re.search(r'\d+\.\d+', price_str)
            if m:
                current_price = m.group(0)
    
            imageItem = ImageItem()
            imageItem['thumbnail'] = 'https://s4.thcdn.com/'+thumbnail
            imageItem['image'] = 'https://s4.thcdn.com/'+image
            images = []
            images.append(imageItem)
            colorItem['name'] = color_name
            colorItem['images'] = images       
            colorItem['cover_style'] = cover_style
            
            yield colorItem
    
            if 'skus' not in item.keys():               
                item['skus'] = []
            skuItem = {}
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['id'] = color_name+'*'+'onesize'
            skuItem['list_price'] = item['list_price']
            skuItem['current_price'] = current_price
            skuItem['from_site'] = item['from_site']
            skuItem['color'] = color_name
            skuItem['size'] = 'onesize'
            skuItem['is_outof_stock'] = False
            item['skus'].append(skuItem)

        if len(color_forms) == 0:
            yield item
        else:
            # import pdb;pdb.set_trace()  
            color_ajax_url = 'https://www.lookfantastic.com/variations.json?productId='+str(item['show_product_id'])
            color_form_value = color_forms.pop(0)
            # for color_form_value in color_form:
            form_data = {'option1':str(color_form_value), 'selected':'1', 'variation1':'4'}
            # import pdb;pdb.set_trace()
            yield FormRequest(color_ajax_url, formdata=form_data, callback=self.parse_color, meta={'item':item, 'colorItem':colorItem, 'color_forms':color_forms})

        
    def parse_size(self, response):
        item = response.meta['item']
        color_forms = response.meta['color_forms']
        # print color_forms
        
        
        response_body = re.sub(r'null', 'None', response.body)
        color_form_response = eval(response_body)
        if 'images' not in color_form_response.keys():
            return
        thumbnail = color_form_response['images'][0]['name']
        image = color_form_response['images'][3]['name']
        size_name = color_form_response['variations'][0]['options'][0]['name']
        price_str = color_form_response['price']
        m = re.search(r'\d+\.\d+', price_str)
        if m:
            current_price = m.group(0)

        if 'skus' not in item.keys():               
            item['skus'] = []
        skuItem = {}
        skuItem['type'] = 'sku'
        skuItem['show_product_id'] = item['show_product_id']
        skuItem['id'] = size_name+'*'+'onecolor'
        skuItem['list_price'] = item['list_price']
        skuItem['current_price'] = current_price
        skuItem['from_site'] = item['from_site']
        skuItem['color'] = 'onecolor'
        skuItem['size'] = size_name
        skuItem['is_outof_stock'] = False
        item['skus'].append(skuItem)

        if len(color_forms) == 0:
            yield item
        else:
            # import pdb;pdb.set_trace()  
            color_ajax_url = 'https://www.lookfantastic.com/variations.json?productId='+str(item['show_product_id'])
            color_form_value = color_forms.pop(0)
            # for color_form_value in color_form:
            form_data = {'option1':str(color_form_value), 'selected':'1', 'variation1':'1'}
            # import pdb;pdb.set_trace()
            yield FormRequest(color_ajax_url, formdata=form_data, callback=self.parse_size, meta={'item':item, 'color_forms':color_forms})


class LookfantasticSpider(BaseLookfantasticSpider, BaseSpider):
    name = "lookfantastic"
    allowed_domains = ["lookfantastic.com"]
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        # 'http://www.lookfantastic.com/home.dept',
        'https://www.lookfantastic.com/health-beauty/hair/view-all-haircare.list',
        'https://www.lookfantastic.com/health-beauty/make-up/view-all-make-up.list',
        'https://www.lookfantastic.com/health-beauty/face/view-all-skincare.list',
        'https://www.lookfantastic.com/health-beauty/body/view-all-bodycare.list',
        'https://www.lookfantastic.com/health-beauty/men/view-all-men-s.list',
        'https://www.lookfantastic.com/health-beauty/fragrance/view-all-fragrance.list'
        ]

    base_url = 'https://www.lookfantastic.com'
    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)
    def parse(self, response):
        sel = Selector(response)

        if sel.xpath('//div[@class="breadcrumbs_item breadcrumbs_item-active"]') == 'Men':
            gender = 'men'
            product_type_divs = sel.xpath('//div[@class="js-facet-panel"]/div[position()<5]')
            for product_type_div in product_type_divs:
                if product_type_div.xpath('./h2/text()').extract()[1] == 'Brand':
                    continue
                else:
                    product_type = product_type_div.xpath('./h2/text()').extract()[1].strip()
                    cate_lis = product_type_div.xpath('./ul/li')
                    for cate_li in cate_lis:
                        category = cate_li.xpath('./label/text()').extract()[0].strip()
                        cate_url = response.url + '?facetFilters=' + cate_li.xpath('./label/input/@value').extract()[0].strip()
                        yield Request(cate_url, callback=self.parse_list, meta={'gender': gender, 'product_type': product_type, 'category': category})
        else:
            gender = 'women'
            product_type = sel.xpath('//div[@class="js-facet-panel"]/div[2]/h2/text()').extract()[1].strip()
            cate_lis = sel.xpath('//div[@class="js-facet-panel"]/div[2]/ul/li')
            for cate_li in cate_lis:
                category = cate_li.xpath('./label/text()').extract()[1].strip()
                cate_url = response.url + '?facetFilters=' + cate_li.xpath('./label/input/@value').extract()[0].strip()
                yield Request(cate_url, callback=self.parse_list, meta={'gender': gender, 'product_type': product_type, 'category': category})


        # categoryDom = sel.xpath(".//*[contains(@class,'nav-link')]/a")

        # for cate in categoryDom:
        #     category = cate.xpath("./text()").extract()[0]
        #     if category not in ["Home","New","Electrical","Men","ghd","Dermalogica","ELLE Shop","Offers"]:
        #         category_uri = cate.xpath("./@href").extract()[0]
        #         if category != 'ELLE Shop':
        #             url = self.base_url + category_uri
        #         else:
        #             url = category_uri
        #         yield Request(url, callback=self.parse_categories, meta={"category_uri":category_uri, "category":category})

        # submenu_items = sel.xpath('//li[@class="submenu-list-item"]')
        #
        # for submenu_item in submenu_items:
        #     submenu_item_url = submenu_item.xpath('./a/@href').extract()[0]
        #     if re.findall(r'\/men\/', submenu_item_url) and re.findall(r'www', submenu_item_url):
        #         gender='men'
        #         url = submenu_item_url
        #     elif re.findall(r'www', submenu_item_url):
        #         continue
        #     else:
        #         url = self.base_url + submenu_item_url
        #         gender='women'
        #     yield Request(url, callback=self.parse_list, meta={'gender': gender})


    # def parse_categories(self, response):
    #     category = response.meta['category']

    #     sel = Selector(response)

    #     sub_category_dom = sel.xpath(".//*[contains(@class,'list-item sidebar-category')]/a")

    #     if len(sub_category_dom.extract()) > 0:
    #         for sub_cate in sub_category_dom:
    #             sub_category = sub_cate.xpath("./text()").extract()[0]
    #             if sub_category not in ["All Haircare","New in"]:
    #                 sub_category_url = sub_cate.xpath("./@href").extract()[0]
    #                 yield Request(sub_category_url, callback=self.parse_list, meta={"category":category, "sub_category":sub_category})

    #     else:
    #         pass


    def parse_list(self, response):
        # category = response.meta['category']
        # sub_category = response.meta['sub_category']

        sel = Selector(response)
        gender = response.meta['gender']
        category = response.meta['category']
        product_type = response.meta['product_type']
        # breadcrumbs_lis = sel.xpath('//div[@class="breadcrumbs"]//li')
        # if len(breadcrumbs_lis) > 3:
        #     if len(breadcrumbs_lis) < 6:
        #         product_type = breadcrumbs_lis[2].xpath('./a/text()').extract()[0]
        #         category = breadcrumbs_lis[-1].xpath('./text()').extract()[0]
        #     else:
        #         product_type = breadcrumbs_lis[2].xpath('./a/text()').extract()[0] +'-'+ breadcrumbs_lis[4].xpath('./a/text()').extract()[0]
        #         category = breadcrumbs_lis[-1].xpath('./text()').extract()[0]
        #
        # else:
        #     return

        if len(sel.xpath(".//*[@id='divSearchResults']/div/div").extract()) > 0:
            uriDoms = sel.xpath(".//*[@id='divSearchResults']/div/div")

            for dom in uriDoms:
                item = BaseItem()
                item['from_site'] = 'lookfantastic'
                item['type'] = 'base'
                item['gender'] = gender
                item['product_type'] = product_type
                item['category'] = category
                # item['sub_category'] = sub_category
                item['cover'] = handle_no_http(dom.xpath(".//img/@src").extract()[0])
                item['url'] = url = dom.xpath(".//img/parent::*/@href").extract()[0]
                yield Request(url, callback=self.parse_item, meta={"item": item})
            #
            # currentPage = re.findall(r'pageNumber=(\d+)', response.url)
            currentPageArr = re.split(r'(\&pageNumber=)', response.url)
            currentPage = 1 if len(currentPageArr) < 3 else int(currentPageArr[2])

            pagesCount = int(sel.xpath(".//div[@class='pagination_pageNumbers']/a[last()]/text()").extract()[0])

            if currentPage < pagesCount:
                url = currentPageArr[0] + '&pageNumber=' + str(currentPage+1)
                yield Request(url, callback=self.parse_list, meta={'gender': gender, 'product_type': product_type, 'category': category})


    def parse_item(self, response):
        item = response.meta['item']

        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        return BaseLookfantasticSpider.handle_parse_item(self, response, item)
    
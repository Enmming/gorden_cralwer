# -*- coding: utf-8 -*-
import base64
import re

from scrapy import Request
from scrapy.selector import Selector

from ..items import BaseItem, ImageItem, Color
from ..spiders.shiji_base import BaseSpider


class SsenseSpider(BaseSpider):
    name = "ssense"
    allowed_domains = ["ssense.com"]
    
    start_urls = [
        'https://www.ssense.com/en-us/men',
        'https://www.ssense.com/en-us/women'
        ]

    base_url = 'https://www.ssense.com'

    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 0.5,
    }
    
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, cookies={'forced_user_country': 'US', 'forcedCountry': 'US', 'forced_user_country_done': 'US'})

    def parse(self, response):
        
        sel = Selector(response)

        spliter = re.split('/', response.url)
        gender = spliter[-1]

        navDoms = sel.xpath(".//*[@id='product-list']/div[2]/div/div[1]/ul/li")
        if len(navDoms.extract()) > 0:
            for dom in navDoms:
                cate_name = dom.xpath("./h1/a/text()").extract()[0]
                if cate_name != 'All Categories':
                    product_type = cate_name.lower()
                    url = self.base_url + dom.xpath("./h1/a/@href").extract()[0]
                    yield Request(url, callback=self.parse_categories, meta={"gender":gender, "product_type":product_type})

    def parse_categories(self, response):
        product_type = response.meta['product_type']
        gender = response.meta['gender']

        sel = Selector(response)
        if len(sel.xpath(".//ul[@class='nav nav--stacked sublevel']").extract()) == 1:
            category_doms = sel.xpath(".//ul[@class='nav nav--stacked sublevel']/li")
        else:
            category_doms = sel.xpath(".//ul[@class='nav nav--stacked sublevel']//ul[@class='nav nav--stacked sublevel']/li")
        if len(category_doms.extract()):
            for dom in category_doms:
                category = dom.xpath("./a/text()").extract()[0]
                url = self.base_url + dom.xpath("./a/@href").extract()[0]
                if category == 'Tops':
                    yield Request(url, callback=self.parse_categories, meta={"gender":gender, "product_type":product_type})
                else:
                    yield Request(url, callback=self.parse_list, meta={"category":category, "gender":gender, "product_type":product_type})

    def parse_list(self, response):
        product_type = response.meta['product_type']
        gender = response.meta['gender']
        category = response.meta['category']

        sel = Selector(response)
        list_doms = sel.xpath(".//div[@class='browsing-product-list']/div[@class='browsing-product-item']")
        if len(list_doms.extract()):
            for dom in list_doms:
                item = BaseItem()
                item['from_site'] = self.name
                item['type'] = 'base'
                item['category'] = category
                item['product_type'] = product_type
                item['gender'] = gender
                # item['brand'] = dom.xpath("./meta[@itemprop='brand']/@content").extract()[0]
                # item['title'] = dom.xpath("./meta[@itemprop='name']/@content").extract()[0]
                # item['show_product_id'] = dom.xpath("./@data-product-id").extract()[0]
                # item['current_price'] = dom.xpath("./a/@data-product-price").extract()[0]
                item['cover'] = dom.xpath("./meta[@itemprop='image']/@content").extract()[0]
                item['url'] = url = self.base_url + dom.xpath("./a/@href").extract()[0]
                yield Request(url,callback=self.parse_item,meta={"item":item})

            if len(sel.xpath(".//div[@class='browsing-product-list']/div[@data-view='BrowsingPagination']").extract()):
                
                current_page = sel.xpath(".//div[@class='browsing-product-list']/div[@data-view='BrowsingPagination']/div/div[1]//li[@class='active']/text()").extract()[0]
                last_page = sel.xpath(".//div[@class='browsing-product-list']/div[@data-view='BrowsingPagination']/div/div[1]//li[last()-1]")
                
                if len(last_page.xpath('./a/text()')) > 0:
                    last_page = last_page.xpath("./a/text()").extract()[0]
                else:
                    last_page = last_page.xpath("./text()").extract()[0]
                
                current_page = int(current_page.strip())
                last_page = int(last_page.strip())
                if current_page < last_page:
                    # current_page += 1
                    
                    current_next_page = sel.xpath(".//div[@class='browsing-product-list']/div[@data-view='BrowsingPagination']/div/div[1]//li[@class='active']/following-sibling::li/a/@href").extract()[0]
                    
                    url = self.base_url + current_next_page  # '/en-us/men/designers/all/' + product_type + '/' + category + '/pages/' + str(current_page)
                    
                    yield Request(url, callback=self.parse_list, meta={"category":category, "gender":gender, "product_type":product_type})

    def parse_item(self, response):
        item = response.meta['item']

        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)
        current_url = response.url
        is_outof_stock = sel.xpath('//div[@id="product-item"]/div["product-item-container row-fluid"]//form//strong/text()').extract()
        
        if len(is_outof_stock)>0 and ('Sold Out' in is_outof_stock or 'Not available' in is_outof_stock):
            return   
        
        detail_dom = sel.xpath(".//div[@id='product-item']/div[1]/div[1]/div[@class='fixed-wrapper']//div[@class='product-description-container']/div")
        
        if len(detail_dom.extract()) == 0:
            return


        item['brand'] = detail_dom.xpath('./h1[@class="product-brand"]/a/text()').extract()[0]
        item['title'] = detail_dom.xpath('./h2[@class="product-name"]/text()').extract()[0]
        item['show_product_id'] = current_url.split('/')[-1] or current_url.split('/')[-2]
        item['current_price'] = detail_dom.xpath('.//span[@class="price"]/text()').extract()[0]
        list_price = detail_dom.xpath('.//span[@class="price sale"]/text()').re(r'^\$([\d\.]+)')
        if len(list_price) > 0:
            item['list_price'] = list_price[0]
        else:
            item['list_price'] = item['current_price']
            
        item['desc'] = ''.join(detail_dom.xpath(".//p[@itemprop='description']/text()").extract())

        item['colors'] = ['onecolor']
        item['dimensions'] = ['size']
        item['skus'] = []
        sizes_dom = sel.xpath(".//select[@id='size']/option")
        if len(sizes_dom.extract()) > 1:
            item['sizes'] = []
            for dom in sizes_dom:
                size = dom.xpath("./text()").extract()[0]
                
                # size = size.replace('\n','')
                
                dom_content = dom.extract()
                
                if size != 'SELECT A SIZE' and 'disabled' not in dom_content:
                    size = re.sub(r'\s', '', size)
                    
                    item['sizes'].append(size)

                    skuItem = {}
                    skuItem['type'] = 'sku'
                    skuItem['show_product_id'] = item['show_product_id']
                    skuItem['id'] = item["colors"][0] + '*' + size
                    skuItem['color'] = item["colors"][0]
                    skuItem['size'] = size
                    skuItem['from_site'] = self.name
                    skuItem['list_price'] = item['list_price']
                    skuItem['current_price'] = item['current_price']
                    skuItem['is_outof_stock'] = False
                    item['skus'].append(skuItem)
        else:
            item['sizes'] = ['onesize']

            skuItem = {}
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['id'] = item['colors'][0] + '*' + item['sizes'][0]
            skuItem['color'] = item['colors'][0]
            skuItem['size'] = item['sizes'][0]
            skuItem['from_site'] = self.name
            skuItem['list_price'] = item['list_price']
            skuItem['current_price'] = item['current_price']
            skuItem['is_outof_stock'] = False
            item['skus'].append(skuItem)

        img_doms = sel.xpath(".//div[@id='wrap']/div/div[@class='product-images-zoom-wrapper']//img")
        print response.body

        images = []
        if len(img_doms.extract()):
            for dom in img_doms:
                imageItem = ImageItem()
                imageItem['image'] = dom.xpath("./@data-src").extract()[0]
                imageItem['thumbnail'] = imageItem['image']
                images.append(imageItem)

        colorItem = Color()
        colorItem['type'] = 'color'
        colorItem['from_site'] = self.name
        colorItem['show_product_id'] = item['show_product_id']
        colorItem['name'] = item['colors'][0]
        if item['cover'] == '':
            colorItem['cover'] = images[0]['thumbnail']
        else:
            colorItem['cover'] = item['cover']
        
        colorItem['images'] = images
        yield colorItem
        sizelist_url = self.base_url + sel.xpath("//div[@id='product-item']/@data-route-size-chart").extract()[0]
        related_products_url = self.base_url + sel.xpath("//div[@id='product-item']/@data-route-related-products").extract()[0]
        yield Request(sizelist_url, callback=self.parse_sizelist,meta={"item":item, "related_products_url":related_products_url})
        
    def parse_sizelist(self, response):
        item = response.meta['item']
        related_products_url = response.meta['related_products_url']
        lis_str_list = re.search('\<ul\s*class\=\"buttons\-size\s*nav\s*clearfix\"\>([\s\S]+)\<\/ul\>\n+\s*\<ul', response.body)
        if lis_str_list:
            lis_str = lis_str_list.group(1)
            sel = Selector(text=lis_str)
            
            enabled_lis = sel.xpath("//li[not(@class)]")
            
            cm_keys = re.findall('data\-(\d+)\-cm\=\".+\"', lis_str)
            cm_key = list(set(cm_keys))
            cm_key.sort(key=cm_keys.index)
            
            sizes = re.findall('\>(.+)\<\/li\>', lis_str)
            
            cm_sizes = []
            
            for cm_li in enabled_lis:
                cms = cm_li.xpath("./@*").extract()
                cm_list = []
                for cm in cms:
                    if re.findall('cm', cm):
                        cm_list.append(cm)
                if len(cm_list)>0 and (len(cm_list) > 1 or (len(cm_list) < 2 and cm_list[0] != '0 cm' )):
                    cm_sizes.extend(cm_list)

            size0_list = []
            for k,li in enumerate(enabled_lis):
                if len(li.xpath("./@*").extract())>0 and li.xpath("./@*").extract()[0] == '0 cm':
                    size0_list.append(li.xpath("./text()").extract()[0])
                    del enabled_lis[k]
            
            n = 0
            cm_size_list = []
            for cm_size in cm_sizes:
                tempdict = {}
                tempdict[cm_key[n]] = cm_size
                n += 1
                if n >= len(cm_key):
                    n = 0
                cm_size_list.append(tempdict)
            size_dict = {}
            n = 0
            step = len(cm_key)
            for i in range(0, len(cm_size_list), step):
                size_dict[base64.encodestring(sizes[n]).strip()] = cm_size_list[i:i+step]
                n += 1
                
            size0_cm_list = []
            if len(size0_list) >0:
                for size0 in size0_list:
                    for cm in cm_key:
                        size0_cm_list.append({cm:u'0 cm'})
                    size_dict[base64.encodestring(size0).strip()]= size0_cm_list
                    
            item['size_chart'] = size_dict
            if re.search('\<img\s*src\=\"(.+)\"\>',response.body):
                size_url = re.search('\<img\s*src\=\"(.+)\"\>',response.body).group(1)
                item['size_chart_pic'] = self.base_url + size_url
            yield Request(related_products_url, callback=self.parse_related_products,meta={"item":item})
        else:
            yield Request(related_products_url, callback=self.parse_related_products,meta={"item":item})
        
    def parse_related_products(self, response):
        sel = Selector(response)
        item = response.meta['item']
        product_items_div = sel.xpath('//div[@id="product-related-styled"]//div[@class="product-item"]')
        related_items_id = []
        for product_div in product_items_div:
            product_id = product_div.xpath('./@data-product-id').extract()[0]
            related_items_id.append(product_id)
        if related_items_id:
            item['related_items_id'] = related_items_id
        yield item

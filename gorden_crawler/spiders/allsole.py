# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request,FormRequest
from scrapy_redis.spiders import RedisSpider
import re
from urllib import quote,unquote
import json
from gorden_crawler.utils import country


from gorden_crawler.spiders.shiji_base import BaseSpider

class AllsoleSpider(BaseSpider):
    name = "allsole"
    allowed_domains = ["allsole.com"]

    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        
        'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyHttpsUSAMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'https://www.allsole.com/catalogue/women/footwear.list',
        'https://www.allsole.com/catalogue/men/footwear.list',
        'https://www.allsole.com/offers/outlet.list?facetFilters=en_gender_content:Men',
        'https://www.allsole.com/offers/outlet.list?facetFilters=en_gender_content:Women'
        ]

    base_url = 'https://www.allsole.com'
    list_ajax_url = '/searchRequest.facet?facetItemsJson='

    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        current_url = response.url
        find = current_url.find("outlet")
        # category_index = "0"
        # if find != -1:
        #     # gender = current_url[find+3:].lower()
        #     category_index = "2"
        # else:
        #     spliter = re.split('/', response.url)
        #     gender = spliter[-2]
        product_type = 'shoes'

        sel = Selector(response)
        
        menuDoms = sel.xpath(".//div[@class='js-facet-panel']/div[@class='facets_listPanel js-facet-category js-facet-en_FootwearType_content']/ul/li")
        if len(menuDoms.extract()) > 0:
            for dom in menuDoms:
                category = dom.xpath(".//label/text()").extract()[1]
                category = category.strip()
                categoryValue = dom.xpath(".//label/input/@value").extract()[0]
                categoryAjaxParams = {"sectionName":response.url.replace(self.base_url,''),"facetCriteria":[str(categoryValue)],"pageNumber":1,"productsPerPage":33,"sortField":"","searchType":"list"}
                # if category_index == "2":
                    # categoryAjaxParams['facetCriteria'].append(unquote(current_url[find-17:]))
                    # f = categoryAjaxParams['sectionName'].find('?')
                    # if f != -1:
                    #     categoryAjaxParams['sectionName'] = categoryAjaxParams['sectionName'][:f]
                if re.findall('outlet',current_url):
                    url = current_url + '|' + categoryValue
                    gender = ''
                    yield Request(url, callback=self.parse_list, meta={"category":category, "gender":gender, "product_type":product_type, 'type': 'html'})
                else:
                    spliter = re.split('/', response.url)
                    gender = spliter[-2].lower()
                    url = self.base_url + self.list_ajax_url + quote(str(categoryAjaxParams), '/+')
                    yield Request(url, callback=self.parse_list, meta={"category":category, "gender":gender, "product_type":product_type, "categoryAjaxParams": categoryAjaxParams, 'type': 'ajax'})

    def parse_list(self, response):
        category = response.meta['category']
        product_type = response.meta['product_type']
        gender = response.meta['gender']
        type = response.meta['type']
        if type == 'ajax':
            categoryAjaxParams = response.meta['categoryAjaxParams']

            resultJson = json.loads(response.body)

            if len(resultJson['products']) > 0:
                for product in resultJson['products']:
                    item = BaseItem()
                    item['from_site'] = self.name
                    item['type'] = 'base'
                    item['category'] = category
                    item['product_type'] = product_type
                    item['gender'] = gender
                    item['url'] = url = product["url"]
                    item['cover'] = product["images"]['large']
                    item['show_product_id'] = product['id']
                    item['title'] = product['title']
                    if 'brand' in product.keys():
                        item['brand'] = product['brand']
                    item['current_price'] = product['price'][1:]
                    item['size_country'] = country.const.UK
                    # item['list_price'] = product['price'][1:]
                    # url = 'http://www.allsole.com/footwear-accessories/sneaky-spray-eco-pump-special-edition-non-aerosol/11117810.html'
                    # yield Request(url,callback=self.parse_item,meta={"item":item})
                    url = self.base_url + '/en_GB/GBP/sizeguidejson/' + str(product['id']) + '.awesome'
                    yield Request(item['url'], callback=self.parse_item, meta={"item": item})

                pageNumber = resultJson['pageNumber']
                totalpages = resultJson['totalPages']
                if pageNumber < totalpages:
                    categoryAjaxParams['pageNumber'] += 1
                    url = self.base_url + self.list_ajax_url + quote(str(categoryAjaxParams))
                    yield Request(url, callback=self.parse_list, meta={"category":category, "gender":gender, "product_type":product_type, "categoryAjaxParams": categoryAjaxParams, 'type': 'ajax'})

        else:
            sel = Selector(response)
            products = sel.xpath(".//div[@class='item item-health-beauty unit size-1of3 grid thg-track js-product-complex ']")
            for product in products:
                item = BaseItem()
                item['from_site'] = self.name
                item['type'] = 'base'
                item['category'] = category
                item['product_type'] = product_type
                item['gender'] = sel.xpath(".//div[@class='facets_listPanel js-facet-category js-facet-en_gender_content']/ul/li/label/input[@checked='checked']/parent::*/text()").extract()[1].strip().lower()
                item['url'] = url = product.xpath("./div[1]/div/a/@href").extract()[0]
                item['cover'] = 'http:' + product.xpath("./div[1]/div/a/img/@src").extract()[0]
                item['show_product_id'] = product.xpath("./span/@data-product-id").extract()[0]
                item['title'] = product.xpath("./div[1]/div/a/img/@alt").extract()[0]
                item['brand'] = product.xpath("./div[2]/p[@class='product-brand']/text()").extract()[0]
                item['size_country'] = country.const.UK
                url = self.base_url + '/en_GB/GBP/sizeguidejson/' + str(item['show_product_id']) + '.awesome'

                yield Request(item['url'],callback=self.parse_item,meta={"item":item})
            pageNumber = sel.xpath(".//a[@class='pagination_pageNumber js-paging-option pagination_pageNumber-active js-current-page']/text()").extract()[0]
            total_products_str = sel.xpath(".//p[@class='listTitle_results']/text()").extract()[0]
            total_products_num = int(re.search('(\d+)',total_products_str).group(1))
            totalpages = total_products_num / 33 + 1
            if pageNumber < totalpages:
                pageNumber_str = '&pageNumber=' + str(pageNumber + 1)
                if re.findall('pageNumber'):
                    url = re.sub('\&pageNumber\=\d+', pageNumber_str, url)
                else:
                    url = url + pageNumber_str
                yield Request(url, callback=self.parse_list, meta={"category":category, "gender":gender, "product_type":product_type, 'type': 'html'})
        
    def parse_size_info(self, response):
        item = response.meta['item']
        if response.body:
            resultJson = json.loads(response.body)
            if resultJson:
                guideTitle = re.search(r'<caption>(.*)</caption>',resultJson['sizeGuide']).group(1)
                if guideTitle:
                    item['size_info'] = guideTitle
            yield Request(item['url'],callback=self.parse_item,meta={"item":item})

    def parse_item(self, response):
        item = response.meta['item']

        return self.handle_parse_item(response, item)

    def handle_parse_item(self,response,item):
        sel = Selector(response)

        soldout_span = sel.xpath('//div[@class="product-variation"]//span[contains(@class, "soldout")]').extract()
        if len(soldout_span) > 0:
            return

        product_price = eval(re.search(r'productPrice:(.*),', response.body).group(1))
        product_rrp = eval(re.search(r'rrp:(.*),', response.body).group(1))
        rrp_dr = re.compile(r'<[^>]+>',re.S)
        rrp = rrp_dr.sub('',product_rrp)
        rrp_prices = re.split(r': ',rrp)

        item['current_price'] = product_price[6:]
        item['list_price'] = rrp_prices[1][6:]

        if 'show_product_id' not in item.keys():
            item['show_product_id'] = eval(re.search(r'productID:(.*),', response.body).group(1))

        if 'brand' not in item.keys():
            item['brand'] = eval(re.search(r'productBrand:(.*),', response.body).group(1))
        
        if item['brand'] == '':
            item['brand'] = 'allsole'
        
        desc = sel.xpath(".//div[@itemprop='description']/*").extract()
        if len(desc) > 0:
            item['desc'] = desc[0]
        else:
            item['desc'] = ''


        sizeDoms = sel.xpath(".//select[@id='opts-1']/option[string-length(@value) > 0]")
        item['dimensions'] = ['size']
        item['skus'] = []
        if len(sizeDoms.extract()):

            colorDoms = sel.xpath(".//select[@id='opts-2']/option[@value>0]")
            if len(colorDoms.extract()):
                color = colorDoms.xpath("./text()").extract()[0]
                item["colors"] = [color]
            else:
                item["colors"] = ["onecolor"]

            item['sizes'] = []
            for dom in sizeDoms:
                curr_size = dom.xpath("./text()").extract()[0]
                item['sizes'].append(curr_size)

                skuItem = {}
                skuItem['type'] = 'sku'
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['id'] = item["colors"][0] + '*' + curr_size
                skuItem['color'] = item["colors"][0]
                skuItem['size'] = curr_size
                ##skuItem['size_num'] = re.search(r'\d+', curr_size).group(0)
                skuItem['from_site'] = self.name
                skuItem['list_price'] = item['list_price']
                skuItem['current_price'] = item['current_price']
                skuItem['is_outof_stock'] = False
                item['skus'].append(skuItem)


        else:
            item['sizes'] = ['onesize']
            item['colors'] = ['onecolor']

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
            

        imgDoms = sel.xpath(".//div[@class='media']//li[@class='n-unit']")
        images = []
        if len(imgDoms.extract()):
            for dom in imgDoms:
                imageItem = ImageItem()
                imageItem['image'] = dom.xpath("./a/@href").extract()[0]
                imageItem['thumbnail'] = dom.xpath("./a/div/img/@src").extract()[0]
                images.append(imageItem)

        colorItem = Color()
        colorItem['type'] = 'color'
        colorItem['from_site'] = self.name
        colorItem['show_product_id'] = item['show_product_id']
        colorItem['name'] = item['colors'][0]
        colorItem['cover'] = images[0]['thumbnail']
        
        colorItem['images'] = images

        yield colorItem

        yield item



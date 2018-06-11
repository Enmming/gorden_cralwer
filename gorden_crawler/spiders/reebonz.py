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

class ReebonzSpider(BaseSpider):
    name = "reebonz"
    allowed_domains = ["reebonz.com"]

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
        'https://www.reebonz.com/cn/shop-men',
        'https://www.reebonz.com/cn/shop-women'
        ]

    base_url = 'https://www.reebonz.com'

    page_size = '&pagesize=100'

    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)
        if 'shop-men' in response.url:
            gender = 'men'
        elif 'shop-women' in response.url:
            gender = 'women'

        eventsMenu_lis = sel.xpath('//div[@id="eventsMenu"]/ul/li')
        for eventsMenu_li in eventsMenu_lis:
            product_type = eventsMenu_li.xpath('./span/a/text()').extract()[0]
            cat_lis = eventsMenu_li.xpath('./ul/li')
            for cat_li in cat_lis:
                category = cat_li.xpath('./a/text()').extract()[0]
                cat_url = self.base_url + cat_li.xpath('./a/@href').extract()[0] + self.page_size
                yield Request(cat_url, callback=self.parse_list, meta={"category": category, "gender": gender, "product_type": product_type})

    def parse_list(self, response):
        category = response.meta['category']
        product_type = response.meta['product_type']
        gender = response.meta['gender']
        sel = Selector(response)

        products = sel.xpath('//div[@class="row js-productWrapper"]/div/div[@class="productListItem"]/div')
        for product in products:
            item = BaseItem()
            item['from_site'] = self.name
            item['type'] = 'base'
            item['category'] = category
            item['product_type'] = product_type
            item['gender'] = gender
            item['url'] = self.base_url + product.xpath('./div[@class="productImg"]/a/@href').extract()[0]
            item['cover'] = product.xpath('./div[@class="productImg"]/a/img/@src').extract()[0]
            item['show_product_id'] = product.xpath("./@data-productid").extract()[0]
            item['title'] = product.xpath('./div[@class="productInfo"]/div[@class="productName"]/a/text()').extract()[0]
            item['brand'] = product.xpath('./div[@class="productInfo"]/div[@class="productBrand"]/a/text()').extract()[0]

            yield Request(item['url'],callback=self.parse_item,meta={"item":item})

        next_url = sel.xpath('//a[@class="js-filter-links iconCaret iconNext"]')
        if len(next_url) > 0:
            next_url = self.base_url + next_url.extract()[0]
            yield Request(next_url, callback=self.parse_list, meta={"category": category, "gender": gender, "product_type": product_type})

        # pageNumber = sel.xpath(".//a[@class='pagination_pageNumber js-paging-option pagination_pageNumber-active js-current-page']/text()").extract()[0]
        # total_products_str = sel.xpath(".//p[@class='listTitle_results']/text()").extract()[0]
        # total_products_num = int(re.search('(\d+)',total_products_str).group(1))
        # totalpages = total_products_num / 33 + 1
        # if pageNumber < totalpages:
        #     pageNumber_str = '&pageNumber=' + str(pageNumber + 1)
        #     if re.findall('pageNumber'):
        #         url = re.sub('\&pageNumber\=\d+', pageNumber_str, url)
        #     else:
        #         url = url + pageNumber_str
        #     yield Request(url, callback=self.parse_list, meta={"category":category, "gender":gender, "product_type":product_type, 'type': 'html'})
        
    def parse_item(self, response):
        item = response.meta['item']

        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)


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



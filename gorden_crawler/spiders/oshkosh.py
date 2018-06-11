# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy import Request
import re
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from gorden_crawler.spiders.shiji_base import BaseSpider
import logging

class OshKoshSpider(BaseSpider):
#class OshKoshSpider(RedisSpider):
    name = "oshkosh"
    allowed_domains = ["oshkosh.com"]

    base_url = 'http://www.oshkosh.com'

    #正式运行的时候，start_urls为空，通过redis来喂养爬虫


    custom_settings = {
        # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'DOWNLOAD_DELAY': 1,
        'RETRY_TIMES': 40,
        'DOWNLOADER_MIDDLEWARES': {
            # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,'
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware': 1,
            'gorden_crawler.middlewares.proxy_ats.ProxyUSAMiddleware': 100,
            # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }

    start_urls = [
        'http://www.oshkosh.com/oshkosh-baby-girl?navID=header',
        'http://www.oshkosh.com/oshkosh-baby-boy?navID=header',
        'http://www.oshkosh.com/oshkosh-toddler-girl?navID=header',
        'http://www.oshkosh.com/oshkosh-toddler-boy?navID=header',
        'http://www.oshkosh.com/oshkosh-kid-girl?navID=header',
        'http://www.oshkosh.com/oshkosh-kid-boy?navID=header'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def parse(self, response):
        if response.url == 'http://www.oshkosh.com/oshkosh-baby-girl?navID=header' or response.url == 'http://www.oshkosh.com/oshkosh-baby-boy?navID=header' :
            gender='baby'
            size_info = 'http://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Page-Include?cid=sc_oshkosh-baby'
        elif response.url =='http://www.oshkosh.com/oshkosh-toddler-girl?navID=header' or response.url =='http://www.oshkosh.com/oshkosh-toddler-boy?navID=header':
            gender='toddler'
            size_info = 'http://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Page-Include?cid=sc_oshkosh-toddler'
        elif response.url== 'http://www.oshkosh.com/oshkosh-kid-girl?navID=header':
            gender='girls'
            size_info = 'http://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Page-Include?cid=sc_oshkosh-kid-girl'
        else:
            gender='boys'
            size_info = 'http://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Page-Include?cid=sc_oshkosh-kid-boy'
        sel = Selector(response)
        uri_head_lis = sel.xpath('//div[contains(@class, "categorylisting")]/ul[3]/li')
        for li in uri_head_lis:
            url=li.xpath('.//@href').extract()[0]
            category = li.xpath('.//span/text()').extract()[0]
            yield Request(url, callback=self.parse_categories, meta={'category': category, 'gender': gender, 'size_info': size_info})
    #第一个请求下的categories
    def parse_categories(self, response):
        category = response.meta['category']
        gender = response.meta['gender']
        size_info = response.meta['size_info']
        sel = Selector(response)
        uri_categories_lis=sel.xpath('//div[contains(@class, "search-result-content")]/ul/li[contains(@class, "grid-tile3")]')
        for li in uri_categories_lis:
            uri=li.xpath('.//div[@class="product-name"]/h2/a/@href').extract()[0]
            if uri:
                if not re.search(r'http', uri):
                    uri = self.base_url+uri
                image_uri=li.xpath('.//div[contains(@class, "product-image")]/a[@class="thumb-link"]/img/@src').extract()[0]
                item=BaseItem()
                item['type']='base'
                item['category']=category
                item['gender'] = gender
                if category == 'Shoes':
                    item['size_info'] = 'http://www.carters.com/on/demandware.store/Sites-Carters-Site/default/Page-Include?cid=sc_carters-shoes'
                else:
                    item['size_info'] = size_info
                item['url']=uri
                current_price=li.xpath('.//span[contains(@class, "product-sales-price")]/text()')
                if current_price:
                    item['current_price'] = current_price.extract()[0]
                    if re.search(r'-', item['current_price']):
                        item['current_price'] = re.findall(r'\d+', item['current_price'])[0]
                list_price = li.xpath('.//span[contains(@class, "product-standard-price")]/text()').re(r'(\S+)')
                if len(list_price)>0:
                    item['list_price']=list_price[0]
                elif current_price:
                    item['list_price']=item['current_price']
                item['cover']=image_uri
                item['title']=li.xpath('.//div[contains(@class, "product-name")]//a/@title').extract()[0]
                yield Request(uri, callback=self.parse_item, meta={'item': item})

        total_pages_temp=sel.xpath('.//div[contains(@class, "pagination-countprogress")]/span[contains(@class, "total-pages")]/text()')
        if total_pages_temp:
            total_pages=total_pages_temp.extract()[0]
            current_page=sel.xpath('.//div[contains(@class, "pagination-countprogress")]/span[contains(@class, "current-page")]/text()').extract()[0]
        else:
            total_pages=1
            current_page=1


        pnCGID=sel.xpath('.//input[contains(@name, "pnCGID")]/@value').extract()
        if len(pnCGID) == 0:
            return
        pnCGID = pnCGID[0]

        if (int(current_page)+1)<=int(total_pages):
            startRow= int(current_page) * 6
            url=self.base_url+"/"+pnCGID.encode('UTF-8')+"?cgid="+pnCGID.encode('UTF-8')+"&startRow="+str(startRow)+"?infiniteScroll=true"
            yield Request(url, callback=self.parse_categories, meta={'category': category, 'gender': gender, 'size_info': size_info})

    #开始爬取每个category下的items
    def parse_item(self, response):
        item=response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        skus=[]
        sel = Selector(response)
        item['from_site'] = self.name
        if 'whoops' in response.url:
            logging.warning('anti scraping: ' + response.url)
        current_price = sel.xpath('//span[contains(@class, "price-sales")]/text()').extract()
        #show_product_id_selector = sel.xpath('//div[contains(@class, "product-number")]/span/text()').extract()
#         if len(current_price) > 0 and len(show_product_id_selector) > 0:
        if len(current_price) > 0:

            match = re.search(r'"product_id":\s*\[\s*"([^"]+)"\s*\]', response.body)
            if match is None:
                return

            temp_show_product_id = match.group(1)

            current_price = current_price[0].strip()

            if len(current_price) == 0:
                return

            list_price = sel.xpath('//span[contains(@class, "price-standard")]/text()').re(r'(\S+)')

            if len(list_price)>0:
                list_price=list_price[0]
            else:
                list_price=current_price

            item['brand']= self.name
#             item['desc']=".".join(sel.xpath('//div[contains(@class, "additional")]/ul/li/text()').extract())

            desc1 = sel.xpath('//div[@class="categorylisting detail"]/div/div').extract()[0]
            desc2 = sel.xpath('//div[@class="categorylisting fabric"]/div/div').extract()[0]

            item['desc'] = re.sub(r'[\t\n]', '', desc1 + desc2)
            item['desc'] = re.sub('<img.+?>', '', item['desc'])
            if not sel.xpath('//p[contains(@class, "not-available")]/text()'):

                colors = []

                item_colors_links=sel.xpath('//div[@id="product-content"]//ul[contains(@class, "swatches color")]//li[contains(@class,"selected")]/a')
                item_sizes=sel.xpath('//div[@id="product-content"]//div[contains(@class, "value")]//ul[contains(@class, "swatches size")]/li[@class!="emptyswatch unselectable"]//@title').extract()

                item['sizes']=item_sizes
                item['dimensions']=['size']
                item['product_type']='mother-baby'
                if len(item_colors_links) == 0:
                    item_colors_links = ['one_color']
                for item_color_link in item_colors_links:

                    images=[]
                    thumbnails=sel.xpath('//div[@id="thumbnails"]//li[@class!="thumb pdpvideo"]')
                    if thumbnails:
                        for li in thumbnails:
                            imageItem=ImageItem()
                            image_url=li.xpath('./a/img/@src').extract()[0]
                            imageItem['image']=self.handle_image_url(image_url.encode('utf-8'), 1000, 1000)
                            imageItem['thumbnail']=self.handle_image_url(image_url.encode('utf-8'), 350, 350)
                            images.append(imageItem)
                    elif sel.xpath('//div[@id="thumbnails"]/li[@class="thumb pdpvideo"]/a/img/@src'):
                        imageItem=ImageItem()
                        image_url=sel.xpath('//img[@class="primary-image"]/@src').extract()[0]
                        imageItem['image']=self.handle_image_url(image_url.encode('utf-8'), 1000, 1000)
                        imageItem['thumbnail']=self.handle_image_url(image_url.encode('utf-8'), 350, 350)
                        images.append(imageItem)
                    else:
                        imageItem=ImageItem()
                        image_url=sel.xpath('//img[@class="primary-image"]/@src').extract()[0]
                        imageItem['image']=self.handle_image_url(image_url.encode('utf-8'), 1000, 1000)
                        imageItem['thumbnail']=self.handle_image_url(image_url.encode('utf-8'), 350, 350)
                        images.append(imageItem)

                    if len(item_colors_links) > 0:
                        color_name=item_color_link.xpath('./@title').extract()[0]
                        color_cover=item_color_link.xpath('./@style').re('http://[^\)]+')[0]
                    else:
                        color_name = 'one_color'
                        color_cover = images[0]['thumbnail']

                    colors.append(color_name)

                    show_product_id = temp_show_product_id+"*"+color_name
                    item['show_product_id']= show_product_id

                    color=Color()
                    color['type']='color'
                    color['from_site']= self.name
                    color['show_product_id']= show_product_id
                    color['images']=images
                    color['name'] = color_name
                    color['cover'] = color_cover

                    yield color

                    for item_size in item_sizes:
                        skuItem=SkuItem()
                        skuItem['type']='sku'
                        skuItem['show_product_id']= show_product_id
                        skuItem['id']=color['name'].encode("utf-8")+"*"+item_size
                        skuItem['current_price']= current_price
                        skuItem['list_price']=list_price
                        if len(item_colors_links) > 0:
                            skuItem['color']=item_color_link.xpath('./@title').extract()[0]
                        else:
                            skuItem['color'] = 'one_color'
                        skuItem['size']=item_size
                        skuItem['from_site']=self.name
                        skuItem['is_outof_stock']=False
                        skuItem['quantity'] = sel.xpath('//select[contains(@id, "Quantity")]//@value').extract()[0]
                        #yield skuItem
                        skus.append(skuItem)

                item['colors']= colors
                item['skus']=skus

                yield item

    def handle_image_url(self, url, sw, sh):
        (new_url, sw_result) = re.subn(r'sw=\d+', 'sw='+str(sw), url)
        (new_url, sh_result) = re.subn(r'sh=\d+', 'sh='+str(sh), new_url)

        need_question = False
        m = re.search(r'\?', url)
        if m is None:
            need_question = True

        if sw_result == 0:
            if need_question:
                new_url = new_url + "?sw=" + str(sw)
                need_question = False
            else:
                new_url = new_url + "&sw=" + str(sw)

        if sh_result == 0:
            if need_question:
                new_url = new_url + "?sh=" + str(sh)
            else:
                new_url = new_url + "&sh=" + str(sh)

        return new_url

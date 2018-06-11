# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from gorden_crawler.spiders.shiji_base import BaseSpider

import re
import execjs
import demjson


# import json

class AshfordSpider(BaseSpider):
    name = "ashford"
    allowed_domains = ["ashford.com"]

    custom_settings = {
        # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.5,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 10,
        #         'DOWNLOADER_MIDDLEWARES': {
        # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
        #             'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
        #             'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
        #             'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
        #             'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        #         }
    }

    # 正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'http://zh.ashford.com/us/home?locale=zh_US>',
        'http://zh.ashford.com/us/watches/watch-winders/cat5019.cid?locale=zh_US>',
        'http://zh.ashford.com/us/accessories/mens-accessories/cat100014.cid?locale=zh_US>',
    ]
    base_url = 'http://zh.ashford.com'

    cat_url = 'http://zh.ashford.com/us/browse/subcategory.jsp'

    # 爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def parse(self, response):
        sel = Selector(response)
        current_url = response.url
        if current_url.find('home') != -1:
            navDom = sel.xpath(".//ul[@class='navigation jq-touch-navigation navigation-endeca']/li[position()<6]")
            for dom in navDom[2:]:
                product_type = dom.xpath("./a[1]/span/text()").extract()[0].lower()
                if product_type.find("jewelry") != -1:
                    catList = dom.xpath("./div/div/ul")
                    for cat in catList:
                        gender = 'women'
                        category = cat.xpath("./li[1]/a/text()").extract()[0]
                        if category.find(u'\u65f6\u5c1a') != -1:
                            tempCatList = cat.xpath("./li[position()>1]")
                            for tempCat in tempCatList:
                                category = tempCat.xpath("./a/text()").extract()[0]
                                url = self.base_url + tempCat.xpath("./a/@href").extract()[0]
                                yield Request(url, callback=self.parse_list,
                                              meta={"categoryUrl": url, 'gender': gender, 'product_type': product_type,
                                                    'category': category})
                        else:
                            url = self.base_url + cat.xpath("./li[1]/a/@href").extract()[0]
                            yield Request(url, callback=self.parse_list,
                                          meta={"categoryUrl": url, 'gender': gender, 'product_type': product_type,
                                                'category': category})
                else:
                    if product_type.find(u"\u7537") != -1:
                        gender = 'men'
                    else:
                        gender = 'women'
                    catList = dom.xpath("./div/div/ul[3]/li[position()>1]")
                    for cat in catList:
                        category = cat.xpath("./a/text()").extract()[0]
                        if category.find(u"\u914d\u4ef6") != -1:
                            product_type = u'\u914d\u4ef6'
                        url = self.base_url + cat.xpath("./a/@href").extract()[0]
                        yield Request(url, callback=self.parse_list,
                                      meta={"categoryUrl": url, 'gender': gender, 'product_type': product_type,
                                            'category': category})
        else:
            product_type = 'Accessories'
            category = sel.xpath(".//a[@id='finalURL']/text()").extract()[0]
            url = current_url
            gender = 'men'
            yield Request(url, callback=self.parse_list,
                          meta={"categoryUrl": url, 'gender': gender, 'product_type': product_type,
                                'category': category})

    def parse_list(self, response):
        product_type = response.meta['product_type']
        category = response.meta['category']
        gender = response.meta['gender']
        sel = Selector(response)
        current_url = response.url
        checkboxFilters = sel.xpath(".//div[@class='sideBar']/div[@class='filter checkbox-filters']")
        for cb in checkboxFilters:
            if cb.xpath("./h5/text()").extract()[0].strip().lower() == 'gender':
                if current_url.find('4294966899') == -1 and current_url.find('4294966836') == -1:
                    gender_url_list = cb.xpath("./div/div")
                    for genderUrl in gender_url_list:
                        need_parse_url = self.base_url + genderUrl.xpath("./input/@value").extract()[0]
                        gender = genderUrl.xpath("./label/text()").extract()[0].strip()[:2]
                        yield Request(need_parse_url, callback=self.parse_list,
                                      meta={"categoryUrl": need_parse_url, 'gender': gender,
                                            'product_type': product_type, 'category': category})
        listDom = sel.xpath(".//div[@id='grid-4-col']/div")
        if len(listDom.extract()) > 0:
            for dom in listDom[1:]:
                item = BaseItem()
                item['type'] = 'base'
                item['from_site'] = self.name
                item['product_type'] = product_type
                item['category'] = category
                if len(dom.xpath("./div[2]/div[1]/div/div/a/img/@src")) >0:
                    item['cover'] = self.base_url + dom.xpath("./div[2]/div[1]/div/div/a/img/@src").extract()[0]
                else:
                    continue
                url = self.base_url + dom.xpath("./div[2]/div[1]/div/div/a/@href").extract()[0]
                desc = dom.xpath("./div[2]/div[4]/a/text()").extract()[0].strip().lower()
                if (desc.find(u'\u5973') > -1 or desc.find('women') > -1 or gender.find(u'\u5973')) > -1:
                    gender = 'women'
                if (desc.find(u'\u7537') > -1 or desc.find("men's") > -1 or gender.find(u'\u7537')) > -1:
                    gender = 'men'
                item['url'] = url
                item['gender'] = gender
                yield Request(url, callback=self.parse_item, meta={"item": item})

            if len(sel.xpath(".//div[@class='filter_bottom']/ul/li[@class='disabledLink']/a/text()")) > 0:
                currentPage = sel.xpath(".//div[@class='filter_bottom']/ul/li[@class='disabledLink']/a/text()").extract()[0].strip()
            else:
                currentPage = 1

            countStr = sel.xpath(".//div[@class='top clearfix']/h5/text()").extract()[0]
            countTotal = int(re.findall('\d+', countStr)[0])
            lastPage = countTotal / 40 + 1 if countTotal % 40 > 0 else countTotal / 40

            if int(currentPage) < int(lastPage):
                if len(sel.xpath(".//div[@class='filter_bottom']/ul/li[@class='nextLink']")) > 0:
                    list_more_url = self.cat_url + sel.xpath(".//div[@class='filter_bottom']/ul/li[@class='nextLink']/a/@href").extract()[0]
                    yield Request(list_more_url, callback=self.parse_list, meta={"category": category, "product_type": product_type, "gender": gender})

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        sel = Selector(response)

        if len(sel.xpath(".//div[@class='atg_store_noMatchingItem']")) > 0:
            return
        info = sel.xpath(".//div[@class='firstContainer row']")
        item['brand'] = info.xpath("./h1/a[1]/text()").extract()[0]
        item['show_product_id'] = info.xpath("./h1/h2/text()").extract()[0].strip()
        item['title'] = info.xpath("./h1/a[2]/text()").extract()[0]
        # item['desc'] = info.xpath("./h3/text()").extract()[0]
        item['colors'] = []

        if len(sel.xpath(".//div[@id='tab1_info']")) > 0:
            if len(sel.xpath(".//div[@id='tab1_info']/div[2]")) > 0:
                item['desc'] = sel.xpath(".//div[@id='tab1_info']/div[1]/table").extract()[0] + sel.xpath(".//div[@id='tab1_info']/div[2]/table").extract()[0]
            else:
                item['desc'] = sel.xpath(".//div[@id='tab1_info']/div[1]/table").extract()[0]

        skusStr = "".join(re.findall(r'window.universal_variable =.+\}\}<\/script>', response.body, re.S))

        if len(skusStr) > 0:
            context = execjs.compile('''
                var skus = %s;
                function getSkus(){
                    return skus;
                }
            ''' % skusStr[27:-9])
            skusDict = context.call('getSkus')

        item['list_price'] = skusDict['product']['unit_price']
        item['current_price'] = skusDict['product']['unit_sale_price']
        images = []
        imageDom = sel.xpath(".//ul[@class='alt_imgs col-md-12']/li")
        colorItem = Color()
        for dom in imageDom:
            imageItem = ImageItem()
            imageItem['image'] = self.base_url + dom.xpath("./a/@href").extract()[0]
            imageItem['thumbnail'] = re.sub('XA\.', 'LA.', imageItem['image'])
            images.append(imageItem.copy())

        colorItem['images'] = images
        colorItem['type'] = 'color'
        colorItem['from_site'] = item['from_site']
        colorItem['show_product_id'] = item['show_product_id']
        colorItem['name'] = u'one color'
        colorItem['cover'] = self.base_url + sel.xpath(".//ul[@class='alt_imgs col-md-12']/li[1]/a/img/@src").extract()[0]

        yield colorItem

        item['colors'].append(colorItem['name'])
        item['dimensions'] = ['size']
        item['skus'] = []
        sku_item_url_list = []
        sku_size_list = []
        index = 0
        sku_items = sel.xpath(".//div[@id='sizeValues']/div")
        if len(sku_items) > 0:
            for sku_item in sku_items:
                sku_size = sku_item.xpath("./@onclick").extract()[0].split("'")[3]
                ajax_id = sku_item.xpath("./@onclick").extract()[0].split("'")[1]
                if sku_size.find(' ') != -1:
                    sku_size = re.sub(' ', '%20', sku_size)
                sku_item_url = self.base_url + sel.xpath(".//form[@id='colorsizerefreshform']/@action").extract()[
                    0] + '&productId=' + ajax_id + '&selectedSize=' + sku_size
                sku_item_url_list.append(sku_item_url)
                sku_size_list.append(sku_size)
            sku_item_url_list.append(sku_item_url)  # only for avoiding indexError in parse_sku_item when loop reach the last size
            yield Request(sku_item_url_list[0], callback=self.parse_sku_item,
                          meta={"sku_size_list": sku_size_list, "sku_item_url_list": sku_item_url_list, "item": item,
                                "index": index})
        else:
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = skusDict['product']['id']
            skuItem['list_price'] = item['list_price']
            skuItem['current_price'] = item['current_price']
            skuItem['color'] = u'one color'
            skuItem['size'] = u'one size'
            skuItem['id'] = skusDict['product']['sku_code']
            skuItem['from_site'] = item['from_site']
            if skusDict['product']['stock'] == 0:
                skuItem['is_outof_stock'] = True
            item['skus'].append(skuItem)
            item['sizes'] = [u'one size']
            yield item

    def parse_sku_item(self, response):
        sel = Selector(response)
        item = response.meta['item']
        index = response.meta['index']
        sku_size_list = response.meta['sku_size_list']
        sku_item_url_list = response.meta['sku_item_url_list']
        content = demjson.decode(response.body)
        newSizeData = Selector(text=content['newSizeData'])
        if index >= len(sku_size_list):
            item['sizes'] = sku_size_list
            yield item
        else:
            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['color'] = u'one color'
            skuItem['size'] = sku_size_list[index]
            skuItem['id'] = content['prodId']
            skuItem['from_site'] = self.name
            if len(newSizeData.xpath(".//div[@class='outOfStockMsg']")) > 0:
                skuItem['list_price'] = item['list_price']
                skuItem['current_price'] = item['current_price']
                skuItem['is_outof_stock'] = True
            else:
                skuItem['list_price'] = newSizeData.xpath(".//table/tbody/tr[1]/td/text()").extract()[0].strip()[1:]
                skuItem['current_price'] = newSizeData.xpath(".//td[@class='highlight']/text()").extract()[0].strip()[
                                           1:]
                skuItem['is_outof_stock'] = False
            item['skus'].append(skuItem)
            index = index + 1
            yield Request(sku_item_url_list[index], callback=self.parse_sku_item,
                          meta={"sku_size_list": sku_size_list, "sku_item_url_list": sku_item_url_list, "item": item,
                                "index": index})

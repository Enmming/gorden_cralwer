# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from urllib import quote
import re
import execjs

from scrapy.utils.response import get_base_url
import json

# import gc

# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

from gorden_crawler.spiders.shiji_base import BaseSpider

class LeviSpider(BaseSpider):
    name = "levi"
    allowed_domains = ["levi.com"]

    custom_settings = {
        # 'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'RETRY_TIMES': 40,
        'DOWNLOAD_TIMEOUT': 200,
        'DOWNLOADER_MIDDLEWARES': {
              # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,'
            'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        }
    }
    
    #正式运行的时候，start_urls为空，通过redis来喂养爬虫
    start_urls = [
        'http://www.levi.com/US/en_US/category/men/clothing/all',
        'http://www.levi.com/US/en_US/category/women/clothing/all',
        'http://www.levi.com/US/en_US/category/kids/boys/sizegroup/boys8to20-boys8to20husky-boys8to20slim',
        'http://www.levi.com/US/en_US/category/kids/boys/sizegroup/littleboys4to7',
        'http://www.levi.com/US/en_US/category/kids/girls/sizegroup/girls7to16',
        'http://www.levi.com/US/en_US/category/kids/girls/sizegroup/littlegirls4to6',
        'http://www.levi.com/US/en_US/category/kids/sizegroup/toddlerboys2tto4t-toddlergirls2tto4t',
        'http://www.levi.com/US/en_US/category/kids/baby/all',
        'http://www.levi.com/US/en_US/category/accessories/gender/male', #accessories无法区分出unisex
        'http://www.levi.com/US/en_US/category/accessories/gender/female'
        ]

    url_gender_product_type_map = {
        'http://www.levi.com/US/en_US/category/men/clothing/all':{'gender':'men', 'product_type':'clothing'},
        'http://www.levi.com/US/en_US/category/women/clothing/all':{'gender':'women', 'product_type':'clothing'},
        'http://www.levi.com/US/en_US/category/kids/boys/sizegroup/boys8to20-boys8to20husky-boys8to20slim':{'gender':'boys', 'product_type':'mother&baby'},
        'http://www.levi.com/US/en_US/category/kids/boys/sizegroup/littleboys4to7':{'gender':'boys', 'product_type':'mother&baby'},
        'http://www.levi.com/US/en_US/category/kids/girls/sizegroup/girls7to16':{'gender':'girls', 'product_type':'mother&baby'},
        'http://www.levi.com/US/en_US/category/kids/girls/sizegroup/littlegirls4to6':{'gender':'girls', 'product_type':'mother&baby'},
        'http://www.levi.com/US/en_US/category/kids/sizegroup/toddlerboys2tto4t-toddlergirls2tto4t':{'gender':'toddler', 'product_type':'mother&baby'},
        'http://www.levi.com/US/en_US/category/kids/baby/all':{'gender':'baby', 'product_type':'mother&baby'},
        'http://www.levi.com/US/en_US/category/accessories/gender/male':{'gender':'men', 'product_type':'accessories'}, 
        'http://www.levi.com/US/en_US/category/accessories/gender/female':{'gender':'women', 'product_type':'accessories'}
    }

    base_url = 'http://www.levi.com'
    #爬虫解析入口函数，用于解析丢入的第一个请求。每个请求对应一个大类

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    def parse(self, response):
        sel = Selector(response)

        gender = self.url_gender_product_type_map[response.url]['gender']
        product_type = self.url_gender_product_type_map[response.url]['product_type']

        categoryDom = sel.xpath(".//div[@id='facet-itemType']/ul/li")

        for cate in categoryDom:
            category = cate.xpath("./label/text()").extract()[0]
            category_uri = cate.xpath(".//@data-url").extract()
            # curr_url = response.url
            if category != 'All':
                if product_type == 'accessories' and category in ["Boots","Casual Shoes","Oxfords","Sneakers","Sandals & Flip-Flops","Heels","Flats"]:
                    product_type = 'shoes'

                url = self.base_url + category_uri[0]
                yield Request(url, callback=self.parse_list, meta={"list_uri":category_uri[0], "category":category, "gender":gender, "product_type":product_type})


    def parse_list(self,response):
        category = response.meta['category']
        gender = response.meta['gender']
        product_type = response.meta['product_type']

        sel = Selector(response)

        count = int(sel.xpath(".//*[@id='main-container']//*[@class='productCount']/text()").extract()[0])

        if count > 12:
            page = count / 12 + 1 if count % 12 > 0 else count / 12
            for x in range(12,page*12,12):
                list_more_url = self.base_url + '/US/en_US/includes/searchResultsScroll/?nao=' + str(x) + '&url=' + quote(response.meta['list_uri'])
                # print list_more_url
                # print '~~' * 30
                yield Request(list_more_url, callback=self.parse_list_more, meta={"category":category, "product_type":product_type,"gender":gender})

        if len(sel.xpath("//*[@id='container_results']/li").extract()) > 0:

            uriDoms = sel.xpath("//*[@id='container_results']/li")

            for dom in uriDoms:
                uri = dom.xpath('.//@data-product-url').extract()[0]
                item = BaseItem()
                item['from_site'] = 'levi'
                item['type'] = 'base'
                item['category'] = category
                item['product_type'] = product_type
                item['title'] = dom.xpath(".//p[@class='name']/text()").extract()[0]
                item['gender'] = gender
                item['colors'] = [dom.xpath(".//p[@class='finish']/text()").extract()[0]]
                item["show_product_id"] = dom.xpath('.//@data-product-id').extract()[0]
                item['cover'] = dom.xpath(".//img/@src").extract()[0]
                item["url"] = url = self.base_url + uri
                yield Request(url, callback=self.parse_item, meta={"item": item})
        else:
            return


    def parse_list_more(self,response):
        category = response.meta['category']
        product_type = response.meta['product_type']
        gender = response.meta['gender']

        sel = Selector(response)

        if len(sel.xpath("//*[@id='replacement-products']/li").extract()) > 0:

            uriDoms = sel.xpath("//*[@id='replacement-products']/li")
            genderRule = {"infant":"baby","newborn":"baby","baby":"baby","toddler":"toddler","little girls":"girls","little boys":"boys","girls":"girls","boys":"boys"}

            for dom in uriDoms:
                uri = dom.xpath('.//@data-product-url').extract()[0]
                item = BaseItem()
                item['from_site'] = 'levi'
                item['type'] = 'base'
                item['category'] = category
                item['product_type'] = product_type
                item['title'] = dom.xpath(".//p[@class='name']/text()").extract()[0]

                if gender == 'kids':
                    tmpTitle = re.findall(r"\w+",item['title'])
                    tmpGender = tmpTitle[0].lower()
                    if tmpGender in genderRule.keys():
                        gender = genderRule[tmpGender]
                    else:
                        tmpGender += ' ' + tmpTitle[1].lower()
                        if tmpGender in genderRule.keys():
                            gender = genderRule[tmpGender]

                item['gender'] = gender
                item['colors'] = [dom.xpath(".//p[@class='finish']/text()").extract()[0]]
                item["show_product_id"] = dom.xpath('.//@data-product-id').extract()[0]
                item['cover'] = dom.xpath(".//img/@src").extract()[0]
                item["url"] = url = self.base_url + uri
                yield Request(url, callback=self.parse_item, meta={"item": item})
        else:
            return

    def parse_item(self, response):
        item = response.meta['item']

        return self.handle_parse_item(response, item)

    def handle_parse_item(self,response,item):
        current_url = get_base_url(response)
        if current_url == 'http://www.levi.com/US/en_US/error' or current_url == 'http://global.levi.com':
            return

        buyJsonStr = "".join(re.findall(r'(var buyStackJSON = .*;[\s\S]*productCodeMaster\s*=[\s\S]*?;)[\s\S]*?</script>', response.body))
        context = execjs.compile('''
            %s
            function getBuyStackJSON(){
                return buyStackJSON;
            }
            function getProductCodeMaster(){
                return productCodeMaster;
            }
        ''' % buyJsonStr)
        
        stackJson = json.loads(context.call('getBuyStackJSON'))
        productMaster = str(context.call('getProductCodeMaster'))

        if productMaster not in stackJson['colorids']:
            return

        item["show_product_id"] = productMaster
        
        if 'name' in stackJson["colorid"][productMaster].keys():
            item['desc'] = stackJson["colorid"][productMaster]['name']
        item['list_price'] = stackJson["colorid"][productMaster]['price'][0]['amount']
        if len(stackJson["colorid"][productMaster]['price']) > 1:
            item['current_price'] = stackJson["colorid"][productMaster]['price'][1]['amount']
        else:
            item['current_price'] = item['list_price']

        altImgs = stackJson["colorid"][productMaster]['altViews']
        altZoomImgs = stackJson["colorid"][productMaster]['altViewsZoomPaths']
        imgDir = stackJson["colorid"][productMaster]['imageURL']


        images = []
        if len(altImgs):
            imgKey = 0
            for imgVal in altImgs:
                if re.search('alt\d*\-pdp\.jpg', imgVal)> -1:
                    imgDir = re.search(r'(.+' + productMaster[:5] +r').*', imgDir).group(1)
                    imgDir = imgDir +'-'
                imageItem = ImageItem()
                if imgVal[:6] == 'detail':
                    imageItem['image'] = imgDir + imgVal + stackJson["product"]['imageSizeDetail']
                    imageItem['thumbnail'] = imgDir + altZoomImgs[imgKey] + stackJson["product"]['imageSizeDetailThumbnail']
                else:
                    imageItem['image'] = imgDir + imgVal + stackJson["product"]['imageSizeHero']
                    imageItem['thumbnail'] = imgDir + altZoomImgs[imgKey] + stackJson["product"]['imageSizeThumbnail']
                images.append(imageItem)
                imgKey += 1

        colorItem = Color()
        colorItem['type'] = 'color'
        colorItem['from_site'] = item['from_site']
        colorItem['show_product_id'] = productMaster
        colorItem['images'] = images
        colorItem['name'] = stackJson["colorid"][productMaster]['finish']['title']
        colorItem['cover'] = stackJson["colorid"][productMaster]['swatch']
        
        color_name = colorItem['name'] 
        
        yield colorItem


        item['skus'] = []

        item['dimensions'] = []
        item['sizes'] = {}
        if len(stackJson["attrs"]['waist']) > 0:
            item['dimensions'].append('waist')
            item['sizes']['waist'] = stackJson["attrs"]['waist']

        if len(stackJson["attrs"]['length']) > 0:
            item['dimensions'].append('length')
            item['sizes']['length'] = stackJson["attrs"]['length']

        if len(stackJson["attrs"]['size']) > 0:
            item['dimensions'].append('size')
            item['sizes']['size'] = stackJson["attrs"]['size']

        # #有货的未处理
        if stackJson["sku"]:
            for sku in stackJson["sku"]:
                if stackJson["sku"][sku]['colorid'] == productMaster:
                    
                    is_continue = False
                    sku_keys = stackJson["sku"][sku].keys()
                    for one_dimension in item['dimensions']:
                        if one_dimension not in sku_keys:
                            is_continue = True
                            break
                    
                    if is_continue:
                        continue
                    
                    skuItem = {}
                    skuItem['type'] = 'sku'
                    skuItem['show_product_id'] = stackJson["sku"][sku]['colorid']
                    skuItem['id'] = stackJson["sku"][sku]['skuid']
                    skuItem['list_price'] = stackJson["sku"][sku]['price'][0]['amount']
                    if stackJson["sku"][sku]['finalsale']:
                        skuItem['current_price'] = stackJson["sku"][sku]['price'][1]['amount']
                    else:
                        skuItem['current_price'] = skuItem['list_price']
                    skuItem['color'] = color_name #item['colors'][0]
                    
                    if 'size' in stackJson["sku"][sku]:
                        skuItem['size'] = stackJson["sku"][sku]['size']
                    elif 'waist' in stackJson["sku"][sku] and 'length' in stackJson["sku"][sku]:
                        skuItem['size'] = {'waist':stackJson["sku"][sku]['waist'],'length':stackJson["sku"][sku]['length']}
                    elif 'sizedescription' in stackJson["sku"][sku]:
                        skuItem['size'] = stackJson["sku"][sku]['sizedescription']

                    skuItem['from_site'] = 'levi'
                    skuItem['quantity'] = stackJson["sku"][sku]['stock']
                    skuItem['is_outof_stock'] = False
                    item['skus'].append(skuItem)
                    yield skuItem
#         print skuItem
#         print '* ' * 20

        item['colors'] = [color_name]
        


        sel = Selector(response)
        item['brand'] = sel.xpath(".//div[@id='main-container']//meta[@itemprop='brand']/@content").extract()[0]
        size_chart_dom = sel.xpath(".//div[@class='pdp-sizing']/div[@class='pdp-sizes pdp-size-sizes']/a")
        if len(size_chart_dom.extract()):
            size_chart = size_chart_dom.xpath("./p/text()").extract()[0]
            if size_chart == 'Size Chart':
                item['size_info'] = size_chart_dom.xpath("./@href").extract()[0]
                
        yield item
        # gc.collect()

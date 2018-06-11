# -*- coding: utf-8 -*-
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
import re
import execjs
from gorden_crawler.spiders.shiji_base import BaseSpider
from gorden_crawler.utils.debugger import trace


class EastDaneSpider(BaseSpider):
    # class EastDaneSpider(RedisSpider):
    name = "eastdane"
    allowed_domains = ["eastdane.com"]
    start_urls = []
    product_id_type_category_map = {
        '19207' : {'product_type': 'clothing', 'category': 'shirts'},
        '19208' : {'product_type': 'clothing', 'category': 'jeans'},
        '19209' : {'product_type': 'clothing', 'category': 'outerwear'},
        '19210' : {'product_type': 'clothing', 'category': 'pants'},
        '19211' : {'product_type': 'clothing', 'category': 'polos&tees'},
        '19212' : {'product_type': 'clothing', 'category': 'shorts&swim'},
        '19213' : {'product_type': 'clothing', 'category': 'suits&blazers'},
        '19214' : {'product_type': 'clothing', 'category': 'sweaters'},
        '19215' : {'product_type': 'clothing', 'category': 'sweatshirts'},
        '19216' : {'product_type': 'clothing', 'category': 'underwear'},
        '19217' : {'product_type': 'shoes', 'category': 'boots'},
        '19218' : {'product_type': 'shoes', 'category': 'lace-ups'},
        '19219' : {'product_type': 'shoes', 'category': 'loafers&slip-ons'},
        '19220' : {'product_type': 'shoes', 'category': 'sandals'},
        '19221' : {'product_type': 'shoes', 'category': 'sneakers'},
        '19222' : {'product_type': 'accessories', 'category': 'bags'},
        '19223' : {'product_type': 'accessories', 'category': 'belts'},
        '19224' : {'product_type': 'accessories', 'category': 'hats,scarves&golves'},
        '19225' : {'product_type': 'accessories', 'category': 'jewelry'},
        '19226' : {'product_type': 'accessories', 'category': 'home&gifts'},
        '19227' : {'product_type': 'accessories', 'category': 'sunglasses'},
        '19228' : {'product_type': 'accessories', 'category': 'tech accessories'},
        '19229' : {'product_type': 'accessories', 'category': 'ties&pocket squares'},
        '19230' : {'product_type': 'accessories', 'category': 'travel accessories'},
        '19231' : {'product_type': 'accessories', 'category': 'wallets&money clips'},
        '19232' : {'product_type': 'accessories', 'category': 'watches'},
        '20262' : {'product_type': 'accessories', 'category': 'socks'}
    }
    def __init__(self, init_start_urls=False, *args, **kwargs):
        super(EastDaneSpider, self).__init__(*args, **kwargs)

        for filter_context in range(19207, 19233):
            url = 'https://www.eastdane.com/actions/updateFilterOptions.action?department=' + \
                str(filter_context) + '&filterContext=' + \
                str(filter_context) + '&&baseIndex=0'
            self.start_urls.append(url)
        other_url = 'https://www.eastdane.com/actions/updateFilterOptions.action?department=20262&sortBy.sort=PRIORITY%3ANATURAL&filterContext=20262&tDim=220x390&swDim=18x17&baseIndex=0'
        self.start_urls.append(other_url)

    base_item_image_uri_suffix = 'https://images-na.ssl-images-amazon.com/images/G/01/Shopbop/p/'
    base_url = 'http://www.eastdane.com'

    def handle_parse_item(self, response, baseItem):
        
        sel = Selector(response)
        
        product_id = sel.xpath('//div[@id="productId"]/text()').extract()[0]
        
        baseItem['gender'] = 'men'
        baseItem['type'] = 'base'
        baseItem['from_site'] = self.name
        baseItem['show_product_id'] = product_id
        
        baseItem['title'] = sel.xpath(
            '//span[@class="row product-title"]/text()').extract()[0].strip()
        size_fit_container = sel.xpath('//div[@id="sizeFitContainer"]')
        if len(size_fit_container)>0:
            size_fit = size_fit_container.extract()[0]
            baseItem['desc'] = '<div>'+sel.xpath('//div[@itemprop="description"]').extract()[0]+size_fit+"</div>"
        else:
            baseItem['desc'] = sel.xpath('//div[@itemprop="description"]').extract()[0]
        baseItem['dimensions'] = ['size', 'color']
        skus = []
        product_detail_str = "".join(re.findall(
            r"var\s+productDetail[^;]+", response.body))
        if len(product_detail_str) > 0:
            context = execjs.compile('''
                %s
                function get_product_detail(){
                    return productDetail;
                    }
            ''' % (product_detail_str))
        product_detail = context.call('get_product_detail')
        size_js_infos = product_detail['sizes']
        size_infos = {}
        size_values = []
        for size_id in size_js_infos:
            size_infos[size_js_infos[size_id]['sizeCode']] = size_id
            size_values.append(size_id)
        list_price = sel.xpath(
            '//div[@id="productPrices"]//meta[@itemprop="price"]/@content').extract()[0]
        color_price_blocks = sel.xpath(
            '//div[@id="productPrices"]//div[@class="priceBlock"]')
#         color_price_mapping = {}
#         for color_price_block in color_price_blocks:
#             color_name = color_price_block.xpath(
#                 './span[@class="priceColors"]/text()').extract()
#             if len(color_name) > 0:
#                 regular_price_span = color_price_block.xpath(
#                     './span[@class="regularPrice"]/text()').extract()
#                 if len(regular_price_span) > 0:
#                     color_price_mapping[color_name[0]] = regular_price_span[0]
#                 else:
#                     color_price_mapping[color_name[0]] = color_price_block.xpath(
#                         './span[@class="salePrice"]/text()').extract()[0]
        match = re.search(r'productPage\.sellingPrice\=\'([\d\.]+)\';', response.body)
        if match is None:
            current_price = list_price
        else:
            current_price = match.group(1)

        image_items = product_detail['colors']
        color_names = []
        for key in image_items:
            imageItems = image_items[key]['images']
            color_name = image_items[key]['colorName'].strip()+'-'+str(key)
            color_names.append(color_name)
            images = []
            tmp_images = []
            for image_key in imageItems:
                imageItem = ImageItem()
                image = imageItems[image_key]
                imageItem['thumbnail'] = image['thumbnail']
                imageItem['image'] = image['zoom']
                tmp_images.append((image['index'], imageItem))
            tmp_images = sorted(tmp_images, key=lambda x: x[0])
            for tmp_tuple in tmp_images:
                images.append(tmp_tuple[1])
            colorItem = Color()
            colorItem['type'] = 'color'
            colorItem['show_product_id'] = baseItem['show_product_id']
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
                skuItem['show_product_id'] = baseItem['show_product_id']
                skuItem['id'] = key + "-" + size
                skuItem['size'] = size_name
                skuItem['list_price'] = list_price
                skuItem['current_price'] = current_price
#                 if len(color_price_mapping) > 0 and color_name in color_price_mapping.keys():
#                     skuItem['current_price'] = color_price_mapping[
#                         colorItem['name']]
#                 else:
#                     skuItem['current_price'] = skuItem['list_price']
                skuItem['is_outof_stock'] = False
                skus.append(skuItem)
        baseItem['sizes'] = size_values
        baseItem['colors'] = color_names
        baseItem['skus'] = skus

        product_items = sel.xpath('//ul[@id="similarities"]/li[@class="product"]')
        if len(product_items) > 0:
            related_items_id = []
            for product_item in product_items:
                product_id = product_item.xpath('./div/div[@class="info"]/img/@data-product-id').extract()[0]
                related_items_id.append(product_id)
            if related_items_id:
                baseItem['related_items_id'] = related_items_id
        yield baseItem

    def parse_item(self, response):
        baseItem = response.meta['baseItem']
        return self.handle_parse_item(response, baseItem)

    def parse(self, response):
        url = response.url
        response_body_str = response.body
        response_body_str_replace_false = re.sub(
            r'false', 'False', response_body_str)
        response_body_str_replace_true = re.sub(
            r'true', 'True', response_body_str_replace_false)
        response_body = eval(response_body_str_replace_true)
        results = response_body['responseData']['results']
        if url in self.start_urls:
            metadata = results['metadata']
            total_items = metadata['totalProductCount']
            temp1 = total_items / 40
            temp2 = total_items % 40
            if temp2 == 0:
                total_pages = temp1
            else:
                total_pages = temp1 + 1
            page_num = 1
        else:
            page_num = response.meta['page_num']
            total_pages = response.meta['total_pages']

        #yield Request(url, callback=self.parse_page, meta={'results': results})
        #results = response.meta['results']
        metadata = results['metadata']
        filter_context = metadata['filterContext']
        products = results['products']
        product_type = self.product_id_type_category_map[filter_context]['product_type']
        category = self.product_id_type_category_map[filter_context]['category']
        for product in products:
            baseItem = BaseItem()
            baseItem['product_type'] = product_type
            baseItem['category'] = category
            baseItem['show_product_id'] = product['productId']
            baseItem['list_price'] = product['price']['retail']
            baseItem['current_price'] = product['price']['high']
            baseItem['brand'] = product['brand']
            baseItem['url'] = self.base_url + product['productDetailLink']
            baseItem['cover'] = self.base_item_image_uri_suffix + \
                product['colors'][0]['productImage']
            yield Request(baseItem['url'], callback=self.parse_item, meta={'baseItem': baseItem})

        if total_pages > page_num:
            page_num = page_num+1
            base_index = (page_num-1) * 40
            page_url = re.sub(r'baseIndex=\d+',('baseIndex=' + str(base_index)), url)
            yield Request(page_url, callback=self.parse, meta={"page_num": page_num, 'total_pages': total_pages})
    
    
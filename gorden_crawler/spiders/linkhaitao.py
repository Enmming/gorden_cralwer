from scrapy.selector import Selector
from scrapy import Request
from scrapy import Spider
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from gorden_crawler.spiders.shiji_base import BaseSpider
import json
import os
import re
from urllib import unquote


class LinkhaitaoSpider(Spider):
    name = 'linkhaitao'
    start_urls = []
    goods_detail_url = 'http://120.26.117.54:8889/searchht/detailAll'
    token = 'd8b97d6ec14e3087fc029607747dd0b3'
    editor_flag = None
    gender = None
    product_type_id = 0
    category_id = 0

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 10,

        'ITEM_PIPELINES': {
            'gorden_crawler.pipelines.mongodb.SingleMongodbPipeline': 303,
            'gorden_crawler.pipelines.realtime_handle_image.RealtimeHandleImage': 305,
        }
    }

    def __init__(self, name='linkhaitao', url=None, editor_flag=None, gender=None, product_type_id=0, category_id=0, *args, **kwargs):
        super(LinkhaitaoSpider, self).__init__(name, **kwargs)
        if url:
            self.start_urls = [unquote(url)]
        self.editor_flag = editor_flag
        self.gender = gender
        self.product_type_id = product_type_id
        self.category_id = category_id
        os.environ['main_process'] = 'True'
        os.environ['linkhaitao_spider'] = 'True'
        os.environ['need_size_transform'] = 'True'

    def parse(self, response):
        body_json = json.loads(response.body)
        goods_details = body_json['data']['goods']
        total_count = int(body_json['total_count'])
        limit = int(re.search('limit=([\d]+)',response.url).group(1))
        offset = re.search('offset=([\d]+)', response.url).group(1)
        for goods_detail in goods_details:
            item = BaseItem()
            item['type'] = 'base'
            url = self.goods_detail_url + '?token=' + self.token + '&spuid=' + goods_detail['DOCID']
            yield Request(url, callback=self.parse_item, meta={"item": item}, dont_filter=True)

        if int(offset) + limit < int(total_count):
            next_url = re.sub('offset=([\d]+)', 'offset='+str((int(offset)/limit+1)*limit), response.url)
            yield Request(next_url, callback=self.parse)

    def parse_item(self, response):
        item = response.meta['item']
        return self.handle_parse_item(response, item)

    def handle_parse_item(self, response, item):
        body_json = json.loads(response.body)
        goods_detail = body_json['data']
        if goods_detail['inStock'] == 0:
            return
        item['linkhaitao_url'] = response.url
        item['cover'] = goods_detail['coverImgUrl']
        item['desc'] = goods_detail['content']['description']

        if 'product_type_id' in os.environ.keys():
            self.product_type_id = os.environ['product_type_id']
        if 'category_id' in os.environ.keys():
            self.category_id = os.environ['category_id']
        if self.product_type_id:
            item['product_type_id'] = int(self.product_type_id)
            item['product_type'] = 'linkhaitao_' + str(self.product_type_id)
        if self.category_id:
            item['category_id'] = int(self.category_id)
            item['category'] = 'linkhaitao_' + str(self.category_id)

        if 'editor_flag' in os.environ.keys():
            self.editor_flag = os.environ['editor_flag']
        if self.editor_flag:
            item['editor_flag'] = self.editor_flag
        if 'gender' in os.environ.keys():
            self.gender = os.environ['gender']
        if self.gender:
            item['gender'] = self.gender

        item['dimensions'] = ['size', 'color']
        item['brand'] = goods_detail['brand']['name_en']
        item['title'] = goods_detail['name']
        item['current_price'] = goods_detail['realPriceOrg']
        item['list_price'] = goods_detail['mallPriceOrg']
        from_site = ''.join(goods_detail['sellerName']['namecn'].split()).lower()
        if self.is_chinese_word(from_site):
            from_site = ''.join(goods_detail['sellerName']['namecn'].split()).lower()
        if "'" in from_site:
            from_site = from_site.replace("'", "")
        if '/' in from_site:
            from_site = from_site.split('/')[0]
        item['from_site'] = from_site
        if item['from_site'] == '6pm' or item['from_site'] == '6pm/6pm':
            item['from_site'] = 'sixpm'
        spu_id = re.search('spuid=(.+)&?',response.url)
        if spu_id:
            spu_id = spu_id.group(1)
        else:
            spu_id = re.search('&spu=(.+)&?',response.url).group(1)
        item['show_product_id'] = spu_id
        item['url'] = goods_detail['pageUrl']
        if self.editor_flag:
            item['editor_flag'] = self.editor_flag

        if not goods_detail['skuInfo']:
            colorItem = Color()
            images = []
            color_names = []
            skus=[]
            for image in goods_detail['coverImgList']:
                imageItem = ImageItem()
                imageItem['image'] = image
                imageItem['thumbnail'] = image
                images.append(imageItem.copy())
            colorItem['images'] = images
            colorItem['type'] = 'color'
            colorItem['from_site'] = item['from_site']
            colorItem['show_product_id'] = item['show_product_id']
            color_name = 'One Color'
            if color_name not in color_names:
                color_names.append(color_name)
            colorItem['name'] = color_name
            colorItem['cover'] = goods_detail['coverImgUrl']
            yield colorItem

            skuItem = SkuItem()
            skuItem['type'] = 'sku'
            skuItem['show_product_id'] = item['show_product_id']
            skuItem['list_price'] = item['list_price']
            skuItem['current_price'] = item['current_price']
            skuItem['color'] = color_name
            skuItem['id'] = item['show_product_id'] + 'onecolor'
            skuItem['from_site'] = item['from_site']
            if goods_detail['inStock'] == 0:
                skuItem['is_outof_stock'] = True
            skuItem['size'] = 'One Size'
            skus.append(skuItem)
            item['sizes'] = ['One Size']
        else:
            skus_info = goods_detail['skuInfo']['style']['skustylelist']
            color_names = []
            skus = []
            sizes = []
            dimensions_values = {}
            for sku_info in skus_info:
                colorItem = Color()
                images = []
                for image in sku_info['coverImgList']:
                    imageItem = ImageItem()
                    imageItem['image'] = image
                    imageItem['thumbnail'] = image
                    images.append(imageItem.copy())
                colorItem['images'] = images
                colorItem['type'] = 'color'
                colorItem['from_site'] = item['from_site']
                colorItem['show_product_id'] = item['show_product_id']
                if sku_info['style']:
                    color_name = sku_info['style']
                else:
                    color_name = 'One Color'
                if color_name not in color_names:
                    color_names.append(color_name)
                colorItem['name'] = color_name
                colorItem['cover'] = images[0]['image']
                yield colorItem

                for sku in sku_info['data']:
                    skuItem = SkuItem()
                    skuItem['type'] = 'sku'
                    skuItem['show_product_id'] = item['show_product_id']
                    skuItem['list_price'] = sku['mallPriceOrg']
                    skuItem['current_price'] =sku['realPriceOrg']
                    skuItem['color'] = color_name
                    skuItem['id'] = sku['skuid']
                    skuItem['from_site'] = item['from_site']
                    if sku['inStock'] == 0:
                        skuItem['is_outof_stock'] = True
                    if len(sku['attr']) == 0:
                        skuItem['size'] = 'One Size'
                        if skuItem['size'] not in sizes:
                            sizes.append(skuItem['size'])
                    else:
                        skuItem['size'] = {}
                        for attr in sku['attr']:
                            skuItem['size'][attr['attrName'].lower()] = attr['attrValue']
                            if attr['attrName'].lower() not in item['dimensions']:
                                item['dimensions'].append(attr['attrName'].lower())
                            if attr['attrName'].lower() not in dimensions_values.keys():
                                dimensions_values[attr['attrName'].lower()] = [attr['attrValue']]
                            else:
                                dimensions_values[attr['attrName'].lower()].append(attr['attrValue'])
                        if 'size' not in skuItem['size'].keys():
                            skuItem['size']['size'] = 'One Size'
                            dimensions_values['size'] = 'One Size'
                    skus.append(skuItem)
            if sizes:
                item['sizes'] = sizes
            elif dimensions_values:
                item['sizes'] = dimensions_values
            else:
                return
        item['skus'] = skus
        item['colors'] = color_names
        yield item

    def is_chinese_word(self, text):
        return all(u'\u4e00' <= char <= u'\u9fff' for char in text)

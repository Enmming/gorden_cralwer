# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color, DiapersSizeInfoItem
from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from random import random
import re
from urllib import quote
from gorden_crawler.spiders.shiji_base import BaseSpider
import json
import execjs

class DiapersBaseSpider(object):

    custom_settings = {
        #'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_TIMEOUT': 30,
    }

    from_site = "diapers"

    def change_out_of_stock_str(self, stock_str):
        if stock_str.lower() == 'n':
            return False
        else:
            return True

    def parse_size_info(self, response):

        sel = Selector(response)

        diapersSizeInfoItem = DiapersSizeInfoItem()

        diapersSizeInfoItem['size_type'] = sel.xpath('//span[@class="sizeType"]/text()').extract()[0].strip()
        diapersSizeInfoItem['brand_name'] = response.meta['brand_name']
        diapersSizeInfoItem['size_chart_type'] = response.meta['size_chart_type']

        columns = sel.xpath('//div[@class="sizeInfoTable"]//dl')

        size_info = []

        for column in columns:
            key = column.xpath('./dt/div/text()').extract()[0].strip()

            key = key.replace('.', '')

            values = column.xpath('./dd/div/text()').extract()

            for index in range(len(values)):
                if index > len(size_info) - 1:
                    size_info.append({key: values[index].strip()})
                else:
                    size_info[index][key] = values[index].strip()

        diapersSizeInfoItem['size_info'] = size_info
        diapersSizeInfoItem['type'] = 'diapers_size_info'

        yield diapersSizeInfoItem

    def parse_image(self, response):

        color_item = response.meta['item']
        show_product_id = response.meta['show_product_id']

        sel = Selector(response)

        image_boxs = sel.css('.magicThumbBox .clickStreamTag')

        images = []

        for image_box in image_boxs:

            imageItem = ImageItem()

            image = image_box.xpath('@href').extract()[0]
            thumbnail = image_box.xpath('//img/@src').extract()[0]

            if re.match(r'^//', image):
                image = 'https:' + image

            if re.match(r'^//', thumbnail):
                thumbnail = 'https:' + thumbnail

            imageItem['image'] = image
            imageItem['thumbnail'] = thumbnail

            images.append(imageItem)
        if 'cover' not in color_item or 'cover_style' not in color_item:
            color_item['cover'] = images[0]['thumbnail']
        color_item["images"] = images
        color_item['show_product_id'] = show_product_id

        yield color_item

    def handle_parse_item(self, response, item):
        sel = Selector(response)

        product_id_var = re.search(r'var pr_page_id[\s]*=[\s]*([^;]+);', response.body)
        if not product_id_var:
            return
        # if len(sel.xpath('//div[@class="outOfStock outOfStockSpecial"]')) > 0:
        #     return
        product_id = eval(product_id_var.group(1))
        item['show_product_id'] = product_id

        templateid = sel.xpath('//div[@id="templateOption"]/@templateid').extract()

        if len(templateid) > 0:
            templateid = templateid[0]

        color_rows = sel.xpath('//tr[contains(@class, "diaperItemTR")]')
        clothing_shoes_products = sel.xpath('//div[contains(@class, "clothingShoesProducts")]')

        if templateid == '6':
            ''''''
            colorItems = {}
            colorNames = []

            oneColorDiv = sel.xpath('//div[@id="oneSelection"]')
            if len(oneColorDiv.extract()) > 0:
                colorItem = Color()

                color_cover = oneColorDiv.xpath(".//img/@src").extract()[0]

                if re.match(r'^//', color_cover):
                    color_cover = 'https:' + color_cover

                color_name = oneColorDiv.xpath("text()").extract()[0]

                colorItem["cover"] = color_cover

                colorItem["name"] = color_name
                colorItem['type'] = 'color'
                colorItem['from_site'] = self.from_site

                colorItems[color_name] = {"item": colorItem, "handled": False}

                colorNames.append(color_name)
            else:
                colorDivs = sel.xpath('//ul[@id="falvorDrownList"]/li')
                #colorDivs = sel.xpath('//div[contains(@class, "clothingShoesProducts")]/div[contains(@class, "clothProductItem")]//div[contains(@class, "colorPaneItems")]');

                for colorDiv in colorDivs:
                    colorItem = Color()

                    color_cover = colorDiv.xpath(".//img/@src").extract()[0]

                    if re.match(r'^//', color_cover):
                        color_cover = 'https:' + color_cover

                    color_name = colorDiv.xpath("@id").extract()[0]
                    colorItem["cover"] = color_cover

                    colorItem["name"] = color_name
                    colorItem['type'] = 'color'
                    colorItem['from_site'] = self.from_site

                    colorItems[color_name] = {"item": colorItem, "handled": False}

                    colorNames.append(color_name)

            skuHiddens = sel.css('.multiItemBox').xpath('.//input[@class="skuHidden"]')#sel.xpath('//div[@id="clothItem"]//input[@class="skuHidden"]')

            skus = []
            sizes = []
            if len(skuHiddens) > 0:
                for skuHidden in skuHiddens:
                    if skuHidden.xpath('@value').extract()[0] !=  "":

                        skuItem = SkuItem()
                        skuItem['show_product_id'] = item['show_product_id']

                        regular_price = skuHidden.xpath('@regularprice').extract()
                        price = skuHidden.xpath('@price').extract()[0]
                        skuid = skuHidden.xpath('@value').extract()[0]
                        is_outof_stock = skuHidden.xpath('@isoutofstock').extract()[0]
                        skuItem['id'] = skuid

                        if len(regular_price) > 0 and regular_price[0] != '':
                            skuItem["list_price"] = regular_price[0]
                        else:
                            skuItem["list_price"] = price

                        skuItem['current_price'] = price

                        replace_skuid = skuid.replace('-', '_')
                        size = sel.xpath('//ul[@id="diaperItemTR'+replace_skuid+'"]//li[@class="itemSize"]/span/text()').extract()[0].strip()
                        color_name = sel.xpath('//ul[@id="diaperItemTR'+replace_skuid+'"]/@primaryattr').extract()[0]

                        skuItem['size'] = size

                        if not size in sizes:
                            sizes.append(size)

                        skuItem['color'] = color_name
                        skuItem['is_outof_stock'] = self.change_out_of_stock_str(is_outof_stock)

                        skuItem['type'] = 'sku'
                        skuItem['from_site'] = self.from_site
                        #yield skuItem

                        skus.append(skuItem)

                        if colorItems[color_name]["handled"] == False:

                            colorItems[color_name]["handled"] = True

                            url = 'https://www.diapers.com/product/productDetail!GetSkuImage.qs?skuCode='+skuid+'&random='+'%f' %random()

                            yield Request(url, meta={'item': colorItems[color_name]['item'], 'show_product_id': item['show_product_id']}, callback=self.parse_image)

                item["skus"] = skus
                item['sizes'] = sizes
                item['colors'] = colorNames

        elif len(color_rows.extract()) > 0:
            '''只有一个尺寸表格'''
            skus = []
            colorNames = []
            for color_row in color_rows:

                colorItem = Color()
                colorItem['from_site'] = self.from_site
                colorItem['type'] = 'color'

                skuHidden = color_row.xpath('.//input[@class="skuHidden"]')

                skuItem = SkuItem()
                skuItem['show_product_id'] = item['show_product_id']

                regular_price = skuHidden.xpath('@regularprice').extract()
                price = skuHidden.xpath('@price').extract()[0]
                skuid = skuHidden.xpath('@value').extract()[0]
                is_outof_stock = skuHidden.xpath('@isoutofstock').extract()[0]
                skuItem['id'] = skuid
                # print response.url
                # print is_outof_stock
                # print skuHidden.extract()
                if len(regular_price) > 0 and regular_price[0] != '':
                    skuItem["list_price"] = regular_price[0]
                else:
                    skuItem["list_price"] = price

                skuItem['current_price'] = price

                color_cover = color_row.xpath('td[@class="itemImage"]/span[contains(@class, "itemImageDiv")]/img/@src').extract()[0]

                if re.match(r'^//', color_cover):
                    color_cover = 'https:' + color_cover
                colorItem['cover'] = color_cover

                color_name = color_row.xpath('td[contains(@class, "Description")]/text()').extract()

                if len(color_name) > 0:
                    color_name = color_name[0].strip()
                else:
                    color_name = color_row.xpath('td[contains(@class, "elseDescription")]/text()').extract()
                    if len(color_name) > 0:
                        color_name = color_name[0].strip()
                    else:
                        color_name = color_row.xpath('td[contains(@class, "itemDescription")]/text()').extract()
                        if len(color_name) >0 :
                            color_name = color_name[0].strip()

                if not color_name:
                    color_name = 'onecolor'

                colorItem['name'] = color_name
                colorNames.append(color_name)

                skuItem['color'] = color_name
                skuItem['size'] = 'onesize'
                skuItem['is_outof_stock'] = self.change_out_of_stock_str(is_outof_stock)

                skuItem['type'] = 'sku'
                skuItem['from_site'] = self.from_site
                #yield skuItem

                skus.append(skuItem)

                url = 'https://www.diapers.com/product/productDetail!GetSkuImage.qs?skuCode='+skuid+'&random='+'%f' %random()

                yield Request(url, meta={'item': colorItem, 'show_product_id': item['show_product_id']}, callback=self.parse_image)

            item["skus"] = skus
            item['sizes'] = ['onesize']
            item['colors'] = colorNames

        elif len(clothing_shoes_products) > 0:
            '''最常见的格式'''
            colorDivs = sel.xpath('//div[contains(@class, "clothingShoesProducts")]/div[contains(@class, "clothProductItem")]//div[contains(@class, "colorPaneItems")]');
            colorItems = {}
            colorNames = []
            for colorDiv in colorDivs:
                colorItem = Color()

                if len(colorDiv.xpath('./img').extract()) > 0:
                    color_cover = colorDiv.xpath("./img/@src").extract()[0]

                    if re.match(r'^//', color_cover):
                        color_cover = 'https:' + color_cover

                    color_name = colorDiv.xpath("./img/@color").extract()[0]
                    colorItem["cover"] = color_cover
                elif len(colorDiv.xpath("./div/@style").extract()) > 0:
                    cover_style = colorDiv.xpath("./div/@style").extract()[0]
                    color_name = colorDiv.xpath("./div/@color").extract()[0]
                    if 'background:' in cover_style:
                        cover_style = re.search('background:([^;]+)', cover_style).group(1)
                    colorItem["cover_style"] = cover_style
                else:
                    return

                colorItem["name"] = color_name
                colorItem['type'] = 'color'
                colorItem['from_site'] = self.from_site

                colorItems[color_name] = {"item": colorItem, "handled": False}

                colorNames.append(color_name)

            skuHiddens = sel.xpath('//div[@id="clothItem"]//input[@class="skuHidden"]')

            skus = []
            sizes = []
            if len(skuHiddens) > 0:
                for skuHidden in skuHiddens:
                    if skuHidden.xpath('@value').extract()[0] !=  "":
                        skuItem = SkuItem()
                        skuItem['show_product_id'] = item['show_product_id']

                        regular_price = skuHidden.xpath('@regularprice').extract()
                        price = skuHidden.xpath('@price').extract()[0]
                        skuid = skuHidden.xpath('@value').extract()[0]
                        is_outof_stock = skuHidden.xpath('@isoutofstock').extract()[0]
                        skuItem['id'] = skuid

                        if len(regular_price) > 0 and regular_price[0] != '':
                            skuItem["list_price"] = regular_price[0]
                        else:
                            skuItem["list_price"] = price

                        skuItem['current_price'] = price

                        size = sel.xpath('//div[@id="clothItem"]//input[@sku="'+skuid+'"]/@value').extract()[0]
                        color_name = sel.xpath('//div[@id="clothItem"]//input[@sku="'+skuid+'"]/@primaryattributevalue').extract()[0]

                        skuItem['size'] = size

                        if not size in sizes:
                            sizes.append(size)

                        skuItem['color'] = color_name
                        skuItem['is_outof_stock'] = self.change_out_of_stock_str(is_outof_stock)

                        skuItem['type'] = 'sku'
                        skuItem['from_site'] = self.from_site
                        #yield skuItem

                        skus.append(skuItem)
                        if colorItems[color_name]["handled"] == False:

                            colorItems[color_name]["handled"] = True

                            url = 'https://www.diapers.com/product/productDetail!GetSkuImage.qs?skuCode='+skuid+'&random='+'%f' %random()

                            yield Request(url, meta={'item': colorItems[color_name]['item'], 'show_product_id': item['show_product_id']}, callback=self.parse_image)

                item["skus"] = skus
                item['sizes'] = sizes
                item['colors'] = colorNames

        elif len(sel.xpath('//div[@id="templateOption"]/div[contains(@class, "colorSizeFirstStep")]//li[contains(@class, "colorPaneItems")]').extract()) > 0:
            '''判断是否是只有颜色没有尺寸的情况'''
            colorDivs = sel.xpath('//div[@id="templateOption"]/div[contains(@class, "colorSizeFirstStep")]//li[contains(@class, "colorPaneItems")]')
            colorItems = {}
            colorNames = []
            skus = []
            for colorDiv in colorDivs:
                colorItem = Color()

                if len(colorDiv.xpath('./img').extract()) > 0:
                    color_cover = colorDiv.xpath("./img/@src").extract()[0]

                    if re.match(r'^//', color_cover):
                        color_cover = 'https:' + color_cover

                    color_name = colorDiv.xpath("./img/@color").extract()[0]
                    colorItem["cover"] = color_cover
                else:
                    cover_style = colorDiv.xpath("./div/@style").extract()[0]
                    color_name = colorDiv.xpath("./div/@color").extract()[0]
                    if 'background:' in cover_style:
                        cover_style = re.search('background:([^;]+)', cover_style).group(1)
                    colorItem["cover_style"] = cover_style

                colorItem["name"] = color_name
                colorItem['type'] = 'color'
                colorItem['from_site'] = self.from_site

                colorItems[color_name] = {"item": colorItem, "handled": False}

                colorNames.append(color_name)

                skuid = colorDiv.xpath('./img/@sku').extract()[0]

                skuHidden = sel.xpath('//input[@id="skuHidden'+skuid.replace('-', '_')+'"]')

                skuItem = SkuItem()
                skuItem['show_product_id'] = item['show_product_id']

                regular_price = skuHidden.xpath('@regularprice').extract()
                price = skuHidden.xpath('@price').extract()[0]
                is_outof_stock = skuHidden.xpath('@isoutofstock').extract()[0]
                skuItem['id'] = skuid

                if len(regular_price) > 0 and regular_price[0] != '':
                    skuItem["list_price"] = regular_price[0]
                else:
                    skuItem["list_price"] = price

                skuItem['current_price'] = price
                size = 'onesize'

                skuItem['size'] = size

                skuItem['color'] = color_name
                skuItem['is_outof_stock'] = self.change_out_of_stock_str(is_outof_stock)

                skuItem['type'] = 'sku'
                skuItem['from_site'] = self.from_site
                #yield skuItem

                skus.append(skuItem)

                url = 'https://www.diapers.com/product/productDetail!GetSkuImage.qs?skuCode='+skuid+'&random='+'%f' %random()

                yield Request(url, meta={'item': colorItem, 'show_product_id': item['show_product_id']}, callback=self.parse_image)

            item['sizes'] = ['onesize']
            item["skus"] = skus
            item['colors'] = colorNames

        elif len(sel.xpath('//div[@id="templateOption"]/div[contains(@class, "colorSizeFirstStep")]').extract()) > 0:
            colorItem = Color()
#             print sel.xpath('//div[@id="QtyInputDiv"]//li[contains(@class,"itemImage")]').extract()
#             color_cover = sel.xpath('//div[@id="QtyInputDiv"]//li[contains(@class,"itemImage")]//img/@src').extract()[0]
            color_name = 'onecolor'

#             colorItem['cover'] = color_cover
            colorItem['name'] = color_name
            colorItem['type'] = 'color'
            colorItem['from_site'] = self.from_site

            sku_sizes = sel.css('.colorSizeFirstStep .collectionSelections').xpath('./li/input')

            skus = []
            sizes = []
            colorItemSku = ''
            for sku_size in sku_sizes:
                ''''''
                skuItem = SkuItem()
                skuItem['show_product_id'] = item['show_product_id']

                skuid = sku_size.xpath('@sku').extract()[0]
                skuHidden = sel.xpath('//input[@id="skuHidden' + skuid.replace('-', '_')+'"]')

                regular_price = skuHidden.xpath('@regularprice').extract()
                price = skuHidden.xpath('@price').extract()[0]
                is_outof_stock = skuHidden.xpath('@isoutofstock').extract()[0]

                skuItem['id'] = skuid
                if len(regular_price) > 0 and regular_price[0] != '':
                    skuItem["list_price"] = regular_price[0]
                else:
                    skuItem["list_price"] = price
                skuItem['current_price'] = price

                size = sel.xpath('//img[@id="'+skuid.replace('-', '_')+'ColorButton"]/@colorvalue').extract()[0]
                skuItem['size'] = size

                if not size in sizes:
                    sizes.append(size)

                skuItem['color'] = color_name
                skuItem['is_outof_stock'] = self.change_out_of_stock_str(is_outof_stock)

                skuItem['type'] = 'sku'
                skuItem['from_site'] = self.from_site
                #yield skuItem

                if colorItemSku == '':
                    colorItemSku = skuid
                    color_cover = sel.xpath('//img[@id="'+skuid.replace('-', '_')+'ColorButton"]/@imgsrc').extract()[0]

                    if re.match(r'^//', color_cover):
                        color_cover = 'https:' + color_cover

                    colorItem['cover'] = color_cover

                skus.append(skuItem)

            item["skus"] = skus
            item['sizes'] = sizes
            item["colors"] = ['onecolor']

            url = 'https://www.diapers.com/product/productDetail!GetSkuImage.qs?skuCode='+colorItemSku+'&random='+'%f' %random()

            yield Request(url, meta={'item': colorItem, 'show_product_id': item['show_product_id']}, callback=self.parse_image)

        elif templateid == '10':

            # primary_attr = sel.xpath('//table[@id="primaryAttributeList"]/@attributename')
            # primary_attr = primary_attr.extract()[0].strip().lower() if len(primary_attr)>0 else ''
            #
            # second_attr = sel.xpath('//table[@id="secondAttributeList"]/@attributename')
            # second_attr = second_attr.extract()[0].strip().lower() if len(second_attr)>0 else ''
            #
            # third_attr = sel.xpath('//table[@id="thirdAttributeList"]/@attributename')
            # third_attr = third_attr.extract()[0].strip().lower() if len(third_attr)>0 else ''
            #
            # item['dimensions'] = [dimension for dimension in [primary_attr,second_attr,third_attr] if dimension]
            #
            # primary_attr_ids = sel.xpath('//table[@id="primaryAttributeList"]/tr/@id').extract()
            # second_attr_ids = sel.xpath('//table[@id="secondAttributeList"]/tr/@id').extract()
            # third_attr_ids = sel.xpath('//table[@id="thirdAttributeList"]/tr/@id').extract()
            #
            # primary_attr_dict = {}
            # second_attr_dict = {}
            # third_attr_dict = {}
            # item['sizes'] = {}
            skus = []
            # if primary_attr and len(primary_attr_ids) > 0:
            #     item['sizes'][primary_attr] = []
            #     for primary_attr_id in primary_attr_ids:
            #         primary_attr_value = sel.xpath('//table[@id="primaryAttributeList"]/tr[@id="' + str(primary_attr_id) + '"]/td[@class="attributeValue   "]/b/text()').extract()[0]
            #         item['sizes'][primary_attr].append(primary_attr_value)
            #         primary_attr_dict[primary_attr_id] = primary_attr_value
            #
            # if second_attr and len(second_attr_ids) > 0:
            #     item['sizes'][second_attr] = []
            #     for second_attr_id in second_attr_ids:
            #         second_attr_value = sel.xpath('//table[@id="secondAttributeList"]/tr[@id="' + str(second_attr_id) + '"]/td[@class="attributeValue   "]/b/text()').extract()[0]
            #         item['sizes'][second_attr].append(second_attr_value)
            #         second_attr_dict[second_attr_id] = second_attr_value
            #
            # if third_attr and len(third_attr_ids) > 0:
            #     item['sizes'][third_attr] = []
            #     for third_attr_id in third_attr_ids:
            #         third_attr_value = sel.xpath('//table[@id="thirdAttributeList"]/tr[@id="' + str(third_attr_id) + '"]/td[@class="attributeValue   "]/b/text()').extract()[0]
            #         item['sizes'][third_attr].append(third_attr_value)
            #         third_attr_dict[third_attr_id] = third_attr_value

            # if 'sizes' not in item['sizes'].keys():
            #     item['sizes']['size'] = ['One Size']
            # if 'color' not in item['sizes'].keys():
            #     item['colors'] = ['One Color']

            product_json_str = re.search('var pdpOptionsJson\s*=\s*([^\n]+);', response.body)
            if product_json_str:
                product_json_str = product_json_str.group(1)
            product_json = json.loads(product_json_str)
            colors = []
            for sku_json in product_json:
                skuItem = SkuItem()
                skuItem['id'] = sku_json['Sku']
                skuItem['show_product_id'] = item['show_product_id']
                skuItem['size'] = {}
                skuItem['color'] = sku_json['Description']
                skuItem['size'] = 'One Size'
                colors.append(skuItem['color'])

                # if primary_attr and len(primary_attr_dict) > 0 and len(sku_json['PrimaryAttributeValue'])>0:
                #     skuItem['size'][primary_attr] = primary_attr_dict[sku_json['PrimaryAttributeValue']]
                #
                # if second_attr and len(second_attr_dict) > 0 and len(sku_json['SecondAttributeValue'])>0:
                #     skuItem['size'][second_attr] = second_attr_dict[sku_json['SecondAttributeValue']]
                #
                # if third_attr and len(third_attr_dict) > 0 and len(sku_json['ThirdAttributeValue'])>0:
                #     skuItem['size'][third_attr] = third_attr_dict[sku_json['ThirdAttributeValue']]

                # if len(skuItem['size']) == 0:
                #     skuItem['size'] = 'One Size'
                #     skuItem['color'] = 'One Color'
                # else:
                #     if 'size' not in skuItem['size'].keys():
                #         skuItem['size'] = 'One Size'
                #     if 'color' not in skuItem['size'].keys():
                #         skuItem['color'] = 'One Color'

                skuItem['current_price'] = sku_json['RetailPrice']
                if not sku_json['RegularPrice']:
                    skuItem["list_price"] = sku_json['RetailPrice']
                else:
                    skuItem['list_price'] = sku_json['RegularPrice']

                skuItem['is_outof_stock'] = self.change_out_of_stock_str(sku_json['IsOutOfStock'])
                skuItem['type'] = 'sku'
                skuItem['from_site'] = self.from_site
                skus.append(skuItem)

                colorItem = Color()
                colorItem['name'] = skuItem['color']
                colorItem['type'] = 'color'
                colorItem['from_site'] = self.from_site
                color_url = 'https://www.diapers.com/product/productDetail!GetSkuImage.qs?skuCode=' + skuItem["id"] + '&random=' + '%f' % random()

                yield Request(color_url, meta={'item': colorItem, 'show_product_id': item['show_product_id']}, callback=self.parse_image)

            item['skus'] = skus
            item['colors'] = colors
            item['sizes'] = ['One Size']

        else:
            '''告警'''
            # print response.meta['url']
            return

        desc = sel.css('.descriptTabContent').xpath("//div[@class='pIdDesContent']").extract()

        if len(desc) > 0:
            item['desc'] = desc[0]
        else:
            item['desc'] = ''

        '''handle size info'''
        size_chart_type = re.search(r'var sizeChartType[\s]*=[\s]*"([^"]+)";', response.body)
        size_info_brand_name = re.search(r'var brandName[\s]*=[\s]*"([^"]+)";', response.body)

        if size_chart_type and size_info_brand_name:

            size_info_brand_name = size_info_brand_name.group(1)
            size_chart_type = size_chart_type.group(1)

            item['size_info'] = {'brand_name': size_info_brand_name, 'size_chart_type': size_chart_type}

            '''size info chart url'''
            size_info_chart_url = 'https://www.diapers.com/Product/BrandSizeChartHopup.qs?brandName=' + quote(size_info_brand_name) + '&sizeChartType=' + quote(size_chart_type)

            #print size_info_chart_url

            yield Request(size_info_chart_url, meta={'brand_name': size_info_brand_name, 'size_chart_type': size_chart_type}, callback=self.parse_size_info)

        yield item

#class diapersSpider(Spider):
class DiapersSpider(BaseSpider, DiapersBaseSpider):
    name = "diapers"
    allowed_domains = ["diapers.com", "diapers.com:80"]

    custom_settings = {
        'DOWNLOAD_DELAY': 0.01,
        'DOWNLOAD_TIMEOUT': 40,
        'RETRY_TIMES': 30,
        'USER_AGENT': 'search_crawler (+http://www.shijisearch.com)'
        # 'USER_AGENT': 'search_crccccc (+http://www.search2.com)'
    }

    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''
    start_urls = (
        #'http://www.diapers.com/cat=Toddler-Kid-Toys-15000',
        #'http://www.diapers.com/subcat=Baby-Girls-10565/ONSALE_FLAG=Y?PageIndex=49',
        #'http://www.diapers.com/p/marimekko-kukatar-bodysuit-baby-multicolor-1207601',
#         'http://www.diapers.com/subcat=Baby-Girls-10565/ONSALE_FLAG=Y?PageIndex=50',
        #'http://www.diapers.com/p/adidas-toddler-peplum-fleece-set-ny-knicks-2t-1149937',
        #'http://www.diapers.com/p/little-me-bear-quilted-pram-baby-white-lt-blue-1209118',
        #'http://www.diapers.com/p/bravado-designs-seamless-panty-rose-1105792',
        #'http://www.diapers.com/p/burts-bees-baby-bleach-bottom-board-shorts-toddler-kid-midnight-1177434',

        #'http://www.diapers.com/subcat=Girls-10569',
        #'http://www.diapers.com/p/masala-shimmer-cardigan-toddler-kid-teal-1219768',
        #'http://www.diapers.com/subcat=Girls-Shoes-10605',
        #'http://www.diapers.com/subcat=Girls-10569/Categories=Tops',

        'https://www.diapers.com/cat=Diapering-3?icn=DI-nav-Diapering&ici=top',
        'https://www.diapers.com/cat=Feeding-M1?icn=DI-nav-Feeding&ici=top',
        'https://www.diapers.com/cat=Household-Grocery-8592?icn=DI-nav-Householdgrocery&ici=top',
        'https://www.diapers.com/cat=Clothing-Shoes-638',
        'https://www.diapers.com/cat=Toys-Books-8',
    )

    base_url = 'https://www.diapers.com'

    def handle_parse_item(self, response, item):
        return DiapersBaseSpider.handle_parse_item(self, response, item)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url)

    '''具体的解析规则'''
    def parse_item(self, response):

#         item = BaseItem()
#         item['type'] = 'base'
#         item['show_product_id'] = '1209118'
        item = response.meta['item']

        return self.handle_parse_item(response, item)

    '''
    爬虫解析入口函数，用于解析丢入的第一个请求，一般是顶级目录页
    '''
    def parse(self, response):
        sel = Selector(response)
        product_type = 'Mother-Kid'

        if response.url == 'https://www.diapers.com/cat=Baby-Toys-Books-8':
            gender = 'baby'
        elif response.url == 'https://www.diapers.com/cat=Toddler-Kid-Toys-15000':
            gender = 'toddler'
        elif response.url == 'https://www.diapers.com/cat=Diapering-3?icn=DI-nav-Diapering&ici=top':
            gender = 'baby'
        elif response.url == 'https://www.diapers.com/cat=Feeding-M1?icn=DI-nav-Feeding&ici=top':
            gender = 'baby'
        elif response.url == 'https://www.diapers.com/cat=Bath-Skin-Care-1?icn=DI-nav-BathBabyCare&ici=top':
            gender = 'baby'
        elif response.url == 'https://www.diapers.com/cat=Household-Grocery-8592?icn=DI-nav-Householdgrocery&ici=top':
            gender = 'baby'
        else:
            gender = None

        ##uriDoms = sel.xpath('//div[contains(@class,"category-product-item-image")]/a')
        uriDoms = sel.xpath('//div[contains(@class,"child-browse-node-header")]/a')

        for uriDom in uriDoms:
            uri = uriDom.xpath('@href').extract()[0]
            category = uriDom.xpath('@title').extract()[0]

            if category == 'Newborn' or category == 'Baby Girls' or category == 'Baby Boys':
                gender = 'baby'
                category = None
            elif category == 'Toddler Girls' or category == 'Toddler Boys':
                gender = 'toddler'
                category = None
            elif category == 'Girls':
                gender = 'girls'
                category = None
            elif category == 'Boys':
                gender = 'boys'
                category = None
            elif category == 'Girls Shoes':
                continue
            elif category == 'Boys Shoes':
                continue
            elif category == 'Accessories':
                continue
            elif category == 'Maternity':
                gender = 'Women'

            # Gorden: 需要修改
            elif category == 'Cloth Diapers':
                continue
            elif category == 'Breastfeeding':
                continue
            elif category == 'Grocery':
                continue
            elif category == 'Household':
                continue
            uri = uri.replace('PageSize=200', 'PageSize=24')

            if not re.match(r'^https:\/\/', uri):
                url = self.base_url + uri

            if url == "https://www.diapers.com/subcat=Books-12643":
                continue
            yield Request(url, callback=self.parse_categories, meta={"uri": uri, 'category': category, 'gender': gender, 'product_type': product_type})

    '''
    爬虫解析二级页面，用于解析目录页面，进入该页面解析，要先判断是否是目录页，如果不是的话，则进行列表解析，调用parse_list
    '''
    def parse_categories(self, response):

        category = response.meta['category']

        gender = response.meta['gender']
        product_type = response.meta['product_type']

        sel = Selector(response)

        if len(sel.xpath('//div[contains(@class, "child-browse-node-boxes")]').extract()) > 0:
            uriDoms = sel.xpath('//div[contains(@class,"child-browse-node-header")]/a')

            for uriDom in uriDoms:

                uri = uriDom.xpath('@href').extract()[0]
                sub_category = uriDom.xpath('@title').extract()[0]

                # Gorden: 新加
                if sub_category == 'Formula Preparation':
                    continue

                if sub_category != 'Up to 50% off!':

                    if not category:
                        new_category = sub_category
                        sub_category = None
                    else:
                        new_category = category

                    uri = uri.replace('PageSize=200', 'PageSize=24')

                    url = self.base_url + uri
                    yield Request(url, callback=self.parse_list, meta={"uri": uri, 'category': new_category, 'sub_category': sub_category, 'gender': gender, 'product_type': product_type})

        else:
            yield Request(response.url, callback=self.parse_list, meta={'category': category, 'gender': gender, 'product_type': product_type}, dont_filter=True)
            # self.parse_list(response)
#         uri = uris[0]
#         url = self.base_url + uri
#         yield Request(url, callback=self.parse_list)

    '''
    解析列表额外页
    '''
    def parse_list_more(self, response):
        '''加载剩余的8个'''

        category =  response.meta['category']
        if 'sub_category' in response.meta:
            sub_category =  response.meta['sub_category']
        gender = response.meta['gender']
        product_type = response.meta['product_type']


        sel = Selector(response)
        goods = sel.css('.product-item')
        #items = []
        for commodity in goods:

            url = commodity.xpath('@data-pdp-url').extract()

            if len(url):
                item = BaseItem()
                item['from_site'] = 'diapers'
                url = 'https://www.diapers.com' + url[0]
                item['category'] = category
                item['sub_category'] = sub_category
                item['gender'] = gender
                item['product_type'] = product_type

                item['url'] = url

                item['brand'] = commodity.xpath('.//div[@class="product-box-info"]/div[@class="product-meta"]/span[@class="brand-name"]/text()').extract()[0].strip()
                title = commodity.xpath('.//div[@class="product-box-info"]/div[@class="product-meta"]/span[@class="item-name"]/text()').extract()

                if len(title) > 0:
                    item['title'] = title[0].strip()
                else:
                    item['title'] = 'unknown'

                item['cover'] = commodity.xpath('.//div[@class="product-image"]/div[@class="product-image-inner"]/img/@src').extract()[0]

                if re.match(r'^//', item['cover']):
                    item['cover'] = 'https:' + item['cover']

                base_price = commodity.xpath('.//div[@class="product-price"]/span[@class="base-price"]').extract()[0].strip()
                list_price = commodity.xpath('.//div[@class="product-price"]//span[@class="list-price"]').extract()

                if len(list_price) > 0:
                    item['list_price'] = list_price
                    item['current_price'] = base_price
                else:
                    item['list_price'] = base_price
                    item['current_price'] = base_price

                item['type'] = 'base'

                yield Request(url, meta={'item':item, 'url': url, 'dont_merge_cookies': True}, callback=self.parse_item)

    '''
    解析列表页，包括完成下一页链接的递归请求，而且调用parse_more_list，因为diapers网站每页只有16个item，额外8个item通过ajax来实现
    '''
    def parse_list(self, response):
        #'/subcat=Girls-10569/Categories=Tops'
        if 'uri' in response.meta:
            current_uri = response.meta['uri']
        category =  response.meta['category']

        gender = response.meta['gender']
        product_type = response.meta['product_type']

#         more_url = 'http://www.diapers.com/SearchSite/ProductLoader.qs?IsPLPAjax=Y&originUrl=' + quote(current_uri) + "&sectionIndex=1"
#         yield Request(more_url, callback=self.parse_list_more,  meta={'category': category, 'sub_category': sub_category, 'gender': gender, 'product_type': product_type})

        sel = Selector(response)
        goods = sel.xpath('//div[@class="product-box product-box-plp "]')
        for commodity in goods:
            url = commodity.xpath('./a/@href').extract()

            if len(url) > 0:
                item = BaseItem()
                item['from_site'] = 'diapers'

                if not re.match(r'^http(s?):\/\/', url[0]):
                    url = 'http://www.diapers.com' + url[0]
                else:
                    url = url[0]

                item['category'] = category
                if 'sub_category' in response.meta:
                    sub_category = response.meta['sub_category']
                    item['sub_category'] = sub_category
                item['gender'] = gender
                item['product_type'] = product_type

                item['url'] = url
                if len(commodity.xpath('.//div[@class="product-box-info"]/div[@class="product-meta"]//span[@class="brand-name"]/text()'))>0:
                    item['brand'] = commodity.xpath('.//div[@class="product-box-info"]/div[@class="product-meta"]//span[@class="brand-name"]/text()').extract()[0].strip()
                else:
                    item['brand'] = self.name
                title = commodity.xpath('.//div[@class="product-box-info"]/div[@class="product-meta"]//span[@class="item-name"]/text()').extract()

                if len(title) > 0:
                    item['title'] = title[0].strip()
                else:
                    item['title'] = 'unknown'

                cover = commodity.xpath('.//div[@class="q-product-image"]/img/@src').extract()
                if len(cover) > 0:
                    item['cover'] = cover[0]
                else:
                    continue

                if re.match(r'^//', item['cover']):
                    item['cover'] = 'https:' + item['cover']

                base_price = commodity.xpath('.//div[@class="product-price"]//span[@class="q-product-price__current-price"]/text()').re(r'^\s*\$([\d\.]+)')
                if len(base_price) > 0:
                    base_price = base_price[0].strip()
                else:
                    base_price = commodity.xpath('.//div[@class="product-price"]/span[@class="sale-price"]/span/text()').re(r'^\s*\$([\d\.]+)')[0].strip()

                list_price = commodity.xpath('.//div[@class="product-price"]//span[@class="q-product-price__current-price"]/text()').re(r'\$([\d\.]+)\s*$')

                if len(list_price) > 0:
                    item['list_price'] = list_price
                    item['current_price'] = base_price
                else:
                    item['list_price'] = base_price
                    item['current_price'] = base_price

                item['type'] = 'base'
#                 print 'url', url
                ##print urlparse.urlparse(url)
                yield Request(url, meta={'item':item, 'url': url}, callback=self.parse_item)

        next_button = sel.xpath('//ul[contains(@class,"pagination")]/li/a[@class="next"]')

        if len(next_button.extract()) > 0:
            next_uri = next_button.xpath('@href').extract()[0]

            if not re.match(r'^https', next_uri):
                next_uri = 'https://www.diapers.com' + next_uri
            if 'sub_category' in response.meta:
                yield Request(next_uri, callback=self.parse_list, meta={"uri": next_uri, 'category': category, 'sub_category': response.meta['sub_category'], 'gender': gender, 'product_type': product_type})
            else:
                yield Request(next_uri, callback=self.parse_list,
                              meta={"uri": next_uri, 'category': category, 'gender': gender, 'product_type': product_type})
        else:
            return

# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy import Request
import re
import execjs
from gorden_crawler.spiders.shiji_base import BaseSpider
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
import copy
import json
import logging
import difflib
import requests
import datetime

class AsosSpider(BaseSpider):
#class AsosSpider(RedisSpider):
    name = "asos"

    base_url = "http://us.asos.com"

    allowed_domains = ["us.asos.com", "asos-media.com"]

    start_urls = [
        'http://us.asos.com/?hrd=1',
        'http://us.asos.com/women/outlet/',
        'http://us.asos.com/men/outlet/',
    ]

    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 0.2,
        'DOWNLOAD_TIMEOUT': 30,
        'RETRY_TIMES': 20,
        # 'DOWNLOADER_MIDDLEWARES': {
        #     # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
        #     'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
        #     'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
        #     'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
        #     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        # }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=True, cookies={'asos': 'currencyid=1'})

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, cookies={'asos': 'currencyid=1'})

    #yield list items of some brand
    def parse(self, response):
        sel = Selector(response)
        response_url = response.url

        if response_url == "http://us.asos.com/?hrd=1":
            # women
            url_a_s_women = sel.xpath('//li[contains(@class, "floor_1")]//div[@class="sub-floor-menu"]/dl[1]//ul[@class="items"]//li/a')

            li_urls = {}  #key为ProductType, value为ProductType对应的url
            flag=False
            for a in url_a_s_women:
                if len(a.xpath('text()').extract()) == 0:
                    continue
                li_text=a.xpath('text()').extract()[0]
                li_href=a.xpath('@href').extract()[0]
                if li_text == 'Accessories':
                    flag=True
                if li_text == 'Packs SAVE' or li_text == 'Packs Save':
                    flag=False
                if flag:
                    li_urls[li_text]=li_href

            if len(li_urls) > 0:
                for li_item in li_urls.items():
                    item=BaseItem()
                    item['type']='base'
                    item['product_type'] = li_item[0]
                    item['gender'] = 'women'
                    li_url=li_item[1]
                    if item['product_type'] == "Beauty":
                        yield Request(li_url, callback=self.parse_beauty, cookies={'asos': 'currencyid=1'}, meta={'item': item})
                    else:
                        yield Request(li_url, callback=self.parse_categories, cookies={'asos': 'currencyid=1'}, meta={'item': item})

            #men
            url_a_s_men=sel.xpath('//li[contains(@class, "floor_2")]//div[@class="sub-floor-menu"]/dl[1]//ul[@class="items"]//li/a')
            li_urls={}  #key为ProductType, value为ProductType对应的url
            flag=False
            for a in url_a_s_men:
                if len(a.xpath('text()').extract()) == 0:
                    continue
                li_text=a.xpath('text()').extract()[0]
                li_href=a.xpath('@href').extract()[0]
                if li_text == 'Accessories':
                    flag=True
                if li_text == 'Packs SAVE' or li_text == 'Packs Save':
                    flag=False
                if flag:
                    li_urls[li_text]=li_href

            if len(li_urls)>0:
                for li_item in li_urls.items():
                    item=BaseItem()
                    item['type']='base'
                    item['product_type']=li_item[0]
                    item['gender'] = 'men'
                    li_url=li_item[1]
                    yield Request(li_url, callback=self.parse_categories, cookies={'asos': 'currencyid=1'}, meta={'item': item})

        if 'sale' in response.url or 'outlet' in response.url:
            # response_url=="http://us.asos.com/men/outlet/" or response_url=="http://us.asos.com/women/outlet/":
            # outlet women and men
            # if 'women' in response_url:  #response_url=="http://us.asos.com/men/outlet/":
            product_type_str = sel.xpath('//div[@class="lside"]/div/h4/text()').extract()
            if 'Shop by category' in product_type_str:
                position = product_type_str.index('Shop by category')
            elif 'Shop by Category' in product_type_str:
                position = product_type_str.index('Shop by Category')
            product_type_lis = sel.xpath('//div[@class="lside"]/div/h4')[position].xpath('./parent::*/ul/li')
            # product_type_lis = sel.xpath('//div[@class="lside"]/div')[2].xpath('./ul/li')
            # else:
            #     product_type_lis = sel.xpath('//div[@class="lside"]/div')[1].xpath('./ul/li')
            for product_type_li in product_type_lis:
                item = BaseItem()
                item['type']='base'
                if 'women' in response_url: #response_url == "http://us.asos.com/men/outlet/":
                    item['gender'] = 'women'
                else:
                    item['gender'] = 'men'
                url = product_type_li.xpath('./a/@href').extract()[0]
                product_type = product_type_li.xpath('./a/text()').extract()[0]
                item['product_type']=product_type
                yield Request(url, callback=self.parse_categories, cookies={'asos': 'currencyid=1'}, meta={'item': item})

    def parse_beauty(self, response):
        sel=Selector(response)
        item = response.meta['item']
        cat_divs = sel.xpath('//div[@class="boxes"]/div')
        for cat_div in cat_divs:
            url = cat_div.xpath('./a/@href').extract()[0]
            yield Request(url, callback=self.parse_categories, cookies={'asos': 'currencyid=1'}, meta={'item': item})

    def parse_categories(self, response):
        sel=Selector(response)
        item=response.meta['item']
        # if 'on_sale' in response.meta.keys():
        category_link_list_a = sel.xpath('//div[@data-id="attribute_989"]//ul/li/a')
        # else:
        #     category_link_list_a = sel.xpath('//ul[@class="link-list"]/li/a')
        for category_link_a in category_link_list_a:
            item_category = category_link_a.xpath('./span[@class="facetvalue-name"]/text()').extract()
            if len(item_category) > 0:
                item['category']= item_category[0]
                # if 'New In' in item['category']:
                #     continue
                url=category_link_a.xpath('./@href').extract()[0]
                if not re.match(r'^http:\/\/', url):
                    url = re.findall(r'[^\?]+', response.url)[0] + url

                yield Request(url, callback=self.parse_category, cookies={'asos': 'currencyid=1'}, meta={'item': item})

    def parse_category(self, response):
        sel=Selector(response)
        item=response.meta['item']


        li_url=response.url
        li_uri=re.findall(r'[^\?]+', li_url)[0]

        #tail_str='&pgeSize=36&sort=-1'
        #m=re.match(r"http://us.asos.com/[^\&]+", li_url)
        #li_pages=sel.xpath('//ol[@class="page-nos"]/li')
        #if li_pages:
        #    total_items=sel.xpath('//div[@id="pagingHeader"]//span[@class="total-items"]/text()').extract()[0]
        #    page_count=int(total_items)/36
        #    if int(total_items)%36 !=0:
        #        page_count=page_count+1
        # max_page_num=li_pages[-2:-1].xpath('./a/text()').extract()[0]
        #    for pge in range(page_count):
        #        item_list_url=m.group(0)+'&pge='+str(pge)+tail_str

        # next_page_uris = sel.xpath('//li[@class="next"]/a')
        # for next_page_uri in next_page_uris:
        #     if re.search(r'Next',next_page_uri.xpath('text()').extract()[0]):
        #
        #         next_uri = str(next_page_uri.xpath('@href').extract()[0])
        #         if not re.search(r'^http:\/\/', next_uri):
        #             url=li_uri+ next_uri
        #         else:
        #             url = next_uri
        #
        copy_item = copy.deepcopy(item)
        #         yield Request(url, callback=self.parse_category, cookies={'asos': 'currencyid=1'}, meta={'item': copy_item})

        item_lis = sel.xpath('//div[@class="results three-grid"]/ul/li')
        # print item_lis
        for item_li in item_lis:
            item_url = item_li.xpath('./a/@href').extract()[0]

            if not re.match(r'^http:\/\/', item_url):
                item_url = self.base_url + item_url

            item['url'] = item_url
            item['cover'] = item_li.xpath('.//img[@class="product-img"]/@src').extract()[0]

            # rrp_price_sel=item_li.xpath('.//span[@class="recRP rrp"]/text()').extract()
            # if len(rrp_price_sel) > 0 and rrp_price_sel[0]:
            #     item['list_price'] = rrp_price_sel[0]
            #     item['current_price'] = item_li.xpath('.//div[@class="productprice"]/span[@class="price outlet-current-price"]/text()').extract()[0]
            # else:
            #     item['list_price']=item_li.xpath('.//div[@class="productprice"]/span[@class="price"]/text()').extract()[0]
            #
            #     current_price_sel=item_li.xpath('.//span[contains(@class, "prevPrice")]/text()').extract()
            #
            #     if len(current_price_sel) > 0 and current_price_sel[0]:
            #         item['current_price']= current_price_sel[0]
            #     else:
            #         item['current_price']= item['list_price']

            current_price_sel = item_li.xpath('.//div[@class="price-wrap price-current"]/span[@class="price"]/text()').extract()
            if len(current_price_sel) > 0 and current_price_sel[0]:
                item['current_price'] = current_price_sel[0]

            list_price_sel = item_li.xpath('.//div[@class="price-wrap price-previous"]/span[@class="price"]/text()').extract()
            if len(list_price_sel) > 0 and list_price_sel[0]:
                item['list_price'] = list_price_sel[0]
            else:
                item['list_price'] = item['current_price']

            product_id = item_li.xpath('./@data-productid').extract()[0]
            if 'prod/pgeproduct.aspx' in item_url:
                item_url = item_url.replace('prod/pgeproduct.aspx', 'prd/'+str(product_id))
            yield Request(item_url, callback=self.parse_item, meta={'item': item}, cookies={'asos': 'currencyid=1'})

        total_counts = sel.xpath('//span[@class="total-results"]/text()').extract()[0]
        if ',' in total_counts:
            total_counts = total_counts.replace(',', '')
        current_url = response.url
        if 'pge=' in response.url:
            current_page = int(re.search('pge=(\d+)', response.url).group(1)) + 1
        else:
            current_page = 1
        if int(total_counts) % 36>0:
            last_page = int(total_counts)/36 + 1
        else:
            last_page = 1
        if current_page < last_page:
            next_page = current_page + 1
            if 'pge=' in response.url:
                next_url = re.sub('pge=\d+', 'pge=' + str(next_page-1), current_url)
            else:
                next_url = current_url + '&pge=1'
            yield Request(next_url, callback=self.parse_category, cookies={'asos': 'currencyid=1'}, meta={'item': copy_item})

    def parse_item(self, response):
        item=response.meta['item']
        return self.handle_parse_item(response, item)

    def parse_stock(self, response):
        if not response.body:
            return
        item=response.meta['item']
        related_products_url = response.meta['related_products_url']
        goods_details = json.loads(response.body)
        if 'variants' not in goods_details[0]:
            return
        sku_infos = goods_details[0]['variants']
        handle_sku_infos = {}
        for sku in sku_infos:
            handle_sku_infos[sku['variantId']] = sku

        final_skus = []
        for sku in item['skus']:
            if handle_sku_infos[sku['id']]['isInStock'] == True:
                sku['current_price'] = handle_sku_infos[sku['id']]['price']['current']['value']
                sku['list_price'] = handle_sku_infos[sku['id']]['price']['previous']['value']

                final_skus.append(sku)

        item['skus'] = final_skus
        parse_media_url = 'http://video.asos-media.com/products/test-desc/' + str(item['show_product_id']) + '-catwalk-AVS.m3u8'
        try:
            req = requests.head(parse_media_url)
            if req.ok:
                req = requests.get(parse_media_url)
                media_uri = re.search('(ASOS/_media.+?)\.m3u8', req.text).group(1)
                media_url = 'http://video.asos-media.com/products/' + media_uri
                item['media_url'] = media_url
        except Exception as e:
            logging.error('error media url: '+ parse_media_url + ' error msg: ' + str(e))

        yield Request(related_products_url, callback=self.parse_related_products, meta={"item": item})

    def parse_related_products(self, response):
        item = response.meta['item']
        related_items = json.loads(response.body)
        related_items_id = []
        if 'products' in related_items.keys():
            for related_item_detail in related_items['products']:
                if related_item_detail['product']['isInStock'] == True:
                    related_items_id.append(related_item_detail['product']['id'])
        if related_items_id:
            item['related_items_id'] = related_items_id
        yield item

    def handle_parse_item(self, response, item):
        if re.match(r'^http:\/\/us\.asos\.com\/mp_sp\/',response.url):

            sel = Selector(response)

            url = sel.xpath('//li[@id="mp_li_cnti"]/a/@href').extract()[0]

            yield Request(url, callback=self.parse_item, cookies={'asos': 'currencyid=1'}, meta={'item': item})
        else:
            skus=[]
            sel=Selector(response)
            json_info = re.search("view\(\'(.+\})\'\,", response.body)
            if not json_info:
                return
            else:
                json_info = json_info.group(1)
            json_info = "".join(json_info)
            json_info = json_info.decode("string-escape")
            goods_detail = json.loads(json_info)
            descs = sel.xpath('//div[@class="overflow-container"]/div/div')
            item['desc'] = ''
            for desc in descs:
                item['desc'] = item['desc'] + desc.extract()
            item['title'] = goods_detail['name']
            if 'brandName' not in goods_detail.keys():
                item['brand'] = 'asos'
            else:
                item['brand'] = goods_detail['brandName']
            item['from_site'] = self.name
            if 'price' not in goods_detail.keys():
                return
            item['current_price'] = goods_detail['price']['current']
            if float(goods_detail['price']['previous']) != 0:
                item['list_price'] = goods_detail['price']['previous']
            elif float(goods_detail['price']['rrp']) != 0:
                item['list_price'] = goods_detail['price']['rrp']
            else:
                item['list_price'] = goods_detail['price']['current']

            item['show_product_id'] = goods_detail['id']

            sizes = []
            colors = []
            for sku in goods_detail['variants']:
                skuItem = SkuItem()
                skuItem['type'] = "sku"
                skuItem['from_site'] = self.name
                skuItem['is_outof_stock'] = False
                skuItem['id'] = sku['variantId']
                skuItem['show_product_id'] = goods_detail['id']
                skuItem['current_price'] = item['current_price']
                skuItem['list_price'] = item['list_price']
                skuItem['size'] = sku['size']
                if sku['size'] not in sizes:
                    sizes.append(sku['size'])
                skuItem['color'] = sku['colour']

                if sku['colour'] not in colors:
                    colors.append(sku['colour'])
                skus.append(skuItem)
            for color_name in colors:
                images = []
                for image in goods_detail['images']:
                    if image['colour'] == '' or (image['colour'] and color_name and len(image['colour']) == len(color_name) and (len(color_name) - difflib.SequenceMatcher(None,color_name,image['colour']).ratio()*len(color_name)) <=1):
                        imageItem = ImageItem()
                        imageItem['image'] = image['url'] + '?$XXL$'
                        imageItem['thumbnail'] = image['url']
                        images.append(imageItem)

                color = Color()
                color['type'] = 'color'
                color['from_site'] = self.name
                color['show_product_id'] = goods_detail['id']
                color['images'] = images
                color['name'] = color_name
                color['cover'] = images[0]['image']

                yield color

            item['skus'] = skus
            item['sizes'] = list(set(sizes))
            item['dimensions'] = ['size']
            item['colors'] = colors
            related_products_url = 'http://us.asos.com/api/product/catalogue/v2/productgroups/ctl/' + str(item['show_product_id']) + '?store=US&store=US&currency=USD'

            yield Request('http://us.asos.com/api/product/catalogue/v2/stockprice?productIds=' + str(goods_detail['id']) + '&store=US&currency=USD', callback=self.parse_stock, meta={'item': item, 'related_products_url': related_products_url})
    #         color_size_str="".join(re.findall(r"var\s+arrSzeCol_ctl00_ContentMainPage_ctlSeparateProduct[^<]+", response.body))
    #         sep_image_str="".join(re.findall(r"var\s+arrSepImage_ctl00_ContentMainPage_ctlSeparateProduct[^<]+", response.body))
    #         thumb_image_str="".join(re.findall(r"var\s+arrThumbImage_ctl00_ContentMainPage_ctlSeparateProduct[^<]+", response.body))
    #         if len(color_size_str)>0:
    #             context = execjs.compile('''
    #                 %s
    #                 %s
    #                 %s
    #                 function get_color_size(){
    #                     return arrSzeCol_ctl00_ContentMainPage_ctlSeparateProduct;
    #                   }
    #                 function get_sep_image(){
    #                     return arrSepImage_ctl00_ContentMainPage_ctlSeparateProduct;
    #                   }
    #                 function get_thumb_image(){
    #                     return arrThumbImage_ctl00_ContentMainPage_ctlSeparateProduct;
    #                   }
    #             ''' % (color_size_str, sep_image_str, thumb_image_str))
    #             color_sizes = context.call('get_color_size')
    #             sep_image= context.call('get_sep_image')
    #             thumb_images = context.call('get_thumb_image')
    #             #import pdb;pdb.set_trace()
    #         if len(sel.xpath('//div[@id="ctl00_ContentMainPage_ctlSeparateProduct_pnlOutofStock"]').extract()) > 0:
    #             return
    #
    #         if len(sel.xpath('//span[@id="ctl00_ContentMainPage_ctlSeparateProduct_lblProductTitle"]/text()').extract()) > 0:
    #             item['title']=sel.xpath('//span[@id="ctl00_ContentMainPage_ctlSeparateProduct_lblProductTitle"]/text()').extract()[0]
    #
    #             data_dic_str = sel.xpath('//script[@id="dataDictionary"]/text()')
    #
    #             product_data_str=data_dic_str.re(r'^var Product\s*=\s*({.*?});')[0]
    #             product_data=eval(product_data_str)
    #             item['show_product_id']=product_data['ProductIID']
    #             desc=sel.xpath('//div[@id="ctl00_ContentMainPage_productInfoPanel"]//ul')
    #             if len(desc)>0:
    #                 item['desc']=desc.extract()[0]
    #             item['brand']=product_data['ProductBrand']
    #             item['from_site']=self.name
    #
    #             '''有严重问题，注释掉了'''
    # #             gender_category_str=product_data['ProductCategory']
    # #             m=re.search(r'(.+)\|(.+)', gender_category_str)
    # #             if m:
    # #                 item['gender']=m.group(1).strip()
    # #             m=re.search(r'(.+)\|(.+)', gender_category_str)
    # #             if m:
    # #                 item['category']=m.group(2).strip()
    #
    #             sku_data_str = data_dic_str.re(r'var ProductChildSkuInfo\s*=\s*({.*?});')[0]
    #             sku_data=eval(sku_data_str)
    #             sku_data_list=sku_data['ChildSkuInfo'][item['show_product_id']]
    #             #color_list=sel.xpath('//select[@id="ctl00_ContentMainPage_ctlSeparateProduct_drpdwnColour"]').extract()
    #             if color_sizes:
    #                 '''handle color and image'''
    #
    # #                 thumbnail_lis=sel.xpath('//ul[@class="productThumbnails"]//li//img/@src')
    # #                 image_lis=sel.xpath('//div[@id="productImages"]//img/@src')
    # #                 if len(thumbnail_lis)>0:
    # #                     for i in range(len(thumbnail_lis)):
    # #                         imageItem=ImageItem()
    # #                         imageItem['image']=image_lis[i].extract()
    # #                         imageItem['thumbnail']=thumbnail_lis[i].extract()
    # #                         images.append(imageItem)
    #                 #left three imageItem
    #                 images=[]
    #                 for thumb_image in thumb_images:
    #                     imageItem=ImageItem()
    #                     imageItem['image']=thumb_image[2]
    #                     imageItem['thumbnail']=thumb_image[0]
    #                     images.append(imageItem)
    #
    #                 item_color_names=[]
    #                 #all color names of item
    #
    #                 sep_image_dict = {}
    #                 for sep_image_arr in sep_image:
    #                     key = sep_image_arr[3]
    #                     sep_image_dict[key] = {'image': sep_image_arr[2], 'thumbnail': sep_image_arr[0]}
    #
    #                 color_names = sel.xpath('//div[@id="ctl00_ContentMainPage_ctlSeparateProduct_pnlColour"]//option/@value')[1:].extract()
    #                 for color_name in color_names:
    #
    #                     lower_color_name = color_name.lower()
    #                     if '/' in lower_color_name:
    #                         lower_color_name_2 = lower_color_name.replace('/', '')
    #                     else:
    #                         lower_color_name_2 = lower_color_name
    #                     if lower_color_name not in sep_image_dict.keys() and lower_color_name_2 not in sep_image_dict.keys():
    #                         return
    #                     imageItem=ImageItem()
    #                     imageItem['thumbnail']= sep_image_dict[lower_color_name_2]['thumbnail']
    #                     imageItem['image']= sep_image_dict[lower_color_name_2]['image']
    #                     images.insert(0, imageItem)
    #                     #                     import pdb;pdb.set_trace()
    #                     color=Color()
    #                     color['type'] ='color'
    #                     color['from_site'] = self.name
    #                     color['show_product_id'] = product_data['ProductIID']
    #                     color['images'] = images
    #                     color['name'] = color_name
    #                     color['cover'] = sep_image_dict[lower_color_name_2]['thumbnail']
    #
    #                     yield color
    #
    #                     item_color_names.append(color_name)
    #                 '''handle price'''
    #                 #list_price_sel=sel.xpath('//span[@id="ctl00_ContentMainPage_ctlSeparateProduct_lblRRP"]')
    #                 sizes=[]
    #                 for color_size in color_sizes:
    #                     size_id = color_size[0]
    #                     size = color_size[1]
    #                     if not size.strip():
    #                         size = 'onesize'
    #
    #                     if color_size[3] == "False":
    #                         continue
    #
    #                     original_color_name = color_size[2]
    #                     for color_name in item_color_names:
    #                         tmp_color_name = re.sub(r'[^\w]', '', color_name)
    #
    #                         if tmp_color_name == original_color_name:
    #                             original_color_name = color_name
    #
    #                     skuItem=SkuItem()
    #                     skuItem['type']="sku"
    #                     skuItem['from_site']=self.name
    #                     skuItem['is_outof_stock']=False
    #                     skuItem['id']=sku_data_list[str(size_id)+original_color_name]['Sku']
    #                     #skuItem['id']=color_size[0]
    #                     skuItem['show_product_id']=product_data['ProductIID']
    #                     skuItem['current_price']= color_size[5]
    #
    #                     if color_size[6] == color_size[5] and color_size[8] != '0' and color_size[8] != '0.00':
    #                         skuItem['list_price']= color_size[8]
    #                     else:
    #                         skuItem['list_price']= color_size[6]
    #
    #                     sizes.append(size)
    #                     skuItem['color'] = original_color_name
    #                     skuItem['size'] = size
    #                     skus.append(skuItem)
    #
    #                 item['skus']=skus
    #                 item['sizes']=list(set(sizes))
    #                 item['dimensions']=['size']
    #                 item['colors'] = item_color_names
    #                 size_info = sel.xpath('//a[@id="ctl00_ContentMainPage_SizeGuideButton_SizeGuideLink"]/@href')
    #                 if size_info:
    #                     item['size_info'] = size_info.extract()[0]
    #                     if not re.match(r'^http', size_info.extract()[0]):
    #                         item['size_info'] = self.base_url + size_info.extract()[0]
    #             yield item
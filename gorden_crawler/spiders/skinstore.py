# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
from scrapy import Request
from gorden_crawler.spiders.shiji_base import BaseSpider

class SkinStoreSpider(BaseSpider):
	name = 'skinstore'
	allowed_domains = ["skinstore.com"]
	base_url = 'http://www.skinstore.com'
	start_urls = [
		#skin-care
		'http://www.skinstore.com/skin-care-body-products.aspx',
		'http://www.skinstore.com/skin-care-face-products.aspx',
		'http://www.skinstore.com/skin-care-sets-and-kits-products.aspx',
		'http://www.skinstore.com/skin-care-sun-products.aspx',
		'http://www.skinstore.com/skin-care-supplements-products.aspx',
		#cosmetics
		'http://www.skinstore.com/cosmetics-body-products.aspx',
		'http://www.skinstore.com/cosmetics-eye-products.aspx',
		'http://www.skinstore.com/cosmetics-face-products.aspx',
		'http://www.skinstore.com/cosmetics-lip-products.aspx',
		'http://www.skinstore.com/cosmetics-nail-products.aspx',
		'http://www.skinstore.com/cosmetics-sets-and-kits-products.aspx',
		'http://www.skinstore.com/cosmetics-smile-products.aspx',
		'http://www.skinstore.com/cosmetics-tools-products.aspx',
		#hair care
		'http://www.skinstore.com/hair-care-conditioners-products.aspx',
		'http://www.skinstore.com/hair-care-hair-sprays-products.aspx',
		'http://www.skinstore.com/hair-care-hair-styling-products.aspx',
		'http://www.skinstore.com/hair-care-sets-products.aspx',
		'http://www.skinstore.com/hair-care-shampoos-products.aspx',
		'http://www.skinstore.com/hair-care-supplements-products.aspx',
		'http://www.skinstore.com/hair-care-tools-products.aspx',
		'http://www.skinstore.com/hair-care-treatments-products.aspx',
		#nature
		'http://www.skinstore.com/natural-cosmetics-products.aspx',
		'http://www.skinstore.com/natural-fragrance-products.aspx',
		'http://www.skinstore.com/natural-hair-care-products.aspx',
		'http://www.skinstore.com/natural-skin-care-products.aspx',
		'http://www.skinstore.com/natural-men-products.aspx',
		#men
		'http://www.skinstore.com/men-body-products.aspx',
		'http://www.skinstore.com/men-face-products.aspx',
		'http://www.skinstore.com/men-hair-products.aspx',
		'http://www.skinstore.com/men-sets-and-kits-products.aspx',
		'http://www.skinstore.com/men-sun-products.aspx',
		'http://www.skinstore.com/men-supplements-products.aspx',
		#fragrance
		'http://www.skinstore.com/fragrance-mens-products.aspx',
		'http://www.skinstore.com/fragrance-womens-products.aspx',

	]

	product_type_mapping = {
		#skin-care
		'http://www.skinstore.com/skin-care-body-products.aspx' : {'category': 'skin-care-body', 'gender':'women'},
		'http://www.skinstore.com/skin-care-face-products.aspx' : {'category': 'skin-care-face', 'gender':'women'},
		'http://www.skinstore.com/skin-care-sets-and-kits-products.aspx' : {'category': 'skin-care-sets-and-kits', 'gender':'women'},
		'http://www.skinstore.com/skin-care-sun-products.aspx' : {'category': 'skin-care-sun', 'gender':'women'},
		'http://www.skinstore.com/skin-care-supplements-products.aspx' : {'category': 'skin-care-supplements', 'gender':'women'},
		#cosmetics
		'http://www.skinstore.com/cosmetics-body-products.aspx' : {'category': 'cosmetics-body', 'gender':'women'},
		'http://www.skinstore.com/cosmetics-eye-products.aspx' :	{'category': 'cosmetics-eye', 'gender':'women'},
		'http://www.skinstore.com/cosmetics-face-products.aspx' : {'category': 'cosmetics-face', 'gender':'women'},
		'http://www.skinstore.com/cosmetics-lip-products.aspx' : {'category': 'cosmetics-lip', 'gender':'women'},
		'http://www.skinstore.com/cosmetics-sets-and-kits-products.aspx' : {'category': 'cosmetics-sets-and-kits', 'gender':'women'},
		'http://www.skinstore.com/cosmetics-nail-products.aspx': {'category': 'cosmetics-nail', 'gender':'women'},
		'http://www.skinstore.com/cosmetics-smile-products.aspx' : {'category': 'cosmetics-smile', 'gender':'women'},
		'http://www.skinstore.com/cosmetics-tools-products.aspx' : {'category': 'cosmetics-tools', 'gender':'women'},
		#hair care
		'http://www.skinstore.com/hair-care-conditioners-products.aspx' : {'category': 'hair-care-conditioners', 'gender':'women'},
		'http://www.skinstore.com/hair-care-hair-sprays-products.aspx' : {'category': 'hair-care-hair-sprays', 'gender':'women'},
		'http://www.skinstore.com/hair-care-hair-styling-products.aspx' : {'category': 'hair-care-hair-styling', 'gender':'women'},
		'http://www.skinstore.com/hair-care-sets-products.aspx': {'category': 'hair-care-sets', 'gender':'women'},
		'http://www.skinstore.com/hair-care-shampoos-products.aspx': {'category': 'hair-care-shampoos', 'gender':'women'},
		'http://www.skinstore.com/hair-care-supplements-products.aspx': {'category': 'hair-care-supplements', 'gender':'women'},
		'http://www.skinstore.com/hair-care-tools-products.aspx': {'category': 'hair-care-tools', 'gender':'women'},
		'http://www.skinstore.com/hair-care-treatments-products.aspx': {'category': 'hair-care-treatments', 'gender':'women'},
		#nature
		'http://www.skinstore.com/natural-cosmetics-products.aspx': {'category' : 'nature-cosmetics', 'gender' : 'women'},
		'http://www.skinstore.com/natural-fragrance-products.aspx': {'category' : 'nature-fragrance', 'gender' : 'women'},
		'http://www.skinstore.com/natural-hair-care-products.aspx': {'category' : 'nature-hair-care', 'gender' : 'women'},
		'http://www.skinstore.com/natural-skin-care-products.aspx': {'category' : 'nature-skin-care', 'gender' : 'women'},
		'http://www.skinstore.com/natural-men-products.aspx': {'category' : 'men-cosmetics', 'gender' : 'men'},
		#men
		'http://www.skinstore.com/men-body-products.aspx' : {'category' : 'men-body', 'gender' : 'men'},
		'http://www.skinstore.com/men-face-products.aspx' : {'category' : 'men-face', 'gender' : 'men'},
		'http://www.skinstore.com/men-hair-products.aspx' : {'category' : 'men-hair', 'gender' : 'men'},
		'http://www.skinstore.com/men-sets-and-kits-products.aspx' : {'category' : 'men-sets-and-kits', 'gender' : 'men'},
		'http://www.skinstore.com/men-sun-products.aspx' : {'category' : 'men-sun', 'gender' : 'men'},
		'http://www.skinstore.com/men-supplements-products.aspx' : {'category' : 'men-supplements', 'gender' : 'men'},
		#fragrance
		'http://www.skinstore.com/fragrance-mens-products.aspx': {'category' : 'men-fragrance', 'gender' : 'men'},
		'http://www.skinstore.com/fragrance-womens-products.aspx': {'category' : 'women-supplements', 'gender' : 'women'},
	}
	def parse(self, response):
		sel = Selector(response)
		response_url = response.url
		if response_url in self.start_urls:
			category = self.product_type_mapping[response_url]['category']
			gender = self.product_type_mapping[response_url]['gender']
		else:
			category = response.meta['category']
			gender = response.meta['gender']
		product_divs = sel.xpath('//div[@id="productGrid"]/div')
		baseItem = BaseItem()
		baseItem['type'] = 'base'
		baseItem['from_site'] = self.name
		baseItem['product_type'] = 'cosmetics'
		baseItem['category'] = category
		baseItem['gender'] = gender
		baseItem['colors'] = ['one-color']
		baseItem['sizes'] = ['one-size']
		for product_div in product_divs:
			product_a = product_div.xpath('.//div[@class="productImage"]/a')
			url = self.base_url + product_a.xpath('./@href').extract()[0]
			baseItem['url'] = url
			baseItem['cover'] = 'http:'+product_a.xpath('./img/@src').extract()[0]
			baseItem['title'] = product_div.xpath('.//span[@itemprop="name"]/text()').extract()[0]
			baseItem['current_price'] = product_div.xpath('.//div[@class="itemPrice"]/span[@itemprop="price"]/text()').extract()[0]
			list_price_str = product_div.xpath('.//span[@class="valuePrice"]/text()')
			if len(list_price_str)>0:
				baseItem['list_price'] = list_price_str.extract()[0]
			else:
				baseItem['list_price'] = baseItem['current_price']
			baseItem['show_product_id'] = product_div.xpath('.//span[@itemprop="productID"]/text()').extract()[0]
			yield Request(url, callback = self.parse_item, meta={'baseItem': baseItem})

		page_options = sel.xpath('//select[@id="PagerLinksDropDownList"]/option')[1:]
		for page_option in page_options:
			page_url = self.base_url + page_option.xpath('./@value').extract()[0]
			yield Request(page_url, callback=self.parse, meta={'category': category, 'gender': gender})

	def parse_item(self, response):
		baseItem = response.meta['baseItem']
		return self.handle_parse_item(response, baseItem)
	def handle_parse_item(self, response, baseItem):
		sel = Selector(response)
		baseItem['dimensions'] = ['size', 'color']
		baseItem['desc'] = sel.xpath('//div[@id="aDescriptionBody"]').extract()[0]
		baseItem['brand'] = sel.xpath('//span[@itemprop="brand"]/text()').extract()[0]
		skus = []
		skuItem = SkuItem()
		skuItem['type'] = 'sku'
		skuItem['show_product_id'] = baseItem['show_product_id']
		skuItem['from_site'] = self.name
		skuItem['current_price'] = baseItem['current_price']
		skuItem['list_price'] = baseItem['list_price']
		skuItem['is_outof_stock'] = False
		skuItem['color'] = 'one-color'
		skuItem['size'] = 'one-size'
		skuItem['id'] = baseItem['show_product_id']
		skus.append(skuItem)
		imageItem = ImageItem()
		imageItem['image'] = 'http:'+sel.xpath('//img[@id="ImageUrl"]/@src').extract()[0]
		imageItem['thumbnail'] = imageItem['image']

		images = []
		images.append(imageItem)

		colorItem = Color()
		colorItem['type'] = 'color'
		colorItem['show_product_id'] = baseItem['show_product_id']
		colorItem['from_site'] = self.name
		colorItem['images'] = images
		colorItem['name'] = 'one-color'
		yield colorItem
		baseItem['skus'] = skus
		yield baseItem
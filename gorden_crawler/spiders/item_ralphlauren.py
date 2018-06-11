# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector

from gorden_crawler.items import BaseItem, ImageItem, SkuItem, Color
import scrapy
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from scrapy.utils.response import get_base_url
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.ralphlauren import RalphlaurenSpider

class ItemRalphlaurenSpider(ItemSpider):
	name = "item_ralphlauren"
	allowed_domains = ["ralphlauren.com"]

	start_urls = ()

	base_url = 'http://www.ralphlauren.com'
	def parse(self, response):
		sel = Selector(response)
		baseItem = BaseItem()
		baseItem['type'] = 'base'
		baseItem['from_site'] = 'ralphlauren'

		show_product_id_span = sel.xpath('//span[contains(@class, "style-num")]/text()').extract()
		if len(show_product_id_span) == 0:
			return

		baseItem['show_product_id'] = show_product_id_span[0]
		baseItem['url'] = get_base_url(response)
		baseItem['cover'] = ""
		baseItem['product_type'] = ""
		baseItem['category'] = ""
		baseItem['gender'] = ""

		rh = RalphlaurenSpider()

		return rh.handle_parse_item(response, baseItem)
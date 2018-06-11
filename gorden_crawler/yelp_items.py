# -*- coding: utf-8 -*-

from scrapy.item import Field, Item

class ShoppingItem(Item):
	mall = Field()
	status = Field()
	from_site = Field()
	shop_id = Field()
	type = Field()				#value must be 'shopping' 
	name = Field()				#shop name
	address = Field()			#shop address
	telephone = Field()			#shop telephone
	introduction = Field()		#shop introduction			#shop map
	city = Field() 				#shop url
	country = Field()
	coordinate = Field()
	crawl_url = Field()
	shop_url = Field()
	area = Field()
	category = Field()
	cover = Field()
	price_range = Field()
	rating = Field()
	coordinate_zoom = Field()
	open_time_item = Field()
	categories_item = Field()
	country_item = Field()
	city_item = Field()
	images_item = Field()

class CityItem(Item):
	type = Field()
	name = Field()
	country = Field()
	from_site = Field()
	crawl_url = Field()

class CountryItem(Item):
	type = Field()
	name = Field()
	from_site = Field()
	crawl_url = Field()

class OpenTime(Item):
	type = Field()
	day = Field()
	from_site = Field()
	start_time = Field()
	end_time = Field()
	shop_id = Field()

class Category(Item):
	type = Field()
	from_site = Field()
	category = Field()
	crawl_url = Field()
	# subcategory = Field()

class Coordinate(Item):
	longitude = Field()
	latitude = Field()

class Image(Item):
	type = Field()
	shop_id = Field()
	image_id = Field()
	url = Field()
	from_site = Field()
# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
import re
from urllib import unquote
import datetime
import copy
from gorden_crawler.spiders.shiji_base import YelpBaseSpider
from gorden_crawler.yelp_items import ShoppingItem, CityItem, CountryItem, OpenTime, Category, Coordinate, Image
from gorden_crawler.yelp.parse_country.strategy_manager import CountryManager
from urllib import quote
import json
import urlparse
import urllib

class BaseShoppingSpider(object):

	openTime_week_num_mapping = {
		'Mon': 1,
		'Tue': 2,
		'Wed': 3,
		'Thu': 4,
		'Fri': 5,
		'Sat': 6,
		'Sun': 7,
	}

	Japan_openTime_week_num_mapping = {
		u'\u6708': 1,
		u'\u706b': 2,
		u'\u6c34': 3,
		u'\u6728': 4,
		u'\u91d1': 5,
		u'\u571f': 6,
		u'\u65e5': 7,
	}

	Deutschland_openTime_week_num_mapping = {
		u'Mo.' : 1,
		u'Di.' : 2,
		u'Mi.' : 3,
		u'Do.' : 4,
		u'Fr.' : 5,
		u'Sa.' : 6,
		u'So.' : 7,
	}

	Italia_openTime_week_num_mapping = {
		u'lun' : 1,
		u'mar' : 2,
		u'mer' : 3,
		u'gio' : 4,
		u'ven' : 5,
		u'sab' : 6,
		u'dom' : 7,
	}

	France_openTime_week_num_mapping = {
		u'lun.' : 1,
		u'mar.' : 2,
		u'mer.' : 3,
		u'jeu.' : 4,
		u'ven.' : 5,
		u'sam.' : 6,
		u'dim.' : 7,
	}

	Taiwan_openTime_week_num_mapping = {
		u'\u9031\u4e00': 1,
		u'\u9031\u4e8c': 2,
		u'\u9031\u4e09': 3,
		u'\u9031\u56db': 4,
		u'\u9031\u4e94': 5,
		u'\u9031\u516d': 6,
		u'\u9031\u65e5': 7,
	}

	def is_field_empty(self, field):
		if len(field)>0:
			return field[0]
		else:
			return 'None'

	def time_transformer(self, time_str):
		if re.search(r'pm', time_str):
			wanted_time = datetime.datetime.strptime(time_str.strip('pm').strip(), "%H:%M")+datetime.timedelta(hours=12)
			wanted_time_str = datetime.datetime.strftime(wanted_time, "%H:%M")
			return wanted_time_str
			
		elif re.search(r'am', time_str):
			return time_str.strip('am')
			
	def handle_parse_item(self, response, shoppingItem):
		
		sel = Selector(response)
		
		miss_alert = sel.xpath('//b[contains(@class, "i-perm-closed-alert-biz_details-wrap")]').extract()
		if len(miss_alert) > 0:
			return
		
		response_url = str(response.url)
		
		# shop_id = re.search(r'\/([^/]+$)', response_url).group(1)
		shop_id = sel.xpath('//meta[@name="yelp-biz-id"]/@content').extract()
		if len(shop_id) == 0:
			return
		shop_id = shop_id[0]
		
		shoppingItem['type'] = 1
		shoppingItem['mall'] = False
		shoppingItem['from_site'] = 'yelp'
		shoppingItem['name'] = sel.xpath('//h1[contains(@class, "biz-page-title embossed-text-white")]/text()').extract()[0].strip()
		shoppingItem['shop_id'] = shop_id
		rating = sel.xpath('//div[@class="rating-very-large"]//i[contains(@class, "star-img")]/@title').extract()
		if len(rating)>0:
			shoppingItem['rating'] = re.search(r'\d\.\d', self.is_field_empty(rating)).group(0).strip()
		else:
			shoppingItem['rating'] = 0
		telephone = sel.xpath('//span[@class="biz-phone"]/text()').extract()
		temp_telephone = self.is_field_empty(telephone).strip()
		if temp_telephone == 'None':
			shoppingItem['telephone'] = ''
		else:
			shoppingItem['telephone'] = temp_telephone
		price_range = sel.xpath('//dd[@class="nowrap price-description"]/text()').extract()
		temp_price_range = self.is_field_empty(price_range).strip()
		if temp_price_range == 'None':
			shoppingItem['price_range'] = ''
		else:
			shoppingItem['price_range'] = temp_price_range
		address = sel.xpath('//span[@itemprop="streetAddress"]/text()').extract()
		addressLocality = sel.xpath('//span[@itemprop="addressLocality"]/text()').extract()
		shoppingItem['address'] = ''.join(address)+',  '+''.join(addressLocality)

		introduction_dls = sel.xpath('//div[@class="ywidget"]//dl')
		introduction_history_list = sel.xpath('//div[@class="hidden from-biz-owner-wrapper"]//p/text()').extract()
		if len(introduction_history_list)>0:
			introduction_str = ''
			for introduction_history in introduction_history_list:
				introduction_str = introduction_str+introduction_history.strip()+" "
			shoppingItem['introduction'] = introduction_str.strip()
		elif len(introduction_dls) > 0:
			introduction_dl_text = ''
			for introduction_dl in introduction_dls:
				introduction_dl_text = introduction_dl_text + introduction_dl.xpath('./dt/text()').extract()[0].strip()+':'+introduction_dl.xpath('./dd/text()').extract()[0].strip() + '。'
			shoppingItem['introduction'] = str(introduction_dl_text)
		else:
			shoppingItem['introduction'] = ''
		is_shop_url_empty = sel.xpath('//div[@class="biz-website"]/a/@href').extract()
		temp_shop_url = self.is_field_empty(is_shop_url_empty)
		if temp_shop_url == 'None':
			shoppingItem['shop_url'] = ''
		else:
			if re.search(r'http', temp_shop_url):
				shoppingItem['shop_url'] = unquote(re.search(r'http[^&]+', temp_shop_url).group(0))
			else:
				shoppingItem['shop_url'] = unquote(temp_shop_url[0])
		shoppingItem['crawl_url'] = response_url
		
		# open time
		opentimeItem_list = []
		open_time_trs = sel.xpath('//table[@class="table table-simple hours-table"]//tr')
		if len(open_time_trs)>0:
			
			for open_time_tr in open_time_trs:
				openTime = OpenTime()
				openTime['from_site'] = 'yelp'
				# openTime['type'] = 'openTime'
				openTime['shop_id'] = shop_id
				day = open_time_tr.xpath('./th/text()').extract()[0]
				try:
					if shoppingItem['country'] == 'JAPAN':
						openTime['day'] = self.Japan_openTime_week_num_mapping[day]
					elif shoppingItem['country'] == 'DEUTSCHLAND':
						openTime['day'] = self.Deutschland_openTime_week_num_mapping[day]
					elif shoppingItem['country'] == 'ITALIA':
						openTime['day'] = self.Italia_openTime_week_num_mapping[day]
					elif shoppingItem['country'] in ['FRANCE', 'FINLAND']:
						openTime['day'] = self.France_openTime_week_num_mapping[day]
					elif shoppingItem['country'] in ['TAIWAN', 'HONG KONG']:
						openTime['day'] = self.Taiwan_openTime_week_num_mapping[day]
					else:
						openTime['day'] = self.openTime_week_num_mapping[day]
				except:
					print 'day error'+ str(response.url)
				open_time_td = open_time_tr.xpath('./td')[0]
				if len(open_time_td.xpath('./span')) > 0:
					start_time = str(open_time_td.xpath('./span')[0].xpath('./text()').extract()[0])
					end_time = str(open_time_td.xpath('./span')[1].xpath('./text()').extract()[0])
					if shoppingItem['country'] in ['JAPAN', 'DEUTSCHLAND', 'ITALIA', 'FRANCE', 'FINLAND', 'TAIWAN', 'HONG KONG']: 
						openTime['start_time'] = start_time
						openTime['end_time'] = end_time
					else:
						openTime['start_time'] = self.time_transformer(start_time)
						openTime['end_time'] = self.time_transformer(end_time)

				else:
					continue
					# openTime['start_time'] = open_time_td.xpath('./text()').extract()[0]
					# openTime['end_time'] = 'None'
				#yield openTime
				opentimeItem_list.append(openTime)
			
		else: 
			# openTime = OpenTime()
			# # openTime['type'] = 'openTime'
			# openTime['shop_id'] = shop_id
			# openTime['day'] = 'None'
			# openTime['start_time'] = 'None'
			# openTime['end_time'] = 'None'
			# # yield openTime
			# opentimeItem_list.append(openTime)
			pass

		shoppingItem['open_time_item'] = opentimeItem_list
		map_str = str(sel.response.xpath('//div[@class="lightbox-map hidden"]/@data-map-state').extract()[0])
		location = eval(re.sub(r'null', 'None', re.sub(r'true', 'True', re.sub(r'false', 'False', map_str))))
		# coordinate = Coordinate()
		longitude = location['center']['longitude']
		latitude = location['center']['latitude']
		coordinate_dict = []
		coordinate_dict.append(longitude)
		coordinate_dict.append(latitude)
		# coordinate_dict['type'] = 'point'
		# coordinate_dict['coordinates'] = coordinate
		shoppingItem['coordinate'] = coordinate_dict
		shoppingItem['coordinate_zoom'] = location['zoom']
		
		images_url = re.sub(r'biz', 'biz_photos', response_url)
		index = 0
		# yield Request(images_url, callback=self.parse_image_list, meta={'shoppingItem': shoppingItem, 'index': index, 'shop_id': shop_id}, priority=7)
		yield Request(images_url, callback=self.parse_image_list, meta={'shoppingItem': shoppingItem, 'index': index, 'shop_id': shop_id})

	def parse_image_list(self, response):
		
		sel = Selector(response)
		shoppingItem = response.meta['shoppingItem']
		index = response.meta['index']
		shop_id = response.meta['shop_id']
		if index == 0:
			image_list = []
			page_count = len(sel.xpath('//div[contains(@class, "arrange_unit page-option")]')) 
			if page_count == 0:
				page_count = 1
		else:
			page_count = response.meta['page_count']
			image_list = response.meta['image_list']
 
		images = sel.xpath('//ul[@class="photo-box-grid photo-box-grid--highlight photo-box-grid--small clearfix lightbox-media-parent"]//img/@src').extract()
		
		for image in images:
			imageItem = Image()
			# imageItem['type'] = 'image'
			imageItem['from_site'] = 'yelp'
			url = 'http:' + image
			imageItem['url'] = re.sub(r'258s', 'o', url)
			imageItem['shop_id'] = shop_id

			image_list.append(imageItem)

		index = index + 1
		if index == page_count:
			
			shoppingItem['images_item'] = image_list
			yield shoppingItem

		if index < page_count:
			try:
				url = 'http://www.yelp.com'+str(sel.xpath('//div[contains(@class, "arrange_unit page-option")]')[index].xpath('./a/@href').extract()[0])
				yield Request(url, callback=self.parse_image_list, meta={'shoppingItem': shoppingItem, 'index': index, 'shop_id': shop_id, 'page_count': page_count, 'image_list': image_list})
			except:
				shoppingItem['images_item'] = image_list
				yield shoppingItem
			# yield Request(url, callback=self.parse_image_list, meta={'shoppingItem': shoppingItem, 'index': index, 'shop_id': shop_id, 'page_count': page_count, 'image_list': image_list}, priority=7)
			

class YelpShoppingSpider(YelpBaseSpider, BaseShoppingSpider):

	'''
        this proxy below configuration needed when ip is banned by yelp
    '''
	custom_settings = {
#         'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'DOWNLOAD_DELAY': 0.1,
        'DOWNLOADER_MIDDLEWARES': {
            #'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
            #'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
#             'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware':1,
            'gorden_crawler.middlewares.proxy_ats.OpenProxyRandomMiddleware': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        },

        'ITEM_PIPELINES': {
        	'gorden_crawler.pipelines.yelp.YelpPipeline' :  304,
        },
		'DOWNLOAD_TIMEOUT': 30,	
		'COOKIES_ENABLED': True,
    }

	name = 'yelpshopping'

	'''
		caution: JAPAN TAIWAN AUSTRALIA CANADA
	'''

	start_urls = [
		'http://www.yelp.com/locations',      #ok again ok
		'http://nz.yelp.com/locations',       #ok again ok
		'http://zh.yelp.com.hk/locations',    #ok again ok
# 		'http://www.yelp.com.tw/locations',   #ok again ok
		#'http://www.yelp.com.sg/locations',  #ok again ok
# 		'http://en.yelp.my/locations', 
# 		'http://en.yelp.com.ph/locations',
# 		'http://www.yelp.co.jp/locations',    #ok
# 		'http://www.yelp.ca/locations',
# 		'http://www.yelp.com.au/locations',   #ok again ok
# 		'http://www.yelp.at/locations',
# 		'http://en.yelp.be/locations',
# 		'http://www.yelp.pl/locations',
# 		'http://www.yelp.dk/locations',
# 		'http://www.yelp.de/locations',      #not ok 
# 		'http://www.yelp.fr/locations',      #not ok
# 		'http://sv.yelp.fi/locations',
# 		'http://www.yelp.nl/locations',
# 		'http://www.yelp.cz/locations',
# 		'http://www.yelp.no/locations',
# 		'http://www.yelp.pt/locations',
# 		'http://www.yelp.se/locations',
# 		'http://en.yelp.ch/locations',       #ok again
# 		'http://www.yelp.com.tr/locations',
# 		'http://www.yelp.es/locations',      #not ok
		'http://www.yelp.it/locations',      #ok again ok
		'http://www.yelp.co.uk/locations',   #ok again ok
	]

	from_site_url_mapping = {
		'usa': 'http://www.yelp.com/locations',      #ok
		'nz': 'http://nz.yelp.com/locations',       #ok
		'hk': 'http://zh.yelp.com.hk/locations',    #ok again
		'tw': 'http://www.yelp.com.tw/locations',   #ok
		'sg': 'http://www.yelp.com.sg/locations',  #ok
		'my': 'http://en.yelp.my/locations', 
		'ph': 'http://en.yelp.com.ph/locations',
		'jp': 'http://www.yelp.co.jp/locations',   #ok
		'ca': 'http://www.yelp.ca/locations',
		'au': 'http://www.yelp.com.au/locations',  #not ok
		'at': 'http://www.yelp.at/locations',
		'be': 'http://en.yelp.be/locations',
		'pl': 'http://www.yelp.pl/locations',
		'dk': 'http://www.yelp.dk/locations',
		'de': 'http://www.yelp.de/locations',      #not ok 
		'fr': 'http://www.yelp.fr/locations',      #not ok
		'fi': 'http://sv.yelp.fi/locations',
		'nl': 'http://www.yelp.nl/locations',
		'cz': 'http://www.yelp.cz/locations',
		'no': 'http://www.yelp.no/locations',
		'pt': 'http://www.yelp.pt/locations',
		'se': 'http://www.yelp.se/locations',
		'switzerland': 'http://en.yelp.ch/locations',       #not ok
		'tr': 'http://www.yelp.com.tr/locations',
		'spain': 'http://www.yelp.es/locations',      #not ok
		'it': 'http://www.yelp.it/locations',      #ok again
		'uk': 'http://www.yelp.co.uk/locations',   #ok
	}

	country_url_map = {
		'http://www.yelp.com/locations': 'UNITED STATES', 
		'http://nz.yelp.com/locations': 'NEW ZEALAND',	
		'http://zh.yelp.com.hk/locations': 'HONG KONG',
		'http://www.yelp.com.tw/locations': 'TAIWAN',	
		'http://www.yelp.com.sg/locations': 'SINGAPORE',
		'http://en.yelp.my/locations' : 'MALAYSIA', 
		'http://en.yelp.com.ph/locations': 'PHILIPPINES',
		'http://www.yelp.co.jp/locations': 'JAPAN',
		'http://www.yelp.ca/locations': 'CANADA',
		'http://www.yelp.com.au/locations': 'AUSTRALIA',
		'http://www.yelp.at/locations': 'AUSTRIA',
		'http://en.yelp.be/locations': 'BELGIUM',
		'http://www.yelp.pl/locations': 'POLAND',
		'http://www.yelp.dk/locations': 'DANMARK',
		'http://www.yelp.de/locations': 'DEUTSCHLAND',
		'http://www.yelp.fr/locations': 'FRANCE',
		'http://sv.yelp.fi/locations': 'FINLAND',
		'http://www.yelp.nl/locations': 'NEDERLANDS',
		'http://www.yelp.cz/locations': 'CZECH REPUBLIC',
		'http://www.yelp.no/locations': 'NORWAY',
		'http://www.yelp.pt/locations': 'PORTUGAL',
		'http://www.yelp.se/locations': 'SWEDEN',
		'http://en.yelp.ch/locations': 'SWITZERLAND',
		'http://www.yelp.com.tr/locations': 'TURKEY',
		'http://www.yelp.es/locations': 'SPAIN',
		'http://www.yelp.it/locations': 'ITALIA',
		'http://www.yelp.co.uk/locations': 'UNITED KINGDOM',
	}

	country_main_url_mapping = {
		'UNITED STATES' : 'http://www.yelp.com',
		'NEW ZEALAND' : 'http://nz.yelp.com',
		'HONG KONG' : 'http://zh.yelp.com.hk',
		'TAIWAN' : 'http://www.yelp.com.tw',
		'SINGAPORE': 'http://www.yelp.com.sg',
		'MALAYSIA': 'http://en.yelp.my',
		'PHILIPPINES': 'http://en.yelp.com.ph',
		'JAPAN': 'http://www.yelp.co.jp',
		'CANADA': 'http://www.yelp.ca',
		'AUSTRALIA': 'http://www.yelp.com.au',
		'AUSTRIA': 'http://www.yelp.at',
		'BELGIUM': 'http://en.yelp.be',
		'POLAND' :'http://www.yelp.pl',
		'DANMARK':'http://www.yelp.dk',
		'DEUTSCHLAND': 'http://www.yelp.de',
		'FRANCE': 'http://www.yelp.fr', 
		'FINLAND': 'http://sv.yelp.fi',
		'NEDERLANDS': 'http://www.yelp.nl',
		'CZECH REPUBLIC':'http://www.yelp.cz',
		'NORWAY': 'http://www.yelp.no',
		'PORTUGAL': 'http://www.yelp.pt',
		'SWEDEN': 'http://www.yelp.se',
		'SWITZERLAND': 'http://en.yelp.ch',
		'TURKEY': 'http://www.yelp.com.tr',
		'SPAIN': 'http://www.yelp.es',
		'ITALIA': 'http://www.yelp.it',
		'UNITED KINGDOM': 'http://www.yelp.co.uk',
	}

	country_https_mapping = []

	def handle_parse_country(self, country):
		self.name = 'yelpshopping_' + country
		country_start_url = self.from_site_url_mapping[country]
		self.start_urls = [country_start_url]
			

	def parse(self, response):
		sel = Selector(response)
		
		need_https = False
		search_url = response.url
		if re.match(r'^https:\/\/', response.url):
			search_url = re.sub('https', 'http', search_url)
			need_https = True

		country = self.country_url_map[search_url]
		
		if country == 'HONG KONG':
			url = 'http://zh.yelp.com.hk/'
			city = 'hongkong'
			yield Request(url, callback=self.parse_place, meta={'country': country, 'city': city})
		else:
			if need_https:
				self.country_https_mapping.append(country)
			
			base_url = self.get_country_base_url_from_mapping(country)
	
			countryManager = CountryManager(sel, country, base_url)
			strategy = countryManager.getStrategy(country);
			request_array = strategy.parse_country() 
			for request in request_array:
				url = request[0]
				country = request[1]
				city = request[2]
	# 			print 'city:' + city + ',---url:' + url
	 			
				# yield Request(request[0], callback=self.parse_place, meta={'country': request[1], 'city': request[2]}, priority=1)
				yield Request(url, callback=self.parse_place, meta={'country': country, 'city': city})

	def parse_place(self, response):

		country = response.meta['country']
		city = response.meta['city']
		
		# print country+ "  " + city
		
		url = self.get_country_base_url_from_mapping(country) + '/best_of_yelp/shopping/snippet'
		
# 		print url
		
		yield Request(url, callback=self.parse_place_more_shopping, dont_filter=True, meta={'country': country, 'city': city}, headers={'X-Requested-With': 'XMLHttpRequest'})
		
		'''
			the big category is shopping
		'''
# 		temp_url = sel.xpath('//div[@class="navigation"]//li')[3].xpath('./a/@href').extract()[0]
# 		category_url = self.country_main_url_mapping[country] + str(temp_url)
# 		
# 		print 'category_url:'+category_url
# 		# yield Request(category_url, callback=self.parse_big_category, meta={'country': country, 'city': city}, priority=2)
# 		yield Request(category_url, callback=self.parse_big_category, meta={'country': country, 'city': city})

	def parse_place_more_shopping(self, response):
		
		country = response.meta['country']
		city = response.meta['city']
		
		result_json = json.loads(response.body)
		body = result_json['body']

		sel =  Selector(text = body)
		more_a = sel.xpath('//li[@data-section-id="shopping"]//a[@class="link-more"]/@href').extract()
		
		# print more_a[0]
		if len(more_a) > 0:
			url = self.get_country_base_url_from_mapping(country) + more_a[0]

			yield Request(url, callback=self.parse_big_category, meta={'country': country, 'city': city})


	def parse_big_category(self, response):
		sel = Selector(response)
		country = response.meta['country']
		city = response.meta['city']
		category_uls = sel.xpath('//ul[@class="arrange arrange--12 arrange--wrap arrange--6-units"]//ul[@class="ylist"]')
		
		'''
			parse_shops
		'''
		for category_ul in category_uls:
			category_as = category_ul.xpath('./li/a')
			for category_a in category_as:
				temp_url = category_a.xpath('./@href').extract()[0]
				url = self.get_country_base_url_from_mapping(country) + str(temp_url)
				# url = unquote(url)

# 				print url
				# yield Request(url, callback=self.parse_area, meta={'country': country, 'city': city}, priority=3)
				yield Request(url, callback=self.parse_more_shops_url, meta={'country': country, 'city': city})

	def parse_more_shops_url(self, response):
		
		country = response.meta['country']
		city = response.meta['city']
		
		sel = Selector(response)
		
		a = sel.xpath('//a[contains(@class,"button-more")]/@href').extract()
		
		if len(a) > 0:
			url = self.get_country_base_url_from_mapping(country) + a[0]
			
			yield Request(url, callback=self.parse_shops, meta={'area': '','country': country, 'city': city})
		else:
# 			print 'miss----' + response.url
			
			suggestions_grid = sel.xpath('//div[@class="suggestions-grid js-search-exception-links"]/ul/li')
			if len(suggestions_grid) > 0:
				url = self.get_country_base_url_from_mapping(country) + suggestions_grid.xpath('./a/@href').extract()[0]
# 				print url
				yield Request(url, callback=self.parse_shops, meta={'area': '','country': country, 'city': city})
			else:
				country = response.meta['country']
				city = response.meta['city']
				area = ''
				shop_lis = sel.xpath('//ul[@class="ylist ylist-bordered search-results"]/li[@class="regular-search-result"]')
			
				shop_lis_len = len(shop_lis)
				shop_lis_ignore_num = 0
				
				for shop_li in shop_lis:
					
					price_range_len = len(shop_li.xpath('.//span[contains(@class, "business-attribute price-range")]').extract())
					biz_rating_len = len(shop_li.xpath('.//div[contains(@class, "biz-rating")]').extract())
					
					if price_range_len == 0 and biz_rating_len == 0:
						shop_lis_ignore_num = shop_lis_ignore_num + 1
						continue
					
					temp_shop_url = str(shop_li.xpath('.//a[contains(@class,"biz-name")]/@href').extract()[0])
					shop_cover = 'http:' + str(shop_li.xpath('.//img[@class="photo-box-img"]/@src').extract()[0])
					if shop_cover == 'http://s3-media4.fl.yelpcdn.com/assets/srv0/yelp_styleguide/c73d296de521/assets/img/default_avatars/business_90_square.png':
						shop_cover = ''
					else:
						shop_cover = re.sub(r'90s', 'o', shop_cover)
					
					if re.search(r'=http', temp_shop_url):
						re_shop_url = re.search(r'http[^&]+', temp_shop_url).group(0)
						shop_url = unquote(re_shop_url)
					else:
						shop_url = self.get_country_base_url_from_mapping(country) + temp_shop_url
					
					categoryItem_list = []
					category_names = []
					
					categorys = shop_li.xpath('.//span[@class="category-str-list"]/a/@href').extract()
					
					for category in categorys:
						categoryItem = Category()
						categoryItem['from_site'] = 'yelp'
						categoryItem['crawl_url'] = shop_url
						
						query_string_dict = dict(urlparse.parse_qsl(urlparse.urlsplit(category).query))
						
						finalstr = query_string_dict['cflt']
					
						finalstr = urllib.unquote(str(finalstr)).decode('UTF-8')
					
						categoryItem['category'] = finalstr
						category_names.append(finalstr)
						categoryItem_list.append(categoryItem)
					
					shoppingItem = ShoppingItem()
					#categoryItem_list
					shoppingItem['status']=1
					shoppingItem['categories_item'] = categoryItem_list
					shoppingItem['cover'] = shop_cover
					shoppingItem['category'] = category_names
					cityItem = CityItem()
					# cityItem['type'] = 'city'
					cityItem['name'] = city
					cityItem['country'] = country
					cityItem['from_site'] = 'yelp'
					cityItem['crawl_url'] = shop_url
					#city
					shoppingItem['city_item'] = cityItem
					shoppingItem['city'] = city
					shoppingItem['area'] = area
					countryItem = CountryItem()
					# countryItem['type'] = 'country'
					countryItem['name'] = country
					countryItem['from_site'] = 'yelp'
					countryItem['crawl_url'] = shop_url
					
					shoppingItem['country_item'] = countryItem
					shoppingItem['country'] = country
		
					# shoppingItemCopy = copy.deepcopy(shoppingItem)
					# yield Request(shop_url, callback=self.parse_item, meta={'shoppingItem': shoppingItem}, priority=6)
					yield Request(shop_url, callback=self.parse_item, meta={'shoppingItem': shoppingItem})
		
				if shop_lis_ignore_num < shop_lis_len : 
					next_page = sel.xpath('//a[@class="u-decoration-none next pagination-links_anchor"]/@href').extract()
					if len(next_page)>0:
						next_page_url = next_page[0]
						url = self.get_country_base_url_from_mapping(country) + next_page_url
						# yield Request(url, callback=self.parse_shops, meta={'area': area, 'city': city, 'country':country}, priority=5)
						yield Request(url, callback=self.parse_shops, meta={'area': area, 'city': city, 'country':country})
			
	def parse_shops(self, response):
		
		sel = Selector(response)
		
		country = response.meta['country']
		city = response.meta['city']
		area = response.meta['area']
		
		suggestions_grid = sel.xpath('//div[@class="suggestions-grid js-search-exception-links"]/ul/li')
		if len(suggestions_grid) > 0:
			url = self.get_country_base_url_from_mapping(country) + suggestions_grid.xpath('./a/@href').extract()[0]
			yield Request(url, callback=self.parse_shops, meta={'area': '','country': country, 'city': city})
		else:
			shop_lis = sel.xpath('//ul[@class="ylist ylist-bordered search-results"]/li[@class="regular-search-result"]')
			
			shop_lis_len = len(shop_lis)
			shop_lis_ignore_num = 0
			
			for shop_li in shop_lis:
				
				price_range_len = len(shop_li.xpath('.//span[contains(@class, "business-attribute price-range")]').extract())
				biz_rating_len = len(shop_li.xpath('.//div[contains(@class, "biz-rating")]').extract())
				
				if price_range_len == 0 and biz_rating_len == 0:
					shop_lis_ignore_num = shop_lis_ignore_num + 1
					continue
				
				temp_shop_url = str(shop_li.xpath('.//a[contains(@class,"biz-name")]/@href').extract()[0])
				shop_cover = 'http:' + str(shop_li.xpath('.//img[@class="photo-box-img"]/@src').extract()[0])
				if shop_cover == 'http://s3-media4.fl.yelpcdn.com/assets/srv0/yelp_styleguide/c73d296de521/assets/img/default_avatars/business_90_square.png':
					shop_cover = ''
				else:
					shop_cover = re.sub(r'90s', 'o', shop_cover)
				
				if re.search(r'=http', temp_shop_url):
					re_shop_url = re.search(r'http[^&]+', temp_shop_url).group(0)
					shop_url = unquote(re_shop_url)
				else:
					shop_url = self.get_country_base_url_from_mapping(country) + temp_shop_url
				
				categoryItem_list = []
				category_names = []
				categoryItem = Category()
				
				categoryItem['from_site'] = 'yelp'
				categorys = shop_li.xpath('.//span[@class="category-str-list"]/a/@href').extract()
				categoryItem['crawl_url'] = shop_url
				for category in categorys:
					query_string_dict = dict(urlparse.parse_qsl(urlparse.urlsplit(category).query))
					
					finalstr = query_string_dict['cflt']
					
					finalstr = urllib.unquote(str(finalstr)).decode('UTF-8')
				
					categoryItem['category'] = finalstr
					category_names.append(finalstr)
					categoryItem_list.append(categoryItem)
	
				shoppingItem = ShoppingItem()
				#categoryItem_list
				shoppingItem['status']=1
				shoppingItem['categories_item'] = categoryItem_list
				shoppingItem['cover'] = shop_cover
				shoppingItem['category'] = category_names
				cityItem = CityItem()
				# cityItem['type'] = 'city'
				cityItem['name'] = city
				cityItem['country'] = country
				cityItem['from_site'] = 'yelp'
				cityItem['crawl_url'] = shop_url
				#city
				shoppingItem['city_item'] = cityItem
				shoppingItem['city'] = city
				shoppingItem['area'] = area
				countryItem = CountryItem()
				# countryItem['type'] = 'country'
				countryItem['name'] = country
				countryItem['from_site'] = 'yelp'
				countryItem['crawl_url'] = shop_url
				
				shoppingItem['country_item'] = countryItem
				shoppingItem['country'] = country
	
				# shoppingItemCopy = copy.deepcopy(shoppingItem)
				# yield Request(shop_url, callback=self.parse_item, meta={'shoppingItem': shoppingItem}, priority=6)
				yield Request(shop_url, callback=self.parse_item, meta={'shoppingItem': shoppingItem})
	
			if shop_lis_ignore_num < shop_lis_len : 
				next_page = sel.xpath('//a[@class="u-decoration-none next pagination-links_anchor"]/@href').extract()
				if len(next_page)>0:
					next_page_url = next_page[0]
					url = self.get_country_base_url_from_mapping(country) + next_page_url
					# yield Request(url, callback=self.parse_shops, meta={'area': area, 'city': city, 'country':country}, priority=5)
					yield Request(url, callback=self.parse_shops, meta={'area': area, 'city': city, 'country':country})

	def parse_item(self, response):
		shoppingItem = response.meta['shoppingItem']
		return self.handle_parse_item(response, shoppingItem)

	def handle_parse_item(self, response, shoppingItem):
		return BaseShoppingSpider.handle_parse_item(self, response, shoppingItem)


	def get_country_base_url_from_mapping(self, country):
		country_base_url = self.country_main_url_mapping[country]
		
		if country in self.country_https_mapping and re.match(r'^http:\/\/', country_base_url):
			country_base_url = re.sub('http', 'https', country_base_url)
			
		return country_base_url


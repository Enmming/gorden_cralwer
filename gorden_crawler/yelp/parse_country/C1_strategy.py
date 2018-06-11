from base_strategy import BaseCountry
from scrapy import Request

class C1Country(BaseCountry):

	def __init__(self, sel, base_url, country):
		BaseCountry.__init__(self, sel, base_url, country)

	def parse_country(self):
		place_lis = self.sel.xpath('//ul[@class="locations-list"]')[-3].xpath('./li')[1:].xpath('.//li')
		temp_place_lis = self.sel.xpath('//ul[@class="locations-list"]')[-2:].xpath('.//ul[@class="cities"]/li')
		place_lis.extend(temp_place_lis)
		request_array = []
		for place_li in place_lis:
			city = place_li.xpath('./a/text()').extract()[0]			# cities is a list
			temp_url = place_li.xpath('./a/@href').extract()[0]
			place_url = self.base_url + str(temp_url)
			request_array.append((place_url, self.country, city))

		return request_array
		

from base_strategy import BaseCountry

class Austria(BaseCountry):
	def __init__(self, sel, base_url, country):
		self.sel = sel
		self.base_url = base_url
		self.country = country

	def parse_country(self):
		place_lis = self.sel.xpath('//div[contains(@class, "column column-alpha")]/ul')[0:2].xpath('.//ul[@class="cities"]/li')
		place_lis_temp = self.sel.xpath('//div[contains(@class, "column column-alpha")]/ul')[2].xpath('./li')[0].xpath('.//li')
		place_lis.extend(place_lis_temp)
		request_array = []
		for place_li in place_lis:
			city = place_li.xpath('./a/text()').extract()[0]			# cities is a list
			temp_url = place_li.xpath('./a/@href').extract()[0]
			place_url = self.base_url + str(temp_url)
			request_array.append((place_url, self.country, city))
		return request_array
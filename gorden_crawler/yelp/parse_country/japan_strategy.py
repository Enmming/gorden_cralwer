from base_strategy import BaseCountry

class Japan(BaseCountry):
	def __init__(self, sel, base_url, country):
		self.sel = sel
		self.base_url = base_url
		self.country = country

	def parse_country(self):
		place_lis = self.sel.xpath('//div[contains(@class, "column column-alpha")]/ul')[0:5].xpath('.//ul[@class="cities"]/li')
		request_array = []
		for place_li in place_lis:
			city = place_li.xpath('./a/text()').extract()[0]			# cities is a list
			temp_url = place_li.xpath('./a/@href').extract()[0]
			place_url = self.base_url + str(temp_url)
			request_array.append((place_url, self.country, city))
		return request_array


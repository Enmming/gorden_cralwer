from base_strategy import BaseCountry

class C2Country(BaseCountry):

	def __init__(self, sel, base_url, country):
		BaseCountry.__init__(self, sel, base_url, country)

	def parse_country(self):
		place_lis = self.sel.xpath('//ul[@class="locations-list"]')[0].xpath('./li[@class="state"]')[0].xpath('.//ul[@class="cities"]/li')
		request_array = []
		for place_li in place_lis:
			city = place_li.xpath('./a/text()').extract()[0]
			temp_url = place_li.xpath('./a/@href').extract()[0]
			place_url = self.base_url + str(temp_url)
			request_array.append((place_url, self.country, city))

		return request_array
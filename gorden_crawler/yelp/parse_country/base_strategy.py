from abc import abstractmethod

class BaseCountry(object):
	def __init__(self, sel, base_url, country):
		self.sel = sel
		self.base_url = base_url
		self.country = country

	@abstractmethod
	def parse_country(self):
		pass
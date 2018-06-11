from .C1_strategy import C1Country
from .C2_strategy import C2Country
from .taiwan_strategy import Taiwan
from .sweden_strategy import Sweden
from .austria_strategy import Austria
from .canada_strategy import Canada
from .japan_strategy import Japan

class CountryManager(object):
	#us
	C1 = ['UNITED STATES']
	#uk
	C2 = ['NEW ZEALAND', 'SWITZERLAND', 'HONG KONG', 'SINGAPORE', 'MALAYSIA', 'PHILIPPINES', 'BELGIUM',  'FINLAND', 'CZECH REPUBLIC', 'NORWAY', 'PORTUGAL', 'TURKEY']  
	#one and half column
	TAIWAN = ['TAIWAN', 'NEDERLANDS']
	#two column
	SWEDEN = ['SWEDEN', 'POLAND',  'DANMARK']
	#two and half column
	AUSTRIA = ['AUSTRIA']
	# four and half column
	CANADA = ['CANADA','DEUTSCHLAND', 'FRANCE', 'ITALIA']
	#five column
	JAPAN = ['JAPAN', 'AUSTRALIA', 'SPAIN', 'UNITED KINGDOM'] 
	
	# C3 = ['TAIWAN', 'JAPAN', 'CANADA', 'AUSTRALIA', 'AUSTRIA', 'DEUTSCHLAND', 'FRANCE', 'NEDERLANDS', 'SWEDEN',, 'SPAIN', 'ITALIA', 'UNITED KINGDOM']

	def __init__(self, sel, country, base_url):
		self.sel = sel
		self.country = country
		self.base_url = base_url

	def getStrategy(self, country):
		if country in self.C1:
			return C1Country(self.sel, self.base_url, self.country)
		elif country in self.C2:
			return C2Country(self.sel, self.base_url ,self.country)
		elif country in self.TAIWAN:
			return Taiwan(self.sel, self.base_url, self.country)
		elif country in self.SWEDEN:
			return Sweden(self.sel, self.base_url, self.country)
		elif country in self.AUSTRIA:
			return Austria(self.sel, self.base_url, self.country)
		elif country in self.CANADA:
			return Canada(self.sel, self.base_url, self.country)
		elif country in self.JAPAN:
			return Japan(self.sel, self.base_url, self.country)
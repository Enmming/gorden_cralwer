class BaseStrategy(object):
    
    SIZE_TYPE_US = 'us'
    SIZE_TYPE_EU = 'eu'
    SIZE_TYPE_UK = 'uk'
    SIZE_TYPE_IT = 'it'
    SIZE_TYPE_FR = 'fr'
    SIZE_TYPE_Dk = 'dk'
    SIZE_TYPE_AU = 'au'
    SIZE_TYPE_JP = 'jp'
    
    def getRemap(self):
        pass
    
    def transform(self, size, re, site, key):
        pass
    
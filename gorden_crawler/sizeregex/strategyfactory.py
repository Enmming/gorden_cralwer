class StrategyFactory(object):
    
    def getStrategy(self, site):
        rc = __import__('gorden_crawler.sizeregex.' + site, globals={}, locals={}, fromlist=site)
        
        return getattr(rc, site.capitalize())
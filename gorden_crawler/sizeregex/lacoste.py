import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Lacoste (BaseStrategy):

    def transform(self, size, reg, site, key):
        p = re.compile(reg)
        m = p.match(size)
        if m:
            if(len(m.groups()) < 2):
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(1)
            else:
                sizeType = m.group(1)
                if(sizeType == 'US'):
                    sizeType = self.SIZE_TYPE_US
                elif(sizeType == 'EU' or 'eu' or 'EUR' or 'eur'):
                    sizeType = self.SIZE_TYPE_EU
                standardSize = m.group(2).strip()

            p2 = re.compile('/^(\d)T\/(\d)T$/')
            m2 = p2.match(standardSize)
            if m2:
                standardSize = m2.group(1) + '/' + m2.group(2)
            return [sizeType, standardSize]
        return
    
    
    def getReMap(self):  
        return[
               #10 (UK 8)
               '^([\d\.]+)\s*\(UK\s*[A-Za-z\d\.]+\)$',
               #XL (EUR XL)
               '^([A-Za-z]+)\s*\(EUR\s*[A-Za-z]+\)$',
               #43 IN (EUR 110)
               '^[\d\.]+\s*IN\s*\((EUR|eur)\s*([\d\.]+)\s*\)$',
               
               
               
               
               ]
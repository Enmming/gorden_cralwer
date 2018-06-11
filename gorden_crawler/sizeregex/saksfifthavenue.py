import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Saksfifthavenue (BaseStrategy):

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
            
            if key == 3 and (re.findall(r'-', m.group(1))):
                standardSize = re.sub(r'-', '', m.group(1))
                
            return [sizeType, standardSize]
        return
    
    
    def getReMap(self):  
        return[
               #38 (8)
               '^[\d\.-\/]+\s*\(([\d\.-]+)\)$',
               #MED
               '^[\d\.]*\s*\(?(M)[EDIUM]+\)?$',
               #UK 10 (6)
               '^UK\s*[\d\.]+\s*\(([\d\.]+)\)$',
               #XLRG
               '^[\d\.]*\s*\(?(X*[LS-]+)[ARGEML]+\)?$',
               #36/6
               '^[\d\.]+\/([\d\.]+)$'
               ]
import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Farfetch (BaseStrategy):

    def transform(self, size, reg, site, key):
        p = re.compile(reg)
        m = p.match(size)
        if m:
            if(len(m.groups()) < 2):
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(1)
            else:
                sizeType = m.group(2)
                if(sizeType == 'US'):
                    sizeType = self.SIZE_TYPE_US
                elif(sizeType == 'EU'):
                    sizeType = self.SIZE_TYPE_EU
                elif(sizeType == 'IT'):
                    sizeType = self.SIZE_TYPE_IT
                elif(sizeType == 'AU'):
                    sizeType = self.SIZE_TYPE_AU
                elif(sizeType == 'JP'):
                    sizeType = self.SIZE_TYPE_JP
                    
                standardSize = m.group(1).strip()
            return [sizeType, standardSize]
        else:
            return
    
    
    def getReMap(self):
        
        return [
                #40 IT
                '^\s*([\d\.]+)\s*(IT|US|UK|FR|BR|AU|EU)\s*$',
                #3 yrs
                '^\s*([\d\.-]+)\s*[yrsmth]+\s*$'
                
                
                
                ] 
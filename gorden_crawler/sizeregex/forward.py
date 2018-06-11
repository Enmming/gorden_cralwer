import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Forward (BaseStrategy):

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
                elif(sizeType == 'EU'):
                    sizeType = self.SIZE_TYPE_EU
                elif(sizeType == 'IT'):
                    sizeType = self.SIZE_TYPE_IT
                elif(sizeType == 'AU'):
                    sizeType = self.SIZE_TYPE_AU
                elif(sizeType == 'JP'):
                    sizeType = self.SIZE_TYPE_JP
                    
                standardSize = m.group(2).strip()
            return [sizeType, standardSize]
        else:
            return
    
    
    def getReMap(self):
        
        return [
                #40 IT
                '^\s*(IT|US|UK|FR|BR|AU)\s*([\d\.]+)\s*$',
                #Aus 10/US 6
                '^\s*Aus\s*[\d\.]+\s*/\s*(US)\s*([\d\.]+)\s*$',
                #36 (2)
                '^\s*[\d\.]+\s*\(\s*([\d\.]+)\s*\)\s*$',
                #JP6 / US10-11
                '^\s*[JPEur]+\s*[\d\.]+\s*/\s*(US)\s*[\d\.\-]+\s*$'
                
                ] 
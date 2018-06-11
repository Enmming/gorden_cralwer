import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Levi (BaseStrategy):

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
                standardSize = m.group(2).strip()
            if key == 1:
                sizeType = self.SIZE_TYPE_US
                standardSize = int(m.group(1))*'X' + m.group(2)
                
            return [sizeType, standardSize]
        else:
            return
    
    
    def getReMap(self):
    
        return[               
               #18M
               '^\s*([\d\.]+)\s*[MTR]+\s*$',
               #2XL
               '^\s*([\d]+)X(L|S)\s*$',
               ]
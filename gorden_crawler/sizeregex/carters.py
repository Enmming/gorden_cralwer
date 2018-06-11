import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Carters (BaseStrategy):

    def transform(self, size, reg, site, key):
        p = re.compile(reg)
        m = p.match(size)
        if m:
#             if key == 0:
#                 sizeType = self.SIZE_TYPE_US;
#                 standardSize = 'One Size'
#                 return [sizeType, standardSize]
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
                sizeType = self.SIZE_TYPE_US;
                standardSize = m.group(1) + '-' + m.group(2)
            return [sizeType, standardSize]
        else:
            return
    
    
    def getReMap(self):
        
        return [
#                 'OSZ',
                #6M
                '^\s*([\d\.\-]+)\s*[WMT]+\s*$',
                #4Y-8Y
                '^\s*([\d\.]+)Y\s*\-\s*([\d\.]+)Y\s*$'
                
                
                ] 
import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Allsole (BaseStrategy):

    def transform(self, size, reg, site, key):
        p = re.compile(reg)
        m = p.match(size)
        if m:
#             if key == 0:
#                 sizeType = self.SIZE_TYPE_US
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
                elif(sizeType == 'UK'):
                    sizeType = self.SIZE_TYPE_UK
                standardSize = m.group(2).strip()
            return [sizeType, standardSize]
        else:
            return
    
    
    def getReMap(self):
    
        return[
               #onesize
#                '^\s*(OSZ|one-size|one size|onesize|ONESIZE|one size|One Size|no size|No Size|NO SIZE)$',
               #UK 5.5
               '^\s*(UK)\s*([\d\.]+)\s*$',
               #US 6/UK 3
               '^\s*(US)\s*([\d\.]+)\s*\/\s*[UKEU]+\s*[\d\.]+\s*$',
               #EU 39-40/UK 6-7
               '^\s*[EU]+\s*[\d\.\-]+\s*\/\s*(UK)\s*([\d\.\-]+)\s*$',
               #UK 3/EU 36
               '^\s*(UK)\s*([\d\.]+)\s*\/\s*[EU]+\s*[\d\.]+\s*$',
               #UK 11/US 12
               '^\s*[UK]+\s*[\d\.]+\s*\/\s*(US)\s*([\d\.]+)\s*$',
               ]
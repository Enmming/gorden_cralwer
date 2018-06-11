import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Oshkosh (BaseStrategy):

    def transform(self, size, reg, site, key):
        p = re.compile(reg)
        m = p.match(size)
        if m:
            if key == 0:
                sizeType = self.SIZE_TYPE_US
                standardSize = 'One Size'
                return [sizeType, standardSize]
            
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
            if key == 2:
                sizeType = self.SIZE_TYPE_US
                standardSize = standardSize + ' Months'
                
            if key == 3:
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(1) + '/' + m.group(2)
            return [sizeType, standardSize]
        else:
            return
    
    
    def getReMap(self):
    
        return[               
               #onesize
               '^\s*(OSZ|one-size|one size|onesize|ONESIZE|one size|no size|No Size|NO SIZE)$',
               #12M
               '^\s*([\d\.\-\/]+)\s*[MTWRHYP]+\s*$',
               #12-24 mo.
               '^\s*([\d\.\-]+)\s*mo\.\s*$',
               #2T-4T
               '^\s*([\d\.]+)T\s*\-\s*([\d\.]+)T\s*$',
               ]
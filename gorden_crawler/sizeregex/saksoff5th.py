import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Saksoff5th (BaseStrategy):

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
            return [sizeType, standardSize]
        else:
            return
        
    
    def getReMap(self):
    
        return [
                #one-size
#                 '^\s*(one-size|one size|onesize|ONESIZE|ONE SIZE|one size|One Size|no size|No Size|NO SIZE)$',
                #26 (2-4)
                '^\s*[\d\.X]+\s*\(\s*([\d\.\-]+)\s*\)\s*$',
                #8.5 M
                '^\s*([\d\.]+)\s*[MWRLNS]+$',
                #2 (M)
                '^\s*([\d\.]+)\s*\([MSLX]+\)$',
                #6 EE
                '^\s*([\d\.]+)\s*EE$',
                #L (9-10)
                '^\s*[LMXS]\s*\(([\d\.\-]+)\)$',
                #MED
                '^(M)ED$',
                ]
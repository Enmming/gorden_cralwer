# -*- coding: utf-8 -*-
import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Eastdane (BaseStrategy):

    def transform(self, size, reg, site, key):
        p = re.compile(reg)
        m = p.match(size)
        if m:
#             if key == 0 or key == 1:
#                 sizeType = self.SIZE_TYPE_US;
#                 standardSize = 'One Size'
#                 return
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
                #nosize/onesize
#                 '^\s*(onesize|ONESIZE|one size|One Size|no size|No Size|OneSize)\s*$',
                #均码
#                 u'^\s*\u5747\u7801\s*$',
                #40L
                '^\s*([\d\.]+)\s*[RLS]+\s*$'
                
                ] 
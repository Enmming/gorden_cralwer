import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Forzieri (BaseStrategy):

    def transform(self, size, reg, site, key):
        p = re.compile(reg)
        m = p.match(size)
        if m:
#             if key == 7:
#                 sizeType = self.SIZE_TYPE_US
#                 standardSize = 'One Size'
#                 return [sizeType, standardSize]
#             
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
            
            if key == 4 or key == 5:
                sizeType = self.SIZE_TYPE_UK
                standardSize = m.group(1)
            if key == 2:
                sizeType = self.SIZE_TYPE_IT
                standardSize = m.group(1)
            return [sizeType, standardSize]
        return
    
    
    def getReMap(self):  
        return[
               #37 (7 US | 4 UK | 37 EU)
               '^[\d\.\sMFR]*\(?([\d\.]+)\s*[US]*\s*\|[\d\.\sa-zA-Z\|]*\)?\s*$',
               #USA 7 | IT 14 | UK N
               '^\s*USA\s*([\d\.]+)[[\d\.\sa-zA-Z\|]*\s*$',
               #38\" (USA, UK) - 48 (IT)
               '^\s*.+\"\s*\([\.\sa-zA-Z\,]+\)[\s\-]+([\d\.]+)\s*\(IT\)\s*$',
               #8 (USA) - 44 (IT)
               '^\s*([\d\.]+)\s*\(USA\)[\s\-\d\.\(a-zA-Z\)]*$',
               #7.5 (7.5 MENS US| 9.5 WOMENS US|  7.5 UK | 41 EU)
               '^\s*[\d\.\s]+\([\d\.\s]+[WOMENS]+[US\s]+\|\s*[\d\.\s]+[WOMENS]+[US\s]+\|\s*([\d\.]+)\s*(UK)[\s\|\d\.EU]+\)\s*$',
               #9.5 (9.5 MENS US | 9.5 UK | 43 EU) 
               '^\s*[\d\.\s]+\(?[\d\.\s]+[WOMENS]+[\sUS]+\|\s*([\d\.]+)\s*(UK)[\s\|\d\.EU]+\)?\s*$',
               #C - USA 8.75 | IT 18 | UK Q
               '^[ACLBRGT\s-]+(US)A\s*([\d\.]+)\s*[\d\.\sa-zA-Z\|]*$',
               #nosize/onesize
#                '^\s*(onesize|ONESIZE|one size|One Size|no size|No Size)\s*$',
               
               ]
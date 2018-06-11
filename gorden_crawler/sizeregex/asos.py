import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Asos (BaseStrategy):
    def transform(self, size, reg, site, key):
        p = re.compile(reg)
        m = p.match(size)
        if m:
            if key == 14:
                sizeType = self.SIZE_TYPE_US
                if (m.group(2)):
                    standardSize = m.group(1) + ' ' + m.group(2)
                else:
                    standardSize = m.group(1)
                return [sizeType, standardSize]
            
#             if key== 15:
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
            standardSize = standardSize.replace(' ', '')
            return [sizeType, standardSize]
        else:
            return
    def getReMap(self):
        return [
            '^\s*(US)\s*([\d\.]+)\s*$',
#             '^\s*(US)\s*([\d\.]+)\s*(\(W[\d\.]+\s*-\s*[\d\.]+cm\))?',
            '^\s*(EU)\s*([\d\.]+)\s*(\(W[\d\.]+\s*-\s*[\d\.]+cm\))?',

            '^\s*(US)\s*([\d\.]+\s*-\s*[\d\.]+)\s*(\(W[\d\.]+\s*-\s*[\d\.]+cm\))?',
            '^\s*(EU)\s*([\d\.]+\s*-\s*[\d\.]+)\s*(\(W[\d\.]+\s*-\s*[\d\.]+cm\))?',

            '^\s*(US)\s*([\d\.]+[A-Za-z]+(\s*\/[A-Za-l\-]+)?)',
            '^\s*(EU)\s*([\d\.]+[A-Za-z]+(\s*\/[A-Za-l\-]+)?)',

            '^\s*(US)\s*([\d\.]+\s+[A-La-l\-]+\/[A-La-l\-]+)',
            '^\s*(EU)\s*([\d\.]+\s+[A-La-l\-]+\/[A-La-l\-]+)',

            '^\s*(US)\s*([\d\.]+\s*-\s*[\d\.]+\s+[A-La-l\-]+\/[A-La-l\-]+)',
            '^\s*(EU)\s*([\d\.]+\s*-\s*[\d\.]+\s+[A-La-l\-]+\/[A-La-l\-]+)',

            '^\s*(US)\s*([\d\.]+)\s+[L-Z]([A-Za-z\d\.]+)?\s*',
            '^\s*(EU)\s*([\d\.]+)\s+[L-Z]([A-Za-z\d\.]+)?\s*',

            '^\s*Size (\d+)',
            '^\s*US\s+Size\s+(\d+)',
            
            #W32in
            '^\s*([wW\d\.-]+)in\s*([lL\d\.-]+)*[in]*\s*$',
            #nosize/onesize
#             '^\s*(onesize|ONESIZE|one size|One Size|no size|No Size)\s*$',
            #UK12
            '^\s*(UK)\s*([\d\.]+)\s*$',
        ]
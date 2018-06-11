import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Ralphlauren (BaseStrategy):

    def transform(self, size, reg, site, key):
        p = re.compile(reg)
        m = p.match(size)
        if m:
            if key == 0:
                sizeType = self.SIZE_TYPE_US;
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
            
            if key == 1:
                sizeType = self.SIZE_TYPE_US
                standardSize = int(m.group(1))*'X' + m.group(2)
            if key == 3:
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(1) + ' Months'

            if key == 8:
                sizeType = self.SIZE_TYPE_US
                if m.group(2) == 'MOS':
                    standardSize = m.group(1) + ' Months'
                elif m.group(2) == 'WKS':
                    standardSize = m.group(1) + ' Weeks'
                else:
                    return
            return [sizeType, standardSize]
        else:
            return
    
    
    def getReMap(self):
        
        return [
                '^(O/S|onesize|ONESIZE|one size|One Size|no size|No Size)$',
                #2XL
               '^\s*([\d]+)X(L|S)\s*$',
                #12M
               '^\s*([\d\.\-\/]+)\s*[MTWP]+\s*$',
                #9MOS
                '^\s*([\d\.]+)\s*MOS\s*$',
                #Big 3X
                '^\s*[BigTalPetite]+\s*([\d\.XL]+)\s*$',
                #Big X
                '^\s*[BigTal]+\s*([XL]+)\s*$',
                #38 Regular
                '^\s*([\d\.]+)\s*[RegularLongShortEGDB]+\s*$',
                #Petite M
                '^\s*Petite\s*([MXSL]+)\s*$',
                #3 (6-9 MOS)
                '^\s*[\d\.]+\s*\(([\d\.\-]+)\s*(MOS|WKS)\s*\)$',
                ]    
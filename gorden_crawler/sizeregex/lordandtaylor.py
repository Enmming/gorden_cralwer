import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Lordandtaylor (BaseStrategy):

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
                if key == 5:
                    sizeType = self.SIZE_TYPE_US
                    standardSize = m.group(1) + m.group(2)
            if key == 0:
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(1) + m.group(2)

            return [sizeType, standardSize]
        return
    
    
    def getReMap(self):
    
        return[
               #XX-Large
               '^[Petite]*\s*([xX]*)\s*-([lLsS])[mMaA][A-Za-z]+$',
               #Petite 10
               '^Petite\s*([\dMLS]+)[A-Za-z]*$',
               #US 4/UK 8
               '^(US)\s*([\d\.]+)[A-Za-z]*\s*\/UK\s*[\d\.A-Za-z]+$',
               #3M
               '^([\d\.]+)[MTW]$',
               #3 (S)
               '^[\d\.]+\s*\(([XLSM]+)\)$',
               #EU 36/US Small
               '^[EU|UK]+\s*[\d\.A-Za-z]+\/US\s*([xX]*)\s*-*([LSM\d\.]+)[mae]*[A-Za-z]*$',
               ]
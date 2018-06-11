import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Diapers (BaseStrategy):

    def transform(self, size, reg, site, key):
        p = re.compile(reg)
        m = p.match(size)
        if m:
            if key == 0:
                sizeType = self.SIZE_TYPE_US;
                standardSize = 'One Size'
                return
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
                standardSize = m.group(1) + '-' + m.group(2)
            if key == 5:
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(1) + m.group(2)
            if key == 6:
                sizeType =self.SIZE_TYPE_US
                if re.findall('years', standardSize):
                    standardSize = standardSize.replace('years', 'Years')
                if re.findall('months', standardSize):
                    standardSize = standardSize.replace('months', 'Months')
            if key == 7:
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(1) + ' Years'
            if key == 8:
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(1) + ' Months'
            if key == 9:
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(1) + m.group(2) + m.group(3)
#             if key == 10 or key == 11:
#                 sizeType = self.SIZE_TYPE_US
#                 standardSize = m.group(1) + m.group(2) + m.group(3) + m.group(4)
            if key == 12:
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(2) +' Months'
            if key == 13:
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(2) +' Years'
            p2 = re.compile('X-L')
            m2 = p2.match(standardSize)
            if m2:
                re.sub('X-L', 'XL', standardSize)
            
            return [sizeType, standardSize]
        else:
            return
    
    
    def getReMap(self):
        
        return [
                #nosize/onesize
                '^\s*(OSZ|onesize|ONESIZE|one size|One Size|no size|No Size)\s*$',
                #6W
                '^\s*([\d\.\-]+)\s*[WTY]+\s*$',
                #4Y-8Y
                '^\s*([\d\.]+)[YT]+\s*\-\s*([\d\.]+)[YT]+\s*$',
                #small
                '^\s*(S|M|L|P)[malediuargreemie]+$',
                #4 Infant
                '^\s*([\d\.]+)\s*[InfatTodler]+\s*$',
                #X-Large
                '^\s*(X+)\s*-\s*(L|S)[argeml]+\s*$',
                #XL(4-6 years)
                '^\s*[XLMSargedium]+\s*\(([\d\.\syearmonths\-]+)\)\s*$',
                #Toddler(2-4 Yrs)
                '^\s*[InfatTodler]+\s*\(([\d\.\-]+)\s*Yrs\s*\)\s*$',
                #Newborn(0-6 Mo)
                '^[NwboInfatTodler]+\(([\d\.\-]+)\s*Mo\s*\)$',
                #Small/Medium --9
                '^\s*(S|M|L|X\-L)[argemlediu]+\s*(\/)\s*(S|M|L|X\-L)[argemlediu]+\s*$',
#                 #X-Large/Medium
#                 '^\s*(X+)\-(L)[arge]+\s*(\/)\s*(S|M|L)[argemlediu]+\s*$',
#                 #Small/X-Large
#                 '^\s*(S|M|L)[argemlediu]+\s*(\/)\s*(X+)\-(L)[arge]+\s*$',
                #24 EU/8 US
                '^\s*[\d\.]+\s*[EU]+\s*\/\s*([\d\.]+)\s*US\s*$',
                #16R
                '^\s*([\d\.\-]+)\s*[RT]+\s*$',
                #Medium (6-12 M)
                '^\s*(S|M|L|X\-L)[argemlediu]+\s*\(([\d\.\-]+)\s*[Months]+\)\s*$',
                '^\s*(S|M|L|X\-L)[argemlediu]+\s*\(([\d\.\-]+)\s*[Years]+\)\s*$',
#                 #Small (3-6 Months)
#                 '^\s*(S|M|L|X\-L)[argemlediu]+\s*\(([\d\.\-]+)\s*Months\)\s*$',
                #4 US/20 EU
                '^\s*([\d\.]+)\s*US\/[\d\.]+\s*EU\s*$',
                #4 M Inf
                '^\s*([\d\.]+)\s*M\s*[InfTod]+\s*$',
                
                ] 
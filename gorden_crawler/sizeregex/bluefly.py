import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Bluefly (BaseStrategy):

    def transform(self, size, reg, site, key):
        p = re.compile(reg)
        m = p.match(size)
        if m:
            if (len(m.groups()) < 2):
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(1)
            else:
                if (key == 0 or key == 8):
                    sizeType = m.group(3)
                else:
                    sizeType = m.group(1)
                if(sizeType == 'US' or 'us'):
                    sizeType = self.SIZE_TYPE_US
                elif(sizeType == 'EU' or 'EUR' or 'eur' or 'eu'):
                    sizeType = self.SIZE_TYPE_EU
                standardSize = m.group(2).strip()
                
            if key == 5:
                sizeType = self.SIZE_TYPE_US
                standardSize = m.group(1) + m.group(2)
            
            if key == 10:
                standardSize = ''
                if int(m.group(1)) > 10:
                    return
                for i in range(int(m.group(1))):
                    standardSize += 'X'
                standardSize += 'L'
            
            if key == 14:
                sizeType = self.SIZE_TYPE_UK
                standardSize = m.group(2)
            
            if key == 16:
                sizeType = self.SIZE_TYPE_US
                if (len(m.groups()) > 3):
                    standardSize = m.group(1) + m.group(2) + m.group(3) + m.group(4)
                else:
                    standardSize = m.group(1) + m.group(2) + m.group(3)   		
            
            if key == 17:
                sizeType = self.SIZE_TYPE_US;
                standardSize = m.group(1) + m.group(2) + m.group(3)
            
#             if key == 22:
#                 sizeType = self.SIZE_TYPE_US;
#                 standardSize = 'One Size'
#                 return [sizeType, standardSize]
            
            standardSize = standardSize.upper()
            return [sizeType, standardSize]
        else:
            return

    def getReMap(self):
    
        return [
        	#0 #85 eu - 30 us
        	'^[\d\.A-Za-z]+\s*(eu|EU|eur|EUR)\s*-\s*([\d\.A-Za-z]+)\s*(us|US)\s*$',
			#1 #US 32W (EUR 48)
        	'^(US|us)\s*([\d\.]+)[A-Za-z]*\s*\((EUR|eur|ITA|ita|FR|fr)\s*[A-Za-z\d\.]+\)$',
        	#2 #medium
        	'^([mM])[eE][A-Za-z]+$',
        	#3 #US 11.5 (EUR 44.5 - UK 10.5)
        	'^(US|us)\s*([\d\.A-Za-z]+)\s+\((EUR|eur)\s*[A-Za-z\d\.]+\s*-\s*(UK|uk)\s*[A-Za-z\d\.]+\)$',
        	#4 #US 8 (37.5G)
        	'^(US|us)\s*([\d\.A-Za-z]+)\s*\([A-Za-z\d\.]+\)$',
        	#5 #x-large
        	'^[Ee]*\d*([xX]*)[A-Za-z]*\s*[-\s]*([lLsS])[mMaA][A-Za-z]+$',
        	#6 #8EEE
        	'^([\d\.]+)\s*[eE]+$',
        	#7 #xs (4-6)
        	'^[\d\.A-Za-z]+\s*\((\s*[\d\.]+[-\d\.\/]*)\)$',
        	#8 #38 eu (7 us)
        	'^[\d\.A-Za-z]+\s*(eu|EU)\s*\(([\d\.]+)\s*(us|US)\)$',
        	#9 #US M (EUR 50)
        	'^(US|us)\s*([A-Za-z]*)\s*\((EUR|eur)\s*[A-Za-z\d\.]+\)$',
        	#10 #2xl
        	'^(\d+)[xX]+[lL]+$',
        	#11 #6.5 (XS)
        	'^([\d\.]+)\s*\([a-zA-Z]+\)$',
        	#12 #4-xlarge
        	'^\d+\s*-\s*(xl|xs|s|m|l)[a-zA-Z]*$',
        	#13 #36.5 / 6
        	'^[\d\.]*\s+\/\s+([\d\.]+)$',
        	#14 #uk 10
        	'^(UK|uk)\s*(\d+)$',
        	#15 #l
        	'^([XxLlSsMm\/]+)$',
        	#16 #large/extra large
        	'^([sSlLmM])[mMaAeE]*[A-Za-z]*\s*(\/)\s*[Ee]*\d*([xX]*)[A-Za-z]*\s*[-\s]*([lLsSmM])[mMaAeE][A-Za-z]+$',
        	#17 #1-xsmall/ small
        	'^\d+\s*-\s*(xl|xs|s|m|l)[a-zA-Z]*\s*(\/)\s*(xl|xs|s|m|l)[a-zA-Z]*$',
            #18 #uk8/us9 (eur 42)
            '^uk\s*[\d\.]+\/us\s*([\d\.])+\s*\(eur\s*[\d\.]+\)$',
            #19 #17 (eur-43)
            '^([\d\.]+)\s*[a-zA-Z]*\s*\([eurEURITA]+-*\s*[\d\.]+[a-zA-Z]*\)$',
            #20 #US 6 (UK 8)
            '^[us|US]+\s*([\d\.]+)\s*\([uk|UK]+\s*[\d\.]+\)$',
            #21 #eur 42 - us 9
            '^[eur|EUR]+\s*[\d\.]+\s*-\s*[us|US]+\s*([\d\.]+)$',
            #nosize/onesize
#             '^\s*(onesize|ONESIZE|one size|One Size|no size|No Size)\s*$',
            #42 Regular
            '^\s*([\d\.]+)\s*Regular\s*$',
            #4T
            '^\s*([\d\.\/]+)\s*[Tmt]{1}\s*$',
        ]

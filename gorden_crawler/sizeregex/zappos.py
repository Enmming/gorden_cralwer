import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Zappos (BaseStrategy):

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
        
#             if key == 0:
#                 sizeType = self.SIZE_TYPE_US
#                 standardSize = 'One Size'
#                 return
            
            if key == 0:
                sizeType = self.SIZE_TYPE_US
                standardSize = int(m.group(1))*'X' + m.group(2)
                return [sizeType, standardSize]
            
            p2 = re.compile('/^(\d)T\/(\d)T$/')
            m2 = p2.match(standardSize)
            if m2:
                standardSize = m2.group(1) + '/' + m2.group(2)
                
            p3 = re.compile('^(\d+)X(L|S)\s*$')
            m3 = p3.match(standardSize)
            if m3:
                standardSize = int(m3.group(1))*'X' + m3.group(2)
            
            p4 = re.compile('/^(\d+)T$/')
            m4 = p4.match(standardSize)
            if m4:
                standardSize = m4.group(1)
                
            if standardSize in ['SM','LG','MD']:
                standardSize = str(standardSize)[0]
            
            return [sizeType, standardSize]
        else:
            return

    
    def getReMap(self):
        return [
            #nosize/onesize
#             '^\s*(onesize|ONESIZE|one size|One Size|no size|No Size)\s*$',
            #2XL
            '^(\d+)X(L|S)\s*$',
            
            #XL (US 16)
            '^[A-Za-z]+\s+\((US)\s*([\d\.]+\s*-\s*[\d\.]+\s*)\)$',
            '^[A-Za-z]+\s+\((US)\s*([\d\.]+)[\"]*\s*\)$',

            #MD (Women's 6)
            #MD (Women's 6-10)
            '^[\d\.A-Za-z]+\s*\(Women\'s ([\d\.]+)\s*\)$',
            '^[\d\.A-Za-z]+\s*\(Women\'s ([\d\.]+\s*-\s*[\d\.]+)\s*\)$',

            '^[\d\.A-Za-z]+\s*\(Men\'s ([\d\.]+)\s*\)$',
            '^[\d\.A-Za-z]+\s*\(Men\'s ([\d\.]+\s*-\s*[\d\.]+)\s*\)$',

            #36 (US Women's 6)
            '^[\d\.A-Za-z]+\s*\((US) Women\'s ([\d\.]+)\s*\)$',
            #36 (US Women's 6-9)
            '^[\d\.A-Za-z]+\s*\((US) Women\'s ([\d\.]+\s*-\s*[\d\.]+)\s*\)$',

            '^[\d\.A-Za-z]+\s*\((US) Men\'s ([\d\.]+)\s*\)$',
            '^[\d\.A-Za-z]+\s*\((US) Men\'s ([\d\.]+\s*-\s*[\d\.]+)\s*\)$',

            #1 Little Kid
            '^([\d\.A-Za-z]+)\s+[^US(\-]*Kid$',
            '^([\d\.A-Za-z]+)\s+[^US(\-]*Kids$',
            '^([\d\.A-Za-z]+)\s+[^US(\-]*Toddler$',

            #10 (Big Kid)
            '^([\d\.\/]+[A-Za-z]*)\s*\(\D[^US(\-]*Kid\)$',
            '^([\d\.\/]+[A-Za-z]*)\s*\(\D[^US(\-]*Kids\)$',
            '^([\d\.\/]+[A-Za-z]*)\s*\(\D[^US(\-]*Toddler\)$',

            #MD (8-10)
            '^[A-Za-z\d]+\s*\(([\d\.]+\s*-\s*[\d\.]+)\)$',
			
        	#23 (10S Big Kids)
        	'^[\d\.\/]+\s*\((\d+)[a-zA-Z\s]*Kids\)$',
        		
            #MD (10-12 Big Kids)
            #MD (10/12 Big Kids)
            #2XS (5 Little Kids)
            '^[A-Za-z\d]+\s*\(([\d\.A-Za-z]+\s*-\s*[\d\.]+)\s*[^US(\-]*Kid\)$',
            '^[A-Za-z\d]+\s*\(([\d\.A-Za-z]+\s*-\s*[\d\.]+)\s*[^US(\-]*Kids\)$',
            '^[A-Za-z\d]+\s*\(([\d\.]+\s*-\s*[\d\.]+)\s*[^US(\-]*Toddler\)$',
            '^[A-Za-z\d]+\s*\(([\d\.]+\s*\/\s*[\d\.]+)\s*[^US(\-]*Kid\)$',
            '^[A-Za-z\d]+\s*\(([\d\.]+\s*\/\s*[\d\.]+)\s*[^US(\-]*Kids\)$',
            '^[A-Za-z\d]+\s*\(([\d\.]+\s*\/\s*[\d\.]+)\s*[^US(\-]*Toddler\)$',
            '^[A-Za-z\d]+\s*\(([\d\.]+T\s*\/\s*[\d\.]+T)\s*[^US(\-]*Toddler\)$',
            '^[A-Za-z\d]+\s*\(([\d\.]+)\s*[^US(\-]*Kid\)$',
            '^[A-Za-z\d]+\s*\(([\d\.]+)\s*[^US(\-]*Kids\)$',
            '^[A-Za-z\d]+\s*\(([\d\.]+)\s*[^US(\-]*Toddler\)$',

            #2T Toddler
            '^(\dT)\s*[A-Za-z]+$',
            '^(\dT)\s*\([A-Za-z]+\)$',

            #42(US 6)
            '^[\d\.A-Za-z]+\s*\((US) ([\d\.]+)\)$',
            '^[\d\.A-Za-z]+\s*\((US) ([\d\.]+\s*-\s*[\d\.]+)\)$',

            #30 (US 12 Little Kid)
            '^[\d\.]+\s*\((US) ([\d\.]+) [^US(\-]*Kid\)$',
            '^[\d\.]+\s*\((US) ([\d\.]+) [^US(\-]*Kids\)$',
            '^[\d\.]+\s*\((US) ([\d\.]+) [^US(\-]*Toddler\)$',
            '^[\d\.]+\s*\((US) ([\d\.]+\s*-\s*[\d\.]+) [^US(\-]*Kid\)$',
            '^[\d\.]+\s*\((US) ([\d\.]+\s*-\s*[\d\.]+) [^US(\-]*Kids\)$',
            '^[\d\.]+\s*\((US) ([\d\.]+\s*-\s*[\d\.]+) [^US(\-]*Toddler\)$',

            #Men's 11.5
            '^Men\'s ([\d\.]+)$',
            '^Women\'s ([\d\.]+)$',

            #6P
            '^([\d\.]+)P$',

            #8 (EUR 40)
            '^([\d\.A-Za-z]+) \(EUR [\d\.]+\)$',

            #EU 40 (US Women's 9.5)
            '^EU [\d\.]+ \((US) Women\'s ([\d\.A-Za-z]+)\)$',
            '^EU [\d\.]+ \((US) Men\'s ([\d\.A-Za-z]+)\)$',

            #EU 1 (US SM)
            #AU 1 (US SM)
            '^[A-Z]+ [\d\.]+ \((US) ([\d\.A-Za-z]+)\)$',

            #US 28 (EU 36)
            '^(US) ([\d\.]+) \(EU [\d\.]+\)$',
            '^(US) ([\d\.]+\/[\d\.]+) \(EU [\d\.]+\)$',

            #EU 34 (Size 8)
            '^EU [\d\.]+ \(Size ([\d\.A-Za-z]+)\)$',


            #UK 10 (US Men's 11)
            '^[A-Z]+ [\d\.]+ \((US) Men\'s ([\d\.]+)\)$',
            #UK 10 (US Women's 11)
            '^[A-Z]+ [\d\.]+ \((US) Women\'s ([\d\.]+)\)$',


            #US 2/4 (UK 10)
            '^(US) ([\d\.]+\/[\d\.]+) \(UK [\d\.]+\)',
            '^(US) ([\d\.]+) \(UK [\d\.]+\)',
            '^(US) ([\d\.]+) \(UK [\d\.]+\/[\d\.]+\)',
            '^(US) ([\d\.]+\/[\d\.]+) \(UK [\d\.]+\/[\d\.]+\)',

            #1 Infant
            '^([\d\.]+)\s+Infant$',
            '^([\d\.]+\/[\d\.]+)\s+Infant$',

            #30 (US 12 Infant)
            '^[\d\.]+\s*\((US) ([\d\.]+) Infant\)$',
            '^[\d\.]+\s*\((US) ([\d\.]+\s*-\s*[\d\.]+) Infant\)$',


            #41/42 (US Men's 9)
            '^[\d\.A-Za-z]+\/[\d\.A-Za-z]+\s*\((US) Women\'s ([\d\.]+)\s*\)$',
            '^[\d\.A-Za-z]+\/[\d\.A-Za-z]+\s*\((US) Men\'s ([\d\.]+)\s*\)$',

            #9-10 Toddler
            '^([\d\.]+-[\d\.]+)\s+[^US(\-]*Kid$',
            '^([\d\.]+-[\d\.]+)\s+[^US(\-]*Kids$',
            '^([\d\.]+-[\d\.]+)\s+[^US(\-]*Toddler$',
            '^([\d\.]+-[\d\.]+)\s+[^US(\-]*Infant$',

            #16.5 (LG)
            '^([\d\.]+)\s*\([A-Z]+\)$',
            
            #MD
            '^\s*(M|S|L)[DMG]+\s*$',
            #2X
            '^([\d\.]+)\s*[T]+\s*$',

        ]
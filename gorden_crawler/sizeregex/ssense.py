# -*- coding: utf-8 -*-
import re
from gorden_crawler.sizeregex.basestrategy import BaseStrategy

class Ssense (BaseStrategy):

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
                elif(sizeType == 'IT'):
                    sizeType = self.SIZE_TYPE_IT
                elif(sizeType == 'FR'):
                    sizeType = self.SIZE_TYPE_FR
                elif(sizeType == 'DK'):
                    sizeType = self.SIZE_TYPE_Dk
                standardSize = m.group(2).strip()
                
            return [sizeType, standardSize]
        else:
            return
    
    
    def getReMap(self):
    
        return[
               #IT44
               '^\s*(IT)\s*([\d\.]+)[\s\—OnlyoneleftTwoitemsleft]*\s*$',
               #S—Onlyoneleft
               '^\s*([SMXL]+)[\s\—OnlyoneleftTwoitemsleft]*$',
               #US44
               '^\s*(US|FR|DK)\s*([\d\.]+)\s*\=?.*$',
               #FR34=XS—Onlyoneleft
               '^\s*(FR|US|IT)\s*([\d\.]+)\s*\=[XSLM]+[\s\—OnlyoneleftTwoitemsleft]*$',
               #IT50=US34
               '^\s*[ITFRUK]+\s*[\d\.]+\=(US)\s*([\d\.]+)\s*$',
               #M=US34
               '^\s*[SMXL\d\.]+\s*\=\s*(US|IT)\s*([\d\.]+)\s*$',
               #2=M
               '^\s*([\d\.]+)\s*\=\s*[SMXL]+\s*$',
               #UK8=IT42
               '^\s*[UKFR]+\s*[\d\.]+\s*\=\s*(IT)\s*([\d\.]+)\s*$',
               #UK10=M
               '^\s*(UK|DK)\s*([\d\.]+)\s*\=\s*[SMXL]+\s*$',
               #US28x32=US28
               '^\s*US\s*[\d\.]+x[\d\.]+\s*\=\s*(US)\s*([\d\.]+)\s*$',
               
               
               ]
# -*- coding: utf-8 -*-
from gorden_crawler.items import BaseItem
from gorden_crawler.spiders.shiji_base import ItemSpider
from gorden_crawler.spiders.joesnewbalanceoutlet import JoesnewbalanceoutletSpider, JoesnewbalanceoutletBaseSpider

class ItemJoesnewbalanceoutletSpider(ItemSpider, JoesnewbalanceoutletBaseSpider):
#class zappoSpider(RedisSpider):
    name = "item_joesnewbalanceoutlet"
    allowed_domains = ["joesnewbalanceoutlet.com"]
    
    '''
    正式运行的时候，start_urls为空，通过redis来喂养爬虫
    '''
    
    start_urls = (
        #'http://couture.zappos.com/kate-spade-new-york-dawn-black-polished-calf-pumice-polished-calf',
        #'http://www.zappos.com/womens~1a',
        #'http://www.zappos.com/allen-allen-3-4-sleeve-v-angled-tunic-black',
        #'http://www.zappos.com/ogio-brooklyn-purse-red',
        #'http://www.zappos.com/ogio-hudson-pack-cobalt-cobalt-academy',
        #'http://www.zappos.com/natori-natori-yogi-convertible-underwire-sports-bra-731050-midnight-silver-dusk',
    )
    
    base_url = 'https://www.joesnewbalanceoutlet.com/'

    '''具体的解析规则'''
    def parse(self, response):
        
        item = BaseItem()
        item['type'] = 'base'
        item['from_site'] = 'joesnewbalanceoutlet'
        item['url'] = response.url
        
        return self.handle_parse_item(response, item)


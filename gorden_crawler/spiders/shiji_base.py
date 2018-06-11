from scrapy.spiders import Spider
from scrapy import signals
from abc import ABCMeta, abstractmethod
from scrapy_redis.spiders import RedisSpider
from scrapy_redis import connection
import os
from urllib import unquote
from scrapy.exceptions import DontCloseSpider, CloseSpider, NotConfigured
import signal
from scrapy import Request
import urllib2
import logging
import re

class GiltActivtiesSpider(Spider):
    
    API_KEY = 'c316e4ec76c564cd35ecb2d2cc52efb3cbab3f2517191d0ef14ed9835479a553'
    __metaclass__ = ABCMeta
        
    callback_url = None    
        
    def __init__(self, json_url=False, callback_url=False, *args, **kwargs):
        
        if json_url==False or len(json_url) == 0:
            raise NotConfigured('json_url error')
        
        logging.error(json_url)
        
        # elif callback_url==False:
        #     raise NotConfigured('callback_url error')
        super(GiltActivtiesSpider, self).__init__(*args, **kwargs)
        
        self.callback_url = callback_url
        
        url = json_url +'?apikey='+ self.API_KEY
        self.start_urls = [url]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        
        crawler.signals.connect(spider.remessage, signal=signals.spider_closed)
        
        spider._set_crawler(crawler)
        return spider

    def remessage(self, spider):
        response = urllib2.urlopen(spider.callback_url)
        logging.warning(response.read())


class GiltItemBaseSpider(Spider):

    API_KEY = 'c316e4ec76c564cd35ecb2d2cc52efb3cbab3f2517191d0ef14ed9835479a553'
    
    @classmethod
    def update_settings(cls, settings):
        
        dict2 = {
            'SCHEDULER': 'scrapy.core.scheduler.Scheduler',
            'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        }
        
        settingsMerged = dict(cls.custom_settings or {}, **dict2)
         
        if 'DOWNLOAD_TIMEOUT' not in settingsMerged.keys():
            settingsMerged['DOWNLOAD_TIMEOUT'] = 6 
         
        settings.setdict(settingsMerged, priority='spider')
    
    def _set_crawler(self, crawler):
        super(GiltItemBaseSpider, self)._set_crawler(crawler)
        
        if os.environ.get('need_redismxin') == 'True':
            self.setup_redis()
    
    def __init__(self, url='', from_site=None, show_product_id=None, *args, **kwargs):
        super(GiltItemBaseSpider, self).__init__(*args, **kwargs)
        
        if url:
            url = unquote(url)
            if re.search(r'\.json', url):
                url = url+'?apikey='+self.API_KEY
            
            self.start_urls = [url]
            os.environ['item_update_notify_redis'] = 'True'
            os.environ['is_single_item'] = 'True'
            if from_site:
                os.environ['single_item_from_site'] = from_site
            if show_product_id:
                os.environ['single_item_show_product_id'] = show_product_id
            
        else:
            ItemSpider.__bases__ +=  (RedisMixin,)
            os.environ['need_dupefilter'] = 'False'
            os.environ['need_redismxin'] = 'True'
            os.environ['item_update_notify_redis'] = 'True'
            self.start_urls = []
            
            signal.signal(signal.SIGINT, self.grace_stop)
            signal.signal(signal.SIGTERM, self.grace_stop)
        
    def grace_stop(self, signum, frame):
        self.dont_stop = False
    

class BaseSpider(RedisSpider):

    __metaclass__ = ABCMeta

    def handle_dimension_to_name(self, response, item, dimensionid_to_name): pass

    @abstractmethod
    def handle_parse_item(self, response, item): pass
        
    def __init__(self, init_start_urls=False, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        if not init_start_urls:
            self.start_urls = []
            os.environ['spider_set_persist'] = 'True'
            os.environ['main_process'] = 'False'
        else:
            os.environ['spider_set_persist'] = 'False'
            os.environ['main_process'] = 'True'
        os.environ['need_size_transform'] = 'True'

class YelpBaseSpider(RedisSpider):

    __metaclass__ = ABCMeta

    @abstractmethod
    def handle_parse_item(self, response, item): pass
        
    def handle_parse_country(self, country): pass
    
    def __init__(self, init_start_urls=False, country=False, *args, **kwargs):
        super(YelpBaseSpider, self).__init__(*args, **kwargs)
        if not init_start_urls:
            self.start_urls = []
            os.environ['spider_set_persist'] = 'True'
        else:
            os.environ['spider_set_persist'] = 'False' 
            
        if country != False:
            self.handle_parse_country(country)
            os.environ['yelp_country'] = country
            
class ItemSpider(Spider):
    
    @classmethod
    def update_settings(cls, settings):
        
        dict2 = {
            'SCHEDULER': 'scrapy.core.scheduler.Scheduler',
            'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        }
        
        settingsMerged =dict(cls.custom_settings or {}, **dict2)
         
        if 'DOWNLOAD_TIMEOUT' not in settingsMerged.keys():
            settingsMerged['DOWNLOAD_TIMEOUT'] = 6 
         
        settings.setdict(settingsMerged, priority='spider')
    
    def _set_crawler(self, crawler):
        super(ItemSpider, self)._set_crawler(crawler)
        
        if os.environ.get('need_redismxin') == 'True':
            self.setup_redis()

    def __init__(self, url='', from_site=None, show_product_id=None, mode=None, *args, **kwargs):
        super(ItemSpider, self).__init__(*args, **kwargs)

        if url:
            url = unquote(url)
            self.start_urls = [url]
            os.environ['item_update_notify_redis'] = 'True'
            os.environ['is_single_item'] = 'True'
            if from_site:
                os.environ['single_item_from_site'] = from_site
            if show_product_id:
                os.environ['single_item_show_product_id'] = show_product_id
            if mode == 'realtime':
                os.environ['single_item_mode'] = mode
                os.environ['single_item_realtime_url'] = url
            elif mode == 'linkhaitao':
                os.environ['linkhaitao_spider'] = 'True'
            elif mode == 'parse_id':
                os.environ['parse_id'] = 'True'
                os.environ['parse_id_url'] = url
            for key in kwargs:
                os.environ[key] = kwargs[key]

        else:
            ItemSpider.__bases__ +=  (RedisMixin,)
            os.environ['need_dupefilter'] = 'False'
            os.environ['need_redismxin'] = 'True'
            os.environ['item_update_notify_redis'] = 'True'
            self.start_urls = []

            signal.signal(signal.SIGINT, self.grace_stop)
            signal.signal(signal.SIGTERM, self.grace_stop)
        
    def grace_stop(self, signum, frame):
        self.dont_stop = False


class RedisMixin(object):
    """Mixin class to implement reading urls from a redis queue."""
    redis_key = None  # use default '<spider>:start_urls'

    dont_stop = True

    def setup_redis(self):
        """Setup redis connection and idle signal.
        This should be called after the spider has set its crawler object.
        """
        if not self.redis_key:
            self.redis_key = '%s:start_urls' % self.name

        self.server = connection.from_settings(self.crawler.settings)
        # idle signal is called when the spider has no requests left,
        # that's when we will schedule new requests from redis queue
        self.crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)
        self.crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)
#         self.crawler.signals.connect(self.engine_stopped, signal=signals.engine_stopped)
#         self.crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)
        
        self.log("Reading URLs from redis list '%s'" % self.redis_key)

    def next_request(self):
        """Returns a request to be scheduled or none."""
        use_set = self.settings.getbool('REDIS_SET')

        if use_set:
            url = self.server.spop(self.redis_key)
        else:
            url = self.server.lpop(self.redis_key)

        if url:
            return self.make_requests_from_url(url)

    def schedule_next_request(self):
        if self.dont_stop:
            """Schedules a request if available"""
            req = self.next_request()
            if req:
                self.crawler.engine.crawl(req, spider=self)

    def spider_idle(self):
        """Schedules a request if available, otherwise waits."""
        self.schedule_next_request()
        if self.dont_stop:
            raise DontCloseSpider


    def item_scraped(self, *args, **kwargs):
        """Avoids waiting for the spider to  idle before scheduling the next request"""
        if self.dont_stop:
            self.schedule_next_request()

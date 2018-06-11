# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import os

from os.path import join, dirname
from dotenv import load_dotenv
from redis.sentinel import Sentinel

dotenv_path = join(dirname(__file__), '.projectenv')

if os.path.isfile(dotenv_path):
    load_dotenv(dotenv_path)
else:
    dotenv_path = join('/data/scrapyd/', '.projectenv')
    if os.path.isfile(dotenv_path):
        load_dotenv(dotenv_path)

PDB_TRACE = False

# sentry dsnaaa
SENTRY_ENABLE = os.environ.get("SENTRY_ENABLE", '0')
SENTRY_DSN = 'http://7c9fa825b1284f04a467fcbf7faf1c59:0a69247ec66b4f71ab2fc8fb5ef539ac@sentry-log.yiyatech.com/3'

SPECIAL_SPIDER_LIST = ['linkhaitao', 'json_spider', 'shangshangsp', 'amazon_usa_uk']

SIZE_TRANSFORM_LIST = ['allsole', 'forzieri', 'oshkosh', 'levi', 'saksoff5th', 'sevenforallmankind', 'eastdane',
                       'carters',
                       'shopbop', 'asos', 'rebeccaminkoff', 'sixpm', 'zappos', 'saksfifthavenue', 'thecorner',
                       'sierratradingpost', 'ralphlauren',
                       'katespade', 'bluefly', 'diapers', 'lordandtaylor', 'joesnewbalanceoutlet', 'ssense']

'''
SIZE_TRANSFORM_TEST:
    None: production env
    0: 不处理尺码
    1: 批量爬虫批量更新Mongodb
    2: 单个爬虫批量测试不更新Mongodb
    3: 单个爬虫仅更新Mongodb当前商品尺码
    4: 单个爬虫批量更新Mongodb
'''
SIZE_TRANSFORM_TEST = ''

# DOWNLOAD_HANDLERS = {'s3': None,}
# Scrapy settings for gorden_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# DOWNLOADER_CLIENTCONTEXTFACTORY = 'gorden_crawler.downloader.contextfactory.CustomContextFactory'

BOT_NAME = 'gorden_crawler'

SPIDER_MODULES = ['gorden_crawler.spiders']
NEWSPIDER_MODULE = 'gorden_crawler.spiders'

# LOG_LEVEL = logging.WARNING
# LOG_FILE = os.environ.get("LOG_FILE", 'scrapy.log')
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'gorden_crawler123 (+http://www.yourdomain.com)'
USER_AGENT = ''

REACTOR_THREADPOOL_MAXSIZE = 40

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 128

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY=1
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 128
CONCURRENT_REQUESTS_PER_IP = 0

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

RETRY_TIMES = 5
DOWNLOAD_TIMEOUT = 10

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED=False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'gorden_crawler.middlewares.MyCustomSpiderMiddleware': 543,
# }

# DOWNLOAD_HANDLERS_BASE = {
#     'http': 'gorden_crawler.downloader.handler.PhantomJSDownloadHandler',
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'gorden_crawler.middlewares.MyCustomDownloaderMiddleware': 543,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'gorden_crawler.contrib.downloadmiddleware.rotate_useragent.RotateUserAgentMiddleware': 1,
    'gorden_crawler.contrib.downloadmiddleware.retry.RetryMiddleware': 500,
    # 'gorden_crawler.middlewares.proxy_ats.ProxyMiddleware': 100,
    # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
    #    'scrapy.telnet.TelnetConsole': None,
    'gorden_crawler.extensions.signals.Signals': 10,
    'gorden_crawler.scrapy_sentry.extensions.Errors': 11,
}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'gorden_crawler.pipelines.SomePipeline': 300,
    # 'gorden_crawler.pipelines.write_json.JsonWriterPipeline': 300
    # 'scrapy_redis.pipelines.RedisPipeline': 300
    # 'gorden_crawler.pipelines.cover_image.WoaiduCoverImage': 300,
    # 'gorden_crawler.pipelines.mongodb_book_file.MongodbWoaiduBookFile' : 301,
    # 'gorden_crawler.pipelines.drop_none_download.DropNoneBookFile' : 302,
    # 'scrapy_redis.pipelines.RedisPipeline': 300,
    'gorden_crawler.pipelines.mongodb.SingleMongodbPipeline': 303,  # mongodb入库处理器
    # 'gorden_crawler.pipelines.final_test.FinalTestPipeline' :  304,
    'gorden_crawler.pipelines.realtime_handle_image.RealtimeHandleImage': None,  # 实时爬虫图片处理队列
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
# AUTOTHROTTLE_ENABLED=True
# The initial download delay
# AUTOTHROTTLE_START_DELAY=3
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED=True
# HTTPCACHE_EXPIRATION_SECS=0
# HTTPCACHE_DIR='httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES=[]
# HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'

# Enables scheduling storing requests queue in redis.
SCHEDULER = "gorden_crawler.redis.scheduler.Scheduler"

# Don't cleanup redis queues, allows to pause/resume crawls.
# SCHEDULER_PERSIST = True

# Schedule requests using a priority queue. (default)
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'

# Schedule requests using a queue (FIFO).<F2>
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderQueue'

# Schedule requests using a stack (LIFO).
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderStack'

# Max idle time to prevent the spider from being closed when distributed crawling.
# This only works if queue class is SpiderQueue or SpiderStack,
# and may also block the same time when your spider start at the first time (because the queue is empty).
# SCHEDULER_IDLE_BEFORE_CLOSE = 10

# # Store scraped item in redis for post-processing.
# ITEM_PIPELINES = {
#     'scrapy_redis.pipelines.RedisPipeline': 300
# }

# Specify the host and port to use when connecting to Redis (optional).
REDIS_HOST = os.environ.get("REDIS_HOST", 'localhost')
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)

# Specify the full Redis URL for connecting (optional).
# If set, this takes precedence over the REDIS_HOST and REDIS_PORT settings.
REDIS_URL = os.environ.get("REDIS_URL", 'redis://localhost:6379')

MONGODB_SERVER = os.environ.get("MONGODB_SERVER", 'mongodb://yiya:yiya1504!!@localhost:27017/admin')
MONGODB_DB = os.environ.get("MONGODB_DB", 'shiji_crawler_items')

SHOP_MONGODB_SERVER = os.environ.get("SHOP_MONGODB_SERVER", 'mongodb://yiya:yiya1504!!@localhost:27017/admin')
SHOP_MONGODB_DB = os.environ.get("SHOP_MONGODB_DB", 'shiji_shop')

# redis config use sentinel
REDIS1_SENTINEL = os.environ.get("REDIS_SENTINEL", None)
if REDIS1_SENTINEL:
    sentinel = Sentinel([(REDIS1_SENTINEL, 26379)], socket_timeout=0.1)
    CRAWLER_REDIS_HOST = sentinel.discover_master('mymaster')[0]
else:
    CRAWLER_REDIS_HOST = None

ITEM_NOTIFY_REDIS_HOST = CRAWLER_REDIS_HOST or os.environ.get("ITEM_NOTIFY_REDIS_HOST", 'localhost')
ITEM_NOTIFY_REDIS_PORT = os.environ.get("ITEM_NOTIFY_REDIS_PORT", 6379)
ITEM_NOTIFY_REDIS_PASSWORD = os.environ.get("ITEM_NOTIFY_REDIS_PASSWORD", None)

IMGAE_HANDLE_QUEUE_REDIS_HOST = CRAWLER_REDIS_HOST or os.environ.get("IMGAE_HANDLE_QUEUE_REDIS_HOST", 'localhost')
IMGAE_HANDLE_QUEUE_REDIS_PORT = os.environ.get("IMGAE_HANDLE_QUEUE_REDIS_PORT", 6379)
IMGAE_HANDLE_QUEUE_REDIS_PASSWORD = os.environ.get("IMGAE_HANDLE_QUEUE_REDIS_PASSWORD", None)

SIZE_TRANSFORM_QUEUE_REDIS_HOST = CRAWLER_REDIS_HOST or os.environ.get("SIZE_TRANSFORM_QUEUE_REDIS_HOST", 'localhost')
SIZE_TRANSFORM_QUEUE_REDIS_PORT = os.environ.get("SIZE_TRANSFORM_QUEUE_REDIS_PORT", 6379)
SIZE_TRANSFORM_QUEUE_REDIS_PASSWORD = os.environ.get("SIZE_TRANSFORM_QUEUE_REDIS_PASSWORD", None)

REALTIME_IMAGE_HANDLE_QUEUE_REDIS_HOST = CRAWLER_REDIS_HOST or os.environ.get("REALTIME_IMAGE_HANDLE_QUEUE_REDIS_HOST", 'localhost')
REALTIME_IMAGE_HANDLE_QUEUE_REDIS_PORT = os.environ.get("REALTIME_IMAGE_HANDLE_QUEUE_REDIS_PORT", 6379)
REALTIME_IMAGE_HANDLE_QUEUE_REDIS_PASSWORD = os.environ.get("REALTIME_IMAGE_HANDLE_QUEUE_REDIS_PASSWORD", None)

JS_CRAWLER_QUEUE_HOST = CRAWLER_REDIS_HOST or os.environ.get("JS_CRAWLER_QUEUE_HOST", 'localhost')
JS_CRAWLER_QUEUE_PORT = os.environ.get("JS_CRAWLER_QUEUE_PORT", 6379)
JS_CRAWLER_QUEUE_PASSWORD = os.environ.get("JS_CRAWLER_QUEUE_PASSWORD", None)


# yelp configuration
YELP_MONGODB_SERVER = os.environ.get("YELP_MONGODB_SERVER", 'mongodb://localhost:27017/admin')

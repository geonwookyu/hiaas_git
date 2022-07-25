# Scrapy settings for mmg project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
BOT_NAME = 'mi'

SPIDER_MODULES = ['mi.spiders']
NEWSPIDER_MODULE = 'mi.spiders'


# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# The encoding to be used for the feed.
FEED_EXPORT_ENCODING = 'utf-8'


# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2


# Disable cookies (enabled by default)
COOKIES_ENABLED = False


# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False


# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8,ja;q=0.7',
  'referer': 'https://www.google.com'
}


# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
   'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
}
RANDOM_UA_SAME_OS_FAMILY = True
RANDOM_UA_TYPE = 'tablet.chrome'



# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'mi.pipelines.HttpPostPipeline': 800
}

# Url to your server, which accepts POST requests
HTTP_POST_PIPELINE_URL = 'http://localhost'


# If you want to send more items at once (and have less HTTP POST requests incoming.)
# If True items will be send as [{key1:val1},{key1:val1}] instead of {key1:val1}
HTTP_POST_PIPELINE_BUFFERED = True
HTTP_POST_PIPELINE_BUFFER_SIZE = 100

IMAGES_STORE = './images'
if not os.path.isdir(IMAGES_STORE):
        os.mkdir(IMAGES_STORE)


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False


# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 1800
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# log config
LOG_LEVEL = 'DEBUG'
# LOG_FORMAT = '%(levelname)s :: %(asctime)s :: %(module)s ::%(name)s\n%(message)s'
# LOG_FILE = 'log.txt'


# Collection configuration settings
KEYWORD_LIST = []
LIMIT_PAGING_COUNT = 1



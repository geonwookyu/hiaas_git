# Scrapy settings for mi project
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


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
FEED_EXPORT_ENCODING = 'utf-8'

# Collection configuration settings
KEYWORD_LIST = ['매트리스']
LIMIT_PAGING_COUNT = 10

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'ko',
  'referer': 'https://www.google.com'
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'gymcoding_scrapy.middlewares.GymcodingScrapySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'gymcoding_scrapy.middlewares.GymcodingScrapyDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'mi.pipelines.HttpPostPipeline': 800
}

# Url to your server, which accepts POST requests
# HTTP_POST_PIPELINE_URL = 'http://localhost'
HTTP_POST_PIPELINE_URL = 'http://106.252.227.100:8082'

# Any custom headers you want to add, e.g. authentication
HTTP_POST_PIPELINE_HEADERS = {
    'Content-Type': 'text/plain; charset=UTF-8'
}

# If you want to send more items at once (and have less HTTP POST requests incoming.)
# If True items will be send as [{key1:val1},{key1:val1}] instead of {key1:val1}
HTTP_POST_PIPELINE_BUFFERED = False
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







# --------------------------------------COUPANG CONFIG-----------------------------------------
COUPANG_PAGE_COUNT = 3
COUPANG_CRAWL_DELAY = 2.0
COUPANG_KEYWORD = '매트리스'
COUPANG_SORTER = 'scoreDesc'
COUPANG_LISTSIZE = '72'









#----------------------------------------------------------------------------------------------
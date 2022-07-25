from .base import *

# Url to your server, which accepts POST requests
HTTP_POST_PIPELINE_URL = 'http://localhost'

# log config
LOG_LEVEL = 'DEBUG'
# LOG_FORMAT = '%(levelname)s :: %(asctime)s :: %(module)s ::%(name)s\n%(message)s'
# LOG_FILE = 'log.txt'


# Collection configuration settings
KEYWORD_LIST = []
LIMIT_PAGING_COUNT = 1


# --------------------------------------COUPANG CONFIG-----------------------------------------
COUPANG_PAGE_COUNT = 3
COUPANG_CRAWL_DELAY = 2.0
COUPANG_SORTER = 'scoreDesc'
COUPANG_LISTSIZE = '72'



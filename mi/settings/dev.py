from .base import *

# Url to your server, which accepts POST requests
HTTP_POST_PIPELINE_URL = 'http://106.252.227.100:8082'

# log config
LOG_LEVEL = 'ERROR'
# LOG_FORMAT = '%(levelname)s :: %(asctime)s :: %(module)s ::%(name)s\n%(message)s'
# LOG_FILE = 'log.txt'


# Collection configuration settings
KEYWORD_LIST = ["매트리스", "토퍼"]
LIMIT_PAGING_COUNT = 14



# --------------------------------------COUPANG CONFIG-----------------------------------------
COUPANG_PAGE_COUNT = 14
COUPANG_CRAWL_DELAY = 2.0
COUPANG_SORTER = 'scoreDesc'
COUPANG_LISTSIZE = '72'
COUPANG_LINKFILE_PATH = '/tmp/coupang_link.json'

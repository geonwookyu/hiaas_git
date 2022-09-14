from .base import *

# Url to your server, which accepts POST requests
HTTP_POST_PIPELINE_URL = 'http://mi-log-nginx'

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


# --------------------------------------Naver CONFIG-----------------------------------------
NAVER_PAGE_COUNT = 14
NAVER_CRAWL_DELAY = 2.0
NAVER_SORTER = 'rel'
NAVER_LISTSIZE = '80'
NAVER_VIEW_TYPE = 'list'


# --------------------------------------INTERPARK CONFIG-----------------------------------------
INTERPARK_KEYWORD_LIST = ["우머나이저"]
INTERPARK_PAGE_COUNT = 14
INTERPARK_CRAWL_DELAY = 2.0
INTERPARK_SORTER = 'pop-rank'
INTERPARK_LISTSIZE = '52'

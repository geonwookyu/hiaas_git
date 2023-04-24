from .base import *

# Url to your server, which accepts POST requests
HTTP_POST_PIPELINE_URL = 'http://mi-log-nginx'

# log config
LOG_LEVEL = 'ERROR'
# LOG_FORMAT = '%(levelname)s :: %(asctime)s :: %(module)s ::%(name)s\n%(message)s'
# LOG_FILE = 'log.txt'


# Collection configuration settings
KEYWORD_LIST = ["네이쳐스탑", "우머나이저", "퓨어젤", "아크웨이브", "롬프", "위바이브", "노트북", "건강식품"]
LIMIT_PAGING_COUNT = 14



# --------------------------------------COUPANG CONFIG-----------------------------------------
COUPANG_PAGE_COUNT = 14
COUPANG_CRAWL_DELAY = 2.0
COUPANG_SORTER = 'scoreDesc'
COUPANG_LISTSIZE = '72'
COUPANG_LINKFILE_PATH = 'CoupangAutoLoginCookie.json'

GREENSHELF1_KEYWORD = ["우머나이저"]
GREENSHELF1_PRICE_RANGE = ["20000", "100001", "200001", "300001"]
GREENSHELF1_MIN_PRICE = ["20000", "100001", "200001", "300001"]
GREENSHELF1_MAX_PRICE = ["100000", "200000", "300000", "400000"]

GREENSHELF2_KEYWORD = ["퓨어젤"]
GREENSHELF2_PRICE_RANGE = ["10000", "20001", "30001", "40001"]
GREENSHELF2_MIN_PRICE = ["10000", "20001", "30001", "40001"]
GREENSHELF2_MAX_PRICE = ["20000", "30000", "40000", "50000"]

GREENSHELF3_KEYWORD = ["아크웨이브"]
GREENSHELF3_PRICE_RANGE = ["50000", "100001", "200001"]
GREENSHELF3_MIN_PRICE = ["50000", "100001", "200001"]
GREENSHELF3_MAX_PRICE = ["100000", "200000", "300000"]

GREENSHELF4_KEYWORD = ["롬프"]
GREENSHELF4_PRICE_RANGE = ["10000", "30001", "50001", "70001"]
GREENSHELF4_MIN_PRICE = ["10000", "30001", "50001", "70001"]
GREENSHELF4_MAX_PRICE = ["30000", "50000", "70000", "100000"]

GREENSHELF5_KEYWORD = ["위바이브"]
GREENSHELF5_PRICE_RANGE = ["10000", "50001", "100001", "200001"]
GREENSHELF5_MIN_PRICE = ["10000", "50001", "100001", "200001"]
GREENSHELF5_MAX_PRICE = ["50000", "100000", "200000", "300000"]

COUPANG_GENERAL_KEYWORD = ["네이쳐스탑", "노트북"]


# --------------------------------------Naver CONFIG-----------------------------------------
NAVER_PAGE_COUNT = 6
NAVER_CRAWL_DELAY = 2.0
NAVER_SORTER = 'rel'
NAVER_LISTSIZE = '80'
NAVER_VIEW_TYPE = 'list'


# --------------------------------------INTERPARK CONFIG-----------------------------------------
INTERPARK_KEYWORD_LIST = ["우머나이저", "퓨어젤", "아크웨이브", "롬프", "위바이브", "네이쳐스탑", "노트북"]
INTERPARK_PAGE_COUNT = 30
INTERPARK_CRAWL_DELAY = 2.0
INTERPARK_SORTER = 'pop-rank'
INTERPARK_LISTSIZE = '52'
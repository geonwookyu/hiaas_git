import imp
from time import sleep
import scrapy
import requests
import json
import logging
import logging.config
from mi.items import HiLabMIItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from datetime import datetime
from mi.spiders.hiaas_common import HiaasCommon
from mi.spiders.logger import loggerConfig
from scrapy.utils.project import get_project_settings

# logging.config.dictConfig(loggerConfig)
logger = logging.getLogger("naver")

class Naverspider(HiaasCommon):
    name = "naver_keyword"                
    param = {
        'pagingIndex':'1',
        'pagingSize':'80',
        'productSet':'total',
        'sort':'rel',
        'viewType':'list'        
    }
    marketType = "naver"

    # @classmethod
    # def from_crawler(cls, crawler):
    #     params = {}
    #     if crawler.settings.get('KEYWORD_LIST') and crawler.settings.get('LIMIT_PAGING_COUNT'):
    #         params['keywordList'] = crawler.settings['KEYWORD_LIST']
    #         params['limitPagingCount'] = crawler.settings['LIMIT_PAGING_COUNT']
    #     ext = cls(**params)
    #     ext.settings = crawler.settings
        
    #     return ext
    

    def start_requests(self): 
        logger.info('[start_requests] start')
        url = 'https://shopping.naver.com/home/p/index.naver'

      
        logger.info('[start_requests] url conn : %s', url)
        yield scrapy.Request(url=url,                                 
                            callback=self.parse_product,
                            errback=self.errback_httpbin)
                                


    #  parse
    def parse_product(self, response):
        logger.info('[parse_product] start') 

        settings = get_project_settings()
        keywordList = settings.get('KEYWORD_LIST')
        limitPagingCount = settings.get('LIMIT_PAGING_COUNT')    

        for keyword in keywordList :            
            logger.info('[parse_product] keyword : %s', keyword)
            response = requests.get(f'https://search.shopping.naver.com/api/search/all/?frm=NVSHATC&origQuery={keyword}&pagingIndex={self.param["pagingIndex"]}&pagingSize={self.param["pagingSize"]}&productSet={self.param["productSet"]}&query={keyword}&sort={self.param["sort"]}&viewType={self.param["viewType"]}')
            jsonFile = json.loads(response.text)

            searchCnt = int(jsonFile['shoppingResult']['total']) # 검색결과 개수            
            logger.info('[parse_product] searchCnt = %d',searchCnt)
            totalPaging = int((searchCnt/int(self.param['pagingSize']))) +1   # 검색결과 총 페이지 개수
            
            # page index limit 설정
            maxPagingCnt = limitPagingCount
            if totalPaging > limitPagingCount:
                maxPagingCnt = limitPagingCount
            else:
                maxPagingCnt = totalPaging

            logger.info('[parse_product] page index limit = %d',maxPagingCnt)

            for pagingidx in range(1, maxPagingCnt + 1):        
                logger.info("[parse_product] pagingidx : %d", pagingidx)            
                response = requests.get(f'https://search.shopping.naver.com/api/search/all/?frm=NVSHATC&origQuery={keyword}&pagingIndex={pagingidx}&pagingSize={self.param["pagingSize"]}&productSet={self.param["productSet"]}&query={keyword}&sort={self.param["sort"]}&viewType={self.param["viewType"]}')
                jsonFile = json.loads(response.text)                

                for product in jsonFile['shoppingResult']['products']:                    
                    logger.info('[parse_product] [keyword : %s] [pagingIdx : %d] [rank : %s] ', keyword, pagingidx, product['rank'])
                    # if "smartstore" in product['mallProductUrl']:
                        # logger.info('[parse_product] [keyword : %s] [pagingIdx : %d] [rank : %d] ', keyword, pagingidx, product['rank'])
                    item = HiLabMIItem()
                    
                    # 마켓 타입
                    item['mid'] = self.marketType

                    #collection type
                    item['ctype'] = 1

                    # 제품 상세페이지 링크
                    # item['detail_link'] = product['mallProductUrl']

                    # 제품 순위
                    if product['rank'] is None:
                        product['rank'] = 0    
                    item['rank'] = product['rank']
                    
                    # 광고 노출 순위
                    # item['ad'] = 

                    # 카테고리1
                    if product['category1Name'] is None:
                        product['category1Name'] = ''                         
                    item['pr1ca'] = product['category1Name']
                    # 카테고리2
                    if product['category2Name'] is None:
                        product['category2Name'] = ''                                              
                    item['pr2ca'] = product['category2Name']
                    # 카테고리3
                    if product['category2Name'] is None:
                        product['category2Name'] = ''                     
                    item['pr3ca'] = product['category3Name']
                    # 카테고리4
                    if product['category4Name'] is None:
                        product['category4Name'] = ''                         
                    item['pr4ca'] = product['category4Name']

                    # 정렬기준
                    item['sb'] = self.param['sort']

                    # 총 제품 수(임의)
                    if product['keepCnt'] is None:
                        product['keepCnt'] = 0
                    item['prco'] = product['keepCnt']

                    # 제품명
                    if product['productName'] is None:
                        product['productName'] = ''
                    item['pr1nm'] = product['productName']

                    # 가격
                    if product['lowPrice'] is None:
                        product['lowPrice'] = 0
                    item['pr1pr'] = product['lowPrice']

                    # 판매자
                    # item['ta'] = product['mallName']

                    # 평점
                    if product['scoreInfo'] is None:                
                        product['scoreInfo'] = 0.0
                    item['gr'] = product['scoreInfo']
                    
                    # 리뷰 개수
                    if product['reviewCount'] is None:
                        product['reviewCount'] = 0
                    item['revco'] = product['reviewCount']

                    # 할인 정보
                    # item['dcinfo'] = ''

                    # 무료배송 유무
                    if product['hasDeliveryFeeContent'] is None:
                        product['hasDeliveryFeeContent'] = 0
                    item['ts'] = bool(product['hasDeliveryFeeContent'])

                    # 도착 예정일자
                    # item['ardate'] = ''

                    # 멤버십 적용유무
                    # item['ms'] = ''

                    # 다른 구매옵션
                    # item['opo'] = ''

                    # 구매횟수(임의)
                    if product['purchaseCnt'] is None:
                        product['purchaseCnt'] = 0
                    item['purchco'] = product['purchaseCnt']

                    # 재고 현황
                    if product['keepCnt'] is None:
                        product['keepCnt'] = 0
                    item['pr1qt'] = product['keepCnt']
                    
                    # 전체 페이지 수
                    item['pgco'] = totalPaging
                    
                    # 검색 키워드(임의)
                    item['sk'] = keyword

                    # 브랜드
                    if product['brand'] is None:
                        product['brand'] = ''
                    item['pr1br'] = product['brand']
                    # item['brlk'] = ''
                    # item['talk'] = product['mallPcUrl']
                    # item['pr1id'] = ''
                    # item['dcrate'] = ''
                    # item['fullpr'] = response.xpath('//del[contains(@class,"Xdhdpm0BD9")]/span[2]/text()').get()                    
                    # item['fullpr'] = ''
                    # item['dcpr'] = response.xpath('//strong[contains(@class, "aICRqgP9zw")]/span[2]/text()').get()
                    # item['dcpr'] = ''
                    # item['soldout'] = ''
                    # item['pr1va'] = ''
                    # item['msbf'] = ''
                    # item['prdetail'] = ''

                    # item['revsum'] = ''
                    # item['revsb'] = ''
                    # item['reviewer'] = ''
                    # item['ingrade'] = ''
                    # item['revdate'] = ''
                    # item['purchdetail'] = ''
                    # item['revdetail'] = ''
                    # item['blogrev'] = ''
                    # item['revviews'] = ''
                    # item['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%L")

                    yield item
                    sleep(0.1)
                sleep(2)
                    


    def errback_httpbin(self, failure):
        # log all failures
        logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            logger.error('TimeoutError on %s', request.url)


    # 네이버 API 정보를 포함하여 parse에 전달
    # 상세페이지 들어가서 데이터 수집시 필요
    # def start_requests(self): 
    #     logger.info('[start_requests] start')

    #     for keyword in KEYWORD_LIST:
    #         logger.info('[start_requests] keyword : %s', keyword)  
    #         response = requests.get(f'https://search.shopping.naver.com/api/search/all/?frm=NVSHATC&origQuery={keyword}&pagingIndex={self.param["pagingIndex"]}&pagingSize={self.param["pagingSize"]}&productSet={self.param["productSet"]}&query={keyword}&sort={self.param["sort"]}&viewType={self.param["viewType"]}')
    #         jsonFile = json.loads(response.text)

    #         searchCnt = int(jsonFile['shoppingResult']['total']) # 검색결과 개수  
    #         logger.info('[start_requests] searchCnt : %d', searchCnt)    
    #         totalPaging = int((searchCnt/int(self.param['pagingSize']))) +1   # 검색결과 총 페이지 개수
    #         print("totalPaging : ", totalPaging )          

    #         # page index limit 설정
    #         if totalPaging > LIMIT_PAGING_COUNT:
    #             maxPagingCnt = LIMIT_PAGING_COUNT
    #         else:
    #             maxPagingCnt = totalPaging

    #         for pagingidx in range(1, maxPagingCnt + 1):   
    #             logger.info("[start_requests] pagingidx : %d", pagingidx)            
    #             urls = []
    #             response = requests.get(f'https://search.shopping.naver.com/api/search/all/?frm=NVSHATC&origQuery={keyword}&pagingIndex={pagingidx}&pagingSize={self.param["pagingSize"]}&productSet={self.param["productSet"]}&query={keyword}&sort={self.param["sort"]}&viewType={self.param["viewType"]}')
    #             jsonFile = json.loads(response.text)                

    #             for product in jsonFile['shoppingResult']['products']:
    #                 listPageData = {
    #                     'mid' : self.marketType,      
    #                     'detail_link' : product['mallProductUrl'],
    #                     'rank' : product['rank'],
    #                     'pr1ca' : product['category1Name'],
    #                     'pr2ca' : product['category2Name'],
    #                     'pr3ca' : product['category3Name'],
    #                     'pr4ca' : product['category4Name'],
    #                     'sb' : self.param['sort'],
    #                     'prco' : product['keepCnt'],
    #                     'pr1nm' : product['productName'],
    #                     'pr1pr' : product['lowPrice'],
    #                     'ta' : product['mallName'],
    #                     'gr' : product['scoreInfo'],
    #                     'revco' : product['reviewCount'],                        
    #                     'ts' : bool(product['hasDeliveryFeeContent']),
    #                     'purchco' : product['purchaseCnt'],
    #                     'pr1qt' : product['keepCnt'],
    #                     'sk' : keyword,
    #                     'pr1br' : product['brand']
    #                 }  
             
    #                 yield scrapy.Request(url=product['crUrl'], 
    #                     headers=self.headers, 
    #                     callback=self.parse,
    #                     cb_kwargs = listPageData,
    #                     errback=self.errback_httpbin
    #                     )


    # def parse(self, response, **kwargs):
    #     product = response.cb_kwargs
    #     item = HiLabMIItem()
    #     item['mid'] = product['mid']
    #     item['detail_link'] = product['detail_link']
    #     item['rank'] = product['rank']
    #     item['pr1ca'] = product['pr1ca']
    #     item['pr2ca'] = product['pr2ca']
    #     item['pr3ca'] = product['pr3ca']
    #     item['pr4ca'] = product['pr4ca']
    #     item['sb'] = product['sb']
    #     item['prco'] = product['prco']
    #     item['pr1nm'] = product['pr1nm']
    #     item['pr1pr'] = product['pr1pr']
    #     item['ta'] = product['ta']
    #     item['gr'] = product['gr']
    #     item['revco'] = product['revco']
    #     # item['dcinfo'] = ''
    #     item['ts'] = product['ts']
    #     # item['ardate'] = ''
    #     # item['ms'] = ''
    #     # item['opo'] = ''
    #     item['purchco'] = product['purchco']
    #     item['pr1qt'] = product['pr1qt']
    #     # item['pgco'] = ''

    #     item['sk'] = product['sk']
    #     item['pr1br'] = product['pr1br']
    #     # item['brlk'] = ''
    #     # item['talk'] = ''
    #     # item['pr1id'] = ''
    #     # item['dcrate'] = ''
    #     item['fullpr'] = response.xpath('//del[contains(@class,"Xdhdpm0BD9")]/span[2]/text()').get()                    
    #     # item['fullpr'] = ''
    #     item['dcpr'] = response.xpath('//strong[contains(@class, "aICRqgP9zw")]/span[2]/text()').get()
    #     # item['dcpr'] = ''
    #     # item['soldout'] = ''
    #     # item['pr1va'] = ''
    #     # item['msbf'] = ''
    #     # item['prdetail'] = ''

    #     # item['revsum'] = ''
    #     # item['revsb'] = ''
    #     # item['reviewer'] = ''
    #     # item['ingrade'] = ''
    #     # item['revdate'] = ''
    #     # item['purchdetail'] = ''
    #     # item['revdetail'] = ''
    #     # item['blogrev'] = ''
    #     # item['revviews'] = ''
    #     # item['time'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%L")

    #     yield item
    #     sleep(0.2)            
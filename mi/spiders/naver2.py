from time import sleep
import scrapy
import requests
import json
from mi.items import HiLabMIItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from datetime import datetime
from mi.settings import KEYWORD_LIST, LIMIT_PAGING_COUNT

class Naverspider2(scrapy.Spider):
    name = "naver2"            
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}        
    param = {
        'pagingIndex':'1',
        'pagingSize':'80',
        'productSet':'total',
        'sort':'rel',
        'viewType':'list'        
    }
    marketType = "naver"
    

    def start_requests(self): 
        self.logger.info('[start_requests] start')
        url = 'https://shopping.naver.com/home/p/index.naver'

      
        self.logger.info('[start_requests] url conn : %s', url)
        yield scrapy.Request(url=url, 
                                headers=self.headers, 
                                callback=self.parse_product,
                                errback=self.errback_httpbin)
                                


    #  parse
    def parse_product(self, response):
        self.logger.info('[parse_product] start')        

        for keyword in KEYWORD_LIST:
            print("[parse_product] keyword : ", keyword)    
            response = requests.get(f'https://search.shopping.naver.com/api/search/all/?frm=NVSHATC&origQuery={keyword}&pagingIndex={self.param["pagingIndex"]}&pagingSize={self.param["pagingSize"]}&productSet={self.param["productSet"]}&query={keyword}&sort={self.param["sort"]}&viewType={self.param["viewType"]}')
            jsonFile = json.loads(response.text)

            searchCnt = int(jsonFile['shoppingResult']['total']) # 검색결과 개수            
            totalPaging = int((searchCnt/int(self.param['pagingSize']))) +1   # 검색결과 총 페이지 개수
            
            # page index limit 설정
            if totalPaging > LIMIT_PAGING_COUNT:
                maxPagingCnt = LIMIT_PAGING_COUNT
            else:
                maxPagingCnt = totalPaging

            for pagingidx in range(1, maxPagingCnt + 1):        
                self.logger.info("[parse_product] pagingidx : %d", pagingidx)            
                response = requests.get(f'https://search.shopping.naver.com/api/search/all/?frm=NVSHATC&origQuery={keyword}&pagingIndex={pagingidx}&pagingSize={self.param["pagingSize"]}&productSet={self.param["productSet"]}&query={keyword}&sort={self.param["sort"]}&viewType={self.param["viewType"]}')
                jsonFile = json.loads(response.text)                

                for product in jsonFile['shoppingResult']['products']:                    
                    # self.logger.info('[start_requests] [keyword : %s] [pagingIdx : %d] [rank : %s] ', keyword, pagingidx, rank)
                    # if "smartstore" in product['mallProductUrl']:
                        # self.logger.info('[start_requests] [keyword : %s] [pagingIdx : %d] [rank : %d] ', keyword, pagingidx, rank)
                    item = HiLabMIItem()
                    item['mid'] = self.marketType
                    item['detail_link'] = product['mallProductUrl']
                    item['rank'] = product['rank']
                    item['pr1ca'] = product['category1Name']
                    item['pr2ca'] = product['category2Name']
                    item['pr3ca'] = product['category3Name']
                    item['pr4ca'] = product['category4Name']
                    item['sb'] = self.param['sort']
                    item['prco'] = product['keepCnt']
                    item['pr1nm'] = product['productName']
                    item['pr1pr'] = product['price']
                    item['ta'] = product['mallName']
                    item['gr'] = product['scoreInfo']
                    item['revco'] = product['reviewCount']
                    # item['dcinfo'] = ''
                    item['ts'] = product['hasDeliveryFeeContent']
                    # item['ardate'] = ''
                    # item['ms'] = ''
                    # item['opo'] = ''
                    item['purchco'] = product['purchaseCnt']
                    item['pr1qt'] = product['keepCnt']
                    # item['pgco'] = ''

                    item['sk'] = keyword
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
                    sleep(0.2)
                    


    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
from time import time
import scrapy
import requests
import json
from mi.items import HiLabMIItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

class Naverspider2(scrapy.Spider):

    name = "naver2"
    fileName = ''
    keywordList = []
    MaxPagingIndex = 1
    # totalProductData = dict()
    # productsInfo = dict()
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}        
    param = {
        'pagingIndex':'1',
        'pagingSize':'80',
        'productSet':'total',
        'sort':'rel',
        'viewType':'list'        
    }

    def __init__(self, fileName=None, *args, **kwargs):
        super(Naverspider2, self).__init__(*args, **kwargs)

        # config data 추출
        try:
            with open(f'C:\Hiaas_sp\mi\mi_v1\mi\spiders\{fileName}', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.keywordList = config['keyword']
                self.MaxPagingIndex = config['maxPagingIndex']
        except Exception as e:
            print('예외가 발생했습니다.', e)

        print("keyword : ", self.keywordList)
        print("MaxPagingIndex : ", self.MaxPagingIndex)


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

        for keyword in self.keywordList:
            print("[parse_product] keyword : ", keyword)

            for pagingidx in range(1, self.MaxPagingIndex +1):
                response = requests.get(f'https://search.shopping.naver.com/api/search/all/?frm=NVSHATC&origQuery={keyword}&pagingIndex={self.param["pagingIndex"]}&pagingSize={self.param["pagingSize"]}&productSet={self.param["productSet"]}&query={keyword}&sort={self.param["sort"]}&viewType={self.param["viewType"]}')
                jsonFile = json.loads(response.text)
                print("[parse_product] pagingidx : " , pagingidx)  

                for product in jsonFile['shoppingResult']['products']:
                    rank = (pagingidx-1)*int(self.param['pagingSize']) + int(product['rank'])                    
                    # self.logger.info('[start_requests] [keyword : %s] [pagingIdx : %d] [rank : %s] ', keyword, pagingidx, rank)
                    if "smartstore" in product['mallProductUrl']:
                        self.logger.info('[start_requests] [keyword : %s] [pagingIdx : %d] [rank : %d] ', keyword, pagingidx, rank)
                        item = HiLabMIItem()
                        item['detail_link'] = product['mallProductUrl']
                        item['rank'] = str(rank)
                        item['pr1ca'] = product['category1Name']
                        # item['pr2ca'] = product['category2Name']
                        # item['pr3ca'] = product['category3Name']
                        item['sb'] = self.param['sort']
                        item['prco'] = product['keepCnt']
                        item['pr1nm'] = product['productName']
                        item['pr1pr'] = product['price']
                        item['ta'] = product['mallName']
                        item['gr'] = product['scoreInfo']
                        item['revco'] = product['reviewCount']
                        item['dcinfo'] = ''
                        item['ts'] = ''
                        item['ardate'] = ''
                        item['ms'] = ''
                        item['opo'] = ''
                        item['purchco'] = product['purchaseCnt']
                        item['pr1qt'] = product['keepCnt']
                        item['pgco'] = ''

                        item['sk'] = keyword
                        item['pr1br'] = product['brand']
                        item['brlk'] = ''
                        item['talk'] = product['mallPcUrl']
                        item['pr1id'] = ''
                        item['dcrate'] = ''
                        # item['fullpr'] = response.xpath('//del[contains(@class,"Xdhdpm0BD9")]/span[2]/text()').get()                    
                        item['fullpr'] = ''
                        # item['dcpr'] = response.xpath('//strong[contains(@class, "aICRqgP9zw")]/span[2]/text()').get()
                        item['dcpr'] = ''
                        item['soldout'] = ''
                        item['pr1va'] = ''
                        item['msbf'] = ''
                        item['prdetail'] = ''

                        item['revsum'] = ''
                        item['revsb'] = ''
                        item['reviewer'] = ''
                        item['ingrade'] = ''
                        item['revdate'] = ''
                        item['purchdetail'] = ''
                        item['revdetail'] = ''
                        item['blogrev'] = ''
                        item['revviews'] = ''

                        yield item

                    elif product["lowMallList"] is not None:
                        pass


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
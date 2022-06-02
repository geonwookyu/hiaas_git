from ast import keyword
from operator import itemgetter
from pkgutil import iter_modules
from attr import attrib
from pkg_resources import resource_isdir
from scrapy.linkextractors import LinkExtractor
import scrapy

from mi.items import HiLabMIItem

class CoupangSpider(scrapy.Spider):
    name = "coupang"
#    keyword = 'tv'

    def start_requests(self):

        urls=[]
        for i in range(1,14):
            url_page = f'https://www.coupang.com/np/search?q=tv&channel=user&component=&eventCategory=SRP&trcid=&traid=&sorter=scoreDesc&minPrice=&maxPrice=&priceRange=&filterType=&listSize=72&filter=&isPriceRange=false&brand=&offerCondition=&rating=0&page={i}&rocketAll=false&searchIndexingToken=&backgroundColor='
                
            urls.append(url_page)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        try :
        
            coupang_sels = response.css('ul.search-product-list > li')
            
            for coupang_sel in coupang_sels:
                url = 'https://www.coupang.com' + coupang_sel.css('a.search-product-link::attr(href)').get()
                
                yield scrapy.Request(url=url, callback=self.parse_detail)
        except Exception as e:
            print('e: ', e)

    def parse_detail(self, response):
        try:
            item = HiLabMIItem()
            # item['detail_link'] 링크가 끝까지 안 나옴.
            item['detail_link'] = response.url  # 제품 상세페이지 url
            # item['pr1ca'] 조금 더 살펴봐야 함.
            item['pr1ca'] = response.css('a.breadcrumb-link::text').get()   # 카테고리
            item['pr1nm'] = response.css('h2.prod-buy-header__title::text').get()   # 제품명
            item['pr1pr'] = response.css('span.total-price > strong::text').get()   # 가격
            item['ta'] = response.css('a.prod-sale-vendor-name::text').get()    # 판매자
#            if item['ta'] is None:
            # item['ta'] 문제 있음.
#                item['ta'] = response.css('div.product-item__table product-seller > table.prod-delivery-return-policy-table > td[0]').get()
#                item['ta'] = response.css('div.product-item__table product-seller > table > tbody > tr > td').get()
            item['ts'] = response.css('div.prod-shipping-fee-message > span > em.prod-txt-bold::text').get()    # 무료배송 유무
            if item['ts'] is None:  # 무료배송, 로켓배송 아닐 때
                item['ts'] = response.css('div.prod-shipping-fee-message > span::text').get()
            item['pr1qt'] = response.css('div.aos-label::text').get()   # 재고 현황
            item['pr1br'] = response.css('a.prod-brand-name::text').get()   # 브랜드
#            item['pr1id'] = response.css() # SKU
#            item['pr1va'] = response.css() # 제품 구매 옵션


 #           coupang_detail_sels = response.css('section#contents')

 #           for coupang_detail_sel in coupang_detail_sels:
 #               item['pr1nm'] = coupang_detail_sel.css('div > div > div > div > h2::text').get()
 #               item['pr1ca'] = coupang_detail_sel.css('ul#breadcrumb::text').get()
 #               item['pr1pr'] = coupang_detail_sel.css('strong::text').get()

            yield item
        except Exception as e:
            print('e: ', e)
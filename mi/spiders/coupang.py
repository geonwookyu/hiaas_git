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

    def start_requests(self):
        global keyword
        keyword = 'tv'
        listSize = '72'
        sorter = 'scoreDesc' # 쿠팡 랭킹 순
        urls=[]
        for i in range(1,2):
            global url_page
            #url_page = f'https://www.coupang.com/np/search?q=tv&channel=user&component=&eventCategory=SRP&trcid=&traid=&sorter=scoreDesc&minPrice=&maxPrice=&priceRange=&filterType=&listSize=72&filter=&isPriceRange=false&brand=&offerCondition=&rating=0&page={i}&rocketAll=false&searchIndexingToken=&backgroundColor='
            url_page = f'https://www.coupang.com/np/search?rocketAll=false&q={keyword}&brand=&offerCondition=&filter=&availableDeliveryFilter=&filterType=&isPriceRange=false&priceRange=&minPrice=&maxPrice=&page={i}&trcid=&traid=&filterSetByUser=true&channel=user&backgroundColor=&component=&rating=0&sorter={sorter}&listSize={listSize}'
            urls.append(url_page)
            
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        try :
            coupang_sels = response.css('ul.search-product-list > li')

            print(response.css('label.item-name::text'))  # 카테고리
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
            if "scoreDesc" in url_page:
                item['sb'] = "쿠팡 랭킹 순"  # 정렬기준
            item['pr1ca'] = response.css('ul#breadcrumb > li > .breadcrumb-link::text').get()  # 카테고리 동적페이지
            item['pr1nm'] = response.css('h2.prod-buy-header__title::text').get()   # 제품명
            item['pr1pr'] = response.css('span.total-price > strong::text').get()   # 가격
            item['ta'] = response.css('a.prod-brand-name::text').get()    # 판매자
            if response.css('a.prod-brand-name::text').get() == None:
                item['ta'] = response.css('a.prod-sale-vendor-name::text').get()    # 판매자
            item['gr'] = response.css('span.rating-star-num::attr(style)').get().replace("width: ","").replace(";","")      # 평점
            item['revco'] = response.css('span.count::text').get().replace(" 상품평","").replace("개","")   # 리뷰개수
            item['dcinfo'] = response.css('span.discount-rate::text').get().replace("\n","").replace(" ","").replace("%","")   # 할인정보
            if item['dcinfo'] != "":
                item['dcinfo'] = response.css('span.discount-rate::text').get().replace("\n","").replace(" ","")
            item['ts'] = response.css('div.prod-shipping-fee-message > span > em.prod-txt-bold::text').get()    # 무료배송 유무
            if item['ts'] is None:  # 무료배송, 로켓배송 아닐 때
                item['ts'] = response.css('div.prod-shipping-fee-message > span::text').get()

            item['ardate'] = response.css('em.prod-txt-onyx.prod-txt-green-2::text').get()    # 로켓배송 시 도착예정일자
            if response.css('em.prod-txt-onyx.prod-txt-green-2::text').get() == None:
                item['ardate'] = response.css('em.prod-txt-onyx.prod-txt-font-14::text').get()    # 일반배송 시 도착예정일자
                if response.css('em.prod-txt-onyx.prod-txt-font-14::text').get() == None:
                    item['ardate'] = response.css('em.prod-txt-onyx.prod-txt-bold::text').get()    # 일반배송 시 도착예정일자
            item['ms'] = response.css('span.ccid-txt::text').get()
            if response.css('span.ccid-txt::text').get() != None:
                item['ms'] = response.css('span.ccid-txt::text').get().replace("최대 ","").replace(" 카드 즉시할인","")     # 멤버십
            item['opo'] = response.css('span.prod-offer-banner-item::text').get()
            opo_list=[]
            if response.css('span.prod-offer-banner-item::text').get() != None:
                tagIdx = len(response.css('span.prod-offer-banner-item'))
                for i in range(0,tagIdx):
                    opo=[]
                    opo.append(response.css('span.prod-offer-banner-item::text')[i].get())
                    opo.append(response.css('span.prod-offer-banner-item__count::text')[i].get())
                    opo_str = "".join(opo)
                    opo_list.append(opo_str)
                item['opo'] = "/".join(opo_list)     
            item['pr1qt'] = response.css('div.aos-label::text').get()   # 재고 현황
            item['pr1br'] = response.css('a.prod-brand-name::text').get()   # 브랜드

            item['dcrate'] = response.css('span.discount-rate::text').get().replace("\n","").replace(" ","").replace("%","")   # 할인율
            if item['dcrate'] != "":
                item['dcrate'] = response.css('span.discount-rate::text').get().replace("\n","").replace(" ","")
            item['fullpr'] = response.css('span.origin-price::text').get().replace("\n","").replace(" ","")   # 정가
            #item['dcpr'] = response.css('div.prod-sale-price.instant-discount > span.total-price > strong::text').get()   # 쿠팡판매가
            item['dcpr'] = response.css('div.prod-coupon-price.prod-major-price > span.total-price > strong::text').get()   # 와우할인가
            item['soldout'] = response.css('div.aos-label::text').get()   # 품절
            item['prdetail'] = response.css('ul.prod-description-attribute > li.prod-attr-item::text').get()
            prdetail_list=[]
            if response.css('ul.prod-description-attribute > li.prod-attr-item::text').get() != None:
                tagIdx = len(response.css('ul.prod-description-attribute > li.prod-attr-item'))
                for i in range(0,tagIdx):
                    prdetail_list.append(response.css('ul.prod-description-attribute > li.prod-attr-item::text')[i].get())
                item['prdetail'] = "\n".join(prdetail_list)
            item['msbf'] = response.css('strong.reward-final-cashback-amt::text').get()
            # item['pr1va'] = response.css('div.prod-option__selected-container').get()
            # pr1va_list=[]
            # if response.css('div.prod-option__selected-container') != None:
            #     tagIdx = len(response.css('div.prod-option__selected-container')) # 2개
            #     tagIdx2 = len(response.css('div.prod-option__dropdown-item-title')).get() # n개
            #     for i in range(0,tagIdx):
            #         for i in range(0,tagIdx2):
            #             pr1va=[]
            #             pr1va.append(response.css('div.prod-option__dropdown-item-title > strong ::text')[i].get())
            #             pr1va.append(response.css('div.prod-option__dropdown-item-price > strong ::text')[i].get())
            #             pr1va_str = ", ".join(pr1va)
            #             pr1va_list.append(pr1va_str)
            #         item['pr1va'] = "/".join(pr1va_list)   
#            item['pr1va'] = response.css() # 제품 구매 옵션


 #           coupang_detail_sels = response.css('section#contents')

 #           for coupang_detail_sel in coupang_detail_sels:
 #               item['pr1nm'] = coupang_detail_sel.css('div > div > div > div > h2::text').get()
 #               item['pr1ca'] = coupang_detail_sel.css('ul#breadcrumb::text').get()
 #               item['pr1pr'] = coupang_detail_sel.css('strong::text').get()

            yield item
        except Exception as e:
            print('e: ', e)
from ast import keyword
from operator import itemgetter
from pkgutil import iter_modules
from attr import attrib
from pkg_resources import resource_isdir
from scrapy.linkextractors import LinkExtractor
import scrapy
import re
from mi.items import HiLabMIItem

class CoupangSpider(scrapy.Spider):
    name = "coupang"

    def start_requests(self):
        global keyword
        global page
        keyword = 'tv'
        listSize = '72'
        sorter = 'scoreDesc' # 쿠팡 랭킹 순
        urls=[]
        for page in range(1,14):
            global url_page
            
            #url_page = f'https://www.coupang.com/np/search?q=tv&channel=user&component=&eventCategory=SRP&trcid=&traid=&sorter=scoreDesc&minPrice=&maxPrice=&priceRange=&filterType=&listSize=72&filter=&isPriceRange=false&brand=&offerCondition=&rating=0&page={i}&rocketAll=false&searchIndexingToken=&backgroundColor='
            url_page = f'https://www.coupang.com/np/search?rocketAll=false&q={keyword}&brand=&offerCondition=&filter=&availableDeliveryFilter=&filterType=&isPriceRange=false&priceRange=&minPrice=&maxPrice=&page={page}&trcid=&traid=&filterSetByUser=true&channel=user&backgroundColor=&component=&rating=0&sorter={sorter}&listSize={listSize}'
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

            item['detail_link'] = response.url  #링크 끝까지 안 나옴 javascript

            #item['rank']   # 순위 -> javascript

            #item['pr1ca'] = response.xpath('ul#breadcrumb a::text').getall()   # 카테고리 -> '쿠팡 홈'만 나옴 javascript
            ##//*[@id="breadcrumb"]/li[1]/a     카테고리 xpath
            ##//*[@id="breadcrumb"]/li[2]/a
            ##//*[@id="breadcrumb"]/li[3]/a
            ##//*[@id="breadcrumb"]/li[4]/a
            #for category in response.css('#breadcrumb > li'):
                #item['pr2ca'] = category.css('a::text').getall()
                
            if "scoreDesc" in url_page: # 정렬기준(O)
                item['sb'] = "쿠팡 랭킹순"  
            elif "salePriceAsc" in url_page:
                item['sb'] = "낮은가격순"
            elif "salePriceDesc" in url_page:
                item['sb'] = "높은가격순"
            elif "saleCountDesc" in url_page:
                item['sb'] = "판매량순"
            elif "latestAsc" in url_page:
                item['sb'] = "최신순"

            ##item['prco']   # 총 제품 수: 해당없음

            item['pr1nm'] = response.css('h2.prod-buy-header__title::text').get()   # 제품명(O)

            item['pr1pr'] = response.css('span.total-price > strong::text').get()   # 가격(O)

            #item['ta'] = response.xpath('//*[@id="btfTab"]/ul[2]/li[4]/div/table/tbody/tr[1]/td[1]').get()    # 판매자(상호/대표자)(?) - javascript
            #if response.xpath('//*[@id="btfTab"]/ul[2]/li[4]/div/table/tbody/tr[1]/td[1]').get() is None:
            #    item['ta'] = response.xpath('//*[@id="btfTab"]/ul[2]/li[4]/div/table/tbody/tr/td/text()')    # 판매자(쿠팡)(?) - javascript
            ##//*[@id="btfTab"]/ul[2]/li[4]/div/table/tbody/tr[1]/td[1] -> '상호/대표자'가 있을 때 xpath
            ##//*[@id="btfTab"]/ul[2]/li[4]/div/table/tbody/tr/td/text() -> '쿠팡'일 때 xpath

            ##item['gr'] = response.css('span.rating-star-num::attr(style)').get().replace("width: ","").replace(";","")      # 평점 -> 5점 만점이 아닌 %로 나옴
            #***********************************************************************************
            gr = re.sub(r'[^0-9.]', '', str(response.css('span.rating-star-num::attr(style)').get()))      # 평점(O)
            if "100.0" in gr:
                item['gr'] = 5.0
            elif "90.0" in gr:
                item['gr'] = 4.5
            elif "80.0" in gr:
                item['gr'] = 4.0
            elif "70.0" in gr:
                item['gr'] = 3.5
            elif "60.0" in gr:
                item['gr'] = 3.0
            elif "50.0" in gr:
                item['gr'] = 2.5
            elif "40.0" in gr:
                item['gr'] = 2.0
            elif "30.0" in gr:
                item['gr'] = 1.5
            elif "20.0" in gr:
                item['gr'] = 1.0
            elif "10.0" in gr:
                item['gr'] = 0.5
            else:
                item['gr'] = 0

            item['revco'] = re.sub(r'[^0-9]', '', str(response.css('span.count::text').get()))   # 리뷰개수(O)

            ##item['dcinfo'] = response.css('span.discount-rate::text').get().replace("\n","").replace(" ","").replace("%","")   # 할인정보
            ##if item['dcinfo'] != "":
            ##    item['dcinfo'] = response.css('span.discount-rate::text').get().replace("\n","").replace(" ","")
            #******************************************************************************************************************************
            dcinfo = response.css('span.discount-rate::text').get()   # 할인정보(O) - 할인율(%)로 가져오고, 할인 없는 것은 "No Discount"
            if (dcinfo == "%") or (dcinfo is None):
                dcinfo = ""
            item['dcinfo'] = dcinfo.strip()

            item['ts'] = response.css('div.prod-shipping-fee-message > span > em.prod-txt-bold::text').get()    # 무료배송 유무(O)
            if item['ts'] is None:  # 무료배송 아닐 때
                item['ts'] = response.css('div.prod-shipping-fee-message > span::text').get()

            ##item['ardate'] = response.css('em.prod-txt-onyx.prod-txt-green-2::text').get()    # 로켓배송 시 도착예정일자
            ##if response.css('em.prod-txt-onyx.prod-txt-green-2::text').get() == None:
            ##    item['ardate'] = response.css('em.prod-txt-onyx.prod-txt-font-14::text').get()    # 일반배송 시 도착예정일자
            ##    if response.css('em.prod-txt-onyx.prod-txt-font-14::text').get() == None:
            ##        item['ardate'] = response.css('em.prod-txt-onyx.prod-txt-bold::text').get()    # 일반배송 시 도착예정일자
            ## '내일(화)' 같은 텍스트가 필요없음.
            #*****************************************************************************************************************
            ardate = response.css('em.prod-txt-onyx.prod-txt-bold::text').get()    # 로켓 아니고, 도착예정일자 전화/문자로 안내(O)
            if ardate is None:
                ardate = response.css('em.prod-txt-onyx.prod-txt-font-14::text').get()     # 로켓 아닐 때 도착예정일자(O)
                if ardate is None:
                    ardate = response.css('em.prod-txt-onyx.prod-txt-green-2::text').get()     # 로켓일 때 도착예정일자(O)
                    re_pattern = re.compile(r'\d+')
                    ardate = '/'.join(re.findall(re_pattern, str(ardate)))
                    item['ardate'] = ardate
                else:
                    re_pattern = re.compile(r'\d+')
                    ardate = '/'.join(re.findall(re_pattern, str(ardate)))
                    item['ardate'] = ardate
            else:
                item['ardate'] = ardate
            
            
            ##item['ms'] = response.css('span.ccid-txt::text').get()  # 멤버십 적용유무
            ##if response.css('span.ccid-txt::text').get() != None:
            ##    item['ms'] = response.css('span.ccid-txt::text').get().replace("최대 ","").replace(" 카드 즉시할인","")
            #***********************************************************************************************
            ms_list = []
            if response.css('img.delivery-badge-img::attr(src)').get() == "//image10.coupangcdn.com/image/badges/rocket/rocket_logo.png":
                ms_list.append("로켓배송")  # 멤버십 적용유무 -> 로켓배송(O)
            if response.css('img.delivery-badge-img.rocket-install-img::attr(src)').get() == "//image7.coupangcdn.com/image/badges/rocket-install/v3/aos_2/rocket_install_xhdpi.png":
                ms_list.append("로켓설치")  # 멤버십 적용유무 -> 로켓 설치(O)
            if response.css('span.ccid-txt::text').get() is not None:
                ms_list.append(response.css('span.ccid-txt::text').get())   # 멤버십 적용유무 -> 카드할인(O)
            if response.css('span.reward-cash-txt::text').get() is not None:
                ms_list.append(response.css('span.reward-cash-txt::text').get().replace(' ', '').strip().replace('\n\n', ' '))   # 멤버십 적용유무 -> 캐시적립(O)
            item['ms'] = ms_list

            item['opo'] = response.css('span.prod-offer-banner-item::text').get()   # 다른 구매옵션(O)
            opo_list = []
            if response.css('span.prod-offer-banner-item::text').get() != None:
                tagIdx = len(response.css('span.prod-offer-banner-item'))
                for i in range(0,tagIdx):
                    opo = []
                    opo.append(response.css('span.prod-offer-banner-item::text')[i].get())
                    opo.append(response.css('span.prod-offer-banner-item__count::text')[i].get())
                    opo_str = "".join(opo)
                    opo_list.append(opo_str)
                item['opo'] = "/".join(opo_list)
                    
            ##item['purchco']    # 구매횟수: 해당없음

            ##item['pr1qt'] = response.css('div.aos-label::text').get()   # 재고 현황 -> 개수(숫자)만 긁어오게
            #***********************************************************************
            if response.css('div.aos-label::text').get() is None:   # 재고 현황(O)
                item['pr1qt'] = response.css('div.aos-label::text').get()
            else:
                pr1qt = response.css('div.aos-label::text').get()
                item['pr1qt'] = re.sub(r'[^0-9]', '', str(pr1qt))

            item['pgco'] = page   # 전체 페이지 수(O)

    # ---------------------------------------------------------------------------------------------------------------------------------

            item['sk'] = keyword   # 검색 키워드(O)

    # ---------------------------------------------------------------------------------------------------------------------------------

            item['pr1br'] = response.css('a.prod-brand-name::text').get()   # 브랜드(O)

            #item['brlk'] = response.css('a.prod-brand-name::attr(href)').get() # 브랜드샵link javascript

            #item['talk']   # 셀러샵link javascript

            #item['pr1id'] = response.css('#itemBrief > div > table > tbody > tr:nth-child(1) > td:nth-child(2)::text').get()  # SKU javascript
            #item['pr1id'] = response.xpath('//*[@id="contents"]/div[1]/div/div[3]/div[10]/div/div/div/button/table/tbody/tr/td[1]/span[2]/@text').get()  # SKU
            #contents > div.prod-atf > div > div.prod-buy.new-oos-style.not-loyalty-member.eligible-address.without-subscribe-buy-type.DISPLAY_0.has-loyalty-exclusive-price > div.prod-option > div:nth-child(2) > div > div > button > table > tbody > tr > td:nth-child(1) > span.value
            #//*[@id="contents"]/div[1]/div/div[3]/div[10]/div[2]/div/div/button/table/tbody/tr/td[1]/span[2]

            #item['dcrate'] # 할인율 -> dcinfo랑 동일
            #할인정보와 가져오는 위치가 동일함(115)

            ##item['fullpr'] = response.css('span.origin-price::text').get().replace("\n","").replace(" ","")   # 정가 -> 값 안 나오는 거 있음
            #********************************************************************************************
            fullpr = response.css('span.origin-price::text').get()   # 정가(O)
            if fullpr == "원":
                item['fullpr'] = response.css('span.total-price > strong::text').get()
            elif fullpr is None:
                item['fullpr'] = response.css('div.prod-sale-price > strong::text').get()   # 중고상품일 때
            else:
                item['fullpr'] = fullpr.replace("원", "")
            
            # 쿠팡판매가, 와우할인가 나눠져 있을 때
            ##item['dcpr'] = response.css('div.prod-sale-price.instant-discount > span.total-price > strong::text').get()   # 쿠팡판매가
            ##item['dcpr'] = response.css('div.prod-coupon-price.prod-major-price > span.total-price > strong::text').get()   # 와우할인가
            ##item['dcpr'] = response.css('span.total-price > strong::text').getall() ## 쿠팡판매가, 와우판매가 2개 다 cawling
            # 쿠팡판매가, 와우할인가 안 나눠져 있을 때
            ##item['dcpr'] = response.css('prod-sale-price.prod-major-price > span.total-price > strong::text').get()
            #위에 '가격' 크롤링 한 css로 똑같이 가져오면 쿠팡판매가, 와우할인가 나뉘어진 상품은 쿠팡판매가가 나옴.(75)
            ##item['dcpr'] = response.css('span.total-price > strong::text').get()

            soldout = response.css('div.oos-label::text').get()   # 품절 유무(O)
            if soldout is None:
                item['soldout'] = soldout
            else:
                item['soldout'] = soldout.strip()

            #item['pr1va'] = response.css('div.prod-option__dropdown-item-title > strong::text').get()   # 제품 구매 옵션 -> 아직 못 긁어왔음 javascript

            #item['msbf'] = response.css('strong.reward-final-cashback-amt::text').get() # 멤버십 혜택 -> 아직
            #item['msbf'] = response.css('strong.tit-txt::text').getall() # 카드 혜택

            ##item['prdetail'] = response.css('ul.prod-description-attribute > li.prod-attr-item::text').get()    # 제품 상세
            ##prdetail_list=[]
            ###if response.css('ul.prod-description-attribute > li.prod-attr-item::text').get() != None:
            ##    tagIdx = len(response.css('ul.prod-description-attribute > li.prod-attr-item'))
            ##    for i in range(0,tagIdx):
            ##        prdetail_list.append(response.css('ul.prod-description-attribute > li.prod-attr-item::text')[i].get())
            ##    item['prdetail'] = "\n".join(prdetail_list)
            #***********************************************************************
            item['prdetail'] = response.css('li.prod-attr-item::text').getall()    # 제품 상세(O)

    # ---------------------------------------------------------------------------------------------------------------------------------

            #item['revsum'] # 리뷰 특징 요약

            #  정렬기준 -> None으로 뜸        
            #item['revsb'] = response.css('button.sdp-review__article__order__sort__best-btn sdp-review__article__order__sort__btn--active js_reviewArticleHelpfulListBtn js_reviewArticleSortBtn::text').get()

            #item['reviewer'] = response.css('span.sdp-review__article__list__info__user__name js_reviewUserProfileImage::text').get()   # 작성자 -> None

            #item['ingrade'] = response.css('div.sdp-review__article__list__info__product-info__star-orange js_reviewArticleRatingValue')    # 평점 -> 아직

            #item['revdate'] = response.css('div.sdp-review__article__list__info__product-info__reg-date::text').get()    # 작성 일자 -> yet

            
            #item['purchdetail'] = response.css('div.sdp-review__article__list__info__product-info__name::text').get()    # 구매품목 디테일 -> yet
            
            # 리뷰 디테일 -> yet
            #item['revdetail'] = response.css('div.sdp-review__article__list__headline').get() + response.css('div.sdp-review__article__list__review__content js_reviewArticleContent').get()

            #item['blogrev']    # 블로그 리뷰: 해당없음
            #item['revviews']   # 리뷰 조회수: 해당없음

            yield item
        except Exception as e:
            print('e: ', e)
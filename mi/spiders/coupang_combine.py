import re
import scrapy
import asyncio
from playwright.async_api import async_playwright
from mi.items import HiLabMIItem
from mi.spiders.hiaas_common import HiaasCommon
from scrapy.utils.project import get_project_settings

class CoupangCombineSpider(HiaasCommon):
    name = "coupang_combine"
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader
    custom_settings = {
        'TWISTED_REACTOR' : "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        # 'ITEM_PIPELINES' : None    
    }

    marketType = "coupang"
    
    async def parse(self, response):

        settings = get_project_settings()
        KEYWORD_LIST = settings.get('KEYWORD_LIST')
        COUPANG_CRAWL_DELAY = settings.get('COUPANG_CRAWL_DELAY')
        COUPANG_LISTSIZE = settings.get('COUPANG_LISTSIZE')
        COUPANG_PAGE_COUNT = settings.get('COUPANG_PAGE_COUNT')
        COUPANG_SORTER = settings.get('COUPANG_SORTER')

        async with async_playwright() as pw:
            browser = await pw.firefox.launch()
            page = await browser.new_page()
            
            for keyword in KEYWORD_LIST:
                for pagenum in range(1, COUPANG_PAGE_COUNT):
                    search_link = f'https://www.coupang.com/np/search?rocketAll=false&q={keyword}&brand=&offerCondition=&filter=&availableDeliveryFilter=&filterType=&isPriceRange=false&priceRange=&minPrice=&maxPrice=&page={pagenum}&trcid=&traid=&filterSetByUser=true&channel=recent&backgroundColor=&searchProductCount=1857217&component=&rating=0&sorter={COUPANG_SORTER}&listSize={COUPANG_LISTSIZE}'
                    await page.goto(search_link)
                    await asyncio.sleep(COUPANG_CRAWL_DELAY)

                    locators = page.locator('ul.search-product-list> li > a.search-product-link')
                    count = await locators.count()

                    for i in range(count):
                        locator = locators.nth(i)
                        href = await locator.get_attribute('href')
                        detail_link = 'https://www.coupang.com' + href
                        if 'sourceType=srp_product_ads' in href:
                            ad = 'ad'
                        else:
                            ad = None
                        
                        yield scrapy.Request(url=detail_link, callback=self.parse_detail, meta=dict(
                            ad = ad,
                            sk = keyword
                        ))

            await browser.close()

    def parse_detail(self, response):
        try:

            item = HiLabMIItem()

            # 마켓 타입 (ex. naver, coupang)
            item['mid'] = self.marketType

            # collection type (1:키워드, 2:카테고리)
            item['ctype'] = 1

            # 상세페이지 링크
            item['detail_link'] = response.url

            # 순위
            item['rank'] = int(response.url.split('&rank=')[1])

            # 광고 여부
            item['ad'] = response.meta.get('ad')

            ## 카테고리 -> javascript
            # item['pr1ca'] = response.css('ul#breadcrumb a::text').getall()
            #for category in response.css('#breadcrumb > li'):
                #item['pr2ca'] = category.css('a::text').getall()
            
            ## 정렬기준
            # if "scoreDesc" in url_page:
            #     item['sb'] = "쿠팡 랭킹순"  
            # elif "salePriceAsc" in url_page:
            #     item['sb'] = "낮은가격순"
            # elif "salePriceDesc" in url_page:
            #     item['sb'] = "높은가격순"
            # elif "saleCountDesc" in url_page:
            #     item['sb'] = "판매량순"
            # elif "latestAsc" in url_page:
            #     item['sb'] = "최신순"

            ## 총 제품 수: 해당없음
            #item['prco']

            # 제품명
            pr1nm = response.css('h2.prod-buy-header__title::text').get()
            item['pr1nm'] = pr1nm

            # 가격
            pr1pr = response.css('span.total-price > strong::text').get()
            if pr1pr is not None:
                item['pr1pr'] = int(pr1pr.replace(',', ''))
            else:
                item['pr1pr'] = pr1pr

            ## 판매자
            #item['ta'] = response.xpath('//*[@id="btfTab"]/ul[2]/li[4]/div/table/tbody/tr[1]/td[1]').get()    # 판매자(상호/대표자)(?) - javascript
            #if response.xpath('//*[@id="btfTab"]/ul[2]/li[4]/div/table/tbody/tr[1]/td[1]').get() is None:
            #    item['ta'] = response.xpath('//*[@id="btfTab"]/ul[2]/li[4]/div/table/tbody/tr/td/text()')    # 판매자(쿠팡)(?) - javascript
            ##//*[@id="btfTab"]/ul[2]/li[4]/div/table/tbody/tr[1]/td[1] -> '상호/대표자'가 있을 때 xpath
            ##//*[@id="btfTab"]/ul[2]/li[4]/div/table/tbody/tr/td/text() -> '쿠팡'일 때 xpath

            # 평점
            gr = re.sub(r'[^0-9.]', '', str(response.css('span.rating-star-num::attr(style)').get()))
            item['gr'] = float(gr) / 100 * 5

            # 리뷰개수
            item['revco'] = int(re.sub(r'[^0-9]', '', str(response.css('span.count::text').get())))

            ## 할인정보
            ##item['dcinfo'] = response.css('span.discount-rate::text').get().replace("\n","").replace(" ","").replace("%","")
            ##if item['dcinfo'] != "":
            ##    item['dcinfo'] = response.css('span.discount-rate::text').get().replace("\n","").replace(" ","")
            #******************************************************************************************************************************
            # dcinfo = response.css('span.discount-rate::text').get()   # 할인정보: 할인율과 가져오는 정보가 동일하여 일단은 할인율을 가져오고 할인정보는 수집 보류
            # if dcinfo is None:
            #     item['dcinfo'] = None
            # elif dcinfo.strip() == "%":
            #     item['dcinfo'] = None
            # else:
            #     item['dcinfo'] = dcinfo.strip()

            # 무료배송 유무
            ts = response.css('div.prod-shipping-fee-message > span > em.prod-txt-bold::text').get()
            item['ts'] = ts == "무료배송"

            # 도착 예정일자
            # 로켓 아니고, 도착예정일자 전화/문자로 안내
            ardate = response.css('em.prod-txt-onyx.prod-txt-bold::text').get()
            if ardate is None:
                # 로켓 아닐 때 도착예정일자
                ardate = response.css('em.prod-txt-onyx.prod-txt-font-14::text').get()     
                if ardate is None:
                    # 로켓 아닐 때 도착예정일자2
                    ardate = response.css('em.prod-txt-onyx::text').get()
                    if ardate is None:
                        # 로켓일 때 도착예정일자
                        ardate = response.css('em.prod-txt-onyx.prod-txt-green-2::text').get()
                        re_pattern = re.compile(r'\d+')
                        ardate = '/'.join(re.findall(re_pattern, str(ardate)))
                        item['ardate'] = ardate
                    else:
                        re_pattern = re.compile(r'\d+')
                        ardate = '/'.join(re.findall(re_pattern, str(ardate)))
                        item['ardate'] = ardate
                else:
                    re_pattern = re.compile(r'\d+')
                    ardate = '/'.join(re.findall(re_pattern, str(ardate)))
                    item['ardate'] = ardate
            else:
                item['ardate'] = ardate
            
            # 멤버십 적용유무
            ms_list = []
            # 로켓배송
            if response.css('img.delivery-badge-img::attr(src)').get() == "//image10.coupangcdn.com/image/badges/rocket/rocket_logo.png":
                ms_list.append("로켓배송")
            # 로켓 설치
            if response.css('img.delivery-badge-img.rocket-install-img::attr(src)').get() == "//image7.coupangcdn.com/image/badges/rocket-install/v3/aos_2/rocket_install_xhdpi.png":
                ms_list.append("로켓설치")
            if response.css('span.ccid-txt::text').get() is not None:
                # 카드할인
                ms_list.append(response.css('span.ccid-txt::text').get())
            if response.css('span.reward-cash-txt::text').get() is not None:
                # 캐시적립
                ms_list.append(response.css('span.reward-cash-txt::text').get().replace(' ', '').strip().replace('\n\n', ' '))
            item['ms'] = ms_list

            # 다른 구매옵션
            item['opo'] = response.css('span.prod-offer-banner-item::text').get()
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
                    
            ## 구매횟수: 해당없음
            ##item['purchco']

            # 재고 현황
            if response.css('div.aos-label::text').get() is None:
                item['pr1qt'] = None
            else:
                pr1qt = response.css('div.aos-label::text').get()
                item['pr1qt'] = int(re.sub(r'[^0-9]', '', str(pr1qt)))

            ## 전체 페이지 수
            # item['pgco'] = page

    # ---------------------------------------------------------------------------------------------------------------------------------

            # 검색 키워드
            item['sk'] = response.meta.get('sk')

    # ---------------------------------------------------------------------------------------------------------------------------------

            # 브랜드(O)
            # item['pr1br'] = response.css('a.prod-brand-name::text').get()
            item['pr1br'] = pr1nm.split()[0]    # 제품명의 앞 한 단어(임시)

            # 브랜드샵link
            #item['brlk'] = response.css('a.prod-brand-name::attr(href)').get()

            # 셀러샵link
            #item['talk']

            # SKU
            #item['pr1id'] = response.css('#itemBrief > div > table > tbody > tr:nth-child(1) > td:nth-child(2)::text').get()
            #item['pr1id'] = response.xpath('//*[@id="contents"]/div[1]/div/div[3]/div[10]/div/div/div/button/table/tbody/tr/td[1]/span[2]/@text').get()  # SKU
            #contents > div.prod-atf > div > div.prod-buy.new-oos-style.not-loyalty-member.eligible-address.without-subscribe-buy-type.DISPLAY_0.has-loyalty-exclusive-price > div.prod-option > div:nth-child(2) > div > div > button > table > tbody > tr > td:nth-child(1) > span.value
            #//*[@id="contents"]/div[1]/div/div[3]/div[10]/div[2]/div/div/button/table/tbody/tr/td[1]/span[2]

            # 할인율
            dcrate = response.css('span.discount-rate::text').get()
            if dcrate is None:
                item['dcrate'] = None
            elif dcrate.strip() == "%":
                item['dcrate'] = None
            else:
                item['dcrate'] = int(dcrate.strip().replace('%', ''))

            # 정가
            ##item['fullpr'] = response.css('span.origin-price::text').get().replace("\n","").replace(" ","")    -> 값 안 나오는 거 있음
            #********************************************************************************************
            fullpr = response.css('span.origin-price::text').get()   # 정가(O)  # 가격 관련 아이템들은 다시 한번 살펴봐야 할 것
            if fullpr == "원":
                item['fullpr'] = int(response.css('span.total-price > strong::text').get().replace(',', ''))
            else:
                item['fullpr'] = int(fullpr.replace("원", "").replace(',', ''))
            
            # # 할인가: 와우할인가로 가져오기
            # # 쿠팡판매가, 와우할인가 나눠져 있을 때
            # ##item['dcpr'] = response.css('div.prod-sale-price.instant-discount > span.total-price > strong::text').get()   # 쿠팡판매가
            # item['dcpr'] = response.css('div.prod-coupon-price.prod-major-price > span.total-price > strong::text').get()   # 와우할인가
            # # item['dcpr'] = response.css('span.total-price > strong::text').getall() ## 쿠팡판매가, 와우판매가 2개 다 cawling
            # # 쿠팡판매가, 와우할인가 안 나눠져 있을 때
            # item['dcpr'] = response.css('prod-sale-price.prod-major-price > span.total-price > strong::text').get()
            # #위에 '가격' 크롤링 한 css로 똑같이 가져오면 쿠팡판매가, 와우할인가 나뉘어진 상품은 쿠팡판매가가 나옴.(75)
            # ##item['dcpr'] = response.css('span.total-price > strong::text').get()
            
            # 품절 유무
            soldout = response.css('div.oos-label::text').get()
            if soldout is not None:
                item['soldout'] = soldout.strip() == "일시품절"
            else:
                soldout = response.css('div.prod-not-find-known__buy__button').get()
                item['soldout'] = soldout == "품절"

            # 제품 구매 옵션
            #item['pr1va'] = response.css('div.prod-option__dropdown-item-title > strong::text').get()

            # 멤버십 혜택(ex. 카드혜택, 캐시적립혜택)
            item['msbf'] = response.css('strong.tit-txt::text').getall()

            # 제품 상세
            item['prdetail'] = response.css('li.prod-attr-item::text').getall()
            ##item['prdetail'] = response.css('ul.prod-description-attribute > li.prod-attr-item::text').get()
            ##prdetail_list=[]
            ###if response.css('ul.prod-description-attribute > li.prod-attr-item::text').get() != None:
            ##    tagIdx = len(response.css('ul.prod-description-attribute > li.prod-attr-item'))
            ##    for i in range(0,tagIdx):
            ##        prdetail_list.append(response.css('ul.prod-description-attribute > li.prod-attr-item::text')[i].get())
            ##    item['prdetail'] = "\n".join(prdetail_list)
            #***********************************************************************
            

    # ---------------------------------------------------------------------------------------------------------------------------------

            ## 리뷰 특징 요약
            #item['revsum']

            ##  정렬기준
            #item['revsb'] = response.css('button.sdp-review__article__order__sort__best-btn sdp-review__article__order__sort__btn--active js_reviewArticleHelpfulListBtn js_reviewArticleSortBtn::text').get()

            ## 작성자
            #item['reviewer'] = response.css('span.sdp-review__article__list__info__user__name js_reviewUserProfileImage::text').get()

            ## 평점
            #item['ingrade'] = response.css('div.sdp-review__article__list__info__product-info__star-orange js_reviewArticleRatingValue')

            ## 작성 일자
            #item['revdate'] = response.css('div.sdp-review__article__list__info__product-info__reg-date::text').get()

            ## 구매품목 디테일
            #item['purchdetail'] = response.css('div.sdp-review__article__list__info__product-info__name::text').get()
            
            ## 리뷰 디테일
            #item['revdetail'] = response.css('div.sdp-review__article__list__headline').get() + response.css('div.sdp-review__article__list__review__content js_reviewArticleContent').get()

            ## 블로그 리뷰: 해당없음
            #item['blogrev']

            ## 리뷰 조회수: 해당없음
            #item['revviews']
            yield item
            
        except Exception as e:
            print('e: ', e)
            # logger.error('Error [parse_detail]: %s', e)

    # def errback_httpbin(self, failure):
    #     # log all failures
    #     logger.error(repr(failure))

    #     # in case you want to do something special for some errors,
    #     # you may need the failure's type:

    #     if failure.check(HttpError):
    #         # these exceptions come from HttpError spider middleware
    #         # you can get the non-200 response
    #         response = failure.value.response
    #         logger.error('HttpError on %s', response.url)

    #     elif failure.check(DNSLookupError):
    #         # this is the original request
    #         request = failure.request
    #         logger.error('DNSLookupError on %s', request.url)

    #     elif failure.check(TimeoutError, TCPTimedOutError):
    #         request = failure.request
    #         logger.error('TimeoutError on %s', request.url)



    #         logger.error('TimeoutError on %s', request.url)









# ----------------------scrapy-playwright---------------------------
# import asyncio
# import scrapy

# from mi.spiders.hiaas_common import HiaasCommon
# from scrapy.utils.project import get_project_settings
# from scrapy_playwright.page import PageMethod

# class CoupangCombineSpider(HiaasCommon):
#     name = "coupang_combine"
#     # start_urls = ["data:,"]  # avoid using the default Scrapy downloader
#     custom_settings = {
#         'TWISTED_REACTOR' : "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
#         # 'ITEM_PIPELINES' : None,
#         'DOWNLOAD_HANDLERS' : {
#             "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#             "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#         }
#     }

#     def start_requests(self):
#         settings = get_project_settings()
#         KEYWORD_LIST = settings.get('KEYWORD_LIST')
#         COUPANG_PAGE_COUNT = settings.get('COUPANG_PAGE_COUNT')
#         COUPANG_SORTER = settings.get('COUPANG_SORTER')
#         COUPANG_LISTSIZE = settings.get('COUPANG_LISTSIZE')

#         for keyword in KEYWORD_LIST:
#             for pagenum in range(1, COUPANG_PAGE_COUNT):
#                 search_link = f'https://www.coupang.com/np/search?rocketAll=false&q={keyword}&brand=&offerCondition=&filter=&availableDeliveryFilter=&filterType=&isPriceRange=false&priceRange=&minPrice=&maxPrice=&page={pagenum}&trcid=&traid=&filterSetByUser=true&channel=recent&backgroundColor=&searchProductCount=1857217&component=&rating=0&sorter={COUPANG_SORTER}&listSize={COUPANG_LISTSIZE}'

#                 yield scrapy.Request(url=search_link, callback=self.parse_pagelink, meta=dict(
#                     playwright = True,
#                     playwright_include_page = True,
#                     errback=self.errback,
#                 ))
    
#     async def parse_pagelink(self, response):
#         settings = get_project_settings()
#         COUPANG_CRAWL_DELAY = settings.get('COUPANG_CRAWL_DELAY')

#         page = response.meta["playwright_page"]
#         # await asyncio.sleep(COUPANG_CRAWL_DELAY)
#         await page.close()

#         hrefs = response.css('ul.search-product-list > li > a.search-product-link::attr(href)').getall()

#         for href in hrefs:
#             detail_link = 'https://www.coupang.com' + href
#             yield {"detail_link": detail_link}

#     async def errback(self, failure):
#         page = failure.request.meta["playwright_page"]
#         await page.close()
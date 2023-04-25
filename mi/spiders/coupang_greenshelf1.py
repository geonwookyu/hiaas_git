import json
import logging
import re
from time import sleep
from abc import *
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from mi.items import HiLabMIItem
from mi.spiders.hiaas_common import *
from scrapy.utils.project import get_project_settings

def route_intercept(route):
    if route.request.resource_type == "image":
        # print(f"Blocking the image request to: {route.request.url}")
        return route.fallback()

    return route.continue_()

class CoupangGreenshelf1Spider(HiaasCommon):
    name = "coupang_greenshelf1"
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader

    marketType = "coupang"
    
    def parse(self, response):

        settings = get_project_settings()
        KEYWORD_LIST = settings.get('GREENSHELF1_KEYWORD')  # 검색 키워드 리스트
        COUPANG_CRAWL_DELAY = settings.get('COUPANG_CRAWL_DELAY')   # Delay 시간(seconds)
        COUPANG_LISTSIZE = settings.get('COUPANG_LISTSIZE')     # 한 페이지당 상품 개수
        COUPANG_PAGE_COUNT = settings.get('COUPANG_PAGE_COUNT')     # 페이지 수
        COUPANG_SORTER = settings.get('COUPANG_SORTER')     # 상품 정렬 기준
        COUPANG_PRICE_RANGE = settings.get('GREENSHELF1_PRICE_RANGE')   # 가격 필터
        COUPANG_MIN_PRICE = settings.get('GREENSHELF1_MIN_PRICE')   # 가격 필터
        COUPANG_MAX_PRICE = settings.get('GREENSHELF1_MAX_PRICE')   # 가격 필터
        COUPANG_LINKFILE_PATH = settings.get('COUPANG_LINKFILE_PATH')   # Coupang auto-Login cookie

        with sync_playwright() as pw:

            self.browser = pw.firefox.launch(proxy={
                "server": "per-context"
            })

            with open(COUPANG_LINKFILE_PATH, 'r', encoding='UTF-8') as json_file:

                cookies = json.load(json_file)

            for keyword in KEYWORD_LIST:

                for priceIndex in range(len(COUPANG_PRICE_RANGE)):

                    logging.error(f'priceRange: {COUPANG_MIN_PRICE[priceIndex]} ~ {COUPANG_MAX_PRICE[priceIndex]}')

                    self.context = self.browser.new_context(proxy={
                            'server': 'http://proxy.edgenet.site:7777',
                            'username': 'jhnam@hiaas.co.kr',
                            'password': 'hiaas12!@'
                    })

                    for pageNum in range(1, COUPANG_PAGE_COUNT):

                        try:

                            page = self.context.new_page()
                            self.context.add_cookies(cookies)

                            search_link = f'https://www.coupang.com/np/search?rocketAll=false&q={keyword}&brand=&offerCondition=&filter=&availableDeliveryFilter=&filterType=&isPriceRange=false&priceRange={COUPANG_PRICE_RANGE[priceIndex]}&minPrice={COUPANG_MIN_PRICE[priceIndex]}&maxPrice={COUPANG_MAX_PRICE[priceIndex]}&page={pageNum}&trcid=&traid=&filterSetByUser=true&channel=recent&backgroundColor=&searchProductCount=&component=&rating=0&sorter={COUPANG_SORTER}&listSize={COUPANG_LISTSIZE}'

                            page.route("**/*", route_intercept)
                            page.goto(search_link, timeout=0)
                            sleep(COUPANG_CRAWL_DELAY)

                            logging.error(f'pageNum--------------------------------------------------------:{pageNum}')

                            page.locator('ul.search-product-list> li > a.search-product-link').last.wait_for()

                            productLocators = page.locator('ul.search-product-list> li > a.search-product-link')
                            productCnts = productLocators.count()

                            logging.error(f'productCnts:{productCnts}')

                            products = []

                            for productCnt in range(productCnts):

                                productLocator = productLocators.nth(productCnt)

                                pr1nm = productLocator.locator('div.name').inner_text()
                                productName = pr1nm.lower().replace(' ', '')

                                if ('프리미엄에코' in productName) or ('프리미엄eco' in productName) or ('premium에코' in productName) or ('premiumeco' in productName) or ('w500' in productName) or ('pro40' in productName):    continue

                                if ('우머나이저' in productName and '리버티' in productName) or ('우머나이저' in productName and 'liberty' in productName) or ('womanizer' in productName and '리버티' in productName) or ('womanizer' in productName and 'liberty' in productName):

                                    href = productLocator.get_attribute('href')
                                    pr2nm = '리버티'

                                    product_info = {"href" : href, "pr1nm" : pr1nm, "pr2nm" : pr2nm}
                                    products.append(product_info)

                                elif ('우머나이저' in productName and '스탈렛' in productName) or ('우머나이저' in productName and 'starlet' in productName) or ('womanizer' in productName and '스탈렛' in productName) or ('womanizer' in productName and 'starlet' in productName):

                                    href = productLocator.get_attribute('href')

                                    if ('스탈렛3' in productName) or ('starlet3' in productName):
                                    
                                        pr2nm = '스탈렛3'

                                    else: pr2nm = '스탈렛'

                                    product_info = {"href" : href, "pr1nm" : pr1nm, "pr2nm" : pr2nm}
                                    products.append(product_info)

                                elif ('우머나이저' in productName and '듀오' in productName) or ('우머나이저' in productName and 'duo' in productName) or ('womanizer' in productName and '듀오' in productName) or ('womanizer' in productName and 'duo' in productName):

                                    href = productLocator.get_attribute('href')
                                    pr2nm = '듀오'

                                    product_info = {"href" : href, "pr1nm" : pr1nm, "pr2nm" : pr2nm}
                                    products.append(product_info)

                                elif ('우머나이저' in productName and '클래식' in productName) or ('우머나이저' in productName and 'classic' in productName) or ('womanizer' in productName and '클래식' in productName) or ('womanizer' in productName and 'classic' in productName):

                                    href = productLocator.get_attribute('href')
                                    
                                    if ('클래식2' in productName) or ('classic2' in productName) or ('뉴클래식' in productName) or ('뉴classic' in productName) or ('new클래식' in productName) or ('newclassic' in productName):
                                    
                                        pr2nm = '클래식2'

                                    else: pr2nm = '클래식'

                                    product_info = {"href" : href, "pr1nm" : pr1nm, "pr2nm" : pr2nm}
                                    products.append(product_info)

                                elif ('우머나이저' in productName and '프리미엄' in productName) or ('우머나이저' in productName and 'premium' in productName) or ('womanizer' in productName and '프리미엄' in productName) or ('womanizer' in productName and 'premium' in productName):

                                    href = productLocator.get_attribute('href')

                                    if ('뉴프리미엄' in productName) or ('new프리미엄' in productName) or ('newpremium' in productName) or ('프리미엄2' in productName) or ('premium2' in productName):

                                        pr2nm = '프리미엄2'
                                    
                                    else: pr2nm = '프리미엄'

                                    product_info = {"href" : href, "pr1nm" : pr1nm, "pr2nm" : pr2nm}
                                    products.append(product_info)

                                else:   continue

                            for product in products:

                                try:

                                    detail_link = 'https://www.coupang.com' + product['href']
                                    pr1nm = product['pr1nm']
                                    pr2nm = product['pr2nm']

                                    page.route("**/*", route_intercept)
                                    page.goto(detail_link, timeout=120000)
                                    sleep(COUPANG_CRAWL_DELAY)

                                    item = HiLabMIItem()
                                    
                                    # 마켓 타입 (ex. naver, coupang)
                                    item['mid'] = self.marketType

                                    # collection type (1:키워드, 2:카테고리)
                                    item['ctype'] = 1

                                    # 상세페이지 링크
                                    item['detail_link'] = detail_link

                                    # 순위
                                    item['rank'] = int(detail_link.split('&rank=')[1])

                                    # 광고 여부
                                    if 'sourceType=srp_product_ads' in detail_link:

                                        ad = 'ad'

                                    else:
                                        
                                        ad = None

                                    item['ad'] = ad

                                    # 제품명1
                                    item['pr1nm'] = pr1nm

                                    # 제품명2
                                    item['pr2nm'] = pr2nm

                                    # 가격
                                    try:

                                        noWowpr = page.locator('span.total-price > strong').first.inner_text()

                                        if noWowpr == "원":

                                            wowpr = page.locator('tr.choose-item.one-time-li.price-type-item.selected > td.td-price > span.price').inner_text()
                                            item['pr1pr'] = int(re.sub(r'[^0-9]', '', str(wowpr)))

                                        else:

                                            item['pr1pr'] = int(re.sub(r'[^0-9]', '', str(noWowpr)))

                                    except PlaywrightTimeoutError as pr1prError:

                                        item['pr1pr'] = None

                                        logging.error(f'pr1pr: {pr1prError}')
                                        logging.error(f'pr1pr Error: {detail_link}')

                                    # 판매자
                                    try:

                                        ta = page.locator('a.prod-sale-vendor-name').inner_text(timeout=1000)
                                        item['ta'] = ta

                                    except PlaywrightTimeoutError:
                                    
                                        item['ta'] = None

                                    # 정가
                                    try:

                                        fullpr = page.locator('span.origin-price').first.inner_text(timeout=1000)

                                        if fullpr == "원":

                                            item['fullpr'] = item['pr1pr']

                                        else:

                                            item['fullpr'] = int(re.sub(r'[^0-9]', '', str(fullpr)))

                                    except PlaywrightTimeoutError as fullprError:

                                        item['fullpr'] = item['pr1pr']

                                    # 검색 키워드
                                    item['sk'] = keyword

                                    # 브랜드
                                    item['pr1br'] = pr1nm.split()[0]    # 제품명의 앞 한 단어(임시)

                                    # SKU1
                                    SKU = json.loads(page.locator('div.prod-ctl-or-fbt-recommend.impression-log').get_attribute('data-fodium-widget-params'))
                                    item['pr1id'] = SKU['productId']

                                    # SKU2
                                    item['pr2id'] = SKU['itemId']

                                    yield item

                                except Exception as productError:

                                    logging.error(f'product: {productError}')
                                    logging.error(f'product Error: {detail_link}')

                            if productCnts < 72: break

                            page.close()

                        except Exception as pageError:

                            logging.error(f'page Error: {pageError}')

                    self.context.close()

            self.browser.close()
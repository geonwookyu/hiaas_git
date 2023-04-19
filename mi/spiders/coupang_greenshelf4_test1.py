import json
import logging
import re
from time import sleep
from abc import *
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from mi.items import HiLabMIItem
from mi.spiders.hiaas_common import *
from scrapy.utils.project import get_project_settings

class CoupangGreenshelf4Test1Spider(HiaasCommon):
    name = "coupang_greenshelf4_test1"
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader

    marketType = "coupang"
    
    def parse(self, response):

        settings = get_project_settings()
        KEYWORD_LIST = settings.get('GREENSHELF4_KEYWORD')  # 검색 키워드 리스트
        COUPANG_CRAWL_DELAY = settings.get('COUPANG_CRAWL_DELAY')   # Delay 시간(seconds)
        COUPANG_LISTSIZE = settings.get('COUPANG_LISTSIZE')     # 한 페이지당 상품 개수
        COUPANG_PAGE_COUNT = settings.get('COUPANG_PAGE_COUNT')     # 페이지 수
        COUPANG_SORTER = settings.get('COUPANG_SORTER')     # 상품 정렬 기준
        COUPANG_PRICE_RANGE = settings.get('GREENSHELF4_PRICE_RANGE')   # 가격 필터
        COUPANG_MIN_PRICE = settings.get('GREENSHELF4_MIN_PRICE')   # 가격 필터
        COUPANG_MAX_PRICE = settings.get('GREENSHELF4_MAX_PRICE')   # 가격 필터
        COUPANG_LINKFILE_PATH = settings.get('COUPANG_LINKFILE_PATH')   # Coupang auto-Login cookie
        PROXY_LIST = settings.get('PROXY_LIST')     # Proxy IP list

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

                                if ('롬프' in productName and '비트' in productName) or ('롬프' in productName and 'beat' in productName) or ('romp' in productName and '비트' in productName) or ('romp' in productName and 'beat' in productName):

                                    href = productLocator.get_attribute('href')
                                    detail_link = 'https://www.coupang.com' + href
                                    pr2nm = '비트'
                                    products.append(detail_link + '!@#$%' + pr1nm + '!@#$%' + pr2nm)

                                elif ('롬프' in productName and '스위치' in productName) or ('롬프' in productName and 'switch' in productName) or ('romp' in productName and '스위치' in productName) or ('romp' in productName and 'switch' in productName):

                                    href = productLocator.get_attribute('href')
                                    detail_link = 'https://www.coupang.com' + href
                                    pr2nm = '스위치'
                                    products.append(detail_link + '!@#$%' + pr1nm + '!@#$%' + pr2nm)

                                elif ('롬프' in productName and '쥬크' in productName) or ('롬프' in productName and '주크' in productName) or ('롬프' in productName and 'juke' in productName) or ('romp' in productName and '쥬크' in productName) or ('romp' in productName and '주크' in productName) or ('romp' in productName and 'juke' in productName):

                                    href = productLocator.get_attribute('href')
                                    detail_link = 'https://www.coupang.com' + href
                                    pr2nm = '쥬크'
                                    products.append(detail_link + '!@#$%' + pr1nm + '!@#$%' + pr2nm)

                                elif ('롬프' in productName and '프리' in productName) or ('롬프' in productName and 'free' in productName) or ('romp' in productName and '프리' in productName) or ('romp' in productName and 'free' in productName):

                                    href = productLocator.get_attribute('href')
                                    detail_link = 'https://www.coupang.com' + href
                                    pr2nm = '프리'
                                    products.append(detail_link + '!@#$%' + pr1nm + '!@#$%' + pr2nm)

                                elif ('롬프' in productName and '웨이브' in productName) or ('롬프' in productName and 'wave' in productName) or ('romp' in productName and '웨이브' in productName) or ('romp' in productName and 'wave' in productName):

                                    href = productLocator.get_attribute('href')
                                    detail_link = 'https://www.coupang.com' + href
                                    pr2nm = '웨이브'
                                    products.append(detail_link + '!@#$%' + pr1nm + '!@#$%' + pr2nm)

                                elif ('롬프' in productName and '재즈' in productName) or ('롬프' in productName and 'jazz' in productName) or ('romp' in productName and '재즈' in productName) or ('romp' in productName and 'jazz' in productName):

                                    href = productLocator.get_attribute('href')
                                    detail_link = 'https://www.coupang.com' + href
                                    pr2nm = '재즈'
                                    products.append(detail_link + '!@#$%' + pr1nm + '!@#$%' + pr2nm)

                                elif ('롬프' in productName and '샤인' in productName) or ('롬프' in productName and 'shine' in productName) or ('romp' in productName and '샤인' in productName) or ('romp' in productName and 'shine' in productName):

                                    href = productLocator.get_attribute('href')
                                    detail_link = 'https://www.coupang.com' + href
                                    pr2nm = '샤인'
                                    products.append(detail_link + '!@#$%' + pr1nm + '!@#$%' + pr2nm)

                                elif ('롬프' in productName and '하이프' in productName) or ('롬프' in productName and 'hype' in productName) or ('romp' in productName and '하이프' in productName) or ('romp' in productName and 'hype' in productName):

                                    href = productLocator.get_attribute('href')
                                    detail_link = 'https://www.coupang.com' + href
                                    pr2nm = '하이프'
                                    products.append(detail_link + '!@#$%' + pr1nm + '!@#$%' + pr2nm)

                                elif ('롬프' in productName and '플립' in productName) or ('롬프' in productName and 'flip' in productName) or ('romp' in productName and '플립' in productName) or ('romp' in productName and 'flip' in productName):

                                    href = productLocator.get_attribute('href')
                                    detail_link = 'https://www.coupang.com' + href
                                    pr2nm = '플립'
                                    products.append(detail_link + '!@#$%' + pr1nm + '!@#$%' + pr2nm)

                                else:   continue

                            for product in products:

                                try:

                                    detail_link = product.split('!@#$%')[0]
                                    pr1nm = product.split('!@#$%')[1]
                                    pr2nm = product.split('!@#$%')[2]

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

                                        # logging.error(f'fullpr: {fullprError}')
                                        # logging.error(f'fullpr Error: {detail_link}')
                                        logging.error('정가 selector 수정 필요')

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
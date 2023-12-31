import json
import logging
import re
from time import sleep
from abc import *
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from mi.items import HiLabMIItem
from mi.spiders.hiaas_common import *
from scrapy.utils.project import get_project_settings

# block pages by resource type. e.g. image, stylesheet
BLOCK_RESOURCE_TYPES = [
#   'beacon',
#   'csp_report',
  'font',
  'image',
  'imageset',
  'media',
  'object',
#   'texttrack',
#  we can even block stylsheets and scripts though it's not recommended:
  'stylesheet'
# 'script',  
# 'xhr',
]

def route_intercept(route):
    if route.request.resource_type in BLOCK_RESOURCE_TYPES:
        return route.fallback()

    return route.continue_()

class CoupangGeneralSpider(HiaasCommon):
    name = "coupang_general"
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader

    marketType = "coupang"
    
    def parse(self, response):

        settings = get_project_settings()
        KEYWORD_LIST = settings.get('COUPANG_GENERAL_KEYWORD')
        COUPANG_CRAWL_DELAY = settings.get('COUPANG_CRAWL_DELAY')
        COUPANG_LISTSIZE = settings.get('COUPANG_LISTSIZE')
        COUPANG_GENERAL_PAGE_COUNT = settings.get('COUPANG_GENERAL_PAGE_COUNT')
        COUPANG_SORTER = settings.get('COUPANG_SORTER')
        COUPANG_LINKFILE_PATH = settings.get('COUPANG_LINKFILE_PATH')   # Coupang auto-Login cookie

        with sync_playwright() as pw:

            self.browser = pw.firefox.launch(proxy={
                "server": "per-context"
            })

            with open(COUPANG_LINKFILE_PATH, 'r', encoding='UTF-8') as json_file:

                cookies = json.load(json_file)

            for keyword in KEYWORD_LIST:

                logging.error(f'[{keyword}] 검색')

                self.context = self.browser.new_context(proxy={
                        'server': 'http://proxy.edgenet.site:7777',
                        'username': 'jhnam@hiaas.co.kr',
                        'password': 'hiaas12!@'
                })

                for pageNum in range(1, COUPANG_GENERAL_PAGE_COUNT):

                    try:

                        page = self.context.new_page()
                        self.context.add_cookies(cookies)

                        search_link = f'https://www.coupang.com/np/search?rocketAll=false&q={keyword}&brand=&offerCondition=&filter=&availableDeliveryFilter=&filterType=&isPriceRange=false&priceRange=&minPrice=&maxPrice=&page={pageNum}&trcid=&traid=&filterSetByUser=true&channel=recent&backgroundColor=&searchProductCount=1857217&component=&rating=0&sorter={COUPANG_SORTER}&listSize={COUPANG_LISTSIZE}'
                        
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

                            href = productLocator.get_attribute('href')
                            pr1nm = productLocator.locator('div.name').inner_text()

                            product_info = {"href" : href, "pr1nm" : pr1nm}
                            products.append(product_info)

                        for product in products:

                            try:

                                detail_link = 'https://www.coupang.com' + product['href']
                                pr1nm = product['pr1nm']

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
                                # item['pr2nm'] = pr2nm
                                if (keyword == '네이쳐스탑') and ('오메가3' in pr1nm):
                                    item['pr2nm'] = '오메가3'

                                elif (keyword == '네이쳐스탑') and ('초록홍합' in pr1nm):
                                    item['pr2nm'] = '초록홍합'
                                
                                elif (keyword == '네이쳐스탑') and ('쏘팔메토' in pr1nm):
                                    item['pr2nm'] = '쏘팔메토'

                                elif (keyword == '노트북'):
                                    item['pr2nm'] = '노트북'

                                else:
                                    item['pr2nm'] = None

                                # 가격
                                try:

                                    noWowpr = page.locator('span.total-price > strong').first.inner_text(timeout=1000)

                                    if noWowpr == "원":

                                        wowpr = page.locator('tr.choose-item.one-time-li.price-type-item.selected > td.td-price > span.price').inner_text(timeout=1000)
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
                                    # logging.error('정가 selector 수정 필요')

                                # 검색 키워드
                                item['sk'] = keyword

                                # 브랜드
                                item['pr1br'] = pr1nm.split()[0]    # 제품명의 앞 한 단어(임시)

                                # SKU1, SKU2
                                try:
                                
                                    SKU = json.loads(page.locator('div.prod-ctl-or-fbt-recommend.impression-log').get_attribute('data-fodium-widget-params'))
                                    item['pr1id'] = SKU['productId']

                                    item['pr2id'] = SKU['itemId']

                                except PlaywrightTimeoutError as skuError:

                                    item['pr1id'] = None
                                    item['pr2id'] = None

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
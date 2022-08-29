
import asyncio
from curses import window
from email.policy import default
import time
from tkinter.messagebox import NO
import scrapy
import logging
from playwright.async_api import async_playwright
from mi.spiders.hiaas_common import HiaasCommon
from mi.items import HiLabMIItem
from scrapy.utils.project import get_project_settings
import time


class NaverCombineSpider(HiaasCommon):
    name = "naver_combine"
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader
    custom_settings = {
        'TWISTED_REACTOR' : "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        # 'ITEM_PIPELINES' : None    
    }

    marketType = "naver"
    
    async def parse(self, response):

        settings = get_project_settings()
        KEYWORD_LIST = settings.get('KEYWORD_LIST')
        NAVER_CRAWL_DELAY = settings.get('NAVER_CRAWL_DELAY')
        NAVER_LISTSIZE = settings.get('NAVER_LISTSIZE')
        NAVER_PAGE_COUNT = settings.get('NAVER_PAGE_COUNT')
        NAVER_SORTER = settings.get('NAVER_SORTER')
        NAVER_VIEW_TYPE = settings.get('NAVER_VIEW_TYPE')

        logging.log(logging.INFO, KEYWORD_LIST)


        async with async_playwright() as pw:
            browser = await pw.firefox.launch()
            page = await browser.new_page()
            
            for keyword in KEYWORD_LIST:
                for pagenum in range(1, NAVER_PAGE_COUNT+1):
                    logging.log(logging.INFO, "pagenum : %d", pagenum)
                    searchLink = f'https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery={keyword}&pagingIndex={pagenum}&pagingSize={NAVER_LISTSIZE}&productSet=total&query={keyword}&sort={NAVER_SORTER}&timestamp=&viewType={NAVER_VIEW_TYPE}'
                    await page.goto(searchLink)
                    await asyncio.sleep(NAVER_CRAWL_DELAY)
            
                    # scroll to bottom
                    for i in range(2): #make the range as long as needed
                        # page.mouse.wheel(0, 15000)
                        await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                        await asyncio.sleep(NAVER_CRAWL_DELAY)
                        i += 1
            
                    
                    # Get list of AD exclusion details
                    locators = page.locator('//li[@class="basicList_item__0T9JD"]//a[@class="thumbnail_thumb__Bxb6Z"]')
                    
                    # Get list of AD inclusion details
                    # AdLocator = page.locator('//li[@class="basicList_item__0T9JD ad"]//a[@class="thumbnail_thumb__Bxb6Z"]')
                    
                    locatorsCnt = await locators.count()
                    # AdLcatorsCnt = await AdLocator.count()
                    
                    # logging.log(logging.INFO, "nomal product list cnt = %d",locatorsCnt)
                    # logging.log(logging.INFO, "ad product list cnt = %d",AdLcatorsCnt)
                    
                    # 광고 제외 제품의 데이터 추출
                    for locatorIdx in range(locatorsCnt):
                        locator = locators.nth(locatorIdx)
                        
                        dataNclick = await locator.get_attribute('data-nclick')
                        # href = await locator.get_attribute('href')
                        
                        
                        try:
                            # 랭크 파싱
                            rankStr = dataNclick.split(',')[1]
                            rank = int(rankStr[rankStr.find('r:')+2:])
                            
                            # 상품번호 파싱
                            productNumStr = dataNclick.split(',')[2]
                            productNum = productNumStr[productNumStr.find('i:')+2:]
                            
                            # 상품상세 URL 파싱
                            defaultUrl = 'https://search.shopping.naver.com/catalog/' 
                            detailUrl = defaultUrl + productNum
                            
                        except Exception as e:
                            logging.log(logging.ERROR, e)
                    
                    
                        # logging.log(logging.INFO, "rank = %d",rank)
                        # logging.log(logging.INFO, "detailUrl = %s",detailUrl)
                
                
                        yield scrapy.Request(url=detailUrl,
                                            callback=self.parse_detail,
                                            meta=dict(
                                                searchKeyword = keyword,
                                                rank = rank,
                                                productNum = productNum,
                                                detail_link = detailUrl
                                            )
                        )
                
            await browser.close()
                
            

    def parse_detail(self, response):        

        try:
            item = HiLabMIItem()
            
            item['mid'] = self.marketType   # 마켓 타입 (ex. naver, coupang)

            item['ctype'] = 1   # collection type(1:키워드, 2:카테고리)
            
            item['detail_link'] = response.url  # 상세페이지 링크
            
            item['rank'] = response.meta.get('rank')    # 순위
            # logging.log(logging.INFO, "rank = %d", response.meta.get('rank'))
                            
            productName = response.xpath('//h2[@class="topInfo_title__nZW6V"]/text()').get()  # 제품명
            if productName is None:
                productName = ''
            item['pr1nm'] = productName                         
            # logging.log(logging.INFO, "productName = %s", item['pr1nm'])
            
            price = response.xpath('//div[@class="topInfo_price_area__vzPiB"]//em/text()').get()
            if price is None:
                price = 0
            else:
                int(price.replace(',', ''))
            item['pr1pr'] = price  # 가격
            # logging.log(logging.INFO, "price = %d", item['pr1pr'])
            
            score = response.xpath('//span[@class="topInfo_star__Cn7bg"]/text()').get() # 평점
            if score is None:
                score = 0
            item['gr'] = float(score)   # 평점
            # logging.log(logging.INFO, "socre = %f", item['gr'])
            
            reviewCnt = response.xpath('//span[@class="review_text__9ugPR"]//em/text()').get()  # 리뷰개수
            if reviewCnt is None:
                reviewCnt = 0                
            else:
                reviewCnt = int(reviewCnt.replace(',', ''))
            item['revco'] = reviewCnt  # 리뷰개수
            # logging.log(logging.INFO, "review cnt = %d", item['revco'])
            
            deliveryFlag = response.xpath('//span[@class="priceArea_delivery__eook3"]//text()').get()
            if deliveryFlag is None:
                deliveryFlag = False
            item['ts'] = bool(deliveryFlag)
            
            item['sk'] = response.meta.get('searchKeyword')  # 검색 키워드
            # logging.log(logging.INFO, "search word = %s", item['sk'])

            brand = response.xpath('//span[@class="priceArea_mall__aJXlO"]/text()').get()  # 브랜드
            if brand is None:
                brand = ''
            item['pr1br'] = brand
            # logging.log(logging.INFO, "brand = %s", item['pr1br'])

            yield item

        except Exception as e:
            logging.log(logging.ERROR, e)





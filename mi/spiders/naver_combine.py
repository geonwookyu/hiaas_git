
import asyncio
from curses import window
from email.policy import default
import json
import time
import scrapy
import logging
from time import sleep
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from mi.spiders.hiaas_common import HiaasCommon
from mi.items import HiLabMIItem
from mi.spiders.naver_login import NaverLogin
from scrapy.utils.project import get_project_settings
import time
import requests
from bs4 import BeautifulSoup as bs

# 0.1 버전에서 navershopping의 DATA 수집
# 추후 storefarm, 롯데몰, 쿠팡, ... 등 사이트 별 DATA 수집 방법 고려해보아함                     
                        

class NaverCombineSpider(HiaasCommon):
    name = "naver_combine"
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader
    # custom_settings = {
    #     'TWISTED_REACTOR' : "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    #     'RANDOM_UA_TYPE' : "chrome"         
    # }

    marketType = "naver"
    
    def parse(self, response):
        # headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}

        settings = get_project_settings()
        KEYWORD_LIST = settings.get('KEYWORD_LIST')
        NAVER_CRAWL_DELAY = settings.get('NAVER_CRAWL_DELAY')
        NAVER_LISTSIZE = settings.get('NAVER_LISTSIZE')
        NAVER_PAGE_COUNT = settings.get('NAVER_PAGE_COUNT')
        NAVER_SORTER = settings.get('NAVER_SORTER')
        NAVER_VIEW_TYPE = settings.get('NAVER_VIEW_TYPE')

        logging.log(logging.INFO, KEYWORD_LIST)
        
        with sync_playwright() as pw:
            
            self.browser = pw.firefox.launch()
            self.context = self.browser.new_context()
            page = self.context.new_page() 
            logging.log(logging.ERROR, "로그인.....")
            
            login = NaverLogin()
            login.setup(page)
            login.InputID()
            login.InputPasswd()
            login.ClickLogInBtn()
            sleep(NAVER_CRAWL_DELAY)
            logging.log(logging.ERROR, "로그인 완료.....")
            # page.screenshot(path='naverLoginPage2.png', full_page=True)
            
            cookies = self.context.cookies()
            
            for keyword in KEYWORD_LIST:
                logging.log(logging.ERROR, "keyword = %s", keyword)
                self.context = self.browser.new_context()
                for pagenum in range(1, NAVER_PAGE_COUNT+1):
                    
                    page = self.context.new_page()
                    self.context.add_cookies(cookies)
                    
                    searchLink = f'https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery={keyword}&pagingIndex={pagenum}&pagingSize={NAVER_LISTSIZE}&productSet=total&query={keyword}&sort={NAVER_SORTER}&timestamp=&viewType={NAVER_VIEW_TYPE}'
                    # logging.log(logging.ERROR, "test select = %s", searchLink)
                    
                    # 네이버 상품 목록 리스트의 데이터셋 파싱
                    try:                    
                        # rq = requests.get(searchLink)
                        page.goto(searchLink)
                        logging.log(logging.ERROR, "go page")
                        # page.screenshot(path='naverLoginPage3.png', full_page=True)
                        sleep(NAVER_CRAWL_DELAY)
                        
                        # soup = bs(rq.content, 'html.parser')
                        
                        # select = soup.select_one('script[id="__NEXT_DATA__"]')
                        select = page.locator('//*[@id="__NEXT_DATA__"]').inner_text()
                        logging.log(logging.ERROR, "get select")
                        
                        if select is None:
                            logging.log(logging.ERROR, "네이버 데이터셋 획득 실패")
                            return None
                        # attr = select.get_text()                    
                        attr = select
                        jsonFile = json.loads(attr)
                        productList = jsonFile['props']['pageProps']['initialState']['products']['list']
                        
                        with open('data3.json', 'w') as outfile:
                            json.dump(jsonFile, outfile)
                        
                        logging.log(logging.INFO, "productListCnt = %d", len(productList))
                        
                        for product in productList:
                            if product['item']['purchaseConditionInfos'] is None:
                                continue                        
                                
                            item = HiLabMIItem()
                            
                            item['mid'] = self.marketType   # 마켓타입
                            
                            item['ctype'] = 1   # collection 타입                                            
                            
                            rank = product['item']['rank']  # 제품순위
                            if rank is None:
                                rank = 0   
                            item['rank'] = rank                                                                
                            # logging.log(logging.INFO, "rank = %d", rank)
                            
                            category1 = product['item']['category1Name']    # 카테고리1
                            if category1 is None:
                                category1 = ''   
                            item['pr1ca'] = category1
                            # logging.log(logging.INFO, "category1 = %s", category1)
                            
                            category2 = product['item']['category2Name']    # 카테고리2
                            if category2 is None:
                                category2 = ''       
                            item['pr2ca'] = category2                                                
                            # logging.log(logging.INFO, "category2 = %s", category2)
                                            
                            category3 = product['item']['category3Name']    # 카테고리3
                            if category3 is None:
                                category3 = ''                            
                            item['pr3ca'] = category3                                 
                            # logging.log(logging.INFO, "category3 = %s", category3)
                                            
                            category4 = product['item']['category4Name']    # 카테고리4
                            if category4 is None:
                                category4 = ''                            
                            item['pr4ca'] = category4                                 
                            # logging.log(logging.INFO, "category4 = %s", category4)
                            
                            if NAVER_SORTER == 'rel':   # 정렬기준
                                sort = '랭킹'
                            else:
                                sort = ''
                            item['sb'] = sort 
                            
                            keepCnt = product['item']['keepCnt']    # 총 제품 수
                            if keepCnt is None:
                                keepCnt = 0              
                            item['prco'] = keepCnt                                          
                            # logging.log(logging.INFO, "keepCnt = %d", keepCnt)
                            
                            productName = product['item']['productName']    # 제품명
                            if productName is None:
                                productName = ''     
                            item['pr1nm'] = productName                                                    
                            # logging.log(logging.INFO, "productName = %s", productName)
                            
                            lowPrice = product['item']['lowPrice'] # 최저가격
                            if lowPrice is None:
                                lowPrice = 0
                            item['pr1pr'] = lowPrice
                            # logging.log(logging.INFO, "lowPrice = %d", lowPrice)                                                    
                            
                            scoreInfo = product['item']['scoreInfo']    # 평점
                            if scoreInfo is None:
                                scoreInfo = 0    
                            item['gr'] = scoreInfo
                            # logging.log(logging.INFO, "scoreInfo = %f", scoreInfo)
                                                    
                            reviewCount = product['item']['reviewCount']    # 리뷰 개수
                            if reviewCount is None:
                                reviewCount = 0               
                            item['revco'] = reviewCount
                            # logging.log(logging.INFO, "reviewCount = %d", reviewCount)
                            
                            # hasDeliveryFeeContent = product['item']['hasDeliveryFeeContent']    # 무료배송유무
                            # if hasDeliveryFeeContent is None:
                            #     hasDeliveryFeeContent = False
                            # else:
                            #     hasDeliveryFeeContent = True  
                            # item['ts'] = hasDeliveryFeeContent
                            item['ts'] = None
                            # logging.log(logging.INFO, "hasDeliveryFeeContent = %d", hasDeliveryFeeContent)
                                                
                            brand = reviewCount = product['item']['brand']  # 브랜드
                            if brand is None:
                                brand = ''
                            # logging.log(logging.INFO, "brand = %s", brand)  
                            item['pr1br'] = brand
                            
                            item['sk'] = keyword    # 검색키워드
                            
                            # sw add
                            crUrl = product['item']['crUrl']
                            if crUrl is None:
                                crUrl = ''
                            item['detail_link'] = crUrl
                            
                            mallName = product['item']['mallName']
                            if mallName == '':
                                mallName = product['item']['lowMallList'][0]['name']
                            item['ta'] = mallName
                            
                            product2Name = product['item']['productName'].replace(' ', '')    # 제품명
                            if keyword == KEYWORD_LIST[0]:
                                if ('오메가3' in product2Name) or ('오메가-3' in product2Name):
                                    pr2nm = '오메가3'
                                elif ('초록홍합' in product2Name) or ('초록입홍합' in product2Name):
                                    pr2nm = '초록홍합'
                                elif ('쏘팔메토' in product2Name) or ('소팔메토' in product2Name):
                                    pr2nm = '쏘팔메토'
                                else:
                                    pr2nm = None
                            elif keyword == KEYWORD_LIST[1]:           
                                if ('우머나이저' in product2Name and '리버티' in product2Name) or ('우머나이저' in product2Name and 'liberty' in product2Name) or ('womanizer' in product2Name and '리버티' in product2Name) or ('womanizer' in product2Name and 'liberty' in product2Name):
                                    pr2nm = '리버티'
                                elif ('우머나이저' in product2Name and '스탈렛' in product2Name) or ('우머나이저' in product2Name and 'starlet' in product2Name) or ('womanizer' in product2Name and '스탈렛' in product2Name) or ('womanizer' in product2Name and 'starlet' in product2Name):
                                    if ('스탈렛3' in product2Name) or ('starlet3' in product2Name):
                                        pr2nm = '스탈렛3'
                                    else: pr2nm = '스탈렛'
                                elif ('우머나이저' in product2Name and '듀오' in product2Name) or ('우머나이저' in product2Name and 'duo' in product2Name) or ('womanizer' in product2Name and '듀오' in product2Name) or ('womanizer' in product2Name and 'duo' in product2Name):
                                    pr2nm = '듀오'
                                elif ('우머나이저' in product2Name and '클래식' in product2Name) or ('우머나이저' in product2Name and 'classic' in product2Name) or ('womanizer' in product2Name and '클래식' in product2Name) or ('womanizer' in product2Name and 'classic' in product2Name):
                                    if ('클래식2' in product2Name) or ('classic2' in product2Name) or ('뉴클래식' in product2Name) or ('뉴classic' in product2Name) or ('new클래식' in product2Name) or ('newclassic' in product2Name):
                                        pr2nm = '클래식2'
                                    else: pr2nm = '클래식'
                                elif ('우머나이저' in product2Name and '프리미엄' in product2Name) or ('우머나이저' in product2Name and 'premium' in product2Name) or ('womanizer' in product2Name and '프리미엄' in product2Name) or ('womanizer' in product2Name and 'premium' in product2Name):
                                    if ('뉴프리미엄' in product2Name) or ('new프리미엄' in product2Name) or ('newpremium' in product2Name) or ('프리미엄2' in product2Name) or ('premium2' in product2Name):
                                        pr2nm = '프리미엄2'
                                    else: pr2nm = '프리미엄'
                                else:
                                    pr2nm = None
                            elif keyword == KEYWORD_LIST[2]:    
                                if ('퓨어젤' in product2Name and '비건' in product2Name) or ('퓨어젤' in product2Name and 'vegan' in product2Name):
                                    pr2nm = '퓨어 우먼 비건'
                                elif ('퓨어젤' in product2Name and '누드' in product2Name) or ('퓨어젤' in product2Name and 'nude' in product2Name):
                                    pr2nm = '퓨어 우먼 누드'
                                elif ('퓨어젤' in product2Name and '소프트' in product2Name) or ('퓨어젤' in product2Name and 'soft' in product2Name):
                                    pr2nm = '퓨어 우먼 소프트'
                                else:
                                    pr2nm = None    
                            elif keyword == KEYWORD_LIST[3]:        
                                if ('아크웨이브' in product2Name and '이온' in product2Name) or ('아크웨이브' in product2Name and 'ion' in product2Name) or ('arcwave' in product2Name and '이온' in product2Name) or ('arcwave' in product2Name and 'ion' in product2Name):
                                    pr2nm = '이온'
                                elif ('아크웨이브' in product2Name and '보이' in product2Name) or ('아크웨이브' in product2Name and 'voy' in product2Name) or ('arcwave' in product2Name and '보이' in product2Name) or ('arcwave' in product2Name and 'voy' in product2Name):
                                    pr2nm = '보이' 
                                else:
                                    pr2nm = None   
                            elif keyword == KEYWORD_LIST[4]:
                                if ('롬프' in product2Name and '비트' in product2Name) or ('롬프' in product2Name and 'beat' in product2Name) or ('romp' in product2Name and '비트' in product2Name) or ('romp' in product2Name and 'beat' in product2Name):
                                    pr2nm = '비트'
                                elif ('롬프' in product2Name and '스위치' in product2Name) or ('롬프' in product2Name and 'switch' in product2Name) or ('romp' in product2Name and '스위치' in product2Name) or ('romp' in product2Name and 'switch' in product2Name):
                                    pr2nm = '스위치'
                                elif ('롬프' in product2Name and '쥬크' in product2Name) or ('롬프' in product2Name and '주크' in product2Name) or ('롬프' in product2Name and 'juke' in product2Name) or ('romp' in product2Name and '쥬크' in product2Name) or ('romp' in product2Name and '주크' in product2Name) or ('romp' in product2Name and 'juke' in product2Name):
                                    pr2nm = '쥬크'
                                elif ('롬프' in product2Name and '프리' in product2Name) or ('롬프' in product2Name and 'free' in product2Name) or ('romp' in product2Name and '프리' in product2Name) or ('romp' in product2Name and 'free' in product2Name):
                                    pr2nm = '프리'
                                elif ('롬프' in product2Name and '웨이브' in product2Name) or ('롬프' in product2Name and 'wave' in product2Name) or ('romp' in product2Name and '웨이브' in product2Name) or ('romp' in product2Name and 'wave' in product2Name):
                                    pr2nm = '웨이브'
                                elif ('롬프' in product2Name and '재즈' in product2Name) or ('롬프' in product2Name and 'jazz' in product2Name) or ('romp' in product2Name and '재즈' in product2Name) or ('romp' in product2Name and 'jazz' in product2Name):
                                    pr2nm = '재즈'
                                elif ('롬프' in product2Name and '샤인' in product2Name) or ('롬프' in product2Name and 'shine' in product2Name) or ('romp' in product2Name and '샤인' in product2Name) or ('romp' in product2Name and 'shine' in product2Name):
                                    pr2nm = '샤인'
                                elif ('롬프' in product2Name and '하이프' in product2Name) or ('롬프' in product2Name and 'hype' in product2Name) or ('romp' in product2Name and '하이프' in product2Name) or ('romp' in product2Name and 'hype' in product2Name):
                                    pr2nm = '하이프'
                                elif ('롬프' in product2Name and '플립' in product2Name) or ('롬프' in product2Name and 'flip' in product2Name) or ('romp' in product2Name and '플립' in product2Name) or ('romp' in product2Name and 'flip' in product2Name):
                                    pr2nm = '플립'
                                else:
                                    pr2nm = None
                            elif keyword == KEYWORD_LIST[5]:
                                if ('위바이브' in product2Name and '디토' in product2Name) or ('위바이브' in product2Name and 'ditto' in product2Name) or ('wevibe' in product2Name and '디토' in product2Name) or ('wevibe' in product2Name and 'ditto' in product2Name) or ('we-vibe' in product2Name and '디토' in product2Name) or ('we-vibe' in product2Name and 'ditto' in product2Name):
                                    pr2nm = '디토'
                                elif ('위바이브' in product2Name and '멜트' in product2Name) or ('위바이브' in product2Name and 'melt' in product2Name) or ('wevibe' in product2Name and '멜트' in product2Name) or ('wevibe' in product2Name and 'melt' in product2Name) or ('we-vibe' in product2Name and '멜트' in product2Name) or ('we-vibe' in product2Name and 'melt' in product2Name):
                                    pr2nm = '멜트'
                                elif ('위바이브' in product2Name and '자이브' in product2Name) or ('위바이브' in product2Name and 'jive' in product2Name) or ('wevibe' in product2Name and '자이브' in product2Name) or ('wevibe' in product2Name and 'jive' in product2Name) or ('we-vibe' in product2Name and '자이브' in product2Name) or ('we-vibe' in product2Name and 'jive' in product2Name):
                                    pr2nm = '자이브'
                                elif ('위바이브' in product2Name and '노바2' in product2Name) or ('위바이브' in product2Name and 'nova2' in product2Name) or ('wevibe' in product2Name and '노바2' in product2Name) or ('wevibe' in product2Name and 'nova2' in product2Name) or ('we-vibe' in product2Name and '노바2' in product2Name) or ('we-vibe' in product2Name and 'nova2' in product2Name):
                                    pr2nm = '노바2'
                                elif ('위바이브' in product2Name and '본드' in product2Name) or ('위바이브' in product2Name and 'bond' in product2Name) or ('wevibe' in product2Name and '본드' in product2Name) or ('wevibe' in product2Name and 'bond' in product2Name) or ('we-vibe' in product2Name and '본드' in product2Name) or ('we-vibe' in product2Name and 'bond' in product2Name):
                                    pr2nm = '본드'
                                elif ('위바이브' in product2Name and '피봇' in product2Name) or ('위바이브' in product2Name and 'pivot' in product2Name) or ('wevibe' in product2Name and '피봇' in product2Name) or ('wevibe' in product2Name and 'pivot' in product2Name) or ('we-vibe' in product2Name and '피봇' in product2Name) or ('we-vibe' in product2Name and 'pivot' in product2Name):
                                    pr2nm = '피봇'
                                elif ('위바이브' in product2Name and '터치엑스' in product2Name) or ('위바이브' in product2Name and '터치x' in product2Name) or ('위바이브' in product2Name and 'touch엑스' in product2Name) or ('위바이브' in product2Name and 'touchx' in product2Name) or ('wevibe' in product2Name and '터치엑스' in product2Name) or ('wevibe' in product2Name and '터치x' in product2Name) or ('wevibe' in product2Name and 'touch엑스' in product2Name) or ('wevibe' in product2Name and 'touchx' in product2Name) or ('we-vibe' in product2Name and '터치엑스' in product2Name) or ('we-vibe' in product2Name and '터치x' in product2Name) or ('we-vibe' in product2Name and 'touch엑스' in product2Name) or ('we-vibe' in product2Name and 'touchx' in product2Name):
                                    pr2nm = '터치엑스'
                                elif ('위바이브' in product2Name and '탱고엑스' in product2Name) or ('위바이브' in product2Name and '탱고x' in product2Name) or ('위바이브' in product2Name and 'tango엑스' in product2Name) or ('위바이브' in product2Name and 'tangox' in product2Name) or ('wevibe' in product2Name and '탱고엑스' in product2Name) or ('wevibe' in product2Name and '탱고x' in product2Name) or ('wevibe' in product2Name and 'tango엑스' in product2Name) or ('wevibe' in product2Name and 'tangox' in product2Name) or ('we-vibe' in product2Name and '탱고엑스' in product2Name) or ('we-vibe' in product2Name and '탱고x' in product2Name) or ('we-vibe' in product2Name and 'tango엑스' in product2Name) or ('we-vibe' in product2Name and 'tangox' in product2Name):
                                    pr2nm = '탱고엑스'
                                elif ('위바이브' in product2Name and '스페셜에디션' in product2Name) or ('위바이브' in product2Name and '스페셜edition' in product2Name) or ('위바이브' in product2Name and 'special에디션' in product2Name) or ('위바이브' in product2Name and 'specialedition' in product2Name) or ('wevibe' in product2Name and '스페셜에디션' in product2Name) or ('wevibe' in product2Name and '스페셜edition' in product2Name) or ('wevibe' in product2Name and 'special에디션' in product2Name) or ('wevibe' in product2Name and 'specialedition' in product2Name) or ('we-vibe' in product2Name and '스페셜에디션' in product2Name) or ('we-vibe' in product2Name and '스페셜edition' in product2Name) or ('we-vibe' in product2Name and 'special에디션' in product2Name) or ('we-vibe' in product2Name and 'specialedition' in product2Name):
                                    pr2nm = '스페셜에디션'
                                elif ('위바이브' in product2Name and '벡터' in product2Name) or ('위바이브' in product2Name and 'vector' in product2Name) or ('wevibe' in product2Name and '벡터' in product2Name) or ('wevibe' in product2Name and 'vector' in product2Name) or ('we-vibe' in product2Name and '벡터' in product2Name) or ('we-vibe' in product2Name and 'vector' in product2Name):
                                    pr2nm = '벡터'
                                elif ('위바이브' in product2Name and '버지' in product2Name) or ('위바이브' in product2Name and 'verge' in product2Name) or ('wevibe' in product2Name and '버지' in product2Name) or ('wevibe' in product2Name and 'verge' in product2Name) or ('we-vibe' in product2Name and '버지' in product2Name) or ('we-vibe' in product2Name and 'verge' in product2Name):
                                    pr2nm = '버지'
                                elif ('위바이브' in product2Name and '목시' in product2Name) or ('위바이브' in product2Name and 'moxie' in product2Name) or ('wevibe' in product2Name and '목시' in product2Name) or ('wevibe' in product2Name and 'moxie' in product2Name) or ('we-vibe' in product2Name and '목시' in product2Name) or ('we-vibe' in product2Name and 'moxie' in product2Name):
                                    pr2nm = '목시'
                                else:
                                    pr2nm = None
                            else:
                                pr2nm = ''
                            
                            item['pr2nm'] = pr2nm
                            
                            yield item
                            
                    except Exception as e:
                        logging.log(logging.ERROR, e)
                    
                self.context.close()
            
            self.browser.close()
                    
                
                    
                


        # async with async_playwright() as pw:
        #     browser = await pw.firefox.launch()
        #     page = await browser.new_page()
            
        #     for keyword in KEYWORD_LIST:
        #         for pagenum in range(1, NAVER_PAGE_COUNT+1):
        #             searchLink = f'https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery={keyword}&pagingIndex={pagenum}&pagingSize={NAVER_LISTSIZE}&productSet=total&query={keyword}&sort={NAVER_SORTER}&timestamp=&viewType={NAVER_VIEW_TYPE}'
        #             await page.goto(searchLink)
        #             await asyncio.sleep(NAVER_CRAWL_DELAY)
        #             # await page.title()                    
            
        #             # scroll to bottom
        #             for i in range(2): #make the range as long as needed
        #                 # page.mouse.wheel(0, 15000)
        #                 await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        #                 await asyncio.sleep(1)
        #                 i += 1
            
                    
        #             # 광고를 제외한 제품 목록의 데이터를 파싱하기 위한 locator
        #             locators = page.locator('//li[@class="basicList_item__0T9JD"]')                                                            
        #             locatorsCnt = await locators.count()                    
        #             logging.log(logging.INFO, "list count = %d", locatorsCnt)
                
                
        #             # 광고 제외 제품의 데이터 추출
        #             for locatorIdx in range(locatorsCnt):
        #                 locator = locators.nth(locatorIdx)
        #                 dataNclick = await locator.locator('//div[@class="basicList_mall_title__FDXX5"]/a[@target="_blank"]').get_attribute('data-nclick')
                                                                                                                                                                                      
        #                 try:
        #                     # 랭크 파싱
        #                     rankStr = dataNclick.split(',')[2]                            
        #                     rankData = int(rankStr[rankStr.find('r:')+2:])
        #                     logging.log(logging.INFO, "rankData = %d", rankData)
                            
        #                     # 상품번호 파싱
        #                     productNumStr = dataNclick.split(',')[1]                            
        #                     productNum = productNumStr[productNumStr.find('i:')+2:]
        #                     logging.log(logging.INFO, "productNum = %s", productNum)
                            
        #                     # 쇼핑몰 URL 파싱
        #                     shoppingmallUrl = await locator.locator('//div[@class="basicList_mall_title__FDXX5"]/a[@target="_blank"]').get_attribute('href')                            
        #                     if "cr.shopping" in shoppingmallUrl:    # 네이버 쇼핑
        #                         defaultUrl = "https://search.shopping.naver.com/catalog/"
        #                         detailUrl = defaultUrl + productNum
        #                         yield scrapy.Request(url=detailUrl,
        #                                              callback=self.parse_pc_detail,
        #                                              meta=dict(searchKeyword = keyword,
        #                                                        rank = rankData,
        #                                                        productNum = productNum,
        #                                                        detail_link = detailUrl))
                                                                                                                                                                                           
        #                     elif "smartstore" in shoppingmallUrl:   # 네이버 스토어팜
        #                         detailUrl = await locator.locator('//div[@class="basicList_title__VfX3c"]/a[@class="basicList_link__JLQJf"]').get_attribute('href')
        #                         yield scrapy.Request(url=detailUrl,
        #                                              callback=self.parse_pc_detail,
        #                                              meta=dict(searchKeyword = keyword,
        #                                                        rank = rankData,
        #                                                        productNum = productNum,
        #                                                        detail_link = detailUrl))
                                                                                                                         
        #                     else: # 기타 사이트 -> 추후 고려
        #                         detailUrl = shoppingmallUrl
        #                         logging.log(logging.INFO, "해당 사이트는 네이버 쇼핑, 네이버 스토어팜이 아니라 skip")                                                
                                                                                                         
        #                 except Exception as e:
        #                     logging.log(logging.ERROR, e)
                                                        
        #     await browser.close()
                
    def parse_pc_detail(self, response):
        try:
            item = HiLabMIItem()

            # 마켓 타입 (ex. naver, coupang)
            item['mid'] = self.marketType 

            # collection type(1:키워드, 2:카테고리)
            item['ctype'] = 1
            
            # 상세페이지 링크
            item['detail_link'] = response.url
            logging.log(logging.INFO, "detailLink = %s", item['detail_link'])
            
            # 순위
            item['rank'] = response.meta.get('rank')
            logging.log(logging.INFO, "rank = %d", response.meta.get('rank'))
            
            # 제품명
            if "search" in response.url:
                productName = response.xpath('//div[@class="top_summary_title__ViyrM"]/h2/text()').get()
            elif "smartstore" in response.url:
                productName = response.xpath('//h3[@class="_3oDjSvLwq9 _copyable"]/text()').get()
            if productName is None:
                productName = ''
            item['pr1nm'] = productName                         
            logging.log(logging.INFO, "productName = %s", productName)      
            
            # 할인된 가격
            if "search" in response.url:
                price = response.xpath('//em[@class="lowestPrice_num__A5gM9"]/text()').get()
            elif "smartstore" in response.url:
                price = response.xpath('//strong[@class="aICRqgP9zw"]/span[@class="_1LY7DqCnwR"]/text()').get()
            if price is None:
                price = 0
            else:
                price = int(price.replace(',', ''))
            item['pr1pr'] = price
            logging.log(logging.INFO, "price = %d", price)
            
            # 평점
            if "search" in response.url:
                score = response.xpath('//div[@class="top_grade__bvwhB"]/text()').get()
            elif "smartstore" in response.url:
                score = response.xpath('//div[@class="_2Q0vrZJNK1"]/strong[@class="_2pgHN-ntx6"]/text()').get()            
            if score is None:
                score = 0
            item['gr'] = float(score)
            logging.log(logging.INFO, "socre = %f", item['gr'])
            
            # 리뷰개수
            reviewStr = ''         
            if "search" in response.url:
                reviewCntList = response.xpath('//div[@class="totalArea_total_count__kRjVM"]/div[@class="totalArea_value__VV7TJ"]/span/text()').getall()
                for str in reviewCntList:
                    reviewStr = reviewStr + str
                reviewCnt = reviewStr
            elif "smartstore" in response.url:
                reviewCnt = response.xpath('//div[@class="_2Q0vrZJNK1"]/a/strong[@class="_2pgHN-ntx6"]/text()').get()            
            if reviewCnt is None:
                reviewCnt = 0                
            else:
                reviewCnt = int(reviewCnt.replace(',', ''))       
            item['revco'] = reviewCnt
            logging.log(logging.INFO, "review cnt = %d", item['revco'])                                    
            
            
            # 무료배송유무
            if "search" in response.url:
                deliveryFlag = response.xpath('//div[@class="lowestPrice_delivery_price__BoLpP"][text()="무료배송"]/text()').get()
            elif "smartstore" in response.url:
                deliveryFlag = response.xpath('//span[@class="bd_ChMMo"][text()="무료배송"]/text()').get()
            if deliveryFlag == "무료배송":
                deliveryFlag = True
            else:
                deliveryFlag = False
            item['ts'] = deliveryFlag       
            
            # 검색 키워드
            item['sk'] = response.meta.get('searchKeyword') 
            logging.log(logging.INFO, "search word = %s", item['sk'])
            
            # 브랜드
            if "search" in response.url:
                brand = response.xpath('//span[text()="브랜드"]/em/text()').get()
            elif "smartstore" in response.url:
                brand = productName.split()[0]                      
            if brand is None:
                brand = ''
            item['pr1br'] = brand
            logging.log(logging.INFO, "brand = %s", item['pr1br'])

            yield item
            
        except Exception as e:
            logging.log(logging.ERROR, e)


    def parse_mobile_detail(self, response):        

        try:
            item = HiLabMIItem()
            
            item['mid'] = self.marketType   # 마켓 타입 (ex. naver, coupang)

            item['ctype'] = 1   # collection type(1:키워드, 2:카테고리)
            
            item['detail_link'] = response.url  # 상세페이지 링크
            logging.log(logging.INFO, "detailLink = %s", item['detail_link'])
            
            item['rank'] = response.meta.get('rank')    # 순위
            logging.log(logging.INFO, "rank = %d", response.meta.get('rank'))
                            
            productName = response.xpath('//h2[@class="topInfo_title__nZW6V"]/text()').get()  # 제품명
            if productName is None:
                productName = ''
            item['pr1nm'] = productName                         
            logging.log(logging.INFO, "productName = %s", productName)
            
            price = response.xpath('//div[@class="topInfo_price_area__vzPiB"]//em/text()').get()
            if price is None:
                price = 0
            else:
                price = int(price.replace(',', ''))
            item['pr1pr'] = price  # 가격
            logging.log(logging.INFO, "price = %d", price)
            
            score = response.xpath('//span[@class="topInfo_star__Cn7bg"]/text()').get() # 평점
            if score is None:
                score = 0
            item['gr'] = float(score)   # 평점
            logging.log(logging.INFO, "socre = %f", item['gr'])
            
            reviewCnt = response.xpath('//span[@class="review_text__9ugPR"]//em/text()').get()  # 리뷰개수
            if reviewCnt is None:
                reviewCnt = 0                
            else:
                reviewCnt = int(reviewCnt.replace(',', ''))
            item['revco'] = reviewCnt  # 리뷰개수
            logging.log(logging.INFO, "review cnt = %d", item['revco'])
            
            deliveryFlag = response.xpath('//span[@class="priceArea_delivery__eook3"]//text()').get()
            if deliveryFlag is None:
                deliveryFlag = False
            item['ts'] = bool(deliveryFlag) # 무료배송유무            
            
            item['sk'] = response.meta.get('searchKeyword')  # 검색 키워드
            logging.log(logging.INFO, "search word = %s", item['sk'])

            brand = response.xpath('//span[@class="priceArea_mall__aJXlO"]/text()').get()  # 브랜드
            if brand is None:
                brand = ''
            item['pr1br'] = brand
            logging.log(logging.INFO, "brand = %s", item['pr1br'])

            yield item

        except Exception as e:
            logging.log(logging.ERROR, e)





import json
import logging
import re
from unittest import expectedFailure
import scrapy
from time import sleep
from playwright.sync_api import sync_playwright
from mi.items import HiLabMIItem
from mi.spiders.hiaas_common import HiaasCommon
from scrapy.utils.project import get_project_settings
import requests
from bs4 import BeautifulSoup as bs

# image block
def route_intercept(route):
    if route.request.resource_type == "image":
        # print(f"Blocking the image request to: {route.request.url}")
        return route.fallback()

    return route.continue_()

# [수정항목 1] : class 명 작업 사이트에 맞게 변경.
class TimonCombineSpider(HiaasCommon): 
    # [수정항목 2] : scrapy crawl gmarket_combine 명령어에 필요한 spider명 설정. 
    name = "timon_combine" 
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader
 
    # [수정항목 3] : 작업 대상 쇼핑몰 이름 설정.
    marketType = "timon" 
    
    def parse(self, response):
        
        # [수정항목 4] : settings > local.py, dev.py 에 "GMARKET CONFIG" 설정. ( 각 쇼핑몰에 필요한 정보 입력 )
        settings = get_project_settings()
        TIMON_KEYWORD_LIST = settings.get('TIMON_KEYWORD_LIST')
        TIMON_CRAWL_DELAY = settings.get('TIMON_CRAWL_DELAY')
        TIMON_LISTSIZE = settings.get('TIMON_LISTSIZE')
        TIMON_PAGE_COUNT = settings.get('TIMON_PAGE_COUNT')
        TIMON_SORTER = settings.get('TIMON_SORTER')

        logging.log(logging.INFO, TIMON_KEYWORD_LIST)

        with sync_playwright() as pw:
            self.browser = pw.firefox.launch(proxy={
                "server": "per-context"
            })
            
            for keyword in TIMON_KEYWORD_LIST:

                self.context = self.browser.new_context(proxy={
                    'server': 'http://proxy.edgenet.site:7777',
                    'username': 'jhnam@hiaas.co.kr',
                    'password': 'hiaas12!@'
                })

                for pagenum in range(1, TIMON_PAGE_COUNT + 1):
                    page = self.context.new_page()            
                    
                    # [수정항목 5] : 작업 쇼핑몰 사이트 상품리스트 URL 설정.
                    search_link = f'https://search.tmon.co.kr/search/?keyword={keyword}&thr=hs&page={pagenum}'
                    page.route("**/*", route_intercept)
                    page.goto(search_link, timeout=0)
                    
                    sleep(TIMON_CRAWL_DELAY)
                    
                    # [수정항목 6] : 작업 쇼핑몰 사이트 상품리스트 메인 locator 설정.
                    locators = page.locator('//*[@id="content"]//*[@class="item"]')

                    count = locators.count()
                    logging.log(logging.INFO, "count = %d", count)
 
                    for i in range(count):
                        locator = locators.nth(i)
                        # [수정항목 7] : 서치 키워드 외 타 브랜드(회사명) 제외하기 위한 조건문.
                        tmp = locator.locator('//*[@class="tx"]').inner_text().lower().replace(' ', '')
                        print("상품명 (풀네임) : " + tmp)
                        if keyword == TIMON_KEYWORD_LIST[0]:
                            if ('우머나이저' in tmp) or ('womanizer' in tmp):
                                brandYn = True
                            else: brandYn = False
                        elif keyword == TIMON_KEYWORD_LIST[1]:
                            if ('퓨어젤' in tmp):
                                brandYn = True
                            else: brandYn = False
                        elif keyword == TIMON_KEYWORD_LIST[2]:
                            if ('아크웨이브' in tmp) or ('arcwave' in tmp):
                                brandYn = True
                            else: brandYn = False
                        elif keyword == TIMON_KEYWORD_LIST[3]:
                            if ('롬프' in tmp) or ('romp' in tmp):
                                brandYn = True
                            else: brandYn = False
                        elif keyword == TIMON_KEYWORD_LIST[4]:
                            if ('위바이브' in tmp) or ('wevibe' in tmp) or ('we-vibe' in tmp):
                                brandYn = True
                            else: brandYn = False
                        elif keyword == TIMON_KEYWORD_LIST[5]:
                            if ('네이쳐스탑' in tmp) or ('네이처스탑' in tmp) or ('naturestop' in tmp):
                                brandYn = True
                            else: brandYn = False
                            
                        else:   pass
                        
                        # [수정항목 8] : 서치 키워드(브랜드)명인 상품에 대한 정보 가져오기 위한 작업.
                        if brandYn:
                            # [수정항목 9] : 상품 랭킹 정보 crawling. - 티몬은 업체명이 안나옴   
                            # tmp_rank = int(locator.locator('//*[@class = "link__shop"]').get_attribute('data-montelena-tier_asn'))
                            # rank = tmp_rank
                            # logging.log(logging.INFO, "rank = %d", rank)
                            
                            # [수정항목 10] : 상품 상세페이지 URL정보 crawling. 
                            href = locator.locator('//*[@class="anchor"]').get_attribute('href')
                            detail_link = href
                            logging.log(logging.INFO, "href = %s", href)
                            
                            # 날짜
                            # now = datetime.datetime.now()
                            # today = now.strftime("%m월 %d일")
                            # print("날짜 : " + today)
                            
                            # [수정항목 11] : 상품 오픈마켓명 URL정보 crawling. 
                            market_name = self.marketType
                            # print("오픈마켓명 : " + market_name)
                            
                            # [수정항목 12] : 상품 판매자정보(사업자 명) 정보 crawling. 
                            # seller = locator.locator('//*[@class = "link__shop"]').get_attribute('title').replace(" 미니샵으로 이동합니다","").strip()
                            # print("판매자정보(사업자 명) : " + seller) 
                            
                            # [수정항목 13] : 상품번호 정보 crawling. 
                            # item_no = locator.locator('//*[@class = "link__shop"]').get_attribute('data-montelena-goodscode')
                            # logging.log(logging.INFO, "item_no = %s", item_no)

                            # [수정항목 14] : 상품명 (풀네임) 정보 crawling. 
                            title = locator.locator('//*[@class="tx"]').inner_text()
                            title_tmp = title.lower().replace(' ', '')
                            
                            # [수정항목 15] : 브랜드명 정보 crawling. : 각 회사의 상품브랜드를 세분화 하기 위한 조건문 
                            if keyword == TIMON_KEYWORD_LIST[0]:
                                if ('프리미엄에코' in title_tmp) or ('프리미엄eco' in title_tmp) or ('premium에코' in title_tmp) or ('premiumeco' in title_tmp) or ('w500' in title_tmp) or ('pro40' in title_tmp):    continue

                                if ('우머나이저' in title_tmp and '리버티' in title_tmp) or ('우머나이저' in title_tmp and 'liberty' in title_tmp) or ('womanizer' in title_tmp and '리버티' in title_tmp) or ('womanizer' in title_tmp and 'liberty' in title_tmp):
                                    pr2nm = '리버티'
                                elif ('우머나이저' in title_tmp and '스탈렛' in title_tmp) or ('우머나이저' in title_tmp and 'starlet' in title_tmp) or ('womanizer' in title_tmp and '스탈렛' in title_tmp) or ('womanizer' in title_tmp and 'starlet' in title_tmp):
                                    if ('스탈렛3' in title_tmp) or ('starlet3' in title_tmp):
                                        pr2nm = '스탈렛3'
                                    else: pr2nm = '스탈렛'
                                elif ('우머나이저' in title_tmp and '듀오' in title_tmp) or ('우머나이저' in title_tmp and 'duo' in title_tmp) or ('womanizer' in title_tmp and '듀오' in title_tmp) or ('womanizer' in title_tmp and 'duo' in title_tmp):
                                    pr2nm = '듀오'
                                elif ('우머나이저' in title_tmp and '클래식' in title_tmp) or ('우머나이저' in title_tmp and 'classic' in title_tmp) or ('womanizer' in title_tmp and '클래식' in title_tmp) or ('womanizer' in title_tmp and 'classic' in title_tmp):
                                    if ('클래식2' in title_tmp) or ('classic2' in title_tmp) or ('뉴클래식' in title_tmp) or ('뉴classic' in title_tmp) or ('new클래식' in title_tmp) or ('newclassic' in title_tmp):
                                        pr2nm = '클래식2'
                                    else: pr2nm = '클래식'
                                elif ('우머나이저' in title_tmp and '프리미엄' in title_tmp) or ('우머나이저' in title_tmp and 'premium' in title_tmp) or ('womanizer' in title_tmp and '프리미엄' in title_tmp) or ('womanizer' in title_tmp and 'premium' in title_tmp):
                                    if ('뉴프리미엄' in title_tmp) or ('new프리미엄' in title_tmp) or ('newpremium' in title_tmp) or ('프리미엄2' in title_tmp) or ('premium2' in title_tmp):
                                        pr2nm = '프리미엄2'
                                    else: pr2nm = '프리미엄'
                                else:   continue
                                
                            elif keyword == TIMON_KEYWORD_LIST[1]:
                                if ('퓨어젤' in title_tmp and '비건' in title_tmp) or ('퓨어젤' in title_tmp and 'vegan' in title_tmp):

                                    pr2nm = '퓨어 우먼 비건'

                                elif ('퓨어젤' in title_tmp and '누드' in title_tmp) or ('퓨어젤' in title_tmp and 'nude' in title_tmp):

                                    pr2nm = '퓨어 우먼 누드'

                                elif ('퓨어젤' in title_tmp and '소프트' in title_tmp) or ('퓨어젤' in title_tmp and 'soft' in title_tmp):

                                    pr2nm = '퓨어 우먼 소프트'

                                else:

                                    pr2nm = None
                            
                            elif keyword == TIMON_KEYWORD_LIST[2]:
                                if ('아크웨이브' in title_tmp and '이온' in title_tmp) or ('아크웨이브' in title_tmp and 'ion' in title_tmp) or ('arcwave' in title_tmp and '이온' in title_tmp) or ('arcwave' in title_tmp and 'ion' in title_tmp):

                                    pr2nm = '이온'

                                elif ('아크웨이브' in title_tmp and '보이' in title_tmp) or ('아크웨이브' in title_tmp and 'voy' in title_tmp) or ('arcwave' in title_tmp and '보이' in title_tmp) or ('arcwave' in title_tmp and 'voy' in title_tmp):

                                    pr2nm = '보이'

                                else:

                                    pr2nm = None

                            elif keyword == TIMON_KEYWORD_LIST[3]:
                                if ('롬프' in title_tmp and '비트' in title_tmp) or ('롬프' in title_tmp and 'beat' in title_tmp) or ('romp' in title_tmp and '비트' in title_tmp) or ('romp' in title_tmp and 'beat' in title_tmp):

                                    pr2nm = '비트'

                                elif ('롬프' in title_tmp and '스위치' in title_tmp) or ('롬프' in title_tmp and 'switch' in title_tmp) or ('romp' in title_tmp and '스위치' in title_tmp) or ('romp' in title_tmp and 'switch' in title_tmp):

                                    pr2nm = '스위치'

                                elif ('롬프' in title_tmp and '쥬크' in title_tmp) or ('롬프' in title_tmp and '주크' in title_tmp) or ('롬프' in title_tmp and 'juke' in title_tmp) or ('romp' in title_tmp and '쥬크' in title_tmp) or ('romp' in title_tmp and '주크' in title_tmp) or ('romp' in title_tmp and 'juke' in title_tmp):

                                    pr2nm = '쥬크'

                                elif ('롬프' in title_tmp and '프리' in title_tmp) or ('롬프' in title_tmp and 'free' in title_tmp) or ('romp' in title_tmp and '프리' in title_tmp) or ('romp' in title_tmp and 'free' in title_tmp):

                                    pr2nm = '프리'

                                elif ('롬프' in title_tmp and '웨이브' in title_tmp) or ('롬프' in title_tmp and 'wave' in title_tmp) or ('romp' in title_tmp and '웨이브' in title_tmp) or ('romp' in title_tmp and 'wave' in title_tmp):

                                    pr2nm = '웨이브'

                                elif ('롬프' in title_tmp and '재즈' in title_tmp) or ('롬프' in title_tmp and 'jazz' in title_tmp) or ('romp' in title_tmp and '재즈' in title_tmp) or ('romp' in title_tmp and 'jazz' in title_tmp):

                                    pr2nm = '재즈'

                                elif ('롬프' in title_tmp and '샤인' in title_tmp) or ('롬프' in title_tmp and 'shine' in title_tmp) or ('romp' in title_tmp and '샤인' in title_tmp) or ('romp' in title_tmp and 'shine' in title_tmp):

                                    pr2nm = '샤인'

                                elif ('롬프' in title_tmp and '하이프' in title_tmp) or ('롬프' in title_tmp and 'hype' in title_tmp) or ('romp' in title_tmp and '하이프' in title_tmp) or ('romp' in title_tmp and 'hype' in title_tmp):

                                    pr2nm = '하이프'

                                elif ('롬프' in title_tmp and '플립' in title_tmp) or ('롬프' in title_tmp and 'flip' in title_tmp) or ('romp' in title_tmp and '플립' in title_tmp) or ('romp' in title_tmp and 'flip' in title_tmp):

                                    pr2nm = '플립'

                                else:

                                    pr2nm = None

                            elif keyword == TIMON_KEYWORD_LIST[4]:
                                if ('위바이브' in title_tmp and '디토' in title_tmp) or ('위바이브' in title_tmp and 'ditto' in title_tmp) or ('wevibe' in title_tmp and '디토' in title_tmp) or ('wevibe' in title_tmp and 'ditto' in title_tmp) or ('we-vibe' in title_tmp and '디토' in title_tmp) or ('we-vibe' in title_tmp and 'ditto' in title_tmp):

                                    pr2nm = '디토'

                                elif ('위바이브' in title_tmp and '멜트' in title_tmp) or ('위바이브' in title_tmp and 'melt' in title_tmp) or ('wevibe' in title_tmp and '멜트' in title_tmp) or ('wevibe' in title_tmp and 'melt' in title_tmp) or ('we-vibe' in title_tmp and '멜트' in title_tmp) or ('we-vibe' in title_tmp and 'melt' in title_tmp):

                                    pr2nm = '멜트'

                                elif ('위바이브' in title_tmp and '자이브' in title_tmp) or ('위바이브' in title_tmp and 'jive' in title_tmp) or ('wevibe' in title_tmp and '자이브' in title_tmp) or ('wevibe' in title_tmp and 'jive' in title_tmp) or ('we-vibe' in title_tmp and '자이브' in title_tmp) or ('we-vibe' in title_tmp and 'jive' in title_tmp):

                                    pr2nm = '자이브'

                                elif ('위바이브' in title_tmp and '노바2' in title_tmp) or ('위바이브' in title_tmp and 'nova2' in title_tmp) or ('wevibe' in title_tmp and '노바2' in title_tmp) or ('wevibe' in title_tmp and 'nova2' in title_tmp) or ('we-vibe' in title_tmp and '노바2' in title_tmp) or ('we-vibe' in title_tmp and 'nova2' in title_tmp):

                                    pr2nm = '노바2'

                                elif ('위바이브' in title_tmp and '본드' in title_tmp) or ('위바이브' in title_tmp and 'bond' in title_tmp) or ('wevibe' in title_tmp and '본드' in title_tmp) or ('wevibe' in title_tmp and 'bond' in title_tmp) or ('we-vibe' in title_tmp and '본드' in title_tmp) or ('we-vibe' in title_tmp and 'bond' in title_tmp):

                                    pr2nm = '본드'

                                elif ('위바이브' in title_tmp and '피봇' in title_tmp) or ('위바이브' in title_tmp and 'pivot' in title_tmp) or ('wevibe' in title_tmp and '피봇' in title_tmp) or ('wevibe' in title_tmp and 'pivot' in title_tmp) or ('we-vibe' in title_tmp and '피봇' in title_tmp) or ('we-vibe' in title_tmp and 'pivot' in title_tmp):

                                    pr2nm = '피봇'

                                elif ('위바이브' in title_tmp and '터치엑스' in title_tmp) or ('위바이브' in title_tmp and '터치x' in title_tmp) or ('위바이브' in title_tmp and 'touch엑스' in title_tmp) or ('위바이브' in title_tmp and 'touchx' in title_tmp) or ('wevibe' in title_tmp and '터치엑스' in title_tmp) or ('wevibe' in title_tmp and '터치x' in title_tmp) or ('wevibe' in title_tmp and 'touch엑스' in title_tmp) or ('wevibe' in title_tmp and 'touchx' in title_tmp) or ('we-vibe' in title_tmp and '터치엑스' in title_tmp) or ('we-vibe' in title_tmp and '터치x' in title_tmp) or ('we-vibe' in title_tmp and 'touch엑스' in title_tmp) or ('we-vibe' in title_tmp and 'touchx' in title_tmp):

                                    pr2nm = '터치엑스'

                                elif ('위바이브' in title_tmp and '탱고엑스' in title_tmp) or ('위바이브' in title_tmp and '탱고x' in title_tmp) or ('위바이브' in title_tmp and 'tango엑스' in title_tmp) or ('위바이브' in title_tmp and 'tangox' in title_tmp) or ('wevibe' in title_tmp and '탱고엑스' in title_tmp) or ('wevibe' in title_tmp and '탱고x' in title_tmp) or ('wevibe' in title_tmp and 'tango엑스' in title_tmp) or ('wevibe' in title_tmp and 'tangox' in title_tmp) or ('we-vibe' in title_tmp and '탱고엑스' in title_tmp) or ('we-vibe' in title_tmp and '탱고x' in title_tmp) or ('we-vibe' in title_tmp and 'tango엑스' in title_tmp) or ('we-vibe' in title_tmp and 'tangox' in title_tmp):

                                    pr2nm = '탱고엑스'

                                elif ('위바이브' in title_tmp and '스페셜에디션' in title_tmp) or ('위바이브' in title_tmp and '스페셜edition' in title_tmp) or ('위바이브' in title_tmp and 'special에디션' in title_tmp) or ('위바이브' in title_tmp and 'specialedition' in title_tmp) or ('wevibe' in title_tmp and '스페셜에디션' in title_tmp) or ('wevibe' in title_tmp and '스페셜edition' in title_tmp) or ('wevibe' in title_tmp and 'special에디션' in title_tmp) or ('wevibe' in title_tmp and 'specialedition' in title_tmp) or ('we-vibe' in title_tmp and '스페셜에디션' in title_tmp) or ('we-vibe' in title_tmp and '스페셜edition' in title_tmp) or ('we-vibe' in title_tmp and 'special에디션' in title_tmp) or ('we-vibe' in title_tmp and 'specialedition' in title_tmp):

                                    pr2nm = '스페셜에디션'

                                elif ('위바이브' in title_tmp and '벡터' in title_tmp) or ('위바이브' in title_tmp and 'vector' in title_tmp) or ('wevibe' in title_tmp and '벡터' in title_tmp) or ('wevibe' in title_tmp and 'vector' in title_tmp) or ('we-vibe' in title_tmp and '벡터' in title_tmp) or ('we-vibe' in title_tmp and 'vector' in title_tmp):

                                    pr2nm = '벡터'

                                elif ('위바이브' in title_tmp and '버지' in title_tmp) or ('위바이브' in title_tmp and 'verge' in title_tmp) or ('wevibe' in title_tmp and '버지' in title_tmp) or ('wevibe' in title_tmp and 'verge' in title_tmp) or ('we-vibe' in title_tmp and '버지' in title_tmp) or ('we-vibe' in title_tmp and 'verge' in title_tmp):

                                    pr2nm = '버지'

                                elif ('위바이브' in title_tmp and '목시' in title_tmp) or ('위바이브' in title_tmp and 'moxie' in title_tmp) or ('wevibe' in title_tmp and '목시' in title_tmp) or ('wevibe' in title_tmp and 'moxie' in title_tmp) or ('we-vibe' in title_tmp and '목시' in title_tmp) or ('we-vibe' in title_tmp and 'moxie' in title_tmp):

                                    pr2nm = '목시'

                                else:

                                    pr2nm = None
                            
                            elif keyword == TIMON_KEYWORD_LIST[5]:
                            
                                if ('오메가3' in title_tmp):

                                    pr2nm = '오메가3'

                                elif ('초록홍합' in title_tmp) or ('초록입홍합' in title_tmp):

                                    pr2nm = '초록홍합'

                                elif ('쏘팔메토' in title_tmp) or ('소팔메토' in title_tmp):

                                    pr2nm = '쏘팔메토'

                                else:

                                    pr2nm = None
                            else:

                                pr2nm = None

                            brand = title.split()[0]


                            # [수정항목 16] : 상품 판매가(쿠폰 포함) 정보 crawling. 
                            price = int((locator.locator('//*[@class="sale"]//*[@class="num"]').inner_text()).replace(",","").strip())
                            # print("판매가(쿠폰 포함) : " + price)

                            # 이미지
                            # img = locator.locator('//*[@class="imgBox"]//img').get_attribute('src')
                            # print("이미지 : " + img)

                            # [수정항목 17] : 상품 할인된 가격 정보 crawling. 
                            if locator.locator('//*[@class="sale"]//*[@class="blind"]').inner_text() == "판매가:":
                                discount = price                                
                                # print("할인 없는 원가정보 : " + discount)
                            else:
                                discount = int((locator.locator('//*[@class="original"]//*[@class="num"]').inner_text()).replace(",","").strip())
                                # print("할인 있는 원가정보 : " + discount)


                            # 설정된 아이템 필드에 가져온 정보 넣기
                            item = HiLabMIItem()
                            item['mid'] = market_name   # 마켓타입

                            item['ctype'] = 1   # collection 타입

                            item['rank'] = None  # 제품순위

                            item['detail_link'] = detail_link   # 제품 상세페이지 링크

                            item['pr1id'] = None

                            item['pr1nm'] = title

                            item['pr2nm'] = pr2nm

                            item['pr1pr'] = price

                            item['fullpr'] = discount

                            item['ta'] = None

                            item['pr1br'] = brand

                            item['sk'] = keyword

                            yield item

                        else:   pass

                    page.close()
                
                self.context.close()

            self.browser.close()
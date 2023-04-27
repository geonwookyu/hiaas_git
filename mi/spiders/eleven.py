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


class ElevenCombineSpider(HiaasCommon):
    name = "eleven"
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader
    # custom_settings = {
    #     'TWISTED_REACTOR' : "twisted.internet.eactor.electorReactor",
    #     'RANDOM_UA_TYPE' : 'chrome'
    #     # 'ITEM_PIPELINES' : None    
    # }

    marketType = "eleven"
    
    def parse(self, response):

        settings = get_project_settings()
        ELEVEN_KEYWORD_LIST = settings.get('ELEVEN_KEYWORD_LIST')
        ELEVEN_CRAWL_DELAY = settings.get('ELEVEN_CRAWL_DELAY')
        ELEVEN_LISTSIZE = settings.get('ELEVEN_LISTSIZE')
        ELEVEN_PAGE_COUNT = settings.get('ELEVEN_PAGE_COUNT')
        ELEVEN_SORTER = settings.get('ELEVEN_SORTER')

        logging.log(logging.INFO, ELEVEN_KEYWORD_LIST)

        with sync_playwright() as pw:
            self.browser = pw.firefox.launch()
            page = self.browser.new_page()            
            
            for keyword in ELEVEN_KEYWORD_LIST:
                for pagenum in range(1, ELEVEN_PAGE_COUNT + 1):
                    search_link = f'https://search.11st.co.kr/Search.tmall?kwd={keyword}#pageNum%%{pagenum}%%'
                    page.goto(search_link)
                    
                    sleep(ELEVEN_CRAWL_DELAY)
                   
                    #locators = page.locator('//*[@id="section__inner-content-body-container"]//*[@class="box__component box__component-itemcard box__component-itemcard--general"]')
                    # locators = page.locator('//*[text()="일반상품"]/parent::div//ul[@id="normalList"]/li')
                    locators = page.locator('//*[@id="layBodyWrap"]//*[@class="l_content"]//*[@class="s_search s_search_main"]//*[@class="l_search_content"]//*[@data-component-name="list"]//*[@class="search_section"]//*[@class="c_listing c_listing_view_type_list"]//*["li"]//*[@class="c_card c_card_list"]')

                    count = locators.count()
                    logging.log(logging.INFO, "count = %d", count)
 
                    for i in range(count):
                        locator = locators.nth(i)
                        tmp = locator.locator('//*[@class="text__item"]').inner_text().lower().replace(' ', '')
                        print("상품명 (풀네임) : " + tmp)
                        if keyword == ELEVEN_KEYWORD_LIST[0]:
                            if ('우머나이저' in tmp) or ('womanizer' in tmp):
                                brandYn = True
                            else: brandYn = False
                        elif keyword == ELEVEN_KEYWORD_LIST[1]:
                            if ('퓨어젤' in tmp):
                                brandYn = True
                            else: brandYn = False
                        elif keyword == ELEVEN_KEYWORD_LIST[2]:
                            if ('아크웨이브' in tmp) or ('arcwave' in tmp):
                                brandYn = True
                            else: brandYn = False
                        elif keyword == ELEVEN_KEYWORD_LIST[3]:
                            if ('롬프' in tmp) or ('romp' in tmp):
                                brandYn = True
                            else: brandYn = False
                        elif keyword == ELEVEN_KEYWORD_LIST[4]:
                            if ('위바이브' in tmp) or ('wevibe' in tmp) or ('we-vibe' in tmp):
                                brandYn = True
                            else: brandYn = False
                        elif keyword == ELEVEN_KEYWORD_LIST[5]:
                            if ('네이쳐스탑' in tmp) or ('네이처스탑' in tmp) or ('naturestop' in tmp):
                                brandYn = True
                            else: brandYn = False
                            
                        else:   pass
                        
                        if brandYn:
                               
                            tmp_rank = int(locator.locator('//*[@class = "link__shop"]').get_attribute('data-montelena-tier_asn'))
                            rank = tmp_rank
                            logging.log(logging.INFO, "rank = %d", rank)

                            href = locator.locator('//*[@class="link__item"]').get_attribute('href')
                            logging.log(logging.INFO, "href = %s", href)
                            
                            detail_link = href
                            
                            # 날짜
                            # now = datetime.datetime.now()
                            # today = now.strftime("%m월 %d일")
                            # print("날짜 : " + today)
                            # 오픈마켓명
                            market_name = self.marketType
                            # print("오픈마켓명 : " + market_name)
                            # 판매자정보(사업자 명)
                            
                            seller = locator.locator('//*[@class = "link__shop"]').get_attribute('title').replace(" 미니샵으로 이동합니다","").strip()
                            # print("판매자정보(사업자 명) : " + seller) 
                            # 상품번호 
                            item_no = locator.locator('//*[@class = "link__shop"]').get_attribute('data-montelena-goodscode')
                            logging.log(logging.INFO, "item_no = %s", item_no)

                            # 상품명 (풀네임)
                            title = locator.locator('//*[@class="text__item"]').inner_text()
                            title_tmp = title.lower().replace(' ', '')
                            
                            # 브랜드명
                            if keyword == ELEVEN_KEYWORD_LIST[0]:
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
                                
                            elif keyword == ELEVEN_KEYWORD_LIST[1]:
                                if ('퓨어젤' in title_tmp and '비건' in title_tmp) or ('퓨어젤' in title_tmp and 'vegan' in title_tmp):

                                    pr2nm = '퓨어 우먼 비건'

                                elif ('퓨어젤' in title_tmp and '누드' in title_tmp) or ('퓨어젤' in title_tmp and 'nude' in title_tmp):

                                    pr2nm = '퓨어 우먼 누드'

                                elif ('퓨어젤' in title_tmp and '소프트' in title_tmp) or ('퓨어젤' in title_tmp and 'soft' in title_tmp):

                                    pr2nm = '퓨어 우먼 소프트'

                                else:

                                    pr2nm = None
                            
                            elif keyword == ELEVEN_KEYWORD_LIST[2]:
                                if ('아크웨이브' in title_tmp and '이온' in title_tmp) or ('아크웨이브' in title_tmp and 'ion' in title_tmp) or ('arcwave' in title_tmp and '이온' in title_tmp) or ('arcwave' in title_tmp and 'ion' in title_tmp):

                                    pr2nm = '이온'

                                elif ('아크웨이브' in title_tmp and '보이' in title_tmp) or ('아크웨이브' in title_tmp and 'voy' in title_tmp) or ('arcwave' in title_tmp and '보이' in title_tmp) or ('arcwave' in title_tmp and 'voy' in title_tmp):

                                    pr2nm = '보이'

                                else:

                                    pr2nm = None

                            elif keyword == ELEVEN_KEYWORD_LIST[3]:
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

                            elif keyword == ELEVEN_KEYWORD_LIST[4]:
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
                            
                            elif keyword == ELEVEN_KEYWORD_LIST[5]:
                            
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

                            # URL

                            # 판매가(쿠폰 포함)
                            price = int((locator.locator('//*[@class="box__price-seller"]//*[@class="text text__value"]').inner_text()).replace(",","").strip())
                            # print("판매가(쿠폰 포함) : " + price)

                            # 이미지
                            # img = locator.locator('//*[@class="imgBox"]//img').get_attribute('src')
                            # print("이미지 : " + img)

                            # 가격할인정보
                            if locator.locator('//*[@class="box__price-seller"]//*[@class="for-a11y"]').inner_text() == "상품금액":
                                discount = price
                                # print("할인 없는 원가정보 : " + discount)
                            else:
                                discount = int((locator.locator('//*[@class="box__price-original"]//*[@class="text text__value"]').inner_text()).replace(",","").strip())
                                # print("할인 있는 원가정보 : " + discount)

                            # # logging.log(logging.INFO, href)
                            # # if 'sourceType=srp_product_ads' in href:
                            # #     ad = 'ad'
                            # # else:
                            # #     ad = None

                            item = HiLabMIItem()
                            item['mid'] = market_name   # 마켓타입

                            item['ctype'] = 1   # collection 타입

                            item['rank'] = rank  # 제품순위

                            item['detail_link'] = detail_link   # 제품 상세페이지 링크

                            item['pr1id'] = item_no

                            item['pr1nm'] = title

                            item['pr2nm'] = pr2nm

                            item['pr1pr'] = price

                            item['fullpr'] = discount

                            item['ta'] = seller

                            item['pr1br'] = brand

                            item['sk'] = keyword

                            yield item


                            
                            # yield scrapy.Request(url=detail_link, 
                            #                      callback=self.parse_detail, 
                            #                      meta=dict(
                            #                         sk = keyword,
                            #                         rank = rank
                            #                      )
                            # )

                        else:   pass

            self.browser.close()

    def parse_detail(self, response):
        pass
           
         
    

        # try:
        #     item = HiLabMIItem()
            
        #     item['mid'] = self.marketType   # 마켓 타입 (ex. naver, coupang, interpark)

        #     item['ctype'] = 1   # collection type(1:키워드, 2:카테고리)
            
        #     item['detail_link'] = response.url  # 상세페이지 링크
            
        #     item['rank'] = response.meta.get('rank')     # 순위
            # logging.log(logging.INFO, "rank = %d", response.meta.get('rank'))
                           
            # response.xpath('//*[@id="productWrapper"]/div[1]/div/ul/li[1]/a/text()').get() //////카테고리 1

            # response.xpath('//*[@id="productWrapper"]/div[1]/div/ul/li[2]/a/text()').get() //카테고리 2

            # response.xpath('//*[@id="productWrapper"]/div[1]/div/ul/li[3]/a/text()').get() //카테고리 3

            # yield item

        # except Exception as e:
        #     logging.log(logging.ERROR, e)

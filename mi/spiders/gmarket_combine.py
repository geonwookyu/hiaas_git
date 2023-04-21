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


class GmarketCombineSpider(HiaasCommon):
    name = "gmarket_combine"
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader
    # custom_settings = {
    #     'TWISTED_REACTOR' : "twisted.internet.eactor.electorReactor",
    #     'RANDOM_UA_TYPE' : 'chrome'
    #     # 'ITEM_PIPELINES' : None    
    # }

    marketType = "gmarket"
    
    def parse(self, response):

        settings = get_project_settings()
        GMARKET_KEYWORD_LIST = settings.get('GMARKET_KEYWORD_LIST')
        GMARKET_CRAWL_DELAY = settings.get('GMARKET_CRAWL_DELAY')
        GMARKET_LISTSIZE = settings.get('GMARKET_LISTSIZE')
        GMARKET_PAGE_COUNT = settings.get('GMARKET_PAGE_COUNT')
        GMARKET_SORTER = settings.get('GMARKET_SORTER')

        logging.log(logging.INFO, GMARKET_KEYWORD_LIST)

        with sync_playwright() as pw:
            self.browser = pw.firefox.launch()
            page = self.browser.new_page()            
            
            for keyword in GMARKET_KEYWORD_LIST:
                for pagenum in range(1, GMARKET_PAGE_COUNT + 1):
                    search_link = f'https://browse.gmarket.co.kr/search?keyword={keyword}&s=8&k=0&p={pagenum}'
                    page.goto(search_link)
                    
                    sleep(GMARKET_CRAWL_DELAY)
                   
                    locators = page.locator('//*[@id="section__inner-content-body-container"]//*[@class="box__component box__component-itemcard box__component-itemcard--general"]')
                    # locators = page.locator('//*[text()="일반상품"]/parent::div//ul[@id="normalList"]/li')

                    count = locators.count()
                    logging.log(logging.INFO, "count = %d", count)
 
                    for i in range(count):
                        locator = locators.nth(i)
                        tmp = locator.locator('//*[@class="text__item"]').inner_text().lower().replace(' ', '')
                        print("상품명 (풀네임) : " + tmp)
                        if keyword == GMARKET_KEYWORD_LIST[0]:
                            if ('네이쳐스탑' in tmp) or ('네이처스탑' in tmp) or ('naturestop' in tmp):
                                brandYn = True
                            else: brandYn = False
                        elif keyword == GMARKET_KEYWORD_LIST[1]:
                            if ('노트북' in tmp):
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
                            
                            if keyword == GMARKET_KEYWORD_LIST[0]:
                            
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

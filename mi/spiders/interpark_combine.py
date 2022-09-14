import json
import logging
import re
from unittest import expectedFailure
import scrapy
import asyncio
import datetime
from playwright.async_api import async_playwright
from mi.items import HiLabMIItem
from mi.spiders.hiaas_common import HiaasCommon
from scrapy.utils.project import get_project_settings
import requests
from bs4 import BeautifulSoup as bs


class InterparkCombineSpider(HiaasCommon):
    name = "interpark_combine"
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader
    custom_settings = {
        'TWISTED_REACTOR' : "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        'RANDOM_UA_TYPE' : 'chrome'
        # 'ITEM_PIPELINES' : None    
    }

    marketType = "interpark"
    
    async def parse(self, response):

        settings = get_project_settings()
        INTERPARK_KEYWORD_LIST = settings.get('INTERPARK_KEYWORD_LIST')
        INTERPARK_CRAWL_DELAY = settings.get('INTERPARK_CRAWL_DELAY')
        INTERPARKISTSIZE = settings.get('INTERPARK_LISTSIZE')
        INTERPARK_PAGE_COUNT = settings.get('INTERPARK_PAGE_COUNT')
        INTERPARK_SORTER = settings.get('INTERPARK_SORTER')

        logging.log(logging.INFO, INTERPARK_KEYWORD_LIST)

        async with async_playwright() as pw:
            browser = await pw.firefox.launch()
            page = await browser.new_page()

            # await page.goto('https://shopping.interpark.com/product/productInfo.do?prdNo=6173396273&dispNo=008001083&smid1=common_prd')

            # await asyncio.sleep(INTERPARK_CRAWL_DELAY)
            # title = await page.locator('//*[@id="productName"]/span[2]').nth(0).inner_text()
            # title2 = await page.locator('//*[@id="priceWrap"]/div[2]/span[1]/em').nth(0).inner_text()

            # print(title)    
            # print(title2)


            
            
            for keyword in INTERPARK_KEYWORD_LIST:
                for pagenum in range(1, INTERPARK_PAGE_COUNT + 1):
                    search_link = f'https://shopping.interpark.com/shopSearch.do?page={pagenum}&sort={INTERPARK_SORTER}&q={keyword}&rows={INTERPARKISTSIZE}&'
                    await page.goto(search_link)
                    await asyncio.sleep(INTERPARK_CRAWL_DELAY)

                    # locators = page.locator('//*[@id="normalList"]//*[@class="info"]//*[@class="name"]')
                    # locators = page.locator('//div[@class="searchList"]//*[@id="normalList"]/li[@class="goods"]')
                    locators = page.locator('//*[text()="일반상품"]/parent::div//ul[@id="normalList"]/li')
                                        
                    count = await locators.count()
                    logging.log(logging.INFO, "count = %d", count)

                    if pagenum == 1 :
                        end_ad_rank = int(await locators.nth(0).get_attribute('data-srch-list-order')) - 1
                    logging.log(logging.INFO, "end_ad_rank = %d", end_ad_rank)

                    for i in range(count):
                        locator = locators.nth(i)     
                        tmp_rank = int(await locator.get_attribute('data-srch-list-order'))                     
                        rank = tmp_rank - end_ad_rank
                        logging.log(logging.INFO, "rank = %d", rank)

                        href = await locator.locator('//a[@class="name"]').get_attribute('href')
                        logging.log(logging.INFO, "href = %s", href)
                        
                        detail_link = href
                        
                        # 날짜
                        now = datetime.datetime.now()
                        today = now.strftime("%m월 %d일")
                        # print("날짜 : " + today)
                        # 오픈마켓명
                        market_name = self.marketType
                        # print("오픈마켓명 : " + market_name)
                        # 판매자정보(사업자 명)
                        seller = await locator.locator('//*[@class="cname"]').inner_text()
                        # print("판매자정보(사업자 명) : " + seller) 
                        # 상품명 (풀네임)
                        title = await locator.locator('//*[@class="name"]').inner_text()
                        # print("상품명 (풀네임) : " + title) 
                        # 브랜드명
                        # brand = "우머나이저" in title
                        # if brand:
                        #     brand = "우머나이저"
                        #     logging.log(logging.INFO, "브랜드명 = %s", brand)                            
                        # else:
                        #     brand = ""
                        #     logging.log(logging.INFO, "브랜드명 = ")
                        brand = title.split()[0]

                        # URL

                        # 판매가(쿠폰 포함)
                        price = int((await locator.locator('//*[@class="number"]').inner_text()).replace(",","").strip())
                        # print("판매가(쿠폰 포함) : " + price)

                        # 이미지
                        img = await locator.locator('//*[@class="imgBox"]//img').get_attribute('src')
                        # print("이미지 : " + img)

                        # 가격할인정보
                        if await locator.locator('//*[@class="sale"]').inner_text() == "":
                            discount = price
                            # print("할인 없는 원가정보 : " + discount) 
                        else:
                            discount = await locator.locator('//*[@class="under"]').inner_text()
                            discount = int(discount.replace("원가", "").replace(",", "").strip())
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

                        item['pr1nm'] = title

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
            await browser.close()
        
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
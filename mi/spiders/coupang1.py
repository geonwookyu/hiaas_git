# from ast import keyword
# import logging
import asyncio
from time import sleep
import scrapy
from playwright.async_api import async_playwright
from mi.settings import COUPANG_CRAWL_DELAY, COUPANG_KEYWORD, COUPANG_LISTSIZE, COUPANG_PAGE_COUNT, COUPANG_SORTER
# from playwright_stealth import stealth_async

class PlaywrightSpider(scrapy.Spider):
    name = "coupang1"
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader
    custom_settings = {
        'USER_AGENT' : None,
        'TWISTED_REACTOR' : "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        'ITEM_PIPELINES' : None    
    }
    
    async def parse(self, response):
        async with async_playwright() as pw:
            browser = await pw.firefox.launch()
            page = await browser.new_page()
            
            # serch_link = "https://www.coupang.com/np/search?rocketAll=false&q={keyword}&brand=&offerCondition=&filter=&availableDeliveryFilter=&filterType=&isPriceRange=false&priceRange=&minPrice=&maxPrice=&page={pagenum}&trcid=&traid=&filterSetByUser=true&channel=recent&backgroundColor=&searchProductCount=1857217&component=&rating=0&sorter={sorter}&listSize={listSize}"
            for pagenum in range(1, COUPANG_PAGE_COUNT):
                search_link = f'https://www.coupang.com/np/search?rocketAll=false&q={COUPANG_KEYWORD}&brand=&offerCondition=&filter=&availableDeliveryFilter=&filterType=&isPriceRange=false&priceRange=&minPrice=&maxPrice=&page={pagenum}&trcid=&traid=&filterSetByUser=true&channel=recent&backgroundColor=&searchProductCount=1857217&component=&rating=0&sorter={COUPANG_SORTER}&listSize={COUPANG_LISTSIZE}'
                # logging.error(f'search_link = {search_link}')
                await page.goto(search_link)
                # title = await page.title()
                await asyncio.sleep(COUPANG_CRAWL_DELAY)

                locators = page.locator('ul.search-product-list> li > a.search-product-link')
                count = await locators.count()
                # logging.error(f'count = {count}')
                for i in range(count):
                    locator = locators.nth(i)
                    href = await locator.get_attribute('href')
                    detail_link = 'https://www.coupang.com' + href
                    # logging.error(f'href = {href}')
                    # logging.error(f'detail_link = {detail_link}')
                    yield {'detail_link': detail_link}
            await browser.close()
            # await asyncio.sleep(COUPANG_CRAWL_DELAY)
            # await page.screenshot(path='./chrome_headless_stealth.png', full_page=True)
    
    # async def parse_detail(self, response):
    #     page = response.meta["playwright_page"]
    #     title = await page.title()
    #     logging.error(f'url = {response.url}')

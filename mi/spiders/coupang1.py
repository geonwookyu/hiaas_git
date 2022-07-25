import asyncio
from time import sleep
import scrapy
from playwright.async_api import async_playwright
# from mi.settings import COUPANG_CRAWL_DELAY, COUPANG_LISTSIZE, COUPANG_PAGE_COUNT, COUPANG_SORTER, KEYWORD_LIST
from mi.spiders.hiaas_common import HiaasCommon
from scrapy.utils.project import get_project_settings

class PlaywrightSpider(HiaasCommon):
    name = "coupang1"
    start_urls = ["data:,"]  # avoid using the default Scrapy downloader
    custom_settings = {
        'USER_AGENT' : None,
        'TWISTED_REACTOR' : "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        'ITEM_PIPELINES' : None    
    }
    
    async def parse(self, response):

        settings = get_project_settings()
        KEYWORD_LIST = settings.get('KEYWORD_LIST')
        COUPANG_CRAWL_DELAY = settings.get('COUPANG_CRAWL_DELAY')
        COUPANG_LISTSIZE = settings.get('COUPANG_LISTSIZE')
        COUPANG_PAGE_COUNT = settings.get('COUPANG_PAGE_COUNT')
        COUPANG_SORTER = settings.get('COUPANG_SORTER')

        async with async_playwright() as pw:
            browser = await pw.firefox.launch()
            page = await browser.new_page()
            
            for keyword in KEYWORD_LIST:
                for pagenum in range(1, COUPANG_PAGE_COUNT):
                    search_link = f'https://www.coupang.com/np/search?rocketAll=false&q={keyword}&brand=&offerCondition=&filter=&availableDeliveryFilter=&filterType=&isPriceRange=false&priceRange=&minPrice=&maxPrice=&page={pagenum}&trcid=&traid=&filterSetByUser=true&channel=recent&backgroundColor=&searchProductCount=1857217&component=&rating=0&sorter={COUPANG_SORTER}&listSize={COUPANG_LISTSIZE}'
                    await page.goto(search_link)
                    await asyncio.sleep(COUPANG_CRAWL_DELAY)

                    locators = page.locator('ul.search-product-list> li > a.search-product-link')
                    count = await locators.count()
                    for i in range(count):
                        locator = locators.nth(i)
                        href = await locator.get_attribute('href')
                        detail_link = 'https://www.coupang.com' + href
                        if 'sourceType=srp_product_ads' in href:
                            ad = 'ad'
                        else:
                            ad = None
                        yield {'detail_link': detail_link, 
                        'ad': ad,
                        'sk': keyword}
            await browser.close()

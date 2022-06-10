# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import scrapy
from time import sleep
from requests import request
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.utils.python import to_bytes
# useful for handling different item types with a single interface
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from itemadapter import is_item, ItemAdapter

class MiSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SelenuimMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_opened(self, spider):
        print('-------------------------------------------미들웨어 시작-------------------------------------')
        spider.logger.info('Spider opened: %s' % spider.name)

        CHROMEDRIVER_PATH = 'C:\WorkSpace\MarketInsight\mi_collector\mi\chromedriver.exe'
        WINDOW_SIZE = "1920,1080"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={WINDOW_SIZE}")
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,chrome_options = chrome_options)
        self.driver = driver
        
        print('-------------------------------------------미들웨어 끝-------------------------------------')

    def spider_closed(self, spider):
            print('------------------------------------------스파이더 종료--------------------------------------')
            self.driver.close()


    def process_request(self, request, spider):
        print('-------------------------------------------프로세스 리퀘스트 시작-------------------------------------')
        self.driver.get(request.url)
        scroll_location = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            print('--------------------------------스크롤링...----------------------------')
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            sleep(1)
            
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            print('----------------------------'+str(scroll_height)+"높이")
            print('----------------------------'+str(scroll_location)+"현재")
            if scroll_location == scroll_height:
                break

            else:
                scroll_location = self.driver.execute_script("return document.body.scrollHeight")

        sleep(1)
        #self.driver.get('https://search.shopping.naver.com/search/all?query=TV&frm=NVSHATC&prevQuery=TV')
        body = to_bytes(text=self.driver.page_source)
        print('--------------------------------')
        #print(body)
        print('-------------------------------------------프로세스 리퀘스트 끝-------------------------------------')
        return HtmlResponse(url=request.url, body=body, encoding='utf-8', request=request)

    def process_response(self, request, response, spider):
        print('-------------------------------------------프로세스 리턴--------------------------------')
        return response
        
    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        print('-------------------------------------------스타트 리퀘스트 시작-------------------------------------')
       
        for r in start_requests:
            yield r
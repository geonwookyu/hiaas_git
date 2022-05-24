import scrapy

class CoupangSpider(scrapy.Spider):
    name = "coupang"

    def start_requests(self):

        urls=[]
        for i in range(1,14):
            url_page = 'https://www.coupang.com/np/search?q=tv&channel=user&component=&eventCategory=SRP&trcid=&traid=&sorter=scoreDesc&minPrice=&maxPrice=&priceRange=&filterType=&listSize=72&filter=&isPriceRange=false&brand=&offerCondition=&rating=0&page='+str(i)+'&rocketAll=false&searchIndexingToken=&backgroundColor='
                
            urls.append(url_page)
        #User-Agent값으로 유저 정보 입력 
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}

        for url in urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response):
        try :

            item = {}
            coupang_sels = response.css('li.search-product')
            #print(coupang_sels)
            for coupang_sel in coupang_sels:
                # 링크 attr(href)
                item['link'] = 'https://www.coupang.com/' + response.css('li.search-product > a').attrib['href']
                # 상품이름
                item['product'] = coupang_sel.css('.name::text').get()
                # 상품가격
                item['price'] = coupang_sel.css('.price-value::text').get()
                yield item
        except Exception as e:
            print('e: ', e)
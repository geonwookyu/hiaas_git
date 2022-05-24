import scrapy

class Naverspider(scrapy.Spider):
    name = "naver"

    def start_requests(self):
        urls = [
            "https://search.shopping.naver.com/search/all?query=TV&frm=NVSHATC&prevQuery=TV",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        try:
            item = {}
            naver_sels = response.css('li.basicList_item__2XT81')
            #print(naver_sels)
            for naver_sel in naver_sels:
                #item['title'] = naver_sel.css('.basicList_link__1MaTN ::text').get()
                #item['title'] = naver_sel.css('.basicList_title__3P9Q7 > a ::text').get() # 75UP8300ENA
                item['title'] = naver_sel.css('.basicList_title__3P9Q7 > a ::text').get() # 75UP8300ENA 
                item['product'] = naver_sel.css('.basicList_title__3P9Q7 > a ::text').get() 
                item['price'] = naver_sel.css('.price_num__2WUXn ::text').get() 
                item['spec1'] = naver_sel.css('.basicList_detail_box__3ta3h > a::text')[0].get()
                item['spec2'] = naver_sel.css('.basicList_detail_box__3ta3h > a::text')[1].get()
                item['spec3'] = naver_sel.css('.basicList_detail_box__3ta3h > a::text')[2].get()
                item['spec4'] = naver_sel.css('.basicList_detail_box__3ta3h > a::text')[3].get()
                item['spec5'] = naver_sel.css('.basicList_detail_box__3ta3h > a::text')[4].get()
                item['spec6'] = naver_sel.css('.basicList_detail_box__3ta3h > a::text')[5].get()
                item['spec7'] = naver_sel.css('.basicList_detail_box__3ta3h > a::text')[6].get()
                item['spec8'] = naver_sel.css('.basicList_detail_box__3ta3h > a::text')[7].get()
                yield item
        except Exception as e:
            print('e: ', e)
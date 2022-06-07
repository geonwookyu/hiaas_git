import scrapy

class Naverspider(scrapy.Spider):
    name = "naver"

    def start_requests(self):
        urls = [
            "https://search.shopping.naver.com/search/all?query=TV&frm=NVSHATC&prevQuery=TV",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        urls=[]
        try:
            for i in range(1,2):
                url_page = 'https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery=TV&pagingIndex='+str(i)+'&pagingSize=80&productSet=total&query=TV'
                urls.append(url_page)
            #User-Agent값으로 유저 정보 입력 
            headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}
            for url in urls:
                yield scrapy.Request(url=url,headers=headers, callback=self.parse_pdp)
        except Exception as e:
            print('e: ',e)

    def parse_pdp(self, response):
        try:
            item = {}
            naver_pdps = response.css('.style_inner__1Eo2z')
            for naver_pdp in naver_pdps:
                item['brand'] = naver_pdp.css('.top_cell__3DnEV > em ::text')[1].get()
                item['branshop'] = naver_pdp.css('.brandShortCut_info_brand__2nvX3 > a::attr(href)').get()
                item['seller'] = naver_pdp.css('.lowestPrice_delivery_price__3f-2l > span::text').get()
                item['sellershop'] = naver_pdp.css('.buyButton_compare_wrap__7LRui > a::attr(href)').get()
                item['product'] = naver_pdp.css('.top_summary_title__15yAr > h2::text').get()
                item['sku'] = naver_pdp.css('.top_summary_title__15yAr > h2::text').get()
                item['dcprice'] = naver_pdp.css('.lowestPrice_low_price__fByaG > em::text').get()
                item['stock'] = "N/A"
                
                if naver_pdp.css('.lowestPrice_price_area__OkxBK > div::text')[2].get() =="무료배송":
                    #item['deliveryFee'] = naver_pdp.css('.lowestPrice_price_area__OkxBK > div::text')[2].get()
                    item['deliveryFee'] = "Y"
                else: 
                    #item['deliveryFee'] = (naver_pdp.css('.lowestPrice_delivery_price__3f-2l > em::text').get()+"원") 
                    item['deliveryFee'] = "N"
                optionlen = len(naver_pdp.css('.filter_text__3m_XA::text'))
                option = ""
                for i in range(1,optionlen):
                    option = option+naver_pdp.css('.filter_text__3m_XA::text')[i-1].get()

                item['option'] = option
                mem = response.css('.productList_inner__3wBIh')     #멤버쉽 데이터 read용 css path
                membershipIdx = len(mem[0].css('.benefitLayer_benefit__6Fkx6 > p::text'))
                membershipStr = ""
                if membershipIdx != 0:
                    for i in range(0,membershipIdx):
                        if mem[0].css('.benefitLayer_benefit__6Fkx6 > p::text')[i].get() == "원":
                            membershipStr = membershipStr+mem[0].css('p > em::text').get()
                        membershipStr = membershipStr+mem[0].css('.benefitLayer_benefit__6Fkx6 > p::text')[i].get()
                else:
                    membershipStr = "없음"

                item['membership'] = membershipStr
                item['productDetail'] = naver_pdp.css('.specInfo_section_spec__2KP4f > div::text').get()
                item['url'] = response.url
                yield item
        except Exception as e:
            print('e: ', e)
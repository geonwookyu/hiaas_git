import scrapy
import requests
import json

class Naverspider(scrapy.Spider):
    global urlList
    global headers

    urlList = []
    name = "api_test_ver3"
    allowed_domains = ['shopping.naver.com']
    start_urls = ['https://search.shopping.naver.com/search/all?query=TV&frm=NVSHATC&prevQuery=TV']
    custom_settings = {
    #     'DOWNLOADER_MIDDLEWARES' : {
    #         'mi.middlewares.MiDownloaderMiddleware' : 100
    #     }
        'ITEM_PIPELINES': {
            'mi.pipelines.NaverPipeline': 300
        },
        'DOWNLOAD_DELAY' : 1  
    }
    
    def start_requests(self):
        print('-------------------------------------------스파이더 스타트 리퀘스트 시작 ------------------------------------------------------')
        # for i in range(1,2):
        #     url_page = 'https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery=TV&pagingIndex='+str(i)+'&pagingSize=80&productSet=total&query=TV'
        #     #url_page = 'https://search.shopping.naver.com/search/all?query=TV&frm=NVSHATC&prevQuery=TV&pagingIndex='+str(i)
        #     urls.append(url_page)
        # #User-Agent값으로 유저 정보 입력 
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}
        
        urls = [
            "https://search.shopping.naver.com/search/all?query=TV&frm=NVSHATC&prevQuery=TV",
        ]
        
        for url in urls:
           yield scrapy.Request(url=url,headers=headers, callback=self.parse_page)

    def parse_page(self, response):
        print('-------------------------------------------크롤링 시작 ------------------------------------------------------')
        global urlList
        try:

            # def isRepeat(previousItemList, itemList) :

            #     #같은 값을 응답받으면 True 리턴
            #     if previousItemList['shoppingResult']['products'][0]['productName'] == itemList['shoppingResult']['products'][0]['productName']:
            #         print('같아서 끝-----')
            #         return True
            #     #아니면 False 리턴
            #     return False
            
            def makeRequestAndGetResponse(number) :
                pageingIndex = number

                params = (
                    ('sort', 'rel'),
                    ('pagingIndex', pageingIndex),
                    ('pagingSize', '80'),
                    ('viewType', 'list'),
                    ('productSet', 'total'),
                    ('deliveryFee', ''),
                    ('deliveryTypeValue', ''),
                    ('frm', 'NVSHATC'),
                    ('query', 'TV'),
                    ('origQuery', 'TV'),
                    ('iq', ''),
                    ('eq', ''),
                    ('xq', ''),
                )
                print('================================================================ pageIdx : ',pageingIndex)
                response = requests.get('https://search.shopping.naver.com/api/search/all', headers=headers, params=params)
                return response
            # 중복 체크를 위한 변수
            previousItemList = []
            headers = {
                'authority': 'search.shopping.naver.com',
                'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
                'accept': 'application/json, text/plain, */*',
                'sec-ch-ua-mobile': '?0',
                'logic': 'PART',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
                #'lang':'ko_KR',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://search.shopping.naver.com/search/all?frm=NVSHATC&origQuery=TV&pagingIndex=1&pagingSize=80&productSet=total&query=TV',
                'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'cookie': 'NNB=NOLCMFH6MS3WA; NDARK=Y; _ga=GA1.2.36707839.1627031989; _ga_7VKFYR6RV1=GS1.1.1627031988.1.1.1627032122.60; nx_ssl=2; AD_SHP_BID=23; spage_uid=; BMR=s=1631641124319&r=https%3A%2F%2Fm.blog.naver.com%2FPostView.naver%3FisHttpsRedirect%3Dtrue%26blogId%3Dteenager4282%26logNo%3D220962394004&r2=https%3A%2F%2Fwww.google.com%2F; sus_val=G6C9UIqZv3AcfjeJP38FmfXG',
            }
            number = 1
            ForTrycount = 0
            while number < 13 :
                print('number = ',number)

                # 네이버를 향한 Request 생성 and 네이버로부터 response 받기
                response = makeRequestAndGetResponse(number)

                # json을 리스트로 받기
                itemList = json.loads(response.text)

                # 첫번째 호출에는 list가 비교가 안되니 continue를 한다.
                # if number == 1 :
                #     number = number + 1
                #     previousItemList = itemList
                #     #printData(itemList)
                #     continue

                # # 반복 응답 Check Method
                # # 응답이 같은 값으로 반복되었는지 확인하는 메서드를 실행한다. True일 경우 중복이라서 break
                # if isRepeat(previousItemList, itemList) :
                #     break

                #previousItemList = itemList
                number = number + 1
                # 추출하려는 값의 key를 입력
                
                for i in itemList['shoppingResult']['products']:
                    trycount = ForTrycount+1
                    curl = i['crUrl']
                    print('========================================================trycount : ',trycount)
                    yield scrapy.Request(curl,self.parse_pdp)
        except Exception as e:
            print('e: ', e)
    
    def parse_pdp(self, response):

        def itemPicker(xpath): #데이터 추출함수
            value = ""
            try :
                value = naver_pdp.css(xpath).get()
                if len(value) > 0:
                    return value
                else:
                    return 'N/A'
            except :
                return 'N/A'
        global urlList
        try:   
            path = ""
            case = ""  
            if 'smartstore' and 'cr.shopping' not in response.url:
                path = '.style_inner__1Eo2z'
                case = 'naver'
            elif 'smartstore' in response.url:
                path = '._2ZMO1PVXbA'
                case = 'smart'        
            else:
                path = 'drop'
                case = 'drop'

            naver_pdps = response.css(path)          
            item = {}

            if case == 'naver':                 #네이버쇼핑
                for naver_pdp in naver_pdps:
                    tagIdx = len(naver_pdp.css('.top_cell__3DnEV::text'))
                    for i in range(1,tagIdx):
                        if naver_pdp.css('.top_cell__3DnEV::text')[i-1].get() == "브랜드" :
                            item['brand'] = naver_pdp.css('.top_cell__3DnEV > em ::text')[i-1].get()
                            break;
                        else:
                            item['brand'] = 'N/A' 
                
                    item['branshop'] = itemPicker('.brandShortCut_info_brand__2nvX3 > a::attr(href)')
                    item['seller'] = itemPicker('.lowestPrice_delivery_price__3f-2l > span::text')
                    item['sellershop'] = itemPicker('.buyButton_compare_wrap__7LRui > a::attr(href)')
                    item['product'] = itemPicker('.top_summary_title__15yAr > h2::text')
                    item['sku'] = itemPicker('.top_summary_title__15yAr > h2::text')
                    item['dcprice'] = itemPicker('.lowestPrice_low_price__fByaG > em::text')
                    item['stock'] = "N/A"
                    
                    if naver_pdp.css('.lowestPrice_price_area__OkxBK > div::text')[2].get() =="무료배송":
                        item['deliveryFee'] = "Y"
                    else: 
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
                            if (mem[0].css('.benefitLayer_benefit__6Fkx6 > p::text')[i]).get() == "원":
                                membershipStr = membershipStr+mem[0].css('p > em::text').get()
                            membershipStr = membershipStr+mem[0].css('.benefitLayer_benefit__6Fkx6 > p::text')[i].get()
                    else:
                        membershipStr = 'N/A'

                    item['membership'] = membershipStr
                    item['productDetail'] = "N/A"#naver_pdp.css('.specInfo_section_spec__2KP4f > div::text').get()
                    item['url'] = response.url
                    yield item
            elif case == 'smart':               #네이버 스마트쇼핑
                #naver_pdps = response.css('._2ZMO1PVXbA')
                tableIdx = len(naver_pdp.css('._1iuv6pLHMD::text'))
                for naver_pdp in naver_pdps:
                    for i in range(1,tableIdx):
                        if naver_pdp.css('._1iuv6pLHMD')[i-1].get() == "브랜드":
                            item['brand'] = naver_pdp.css('.ABROiEshTD::text')[i-1].get()
                            break;
                        else :
                            item['brand'] = 'N/A'

                    item['branshop'] = 'N/A'
                    item['seller'] = response.css('.KasFrJs3SA::text').get()        #최상위에 있는 판매사이트 명을 가져오기 위해 path를 분리함
                    item['sellershop'] = 'N/A'
                    item['product'] = itemPicker('._3oDjSvLwq9 _copyable::text')
                    for i in range(1,tableIdx):
                        if naver_pdp.css('._1iuv6pLHMD')[i-1].get() == "모델명":
                            item['sku'] = itemPicker('.ABROiEshTD::text')[i-1]                    
                    item['dcprice'] = itemPicker('._1LY7DqCnwR::text')
                    item['stock'] = "N/A"
                    
                    if itemPicker('.bd_ChMMo::text')[1] =="무료배송":
                        item['deliveryFee'] = "Y"
                    else: 
                        item['deliveryFee'] = "N"
                    
                    item['option'] = 'N/A'                   
                    item['membership'] = 'N/A'
                    item['productDetail'] = 'N/A'#naver_pdp.css('.specInfo_section_spec__2KP4f > div::text').get()
                    item['url'] = response.url
                    yield item
            elif case == 'drop' :       #외부 사이트
                item['brand'] = '오류'
                item['branshop'] = '외부사이트'
                item['seller'] ='N/A'
                item['sellershop'] ='N/A'
                item['product'] ='N/A'
                item['sku'] ='N/A'
                item['dcprice'] ='N/A'
                item['stock'] ='N/A'
                item['deliveryFee'] ='N/A'
                item['option'] ='N/A'
                item['membership'] ='N/A'
                item['productDetail'] = 'N/A'
                item['url'] = response.url
                yield item
            else :                      #그 외 오류
                item['brand'] = '오류'
                item['branshop'] = e
                item['seller'] ='N/A'
                item['sellershop'] ='N/A'
                item['product'] ='N/A'
                item['sku'] ='N/A'
                item['dcprice'] ='N/A'
                item['stock'] ='N/A'
                item['deliveryFee'] ='N/A'
                item['option'] ='N/A'
                item['membership'] ='N/A'
                item['productDetail'] = 'N/A'
                item['url'] = response.url           
                yield item
        except Exception as e:
            print('e: ', e)

# import scrapy
# import requests
# import json

# class Naverspider(scrapy.Spider):
#     global headers
#     name = "api_test_ver4"
#     allowed_domains = ['shopping.naver.com']
#     start_urls = ['https://search.shopping.naver.com/search/all?query=TV&frm=NVSHATC&prevQuery=TV']
#     custom_settings = {

#         'ITEM_PIPELINES': {
#             'mi.pipelines.NaverPipeline': 300
#         },
#         'DOWNLOAD_DELAY' : 1  
#     }
    
#     def start_requests(self):
#         print('-------------------------------------------스파이더 스타트 리퀘스트 시작 ------------------------------------------------------')
#         headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}
        
#         urls = [
#             "https://search.shopping.naver.com/search/all?query=TV&frm=NVSHATC&prevQuery=TV",
#         ]
        
#         for url in urls:
#             yield scrapy.Request(url=url,headers=headers, callback=self.parse_page)

#     def parse_page(self, response):
#         print('-------------------------------------------크롤링 시작 ------------------------------------------------------')
#         try:

            
#             def makeRequestAndGetResponse(number) :
#                 pageingIndex = number

#                 params = (
#                     ('sort', 'rel'),
#                     ('pagingIndex', pageingIndex),
#                     ('pagingSize', '20'),
#                     ('viewType', 'list'),
#                     ('productSet', 'total'),
#                     ('deliveryFee', ''),
#                     ('deliveryTypeValue', ''),
#                     ('frm', 'NVSHATC'),
#                     ('query', 'TV'),
#                     ('origQuery', 'TV'),
#                     ('iq', ''),
#                     ('eq', ''),
#                     ('xq', ''),
#                 )
#                 print('================================================================ pageIdx : ',pageingIndex)
#                 response = requests.get('https://search.shopping.naver.com/api/search/all', headers=headers, params=params)
#                 return response
#             # 중복 체크를 위한 변수
#             headers = {
#                 'authority': 'search.shopping.naver.com',
#                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#                 'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
#                 'cache-control': 'no-cache',
#                 'pragma': 'no-cache',
#                 'referer': 'https://shopping.naver.com/home/p/index.naver',
#                 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
#                 'sec-ch-ua-mobile': '?0',
#                 'sec-ch-ua-platform': '"Windows"',
#                 'sec-fetch-dest': 'document',
#                 'sec-fetch-mode': 'navigate',
#                 'sec-fetch-site': 'same-origin',
#                 'sec-fetch-user': '?1',
#                 'upgrade-insecure-requests': '1',
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36',
#             }
#             number = 1
#             item=[]
#             # while number < 2 :
#             #     print('number = ',number)

#             # 네이버를 향한 Request 생성 and 네이버로부터 response 받기
#             response = makeRequestAndGetResponse(number)

#             # json을 리스트로 받기
#             itemList = json.loads(response.text)
#             print(itemList)
#             stopit = 0    
#             for i in itemList['shoppingResult']['products']:
#                 #print('this is test')
#                 stopit = stopit+1               
#                 #item['product'] = i['rank']
#                 print(i['brand'])                
#                 print(i['lowMallList'][0]['name'])
#                 print(i['productTitle'])
#                 print(i['productName'])
#                 print(i['lowPrice'])
#                 option = i['prchCondInfo']
#                 subIdx1 = option.find("|")
#                 option=option[subIdx1+1:len(option)]
#                 subIdx2 = option.find("|")
#                 option = option[1:subIdx2]
#                 print(option)
#                 print(i['characterValue'])
#                 print(i['crUrl'])

#                 print('==================================================')

#                 item['brand'] = i['brand']
#                 item['brandShop'] = 'N/A'
#                 item['seller'] = i['lowMallList'][0]['name']
#                 item['sellerShop'] = 'N/A'
#                 item['product'] = i['productTitle']
#                 item['sku'] = i['productName']
#                 item['dcprice'] = i['lowPrice']
#                 item['soldout'] = 'N/A'
#                 item['freeShipping'] = 'N/A'
#                 option = i['prchCondInfo']
#                 subIdx1 = option.find("|")
#                 option=option[subIdx1+1:len(option)]
#                 subIdx2 = option.find("|")
#                 option = option[1:subIdx2]
#                 item['productOption'] = option
#                 item['membershipBenefit'] = 'N/A'
#                 item['productDetail'] = i['characterValue']
#                 item['url'] = i['crUrl']
#                 yield item  
             
#         except Exception as e:
#             print('e: ', e)
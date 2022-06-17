# import requests
# import json
# import requests

# cookies = {
#     'PCID': '19080755529701281165754',
#     '_fbp': 'fb.1.1650516325815.1379840085',
#     'gd1': 'Y',
#     '_gcl_au': '1.1.1150624454.1652170932',
#     'x-coupang-origin-region': 'KOREA',
#     'x-coupang-target-market': 'KR',
#     'MARKETID': '19080755529701281165754',
#     'sid': '2718becbc0664ce78c0e3bfe79713ae5dd4d365e',
#     'bm_sz': 'F42657972703726F70919DA9B66DA2C0~YAAQTg3VF/liUUuBAQAAce6nXxAApKo/0G5WnAVv0YsXCy2w7CEXFQbLYhIQlgWJ2uS1Ngf5NiXIHSfhHfh2zcsmMUB2A/zSK5wC57HW1vaAQk5GFkvMH77g4UAgm7SMmQJuY5qgfqDwgxLmn1X9soCyKNArcVlWTBVbw97CWaQufuy7hY/vimCiZbLGIMWQ7c03NEz6ydEvUrbA33EDkfzFYkTVfyG3ALM/MQKWaRN5+nJ/hyEVMASK3qOVZDnweoX3UkRmq1SlEdRggkriUWC4B+gdNDVG17M9OpGgvtNMx6NQ~4469825~3356214',
#     'ak_bmsc': 'D9A43C1E0FFA1620DD9BA75537CAE3C7~000000000000000000000000000000~YAAQTg3VF91kUUuBAQAApvOnXxBC9gdkiNb0g1JbeSf7e4LIMsMjKlA5PDWwuQXzpTnDBrjvslxT2O1H8htkI6TBZ3I7+ZHyUKrgmPyVDE9sJPez1PDUdpEMBFtCYldGZhh3pOYK+1RHdqb64FpoeYlHJ66zfB773/cnx+llY8Q8DgCJN5EpFrys6jJmDJmu/X2u5l2+8RM0mFvpKn8TGKSaaoBvh8YLD+rd3jPLmyvkZOElyqU2ihUStYsljpf5hDw2ztIXjt/M2lxpyHvxPaLQ+sfydQ+EQkF0nSO6SWNKzEmV9r32AomOFbVnUkwmuJbsB1s2nIfN6goK+4VchqLNsecssXMoheT1PbFPawgJaYrYWmuBYwaJmhmi/r+s3N8Ffg6GqGbFPu33hf8+G8na5ORJnoL0eqnrW3YanPQ0pil8Xxw+0CYjBiy5v6XFtKzA5LLdFkuKAOEzG+U1mkOnrrMhHoZ7XxTqA6UMDFpVZ0zvej0jzroaprg=',
#     '_abck': '26A3A7A41A8C916C72F5F6CA432FB94E~0~YAAQXw3VF1pAFUKBAQAACUyqXwgGPDoqjLo2npXb0MPvnNBXybVJrz9dUE96Vs6Lg+YF0Iqn/rpYu9NbkRgm/i9zNuyv6VF/j/lyHq6utfIMMWJbnIp79H37wAELHdnny9Psu7OQyl5txs/knUnCqsGruvRS1w/tt3aUzBDMWa+miTvKpwcto9eh+g7lEGnEU8mPAXkw+KeeEDdpqYjt722IBqxUJPdSJB9mCpKeFkYk+l59qsduw2Gck46Xj+6pxEeJqSYpW/maWLDKTiQngLwu9WIH6SwOYkWYBtbZvaPn2aDrp6E0axsJBe9JqK4p+gEqI5dsgeM/C381822S6WY+XNY729Iww6f4LtoK/XcSvuAh6k3ULLm2KQ2/+okSG83cq1cvnr79QsNhAc9y+KQ7UX8RNcMuvA==~-1~-1~-1',
#     'searchKeyword': 'TV',
#     'searchKeywordType': '%7B%22TV%22%3A0%7D',
#     'FUN': '"{\'search\':[{\'reqUrl\':\'/search.pang\',\'isValid\':true}]}"',
#     '_ga': 'GA1.2.645717777.1655169385',
#     '_gid': 'GA1.2.777423709.1655169385',
#     'overrideAbTestGroup': '%5B%5D',
#     'x-coupang-accept-language': 'ko_KR',
#     'X-CP-PT-locale': 'ko_KR',
#     'cto_bundle': 'ij1Ft19idk5tSFZWU0ZRMWFTSXhGS1hRUTJIZ1k5enN1T3Y1ZXp4bGhQSVRxWkhKU3JlNjU3S1pzVEZlQ29PanZlMWpmbHVicmFZZGNnSVl2WDA3aXc2WFIzN0x1blY4JTJCS1ZlRXE2UDR1QUp3TFNVQkZ3YVhGOWN0Wk04SkpUNmJhYkhFN0Fvd1RRVWklMkZSQTJoUTIwVVlWSmdBJTNEJTNE',
#     'baby-isWide': 'small',
#     'bm_sv': 'F4B4BEF55067C873B02177C2500D0590~YAAQlwI1F4ofki2BAQAAPe/qXxAy1aXwmoBYWpiuF7z9v6HO3WBoMR1Vu0Pqty65+ZoNYtHdwYpTubW75QEivPFYL/mkXsbfU6E1b1UyVIJiBKGtBTPXni7zhNkSHJpZavd1uJzI9Yp2TDZVCdKvKsvM3AU1v6VrTd8xy9EfsfIzmIMTSsiyxJbGXNA0Rmr01H+93oiX/61/wBk0VH7DxEM5ci1hreClh9lnsIB4h5DoQ/loQahFmZeZidXORNt7bkE=~1',
# }

# headers = {
#     'Accept': '*/*',
#     'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
#     'Cache-Control': 'no-cache',
#     'Connection': 'keep-alive',
#     # Requests sorts cookies= alphabetically
#     # 'Cookie': 'PCID=19080755529701281165754; _fbp=fb.1.1650516325815.1379840085; gd1=Y; _gcl_au=1.1.1150624454.1652170932; x-coupang-origin-region=KOREA; x-coupang-target-market=KR; MARKETID=19080755529701281165754; sid=2718becbc0664ce78c0e3bfe79713ae5dd4d365e; bm_sz=F42657972703726F70919DA9B66DA2C0~YAAQTg3VF/liUUuBAQAAce6nXxAApKo/0G5WnAVv0YsXCy2w7CEXFQbLYhIQlgWJ2uS1Ngf5NiXIHSfhHfh2zcsmMUB2A/zSK5wC57HW1vaAQk5GFkvMH77g4UAgm7SMmQJuY5qgfqDwgxLmn1X9soCyKNArcVlWTBVbw97CWaQufuy7hY/vimCiZbLGIMWQ7c03NEz6ydEvUrbA33EDkfzFYkTVfyG3ALM/MQKWaRN5+nJ/hyEVMASK3qOVZDnweoX3UkRmq1SlEdRggkriUWC4B+gdNDVG17M9OpGgvtNMx6NQ~4469825~3356214; ak_bmsc=D9A43C1E0FFA1620DD9BA75537CAE3C7~000000000000000000000000000000~YAAQTg3VF91kUUuBAQAApvOnXxBC9gdkiNb0g1JbeSf7e4LIMsMjKlA5PDWwuQXzpTnDBrjvslxT2O1H8htkI6TBZ3I7+ZHyUKrgmPyVDE9sJPez1PDUdpEMBFtCYldGZhh3pOYK+1RHdqb64FpoeYlHJ66zfB773/cnx+llY8Q8DgCJN5EpFrys6jJmDJmu/X2u5l2+8RM0mFvpKn8TGKSaaoBvh8YLD+rd3jPLmyvkZOElyqU2ihUStYsljpf5hDw2ztIXjt/M2lxpyHvxPaLQ+sfydQ+EQkF0nSO6SWNKzEmV9r32AomOFbVnUkwmuJbsB1s2nIfN6goK+4VchqLNsecssXMoheT1PbFPawgJaYrYWmuBYwaJmhmi/r+s3N8Ffg6GqGbFPu33hf8+G8na5ORJnoL0eqnrW3YanPQ0pil8Xxw+0CYjBiy5v6XFtKzA5LLdFkuKAOEzG+U1mkOnrrMhHoZ7XxTqA6UMDFpVZ0zvej0jzroaprg=; _abck=26A3A7A41A8C916C72F5F6CA432FB94E~0~YAAQXw3VF1pAFUKBAQAACUyqXwgGPDoqjLo2npXb0MPvnNBXybVJrz9dUE96Vs6Lg+YF0Iqn/rpYu9NbkRgm/i9zNuyv6VF/j/lyHq6utfIMMWJbnIp79H37wAELHdnny9Psu7OQyl5txs/knUnCqsGruvRS1w/tt3aUzBDMWa+miTvKpwcto9eh+g7lEGnEU8mPAXkw+KeeEDdpqYjt722IBqxUJPdSJB9mCpKeFkYk+l59qsduw2Gck46Xj+6pxEeJqSYpW/maWLDKTiQngLwu9WIH6SwOYkWYBtbZvaPn2aDrp6E0axsJBe9JqK4p+gEqI5dsgeM/C381822S6WY+XNY729Iww6f4LtoK/XcSvuAh6k3ULLm2KQ2/+okSG83cq1cvnr79QsNhAc9y+KQ7UX8RNcMuvA==~-1~-1~-1; searchKeyword=TV; searchKeywordType=%7B%22TV%22%3A0%7D; FUN="{\'search\':[{\'reqUrl\':\'/search.pang\',\'isValid\':true}]}"; _ga=GA1.2.645717777.1655169385; _gid=GA1.2.777423709.1655169385; overrideAbTestGroup=%5B%5D; x-coupang-accept-language=ko_KR; X-CP-PT-locale=ko_KR; cto_bundle=ij1Ft19idk5tSFZWU0ZRMWFTSXhGS1hRUTJIZ1k5enN1T3Y1ZXp4bGhQSVRxWkhKU3JlNjU3S1pzVEZlQ29PanZlMWpmbHVicmFZZGNnSVl2WDA3aXc2WFIzN0x1blY4JTJCS1ZlRXE2UDR1QUp3TFNVQkZ3YVhGOWN0Wk04SkpUNmJhYkhFN0Fvd1RRVWklMkZSQTJoUTIwVVlWSmdBJTNEJTNE; baby-isWide=small; bm_sv=F4B4BEF55067C873B02177C2500D0590~YAAQlwI1F4ofki2BAQAAPe/qXxAy1aXwmoBYWpiuF7z9v6HO3WBoMR1Vu0Pqty65+ZoNYtHdwYpTubW75QEivPFYL/mkXsbfU6E1b1UyVIJiBKGtBTPXni7zhNkSHJpZavd1uJzI9Yp2TDZVCdKvKsvM3AU1v6VrTd8xy9EfsfIzmIMTSsiyxJbGXNA0Rmr01H+93oiX/61/wBk0VH7DxEM5ci1hreClh9lnsIB4h5DoQ/loQahFmZeZidXORNt7bkE=~1',
#     'Pragma': 'no-cache',
#     'Referer': 'https://www.coupang.com/',
#     'Sec-Fetch-Dest': 'script',
#     'Sec-Fetch-Mode': 'no-cors',
#     'Sec-Fetch-Site': 'same-site',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36',
#     'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
# }

# params = {
#     'page': '0',
#     'callback': 'jQuery111108868813053701661_1655171639221',
#     '_': '1655171639222',
# }

# response = requests.get('https://reco.coupang.com/api/v2/viewed-products', params=params, cookies=cookies, headers=headers)
# #print(response.text)
# itemList = json.loads(response.text)
# print(itemList)
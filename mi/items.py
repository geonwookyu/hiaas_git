# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class HiLabMIItem(scrapy.Item):
    detail_link = scrapy.Field()    # 제품 상세페이지 링크
    
    # <카테고리 페이지>
    pr1ca = scrapy.Field()   # 카테고리_1 카테고리
    #pr2ca = scrapy.Field()
    #pr3ca = scrapy.Field()
    sb = scrapy.Field() # 카테고리_3 정렬기준(임의) - sort by
    prco = scrapy.Field()  # 카테고리_4 총 제품 수(임의) - product count
    pr1nm = scrapy.Field()   # 카테고리_5 제품명
    pr1pr = scrapy.Field()  # 카테고리_6 가격
    ta = scrapy.Field() # 카테고리_7 판매자
    gr = scrapy.Field()  # 카테고리_8 평점(임의) - grade
    revco = scrapy.Field()   # 카테고리_9 리뷰 개수(임의) - review count
    dcinfo = scrapy.Field()   # 카테고리_10 할인 정보(임의) - discount information
    ts = scrapy.Field() # 카테고리_11 무료배송 유무
    ardate = scrapy.Field()  # 카테고리_12 도착 예정일자(임의) - arrive date
    ms = scrapy.Field() # 카테고리_13 멤버십 적용유무(임의) - membership
    opo = scrapy.Field()    # 카테고리_14 다른 구매옵션(임의) - other purchase option
    purchco = scrapy.Field()    # 카테고리_15 구매횟수(임의) - purchase count
    pr1qt = scrapy.Field()  # 카테고리_16 재고 현황
    pgco = scrapy.Field()    # 카테고리_17 전체 페이지 수(임의) - page count

    # <검색결과 페이지>
    sk = scrapy.Field()    # 검색결과_1 검색 키워드(임의) - search keyword
    # 검색결과_3 ~ 검색결과_17은 카테고리_3 ~ 카테고리_17과 중복됨.

    # <PDP(상품정보) 페이지>
    pr1br = scrapy.Field()  # 상품정보_1 브랜드
    brlk = scrapy.Field() # 상품정보_2 브랜드샵 link(임의) - brand link
    # 상품정보_3은 #카테고리_7과 중복됨.
    talk = scrapy.Field() # 상품정보_4 셀러 샵 link(임의)
    # 상품정보_5 카테고리_5와 중복됨.
    pr1id = scrapy.Field()  # 상품정보_6 SKU
    dcrate = scrapy.Field()   # 상품정보_7 할인율(임의) - discount rate
    fullpr = scrapy.Field() # 상품정보_8 정가(임의) - full price
    dcpr = scrapy.Field() # 상품정보_9 할인가(임의) - discount price
    soldout = scrapy.Field()    # 상품정보_10 품절 유무(임의)
    # 상품정보_11은 카테고리_16과 중복됨.
    # 상품정보_12은 카테고리_11과 중복됨.
    # 상품정보_13은 카테고리_12와 중복됨.
    pr1va = scrapy.Field()  # 상품정보_14 제품 구매 옵션
    # 상품정보_15 멤버십 혜택
    prdetail = scrapy.Field()   # 상품정보_16 제품 상세(임의) - product detail

    # <리뷰 페이지>
    # 리뷰_1은 카테고리_8과 중복될 수도 있음.
    # 리뷰_2 카테고리_9와 중복될 수도 있음.
    revsum = scrapy.Field()  # 리뷰_3 리뷰 특징 요약(임의) - reviews summary
    revsb = scrapy.Field() # 리뷰_4 정렬기준(임의) - review sort by
    reviewer = scrapy.Field()   # 리뷰_5 작성자(임의) - reviewer
    ingrade = scrapy.Field()   # 리뷰_6 평점(임의) - individual grade
    revdate = scrapy.Field()    # 리뷰_7 작성 일자(임의) - reviews date
    purchdetail = scrapy.Field()    # 리뷰_8 구매품목 디테일(임의) - purchase detail
    revdetail = scrapy.Field()  # 리뷰_9 리뷰 디테일(임의) - reivew detail
    blogrev = scrapy.Field()    # 리뷰_10 블로그 리뷰(임의) - blog review
    revviews = scrapy.Field()   # 리뷰_11 리뷰 조회수(임의) - review views
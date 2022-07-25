import scrapy



class HiaasCommon(scrapy.Spider):

    @classmethod
    def from_crawler(cls, crawler):
        params = {}
        if crawler.settings.get('KEYWORD_LIST') and crawler.settings.get('LIMIT_PAGING_COUNT'):
            params['keywordList'] = crawler.settings['KEYWORD_LIST']
            params['limitPagingCount'] = crawler.settings['LIMIT_PAGING_COUNT']
            params['coupangCrawlDelay'] = crawler.settings['COUPANG_CRAWL_DELAY']
            params['CoupangListsize'] = crawler.settings['COUPANG_LISTSIZE']
            params['CoupangPageCount'] = crawler.settings['COUPANG_PAGE_COUNT']
            params['CoupangSorter'] = crawler.settings['COUPANG_SORTER']

        ext = cls(**params)
        ext.settings = crawler.settings
        
        return ext
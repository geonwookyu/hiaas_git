import json
# import logging

import requests
from scrapy.utils.serialize import ScrapyJSONEncoder
from twisted.internet.defer import DeferredLock
from twisted.internet.threads import deferToThread
from itemadapter import is_item, ItemAdapter


class HttpPostPipeline(object):
    settings = None
    items_buffer = []

    DEFAULT_HTTP_POST_PIPELINE_BUFFERED = False
    DEFAULT_HTTP_POST_PIPELINE_BUFFER_SIZE = 100

    def __init__(self, url, headers=None):
        """Initialize pipeline.
        Parameters
        ----------
        url : StrictRedis
            Redis client instance.
        serialize_func : callable
            Items serializer function.
        """
        self.url = url
        self.headers = headers if headers else {}
        # self.serialize_func = serialize_func
        self._lock = DeferredLock()

    @classmethod
    def from_crawler(cls, crawler):
        params = {
            'url': crawler.settings.get('HTTP_POST_PIPELINE_URL'),
        }
        if crawler.settings.get('HTTP_POST_PIPELINE_HEADERS'):
            params['headers'] = crawler.settings['HTTP_POST_PIPELINE_HEADERS']

        ext = cls(**params)
        ext.settings = crawler.settings

        return ext

    def process_item(self, item, spider):
        if self.settings.get('HTTP_POST_PIPELINE_BUFFERED', self.DEFAULT_HTTP_POST_PIPELINE_BUFFERED):
            self._lock.run(self._process_items, item)
            return item
        else:
            return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        data = self._serialize_func(item)
        requests.post(self.url, data=data, headers=self.headers)
        return item

    def _process_items(self, item):
        self.items_buffer.append(item)
        if len(self.items_buffer) >= int(self.settings.get('HTTP_POST_PIPELINE_BUFFER_SIZE',
                                                           self.DEFAULT_HTTP_POST_PIPELINE_BUFFER_SIZE)):
            deferToThread(self.send_items, self.items_buffer)
            self.items_buffer = []
            
    def send_items(self, items):
        serialized_items = [self._serialize_func(item) for item in items]
        requests.post(self.url, data=[json.loads(data) for data in serialized_items], headers=self.headers)

    def close_spider(self, spider):
        if len(self.items_buffer) > 0:
            deferToThread(self.send_items, self.items_buffer)
    
    def _serialize_func(self, item):
        encoding= self.settings.get('FEED_EXPORT_ENCODING','utf-8')
        d = ItemAdapter(item).asdict()
        data = json.dumps(d,ensure_ascii=False).encode(encoding)
        return data


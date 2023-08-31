# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging

import requests
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware, BackwardsCompatibilityMetaclass
from scrapy.utils.response import response_status_message
from fake_useragent import UserAgent
import time
import random
import base64
import os
import json



# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class GubaSpiderMiddleware:
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
        spider.logger.info("Spider opened: %s" % spider.name)


class GubaDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class RandomheaderDownloaderMiddleware:
    # 创建 Ua对象
    ua = UserAgent()

    def process_request(self, request, spider):
        # 设置请求头 User-Agent值
        request.headers['User-Agent'] = self.ua.random

        return None


class ProxyMiddleware(object):
    """
    开源代理
    https://github.com/jhao104/proxy_pool
    """
    def __init__(self, settings):
        self.proxy_server_host = settings.get('PROXY_SERVER_HOST')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def get_proxy(self):
        return requests.get(rf"http://{self.proxy_server_host}/get/").json()

    def delete_proxy(self,proxy):
        requests.get("http://{}/delete/?proxy={}".format(self.proxy_server_host, proxy))

    def process_request(self, request, spider):
        proxy_server = self.get_proxy().get("proxy")
        logging.info('get proxy from pool : {} , {}'.format(proxy_server, request.url))
        request.meta["proxy"] = 'http://'+proxy_server


class ABYProxyMiddleware(object):
    """
    阿布云代理中间件
    """

    def get_abyun_secret(self):
        filename = os.path.join('.env', 'abyun_secret.json')
        if not os.path.exists(filename):
            raise FileNotFoundError('file not found {}'.format(filename))

        data = json.load(open(filename))

        return data['username'], data['password']

    def __init__(self, settings):
        self.proxy_server = 'http://http-dyn.abuyun.com:9020'
        proxy_user, proxy_pass = self.get_abyun_secret()

        self.proxy_auth = "Basic " + base64.urlsafe_b64encode(bytes((proxy_user + ":" + proxy_pass), "ascii")).decode("utf8")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        request.meta["proxy"] = self.proxy_server
        request.headers["Proxy-Authorization"] = self.proxy_auth


class GubaRetryMiddleware(RetryMiddleware, metaclass=BackwardsCompatibilityMetaclass):
    logger = logging.getLogger(__name__)

    def __init__(self, settings):
        super().__init__(settings=settings)
        self.proxy_server_host = settings.get('PROXY_SERVER_HOST')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    
    def delete_proxy(self, proxy):
        if self.proxy_server_host and proxy:
            requests.get("http://{}/delete/?proxy={}".format(self.proxy_server_host, proxy))

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            # 删除该代理
            self.delete_proxy(request.meta.get('proxy', False))
            time.sleep(random.randint(3, 5))
            self.logger.warning('response status error, status:{} , {}'.format(response.status, response.url))
            return self._retry(request, reason, spider) or response
        return response
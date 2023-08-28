import logging
import urllib

import scrapy
from scrapy import Selector
from guba.items import EastMoneyPostItem, EastmoneySpiderItem, EastmoneyCommentItem
import re
import math
import json
import time
import numpy

class EastmoneySpider(scrapy.Spider):
    name = "eastmoney"
    allowed_domains = ["guba.eastmoney.com"]
    start_urls = [
        #沪市
        'http://guba.eastmoney.com/remenba.aspx?type=1&tab=1',
        #深市
        # 'http://guba.eastmoney.com/remenba.aspx?type=1&tab=2',
    ]

    def parse(self, response):
        """
        获取所有股票的首页信息
        :param response:
        :return:
        """
        stock_list = Selector(response).xpath(
            '//div[@class="ngbglistdiv"]/ul/li'
        ).extract()

        count = 0

        for stock in stock_list:
            item = EastmoneySpiderItem()
            item['stockname'] = re.sub(r'<.*?>', '', stock)
            item['home_page'] = "http://guba.eastmoney.com/" + Selector(text=stock).xpath('//a/@href').extract_first()

            #TODO 添加中间件，如果该标的已经完成，则跳过
            #TODO 状态信息可以通过文件或者redis等分布式信息中

            yield scrapy.Request(
                url=item['home_page'],
                meta={'item': item},
                callback=self.parse_page_num,
                dont_filter=True
            )
            count += 1

            # 测试，仅获取1个
            if count > 1:
                break

    def get_article_list(self, response):
        scripts = Selector(response).xpath('//script/text()').getall()

        if len(scripts) >= 3:
            script = scripts[2]

            _json = script.replace('var article_list=', '').replace('\t', '')
            _json = _json[0:_json.find(';    var other_list=')]

            try:
                _json = json.loads(_json)
            except Exception as e:
                print(script)

            return _json

    def parse_page_num(self, response):
        """
        获取每个股吧所有的页面list
        :param response:
        :return:
        """
        item = response.meta['item']
        _json = self.get_article_list(response=response)
        if _json is None:
            retry_request = response.request.copy()
            retry_request.dont_filter = True
            logging.info('scripts len error ,retry ... ')
            return retry_request

        size = 80
        count = _json['count']
        page_size = int(count/size)
        if page_size % size > 0:
            page_size += 1

        count = 0
        for p in range(page_size):
            page_url = response.url.split('.html')[0] + '_' + str(p + 1) + '.html'

            count +=1
            if count>1:
                break

            yield scrapy.Request(
                url=page_url,
                meta={'item': item},
                callback=self.get_article_url,
                dont_filter=True
            )

    def get_article_url(self, response):
        """
        获取每个页面的帖子列表
        :param response:
        :return:
        """
        logging.info(response.url)

        stock_name = response.meta['item']['stockname']

        _json = self.get_article_list(response=response)
        if _json is None:
            retry_request = response.request.copy()
            retry_request.dont_filter = True
            logging.info('scripts len error ,retry ... ')
            return retry_request

        count = 0

        for post in _json['re']:
            item = EastMoneyPostItem(post)

            yield item

            # 有post_source_id的是市场相关的帖子
            if item['post_source_id'] == '':
                # yield item
                stockbar_code = item['stockbar_code']
                post_id = item['post_id']

                #请求帖子
                # yield scrapy.Request(
                #     url='http://guba.eastmoney.com/news,{},{}.html'.format(stockbar_code, post_id),
                #     meta={'item': item},
                #     callback=self.get_article_detail,
                #     dont_filter=True
                # )

                #请求评论列表信息
                ts = int(time.time() * 1000)
                callback_id = 'jQuery1830{}{}_{}'.format(int(numpy.random.random_sample() * 10000000),
                                                         int(numpy.random.random_sample() * 10000000), ts)
                page = 1
                page_size = 10000
                url = rf'https://gbapi.eastmoney.com/reply/JSONP/ArticleNewReplyList?callback={callback_id}&plat=web&version=300&product=guba&postid={post_id}&sort=1&sorttype=1&p={page}&ps={page_size}&type=0'

                yield scrapy.Request(
                    url=url,
                    meta={'callback_id': callback_id},
                    callback=self.get_comment_list,
                    dont_filter=True
                )


    def get_article_detail(self, response):
        """
        每个帖子的详情
        :param response:
        :return:
        """
        logging.info(response.url)

        scripts = Selector(response).xpath('//script/text()').getall()

        # index = 0
        # for script in scripts:
        #     logging.info('[{}] {}'.format(index, script))
        #     index += 1

        if len(scripts) >= 4:
            script = scripts[3]
            _json = script.replace('var post_article=', '').replace('\t', '')
            # _json = _json[0:_json.find(';    var other_list=')]
            _json = json.loads(_json)
            print(_json)
            #拿到帖子具体信息

        pass



    def get_comment_list(self, response):
        """
        获取评论分页
        :param response:
        :return:
        """
        logging.info(response.url)

        callback_id = response.meta['callback_id']
        text = response.text.replace('\t', '')

        _json = json.loads(text[len(callback_id) + 1:-1])

        if len(_json['re']) == 0:
            retry_request = response.request.copy()
            retry_request.dont_filter = True
            logging.info('comments len error ,retry ... ')
            return retry_request

        for comment in _json['re']:
            item = EastmoneyCommentItem(comment)
            yield item
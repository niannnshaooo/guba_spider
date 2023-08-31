import logging
import urllib

import scrapy
from scrapy import Selector
from guba_spider.items import EastMoneyPostItem, EastmoneySpiderItem, EastmoneyCommentItem
import re
import math
import json
import time
import numpy

class EastmoneySpider(scrapy.Spider):

    #开始hi时间，早于这个时间就不进行爬取了
    start_date = '2023-08-01'

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
        li_list = Selector(response).xpath(
            '//div[@class="ngbglistdiv"]/ul/li'
        ).extract()

        count = 0

        stock_list = []
        for item in li_list:
            stock_list.append(Selector(text=item).xpath('//a/@href').extract_first())

        stock_list = '600030,601998,601669,601728,601818,600028,601377,601800,601236,601816'.split(',')
        # stock_list = '601601,601166,600999,603288,600958,601888,601186,601006,603501,601328'.split(',')
        # stock_list = '600030,601998,601669,601728,601818,600028,601377,601800,601236,601816,601601,601166,600999,603288,600958,601888,601186,601006,603501,601328,600690,600887,600637,600519,600009,600795,600150,601995,600438,601198,600104,601857,601336,603260,600436,601628,601066,601658,601225,601985,600919,601211,600276,600019,600606,601088,601988,600036,601939,601319,603259,601633,601878,600809,600050,600111,600703,600089,600048,600109,601229,601111,601989,688599,688111,600485,600015,603986,601788,603160,601318,601919,601899,601901,601766,601881,600346,600018,601390,600900,603993,600000,600016,600745,600918,600196,600585,600837,600340,600570,600010,601398,601688,600518,601138,601727,601360,600029,600893,601668,600309,600905,600031,600406,601288,600100,603799,600547,600588,601169,601012'.split(',')

        for stock in stock_list:
            item = EastmoneySpiderItem()
            item['stockname'] = re.sub(r'<.*?>', '', stock)
            item['page'] = 1 #从第一页开始
            item['home_page'] = "http://guba.eastmoney.com/list,"+item['stockname'] + '_' + str(item['page']) +'.html'

            yield scrapy.Request(
                url=item['home_page'],
                meta={'item': item},
                callback=self.get_article_url,
                dont_filter=True
            )
            count += 1

            # # 测试，仅获取1个
            # if count >= 10:
            #     break

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
        page = item['page']
        code = item['stockname']

        _json = self.get_article_list(response=response)
        if _json is None:
            retry_request = response.request.copy()
            retry_request.dont_filter = True
            logging.info('scripts len error ,retry ... {}'.format(response.url))
            yield retry_request
        else:
            size = 80
            count = _json['count']
            page_size = int(count/size)
            if page_size % size > 0:
                page_size += 1

            # for p in range(page_size):
            #     page_url = response.url.split('.html')[0] + '_' + str(p + 1) + '.html'
            #
            #     # count +=1
            #     # if count>1:
            #     #     break
            #
            #     yield scrapy.Request(
            #         url=page_url,
            #         meta={'item': item},
            #         callback=self.get_article_url,
            #         dont_filter=True
            #     )

            # 获取帖子详情和评论内容
            yield scrapy.Request(
                url='http://guba.eastmoney.com/list,'+code + '_' + str(page) + '.html',
                meta={'item': item},
                callback=self.get_article_url,
                dont_filter=True
            )



            # 还有分页，继续
            if page < page_size:
                item['page'] = page + 1
                yield scrapy.Request(
                    url='http://guba.eastmoney.com/list,'+code + '_' + str(page+1) + '.html',
                    meta={'item': item},
                    callback=self.parse_page_num,
                    dont_filter=True
                )

    def get_article_url(self, response):
        """
        获取每个页面的帖子列表
        :param response:
        :return:
        """
        logging.info(response.url)

        rep_item = response.meta['item']
        code = rep_item['stockname']
        page = rep_item['page']

        _json = self.get_article_list(response=response)
        if _json is None:
            retry_request = response.request.copy()
            retry_request.dont_filter = True
            logging.info('scripts len error ,retry ... {}'.format(response.url))
            yield retry_request
        else:
            count = 0

            go_next_page = True
            size = 80
            count = _json['count']
            page_size = int(count / size)
            if page_size % size > 0:
                page_size += 1
            if page >= page_size:
                logging.info(rf'[{code}] last page ({page}/{page_size}), done!')
                go_next_page = False

            # mainlist > div > ul > li.defaultlist > table > tbody > tr:nth-child(57) > td:nth-child(3) > div > a
            a_list = Selector(response).xpath(
                '//tbody[@class="listbody"]/tr[@class="listitem"]/td[3]/div/a'
            ).extract()

            title_url = {}
            for item in a_list:
                href = Selector(text=item).xpath('//a/@href').extract_first()
                title = Selector(text=item).xpath("//a/text()").extract_first()
                title_url[title] = href

            for item in _json['re']:
                publish_date = item['post_last_time'][0:11]

                if publish_date < self.start_date:
                    go_next_page = False
                    continue

                if item['post_title'] in title_url:
                    # yield item
                    post_id = item['post_id']

                    path = title_url[item['post_title']]
                    if title_url[item['post_title']].startswith('//'):
                        url = 'https:'+path
                        # 财富号的帖子
                        yield scrapy.Request(
                            url=url,
                            meta={'item': item},
                            callback=self.get_caifuhao_detail,
                            dont_filter=True
                        )
                    else:
                        url = 'http://guba.eastmoney.com' + path
                        # 用户帖
                        yield scrapy.Request(
                            url=url,
                            meta={'item': item},
                            callback=self.get_article_detail,
                            dont_filter=True
                        )

                    #请求评论列表信息
                    ts = int(time.time() * 1000)
                    callback_id = 'jQuery1830{}{}_{}'.format(int(numpy.random.random_sample() * 10000000),
                                                             int(numpy.random.random_sample() * 10000000), ts)
                    p = 1
                    ps = 10000
                    url = rf'https://gbapi.eastmoney.com/reply/JSONP/ArticleNewReplyList?callback={callback_id}&plat=web&version=300&product=guba&postid={post_id}&sort=1&sorttype=1&p={p}&ps={ps}&type=0'

                    yield scrapy.Request(
                        url=url,
                        meta={'callback_id': callback_id, 'stock_name': code, 'post_id': post_id},
                        callback=self.get_comment_list,
                        dont_filter=True
                    )

            if go_next_page:
                # 获取下一页
                rep_item['page'] = page+1
                yield scrapy.Request(
                    url='http://guba.eastmoney.com/list,' + code + '_' + str(rep_item['page']) + '.html',
                    meta={'item': rep_item},
                    callback=self.get_article_url,
                    dont_filter=True
                )
            else:
                logging.info(rf'{code} finished!')


    def get_caifuhao_detail(self, response):

        logging.info('caifuhao_detail:{}'.format(response.url))

        # title = Selector(response).xpath('//*[@id="main"]/div[2]/div[1]/div[1]/div[1]/div[1]/h1/text()').extract_first().replace("\r\n", "").replace(" ", "")
        content = Selector(response).xpath('//*[@id="main"]/div[2]/div[1]/div[1]/div[1]/div[3]/div[1]').extract_first()

        item = response.meta['item']
        item['post_content'] = content

        item = EastMoneyPostItem(item)

        return item

    def get_article_detail(self, response):
        """
        每个帖子的详情
        :param response:
        :return:
        """
        logging.info('article_detail:{}'.format(response.url))

        scripts = Selector(response).xpath('//script/text()').getall()

        item = response.meta['item']

        # index = 0
        # for script in scripts:
        #     logging.info('[{}] {}'.format(index, script))
        #     index += 1

        if len(scripts) >= 4:
            script = scripts[3]
            _json = script.replace('var post_article=', '').replace('\t', '')
            # _json = _json[0:_json.find(';    var other_list=')]
            _json = json.loads(_json)
            # print(_json)
            item['post_content'] = _json['post_content']
            item = EastMoneyPostItem(item)

            yield item
            #拿到帖子具体信息

        pass



    def get_comment_list(self, response):
        """
        获取评论分页
        :param response:
        :return:
        """
        logging.info('comment_list:{}'.format(response.url))

        callback_id = response.meta['callback_id']
        text = response.text.replace('\t', '')

        _json = json.loads(text[len(callback_id) + 1:-1])

        # if len(_json['re']) == 0:
        #     retry_request = response.request.copy()
        #     retry_request.dont_filter = True
        #     logging.info('comments len error ,retry ... ')
        #     return retry_request

        if _json['re'] is not None:
            for comment in _json['re']:
                item = EastmoneyCommentItem(comment)
                yield item
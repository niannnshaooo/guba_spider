# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import os

import pymongo.errors
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from guba_spider.items import EastMoneyPostItem, EastmoneyCommentItem
from scrapy import signals
from scrapy.exporters import CsvItemExporter
from pymongo.mongo_client import MongoClient

class GubaSpiderPipeline:
    def process_item(self, item, spider):
        return item


class MongoDBPipeline(object):
    """保存爬虫数据到mongodb中"""

    dbs = {
        EastMoneyPostItem.__name__.lower(): 'post',
        EastmoneyCommentItem.__name__.lower(): 'comment'
    }

    DB_URI = 'mongodb://admin:123456@192.168.1.102/admin'
    DB_NAME = 'guba'

    #
    # def __init__(self, settings):
    #     super().__init__(settings=settings)
    #     self.DB_URI = settings.get('MONGO_DB_URI')
    #     self.DB_NAME = settings.get('MONGO_DB_NAME')
    #
    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(crawler.settings)

    def open_spider(self, spider):
        """spider处理数据前，调用该方法，此处主要打开数据库"""
        self.client = MongoClient(self.DB_URI)
        self.db = self.client[self.DB_NAME]

    def close_spider(self, spider):
        """spider关闭时，调用该方法，关闭数据库"""
        self.client.close()

    def process_item(self, item, spider):
        collection = self.dbs[type(item).__name__.lower()]
        # post = dict(item)
        try:
            self.db[collection].insert_one(dict(item))
        except pymongo.errors.DuplicateKeyError as e:

            pass
        return item


DATADIR = r'.'

class ExportPipeline:
    dbs = [EastMoneyPostItem, EastmoneyCommentItem]
    exporters = {}

    @staticmethod
    def dbname(db):
        return db.__name__.lower()

    @staticmethod
    def file_path(file, folder=DATADIR):
        return os.path.abspath(os.path.join(folder, file))

    def open_spider(self, spider):

        for db in self.dbs:
            db_name = self.dbname(db)
            logging.info(f"exporting {db_name}s to {db_name}s.csv")
            e = CsvItemExporter(open(self.file_path(f"{db_name}s.csv"), 'wb'))
            self.exporters[db_name] = e
            self.exporters[db_name].start_exporting()

        return spider

    def close_spider(self, spider):
        for k, e in self.exporters.items():
            e.finish_exporting()

        return spider

    def process_item(self, item, spider):
        for db in self.dbs:
            if isinstance(item, db):
                db_name = self.dbname(db)
                self.exporters[db_name].export_item(item)
        return item
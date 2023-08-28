# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import os

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from guba_spider.items import EastMoneyPostItem, EastmoneyCommentItem
from scrapy import signals
from scrapy.exporters import CsvItemExporter

class GubaSpiderPipeline:
    def process_item(self, item, spider):
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
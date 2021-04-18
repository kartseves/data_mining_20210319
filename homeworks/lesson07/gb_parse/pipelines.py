# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request

import os
import dotenv
from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient


class GbParsePipeline:
    def process_item(self, item, spider):
        return item


class GbParseMongoPipeline:
    def __init__(self):
        self.db_client = MongoClient()
        mongo_server = SSHTunnelForwarder(
            "192.168.1.13",
            ssh_username=os.getenv("SSH_USERNAME"),
            ssh_password=os.getenv("SSH_PASSWORD"),
            remote_bind_address=('127.0.0.1', 27017)
        )
        mongo_server.start()
        self.mongo_server = mongo_server
        mongo_client = MongoClient('127.0.0.1', mongo_server.local_bind_port)
        self.db = mongo_client["gb_data_mining_20210319"]

    def process_item(self, item, spider):
        self.db[f"{spider.name}_{spider.coll_name}"].insert_one(item)
        return item


class GbImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item.get("photos", []):
            yield Request(url)

    def item_completed(self, results, item, info):
        if "photos" in item:
            item["photos"] = [itm[1] for itm in results]
        return item

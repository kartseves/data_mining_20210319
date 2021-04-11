# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
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
            ssh_username="username",
            ssh_password="********",
            remote_bind_address=('127.0.0.1', 27017)
        )
        mongo_server.start()
        self.mongo_server = mongo_server
        mongo_client = MongoClient('127.0.0.1', mongo_server.local_bind_port)
        self.db = mongo_client["gb_data_mining_20210319"]

    def process_item(self, item, spider):
        self.db[f"{spider.name}_{spider.coll_name}_xpath"].insert_one(item)
        return item

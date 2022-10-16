import pymongo

class MongoDB():
    def __init__(self, mondb_addr, db_name, collection) -> None:
        self.client = pymongo.MongoClient(mondb_addr)
        db = self.client[db_name]
        if collection not in db.list_collection_names():
            raise Exception("Collection {} doesn't exist. Pls create it in mongdb")
        self.collection = db[collection]

    def insert_data(self, data_in_json):
        self.collection.insert_one(data_in_json)

    def find_data(self, mongo_scipt, order = pymongo.DESCENDING):
        return self.collection.find(mongo_scipt)

    def find_data_order_by_date(self, mongo_scipt, order = pymongo.DESCENDING):
        return self.collection.find(mongo_scipt).sort('date',pymongo.DESCENDING)

    def find_one(self, mongo_scipt):
        a = self.collection.count_documents(mongo_scipt)
        print(a)
        return a

    def check_exist(self, mongo_scipt):
        return self.collection.count_documents(mongo_scipt) > 0

    def find_data_distinct(self, mongo_scipt):
        return self.collection.distinct(mongo_scipt)

    def delete_one(self, mongo_scipt):
        return self.collection.delete_one(mongo_scipt)
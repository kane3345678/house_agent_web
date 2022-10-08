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

    def find_data(self, mongo_scipt):
        return self.collection.find(mongo_scipt)

    def find_one(self, mongo_scipt):
        a = self.collection.count_documents(mongo_scipt)
        print(a)
        return a

    def check_exist(self, mongo_scipt):
        return self.collection.count_documents(mongo_scipt) > 0

'''


import datetime
db = MongoDB("mongodb://localhost:27017/", "house", "house_hist")
#db.insert_data({"house_name": "", "price": 50, "address": "新北市中和區","date":datetime.datetime(2022, 10, 8, 11)})
#db.insert_data({"house_name": "", "price": 50, "address": "新北市中和區","date":datetime.datetime(2022, 10, 9, 11)})
d = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, datetime.datetime.now().hour)
print(d)
data = db.find_data({"date": {"$eq": d}})
for i in data:
    print(i)
exit(0)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["house"]
dblst = myclient.list_database_names()
mycol = mydb["house"]
collst = mydb.list_collection_names()
if "house" in collst:
  print("testMongoCol集合已存在！")
  mytestData = { "name": "Allen", "gender": "male", "address": "苗栗縣苑裡鎮" }
  x = mycol.insert_one(mytestData)
  x = mycol.find_one()
print(x)
'''
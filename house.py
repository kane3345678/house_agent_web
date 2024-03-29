import common
from mongo import MongoDB
import datetime
from pathlib import Path
from selenium.webdriver.common.by import By
import os
import time
from bson.objectid import ObjectId
class house_info():
    def __init__(self, name, obj_id, url, price, addr, timestamp, community = "TBD", year = 0, floor = -1, age = -1, need_update = False) -> None:
        self.url = url
        self.year = year
        self.name = name
        self.obj_id = obj_id
        self.price = price
        self.addr = addr
        self.floor = floor
        self.age = age
        self.community = community
        self.now_timestamp = timestamp
        self.date_time_str = self.now_timestamp.strftime("%Y-%m-%d-%H")
        self.need_update = need_update

    def house_info_to_json_data(self):
        price_history = {"date":self.date_time_str, "price":self.price}
        house_data = {"name":self.name, 'price':[price_history], 'addr':self.addr, 'url':self.url}
        return house_data

    def save_house_info_to_json_data(self, json_path):
        house_data = self.house_info_to_json_data()
        history = common.read_json(json_path)
        if history != None:
            house_data = history
            # since we have a history for this house, let's append the price to the history
            price_info = {"date":self.date_time_str, "price":self.price}
            # check if the price history exist or not
            house_data['price'].append(price_info)

        common.save_json(house_data, json_path)

    def get_price(self):
        # get price
        pass

    def get_screenshot(self):
        pass

 
# Abstract class for house agent webcrawler
# will be used in future
class house_agent_web():
    def __init__(self, webdriver, url, region) -> None:
        self.init_time_stamp()
        self.webdriver = webdriver
        self.url = url
        self.region = region
        self.house_obj_list = []
        self.new_house_obj_list = []
        self.num_house = 0
        self.house_list = []
        self.num_pages = 0
        self.db = MongoDB(common.get_config("mongodb", "mongodb://localhost:27017/"),
            common.get_config("mongodb_dbname", "house"),
            common.get_config("mongodb_collection", "house_hist"))

    def get_house_list(self):
        pass

    def screen_shot_house_briefly(self, url):
        pass

    def create_host_list(self):
        pass

    def delete_house_by_price_db(self, obj_id, price):
        same_price_house = list(self.db.find_data({"house_obj_id":obj_id, "price":price}))
        for i in range(len(same_price_house) - 1):
            self.db.delete_one({"_id":ObjectId(same_price_house[i]["_id"])})

    def screen_shot_house_and_save_house_info(self):
        house_no = 0
        retry = 0
        while house_no < len(self.house_obj_list):
            house_info_obj = self.house_obj_list[house_no]

            try:
                print(house_info_obj.name, house_info_obj.price, house_info_obj.url, house_info_obj.addr)
                last_hist_price = self.check_latest_price_from_mongodb(house_info_obj.obj_id)
                need_to_fetch = False
                self.house_obj_list[house_no].community = self.get_comm_name_in_db(house_info_obj.obj_id)
                self.house_obj_list[house_no].floor = self.get_floor_in_db(house_info_obj.obj_id)

                # when the floor in db is -1, better to let it check the info on website
                if self.house_obj_list[house_no].floor == -1:
                    need_to_fetch = True
                self.house_obj_list[house_no].age = self.get_age_in_db(house_info_obj.obj_id)
                # this will find out if the house is updated by datetime.now() or not
                if last_hist_price == house_info_obj.price and need_to_fetch == False:
                    print("obj_id {}, price unchanged {}, skip and kill same record".format(house_info_obj.obj_id, house_info_obj.price))
                    # rm the same price in db
                    self.delete_house_by_price_db(house_info_obj.obj_id, last_hist_price)
                else:
                    print("obj_id {}, price changed; before: {}, after: {}".format(house_info_obj.obj_id, last_hist_price, house_info_obj.price))

                    obj_number = house_info_obj.obj_id
                    house = self.get_web_obj_for_screen_shot(house_info_obj)

                    self.house_obj_list[house_no].community = self.get_community_name()
                    self.house_obj_list[house_no].floor = self.get_house_floor()

                    # if the house is close already, then skip
                    if self.house_obj_list[house_no].community == "close":
                        print("house %s  is close" % house_info_obj.name)
                        self.house_obj_list.pop(house_no)
                        continue

                    self.house_obj_list[house_no].age = self.get_house_age()

                    screen_shot_path = os.path.join("data", self.agent_name.lower(), self.region, obj_number)
                    Path(screen_shot_path).mkdir(parents=True, exist_ok=True)

                    png_path = os.path.join(screen_shot_path, "{}_house.png".format(self.date_time_str))
                    json_path = os.path.join(screen_shot_path, "{}_house.json".format(obj_number))
                    house_info_obj.save_house_info_to_json_data(json_path)
                    house.screenshot(png_path)
                    self.webdriver.execute_script("window.scrollTo(0, 800);")
                    time.sleep(0.5)
                    png_path = os.path.join(screen_shot_path, "{}_house2.png".format(self.date_time_str))
                    house.screenshot(png_path)
                    time.sleep(1.5)

            except Exception as e:
                print("While screenshot {}", house_info_obj.url)
                print("Exception happen {}", str(e))
                print("take a rest for 5 mins since we migh blocked by the server now, retry = {}".format(retry))
                time.sleep(300)
                if retry < 3:
                    retry += 1
                    continue
                print("Give up retry")

            print("{}/{} houses are captured".format(house_no, len(self.house_obj_list)))
            retry = 0
            house_no += 1

    def init_time_stamp(self):
        self.now = datetime.datetime.now()
        self.date_time_str = self.now.strftime("%Y-%m-%d-%H")

    # This function will check if the given house info with timestamp ever captured

    def house_info_exist_in_db(self, house_info_obj):
        date = datetime.datetime(self.now.year, self.now.month,
                                    self.now.day, self.now.hour)
        return self.db.check_exist({"date": {"$eq": date}, "house_obj_id":house_info_obj.obj_id})

    def get_comm_name_in_db(self, objid):
            # check if community is filled in db:
        filter = {"house_obj_id":objid, "community":{"$ne":"TBD"}}
        data = list(self.db.find_data(filter))
        if len(data) != 0:
            return data[0]["community"]
        else:
            return "TBD"

    def get_age_in_db(self, objid):
        filter = {"house_obj_id":objid, "age": {"$exists": True}}
        data = list(self.db.find_data(filter))
        if len(data) != 0:
            return data[0]["age"]
        else:
            return -1

    def get_floor_in_db(self, objid):
        filter = {"house_obj_id":objid, "floor": {"$exists": True}}
        data = list(self.db.find_data(filter))
        if len(data) != 0:
            return data[-1]["floor"]
        else:
            return -1

    def save_house_to_mongodb(self):
        # The timestamp in database is 8 hour basis
        # ex: if we fetch data at 10PM, then the data fetched in 2PM is considered exist
        db_data_date = datetime.datetime(self.now.year, self.now.month,
                                    self.now.day, max(self.now.hour - 8, 0))
        new_data_date = datetime.datetime(self.now.year, self.now.month,
                                    self.now.day, self.now.hour)

        for house in self.house_obj_list:
            data = {"house_name": house.name, "house_obj_id":house.obj_id, "price":house.price,
                    "addr":house.addr, "url":house.url, "community":house.community, "date":new_data_date,
                    "age":house.age, "floor":house.floor}
            #if not self.db.check_exist({"date": {"$gte": db_data_date}, "house_obj_id":house.obj_id}):
            # remove redundant data in db
            self.delete_house_by_price_db(house.obj_id, house.price)
            self.db.insert_data(data)

    def check_latest_price_from_mongodb(self, obj_id):
        data = list(self.db.find_data_order_by_date({"house_obj_id":obj_id}))
        if len(data) == 0:
            return None
        else:
            return int(data[0]['price'])

    def check_price_changed(self, obj_id, price):
        last_hist_price = self.check_latest_price_from_mongodb(obj_id)
        if last_hist_price == None:
            return False
        else:
            return last_hist_price != price

    def check_new_house(self, house_obj_id):
        filter = {"house_obj_id":house_obj_id}
        return not self.db.check_exist(filter)

    def is_house_close(self, house_obj_id):
        filter = {"house_obj_id":house_obj_id}
        return not self.db.check_exist(filter)
import common
from mongo import MongoDB
import datetime

class house_info():
    def __init__(self, name, obj_id, url, price, addr, timestamp, community = "TBD", year = 0) -> None:
        self.url = url
        self.year = year
        self.name = name
        self.obj_id = obj_id
        self.price = price
        self.addr = addr
        self.community = community
        self.now_timestamp = timestamp
        self.date_time_str = self.now_timestamp.strftime("%Y-%m-%d-%H")

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
            for p_info in house_data['price']:
                if price_info["date"] not in p_info["date"]:
                    house_data['price'].append(price_info)
                else:
                    print("skip")
                    break

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
        self.db = MongoDB("mongodb://localhost:27017/", "house", "house_hist")

    def get_house_list(self):
        pass

    def screen_shot_house_briefly(self, url):
        pass

    def create_host_list(self):
        pass

    def screen_shot_house_and_save_house_info(self):
        pass

    def init_time_stamp(self):
        self.now = datetime.datetime.now()
        self.date_time_str = self.now.strftime("%Y-%m-%d-%H")

    # This function will check if the given house info with timestamp ever captured
    # The timestamp in database is hour basis
    def house_info_exist_in_db(self, house_info_obj):
        date = datetime.datetime(self.now.year, self.now.month,
                                    self.now.day, self.now.hour)        
        return self.db.check_exist({"date": {"$eq": date}, "house_obj_id":house_info_obj.obj_id})

    def save_house_to_mongodb(self):
        date = datetime.datetime(self.now.year, self.now.month,
                                    self.now.day, self.now.hour)

        for house in self.house_obj_list:
            data = {"house_name": house.name, "house_obj_id":house.obj_id, "price":house.price,
                    "addr":house.addr, "url":house.url, "community":house.community, "date":date}
            if not self.db.check_exist({"date": {"$eq": date}, "house_obj_id":house.obj_id}):
                self.db.insert_data(data)

    def check_new_house(self, house_obj_id):
        filter = {"house_obj_id":house_obj_id}
        return not self.db.check_exist(filter)
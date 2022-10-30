from selenium import webdriver
import time
from sinyi import sinyi_web
from yunching import yun_ching_web
import common
from argparse import ArgumentParser
import common as c
from mongo import MongoDB
import datetime
import os
import datetime
from tqdm import tqdm

date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H")

parser = ArgumentParser()
parser.add_argument("-f", "--function", help="Decide what function is run", dest="func", default="fetch_price")
args = parser.parse_args()
all_agents = [
        {
            "agent":yun_ching_web,
            "website": [
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%B0%B8%E5%92%8C%E5%8D%80_c/2000-4900_price", "region":"永和"},
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E4%B8%AD%E5%92%8C%E5%8D%80_c/2000-4900_price/", "region":"中和"},
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%96%B0%E8%8E%8A%E5%8D%80_c/2000-4900_price/", "region":"新莊"},
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%9D%BF%E6%A9%8B%E5%8D%80_c/2000-4900_price/", "region":"板橋"}

            ]
        },
        {
            "agent":sinyi_web,
            "website": [
                {"url":"https://www.sinyi.com.tw/buy/list/2000-4500-price/NewTaipei-city/234-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"永和"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-4500-price/NewTaipei-city/242-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"新莊"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-4500-price/NewTaipei-city/235-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"中和"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-4500-price/NewTaipei-city/220-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"板橋"}

            ]
        }
]

def init_browser():
    configs = common.read_json("config.json")
    driver = webdriver.Chrome(executable_path=configs["chromedriver_path"])
    driver.maximize_window()
    return driver

def init_database(db_name=None, collection=None):
    if db_name == None:
        print("Loading database assigned by config.json")
        db = MongoDB(c.get_config("mongodb", "mongodb://localhost:27017/"),
                c.get_config("mongodb_dbname", "house"),
                c.get_config("mongodb_collection", "house_hist"))
    else:
        print("Loading database assigned {}, {}".format(db_name, collection))
        db = MongoDB("mongodb://localhost:27017/", db_name, collection)
    return db

def fetch_price():
    configs = common.read_json("config.json")
    driver = webdriver.Chrome(executable_path=configs["chromedriver_path"])
    driver.maximize_window()
    for ag in all_agents:
        agent_class = ag["agent"]
        for website in ag["website"]:
            ag_web = agent_class(driver, website["url"], website["region"])
            print("Capturing data for {} from agent {}".format(website["region"], ag_web.agent_name))
            ag_web.get_house_list()
            ag_web.screen_shot_house_and_save_house_info()
            ag_web.save_house_to_mongodb()

            print("New houses:")
            for i in ag_web.new_house_obj_list:
                print(i.url)
            print()
            print("sleep 300s in case you are blocked by target server")
            time.sleep(1)

    driver.quit()

def show_price_cut():
    db = init_database()
    house_obj_list = db.find_data_distinct("house_obj_id")
    all_data = {"full_data":[]}

    for i in tqdm(house_obj_list):
        house_data = db.find_data_order_by_date({"house_obj_id":i})
        house_data = list(house_data)
        # compare the first and last data to decide if price is changed
        if house_data[-1]['price'] != house_data[0]['price']:
            print("=" * 20)
            print(house_data[0])
            print(house_data[-1])
            print("=" * 20)
            house_data[0].pop("_id")

            # save it to mongo db
            house_data[0]["price_changed"] = "yes"
            db.insert_data(house_data[0])

            house_data[0]['prve_price'] = house_data[-1]['price']
            house_data[0]['date'] = str(house_data[0]['date'])
            house_data[0].pop("_id")

            all_data["full_data"].append(house_data[0])

    if len(all_data["full_data"]):
        c.save_json(all_data, os.path.join("sales_history","price_cut_" + date_str + ".json"))

def show_new_house():
    db = init_database()

    house_obj_list = db.find_data_distinct("house_obj_id")
    all_data = {"full_data":[]}

    for i in tqdm(house_obj_list):
        house_data = db.find_data({"house_obj_id":i})
        house_data = list(house_data)

        if len(house_data) == 1:
            latest_data_date = house_data[0]['date']
            now = datetime.datetime.now()
            diff = now - latest_data_date
            # new house data must be one day old only
            if diff.days * 86400 + diff.seconds < 86400:
                print("=" * 20)
                print(house_data[0])
                print("=" * 20)
                house_data[0].pop("_id")
                house_data[0]['date'] = str(house_data[0]['date'])
                all_data["full_data"].append(house_data[0])

    if len(all_data["full_data"]):
        c.save_json(all_data, os.path.join("sales_history","new_house_" + date_str + ".json"))

def check_house_close_on_website(driver, url):
    yc_web = yun_ching_web(driver, "", "")
    sinyi = sinyi_web(driver, "", "")
    if "yungching" in url:
        return yc_web.check_house_obj_close(url)
    else:
        return sinyi.check_house_obj_close(url)

def find_close_case():
    db = init_database()
    driver = init_browser()

    house_obj_list = db.find_data_distinct("house_obj_id")
    all_data = {"full_data":[]}

    def all_data_append(house_data):
        house_data[0].pop("_id")
        house_data[0]['date'] = str(house_data[0]['date'])
        all_data["full_data"].append(house_data[0])

    for i in tqdm(house_obj_list):
        house_data = db.find_data_order_by_date({"house_obj_id":i})
        house_data = list(house_data)

        latest_data_date = house_data[0]['date']
        now = datetime.datetime.now()
        diff = now - latest_data_date
        if diff.days <= 0:
            # it means the house data is updated today
            continue
        elif db.check_exist({"close":'yes', "house_obj_id":i}):
            # database indicates the house data is closed before
            all_data_append(house_data)
            continue
        elif check_house_close_on_website(driver, house_data[0]["url"]):
            # found house is not updated and not found on website
            print("=" * 20)
            print(house_data[0])
            print("=" * 20)
            all_data_append(house_data)
            # save it to mongo db
            db.insert_data(house_data[0])
    if len(all_data["full_data"]):
        c.save_json(all_data, os.path.join("sales_history","close_case_" + date_str + ".json"))

args.func = "show_price_cut"
if args.func == "fetch_price":
    fetch_price()

elif args.func == "show_price_cut":
    show_price_cut()

elif args.func == "show_new_house":
    show_new_house()

elif args.func == "find_close_case":
    find_close_case()
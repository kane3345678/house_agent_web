from selenium import webdriver
import time
from sinyi import sinyi_web
from yunching import yun_ching_web
from fivenineone import fivenineone_web
import random
import common
from argparse import ArgumentParser
import common as c
from mongo import MongoDB
import datetime
import os
import datetime
from tqdm import tqdm
from datetime import date
import house_list
from selenium.webdriver.chrome.service import Service
from bson.objectid import ObjectId

date_str = datetime.datetime.now().strftime("%Y-%m-%d-%H")
today = date.today()
today_with_time = datetime.datetime(
    year=today.year,
    month=today.month,
    day=today.day,
)

parser = ArgumentParser()
parser.add_argument("-f", "--function", help="Decide what function is run", dest="func", default="fetch_price")
parser.add_argument("-j", "--json", help="json file", dest="js", default="")
parser.add_argument("-p", "--period", help="", dest="period", default=2)
parser.add_argument("-d", "--dist", help="", dest="district", default="")

args = parser.parse_args()

def init_browser():
    configs = common.read_json("config.json")
    s = Service(configs["chromedriver_path"])
    driver = webdriver.Chrome(service=s)
    driver.maximize_window()
    return driver

def init_database(db_name=None, collection=None):
    if db_name is None:
        db_name = c.get_config("mongodb_dbname", "house")
    if collection is None:
        collection = c.get_config("mongodb_collection", "house_hist")
    print("Loading database assigned {}, {}".format(db_name, collection))
    db = MongoDB(c.get_config("mongodb", "mongodb://localhost:27017/"), db_name, collection)
    return db

def fetch_price():
    """
    This function captures the data for all house agents websites, saves the house information to MongoDB, and takes a screenshot of the house.
    """
    configs = common.read_json("config.json")
    driver = webdriver.Chrome(executable_path=configs["chromedriver_path"])
    driver.maximize_window()
    for ag in house_list.all_agents:
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

def check_price_cut():
    """
    This function checks if the price of a house has changed and saves the information to MongoDB.
    """
    price_drop_db = init_database("house", "price_drop")
    db = init_database()
    house_obj_list = db.find_data_distinct("house_obj_id")
    all_data = {"full_data":{}}

    for i in tqdm(house_obj_list):
        house_data = db.find_data_order_by_date({"house_obj_id":i})
        house_data = list(house_data)
        latest_house_data = house_data[0]
        first_house_data = house_data[-1]
        # compare the first and last data to decide if price is changed
        if first_house_data['price'] != latest_house_data['price']:
            print("=" * 20)
            print(latest_house_data)
            print(first_house_data)
            print("=" * 20)
            latest_house_data.pop("_id")

            # save it to mongo db
            latest_house_data["price_changed"] = "yes"
            latest_house_data["date"] = today_with_time
            latest_house_data["region"] = c.get_region_from_addr(latest_house_data["addr"])
            latest_house_data['prve_price'] = house_data[-1]['price']
            price_drop_db.update_data({"house_obj_id":latest_house_data["house_obj_id"], "date":today_with_time},
                                 latest_house_data)
            latest_house_data['date'] = str(latest_house_data['date'])
            if latest_house_data["region"] not in all_data["full_data"]:
                all_data["full_data"][latest_house_data["region"]] = []
            all_data["full_data"][latest_house_data["region"]].append(latest_house_data)

    if len(all_data["full_data"]):
        c.save_json(all_data, os.path.join("sales_history","price_cut_" + date_str + ".json"))

def check_new_house():
    """
    This function checks for new house data that is one day old or less and saves it to a new_house_db.
    """
    db = init_database()
    new_house_db = init_database("house", "new_house")

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
            if diff.days < 1:
                house_data[0].pop("_id")
                house_data[0]['date'] = today_with_time
                all_data["full_data"].append(house_data[0])
                new_house_db.update_data({"house_obj_id":house_data[0]["house_obj_id"], "date":today_with_time},
                                 house_data[0])

def check_house_close_on_website(driver, url):
    yc_web = yun_ching_web(driver, "", "")
    sinyi = sinyi_web(driver, "", "")
    if "yungching" in url:
        return yc_web.check_house_obj_close(url)
    else:
        return sinyi.check_house_obj_close(url)

def locate_house_png(house_data):
    """
    This function locates the house png file in the data folder.
    and return the latest png file to the caller
    """
    # get current working folder path
    if "sinyi" in house_data["url"]:
        folder = os.path.join(os.getcwd(), "data", "sinyi")
    else:
        folder = os.path.join(os.getcwd(), "data", "yunching")
    possible_folder = c.search_folder(folder, house_data["house_obj_id"])
    return "file://" + c.find_latest_png_file(possible_folder)

def find_close_case():
    """
    This function checks if a house has been closed and saves the information to close_case collection in MongoDB.
    """
    db = init_database()
    driver = init_browser()
    db_close = init_database("house", "close_case")

    house_obj_list = db.find_data_distinct("house_obj_id")
    all_data = {"full_data":[]}

    def append_house_data(house_data):
        house_data[0].pop("_id")
        house_data[0]['date'] = str(house_data[0]['date'])
        all_data["full_data"].append(house_data[0])

    for i in tqdm(house_obj_list):
        house_data = db.find_data_order_by_date({"house_obj_id":i})
        house_data = list(house_data)
        latest_data_date = house_data[0]['date']
        now = datetime.datetime.now()
        diff = now - latest_data_date
        if diff.days <= 4:
            # it means the house data is updated today
            continue
        elif db.check_exist({"close":'yes', "house_obj_id":i}):
            # database indicates the house data is closed before
            append_house_data(house_data)
            continue
        elif check_house_close_on_website(driver, house_data[0]["url"]):
            # found house is not updated and not found on website
            print("=" * 20)
            print(house_data[0])
            print("=" * 20)
            # update all data to indicate it is closed
            if "age" not in house_data[0]:
                print("age doesn't exist, please input the age")

                # open png file in browser
                driver.get(locate_house_png(house_data[0]))
                age = float(input())
                for j in house_data:
                    j["age"] = age
            if house_data[0]["community"] == "NULL" and house_data[0]["age"] < 20:
                # open png file in browser
                driver.get(locate_house_png(house_data[0]))

                print(house_data[0])
                print("community is NULL, please input the community name")
                community = input()
                if community == "":
                    community = "NULL"
                for j in house_data:
                    j["community"] = community
            for j in house_data:
                j["close"] = "yes"
                db.update_data({"_id":j["_id"]}, j)
            # save it to mongo db
            house_data[0].pop("_id")
            db_close.insert_data(house_data[0])

            append_house_data(house_data)
    if len(all_data["full_data"]):
        c.save_json(all_data, os.path.join("sales_history","close_case_" + date_str + ".json"))
if args.func == "fetch_price":
    fetch_price()
    check_price_cut()
    check_new_house()

elif args.func == "check_price_cut":
    check_price_cut()

elif args.func == "check_new_house":
    check_new_house()

elif args.func == "find_close_case":
    find_close_case()

elif args.func == "show_price_drop_hist":
    db = init_database("house", "price_drop")
    start_date = datetime.datetime(2022, 10, 12)
    end_date = datetime.datetime.now()

    delta = datetime.timedelta(days=1)
    # iterate date from 10-12 to 12-31
    while (start_date <= end_date):
        mon = start_date.month
        day = start_date.day

        query = {"date": {"$gte": start_date,"$lt": start_date + delta}}
        data = list(db.find_data(query))
        if len(data) != 0:
            all_region = {}
            print("*"*50)
            print("date {}-{} = {}".format(mon, day, len(data)))
            for house in data:
                region = c.get_region_from_addr(house["addr"])
                if region not in all_region:
                    all_region[region] = []
                all_region[region].append(data)
            for i in all_region:
                print(i, len(all_region[i]))
        start_date += delta

elif args.func == "show_num_house_by_region":
    db = init_database()
    data = db.find_data_distinct("house_obj_id")

    all_region = {}
    for i in tqdm(range(len(data))):
        houseid = data[i]
        house_info = db.find_data({"house_obj_id":houseid})
        for house in house_info:
            addr = house["addr"]
            region = addr[0:6]
            # region is the first 6 unicode, ex: 新北市中和區
            if region not in all_region:
                all_region[region] = []
            all_region[region].append(data[i])
            break

    for i in all_region:
        print(i, len(all_region[i]))

elif args.func == "browse_new_house":
    new_house_db = init_database("house", "new_house")
    driver = init_browser()
    i = 0
    query_date = today_with_time
    while i < int(args.period):
        new_house = list(new_house_db.find_data({"date":query_date}))
        print("browse new house in {}".format(str(query_date)))
        for house in tqdm(new_house):
            driver.get(house["url"])
            input("press any key to continue browsing")
        query_date = query_date - datetime.timedelta(days=1)
        i += 1
    driver.close()

elif args.func == "browse_new_discounted_house":
    """
    This function browses discounted house data within the last ten days
    """
    price_drop_db = init_database("house", "price_drop")
    query_date_start = datetime.datetime(
        year=today.year,
        month=today.month,
        day=today.day,
    )

    # iterate last 10 days until it can find discounted house
    i = 10
    while i > 0:
        new_price_drop_house = price_drop_db.find_data({"date":query_date_start})
        time.sleep(1)
        discount_houses = list(new_price_drop_house)
        if len(discount_houses) != 0:
            print("found {} discounted house in {} ".format(len(discount_houses), str(query_date_start)))
            break
        print("No discounted house {}".format(str(query_date_start)))
        delta = datetime.timedelta(days=1)
        query_date_start -= delta
        i-=1

    driver = init_browser()
    query_date_end = query_date_start - datetime.timedelta(days=int(args.period))
    for house in tqdm(discount_houses):
        old_hist = {"house_obj_id":house["house_obj_id"],"date":{"$lt": query_date_end}}
        house_drop_hist = price_drop_db.find_data(old_hist)
        if len(list(house_drop_hist)) == 0:
            driver.get(house["url"])
            # press any key to continue browsing
            input("press any key to continue browsing")

    driver.close()

elif args.func == "591_collect_deal_by_region":
    driver = init_browser()
    fivenineone = fivenineone_web(driver, "", "")
    db = init_database("house", "deal")

    for gov_deal in house_list.gov_deal_591:
        comm_list = fivenineone.get_community_list(gov_deal["url"], gov_deal["district"])

        for comm in comm_list:
            comm_num_of_price = fivenineone.get_num_of_price(comm)
            db_num_of_price = len(list(db.find_data({"comm_id":comm["id"]})))
            if db_num_of_price == comm_num_of_price:
                print("{} no update".format(comm["name"]))
                continue
            comm_deal = fivenineone.get_deal_per_community(comm)
            for deal in comm_deal:
                deal["data_date"] = today_with_time
                db.insert_data(deal)


elif args.func == "cpking_collect_deal_by_region":
    from cpking import cpking_web
    driver = init_browser()
    cpking = cpking_web(driver, "", "")
    db = init_database("house", "deal_cpking")
    comm_db = init_database("house", "deal_comm_list_cpking")

    for gov_deal in house_list.gov_deal_cpking:
        # if args.district is provided, then only collet the deal data by given district
        if args.district != "" and gov_deal["district"] != args.district:
            continue
        comm_list = cpking.get_community_list(gov_deal["url"],gov_deal["district"])
        # save to mongo db

        for comm in tqdm(comm_list):
            comm_db.update_data({"id":comm["id"]}, comm)
            latest_comm_data = db.find_data({"communityID":comm["id"]})
            comm["num_data_in_db"] = len(list(latest_comm_data))
            if comm["dealCaseCount"] == comm["num_data_in_db"]:
                print("{} num of case no update".format(comm["name"]))
                continue
            time.sleep(random.randint(0,3))
            comm_deal = cpking.get_deal_per_community(comm)
            if comm_deal == []:
                print("{} no update".format(comm["name"]))
                continue
            # need to update community data
            db.delete_many({"communityID":comm["id"]})
            for deal in comm_deal:
                deal["data_date"] = today_with_time
                if len(comm_deal[0]["communityTags"]) != 0:
                    deal["comm_name"] = comm_deal[0]["communityTags"][0]
                else:
                    deal["comm_name"] = comm["name"]
                db.insert_data(deal)

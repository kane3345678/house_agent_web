from selenium import webdriver
import time
from sinyi import sinyi_web
from yunching import yun_ching_web
import common
from argparse import ArgumentParser

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
    from mongo import MongoDB
    db = MongoDB("mongodb://localhost:27017/", "house", "house_hist")
    house_obj_list = db.find_data_distinct("house_obj_id")
    for i in house_obj_list:
        house_data = db.find_data_order_by_date({"house_obj_id":i})
        house_data = list(house_data)

        # compare the first and last data to decide if price is changed
        if house_data[-1]['price'] != house_data[0]['price']:
            print("=" * 20)
            print(house_data[0])
            print(house_data[-1])
            print("=" * 20)

if args.func == "fetch_price":
    fetch_price()

elif args.func == "show_price_cut":
    show_price_cut()

from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import time
from pathlib import Path
from sinyi import sinyi_web
from yunching import yun_ching_web
import common

all_agents = [
        {
            "agent":yun_ching_web,
            "website": [
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%B0%B8%E5%92%8C%E5%8D%80_c/3000-4900_price/-15_age/", "region":"永和"},
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E4%B8%AD%E5%92%8C%E5%8D%80_c/3000-4900_price/-10_age/", "region":"中和"},
                #{"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%96%B0%E8%8E%8A%E5%8D%80_c/3000-4900_price/-10_age/", "region":"新莊"}
            ]
        },
        {
            "agent":sinyi_web,
            "website": [
                {"url":"https://www.sinyi.com.tw/buy/list/3000-4500-price/0-12-year/NewTaipei-city/234-zip/Taipei-R-mrtline/03-mrt/default-desc/index", "region":"永和"}
            ]
        }
]

configs = common.read_json("config.json")
driver = webdriver.Chrome(executable_path=configs["chromedriver_path"])
driver.maximize_window()
for ag in all_agents:
    agent_class = ag["agent"]
    for website in ag["website"]:
        ag_web = agent_class(driver, website["url"], website["region"])
        print("Capturing data for {} from agent {}".format(website["region"], ag_web.agent_name))
        ag_web.get_house_list()
        ag_web.create_host_list()
        ag_web.screen_shot_house_and_save_house_info()
        ag_web.save_house_to_mongodb()

        print("New houses:")
        for i in ag_web.new_house_obj_list:
            print(i.url)
        print()
        print("sleep 300s in case you are blocked by target server")
        time.sleep(1)

driver.quit()

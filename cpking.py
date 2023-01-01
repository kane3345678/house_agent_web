from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from pathlib import Path
from house import house_info
from house import house_agent_web
import re
import common as comm
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm
import datetime

class cpking_web(house_agent_web):
    def __init__(self, webdriver, url, region = "永和") -> None:
        super().__init__(webdriver, url, region)
        self.agent_name = "fivenineone"


    def get_num_pages(self):
        pass

    def get_house_list(self):
        pass

    def screen_shot_house_briefly(self, url):
        pass

    def create_host_list(self):
        pass

    def get_web_obj_for_screen_shot(self, house_info_obj):
        pass

    def check_house_obj_close(self, url):
        pass

    def scroll_down_up_to_refrest(self):
        # selenum scroll down to the bottom of the page
        self.webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        # selenum scroll up to the top of the page 
        self.webdriver.execute_script("window.scrollTo(0, 0);")

    def get_community_list(self, url, district_name):
        all_comm = []
        for page in range(1, 100):
            data = comm.download_json(self.webdriver, 
                    "{}/?p={}".format(url, page))
            if len(data["searchList"]) == 0:
                break
            for i in data["searchList"]:
                all_comm.append(i)
            time.sleep(0.4)
        print("Found {} communities".format(len(all_comm)))
        return all_comm


    def get_num_of_price(self, community_info):
        all_deal = []
        for page in range(1, 3):

            url = "https://community.houseprice.tw/ws/building/{}/price/date-desc_sort/?p={}".format(community_info["id"], page)
            data = comm.download_json(self.webdriver, url)
            for i in data["deal"]["list"]:
                all_deal.append(i)
        print("Found {} deals".format(len(all_deal)))
        return all_deal


    def get_deal_per_community(self, community_info):
        all_deal = []
        num_items = 1000000
        page = 1
        while len(all_deal) < num_items:
            try:
                url = "https://community.houseprice.tw/ws/building/{}/price/date-desc_sort/?p={}".format(community_info["id"], page)
                data = comm.download_json(self.webdriver, url)
                num_items = data["deal"]["pa"]["totalitemcount"]
            except Exception as e:
                print("page load failretry {}".format(url))
                time.sleep(10)
                continue
            if len(data["deal"]["list"]) == 0:
                print("No data found, keep trying page {}".format(page))
                time.sleep(10)
                continue
            page += 1
            # compare num data btwn cpking and db, see if it's necesary to update
            if community_info["num_data_in_db"] == num_items:
                print("latest data is same with database")
                return []

            for i in data["deal"]["list"]:
                all_deal.append(i)
            time.sleep(0.5)
        if len(all_deal) == 1:
            print("wrong")
        print("Found {} deals".format(len(all_deal)))
        return all_deal


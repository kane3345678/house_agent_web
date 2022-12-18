from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
from pathlib import Path
from house import house_info
from house import house_agent_web
import re

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm
import datetime

class fivenineone_web(house_agent_web):
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
        self.webdriver.get(url)

        WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "community-card")))

        # get num of community
        num_comm_obj = self.webdriver.find_elements(By.XPATH, '//*[@id="documentRef"]/section[1]/section[2]/div[1]/section')
        total_num_comm = num_comm_obj[0].text
        total_num_comm = int(re.findall("\d+", total_num_comm)[0])
        self.comm_list = []
        # keep refreshing the page to collect community
        while(len(self.comm_list) < total_num_comm):
            self.scroll_down_up_to_refrest()
            self.comm_list = self.webdriver.find_elements(By.XPATH, '//*[@id="documentRef"]/section[1]/section[2]/div[1]/a[*]')


        # collect all community info
        all_comm_list_dict = []
        for comm in self.comm_list:
            # selenium to get top-container class object of each community
            comm_info = comm.find_elements(By.CLASS_NAME, "top-container")[0]
            comm_url = comm.get_attribute('href')
            comm_name = comm_info.text.split("\n")[0]
            comm_dict = {"id":comm_url.split("/")[-1],
                         "name":comm_name,
                         "url":comm_url,
                         "district":district_name}
            print(comm_info.text.split("\n")[0], comm.get_attribute('href'))
            all_comm_list_dict.append(comm_dict)
        print("{} community are found".format(len(all_comm_list_dict)))
        return all_comm_list_dict


    def get_num_of_price(self, community_info):
        url = community_info["url"]
        self.webdriver.get(url + "/price")
        num_price_xpath = ['//*[@id="__nuxt"]/main/section/section[2]/div[3]/span/strong',
                            '//*[@id="__nuxt"]/main/section/section[2]/div[2]/span/strong']
        for xpath in num_price_xpath:
            try:
                WebDriverWait(self.webdriver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "total")))
                # get num of price
                num_comm_obj = self.webdriver.find_elements(By.XPATH, xpath)

                total_num_price = num_comm_obj[0].text
                total_num_price = int(re.findall("\d+", total_num_price)[0])
                return total_num_price
            except Exception as e:
                print(e)
                print(community_info)
                total_num_price = 0
        return total_num_price

    def get_deal_per_community(self, community_info):
        total_num_price = self.get_num_of_price(community_info)
        price_list = []
        while(len(price_list) < total_num_price):
            self.scroll_down_up_to_refrest()
            price_list = self.webdriver.find_elements(By.XPATH, '//*[@id="__nuxt"]/main/section/section[2]/section/section[*]')

        # first element is the column info
        price_list.pop(0)
        full_deal_info = []
        for house in tqdm(price_list):
            deal_info = {}
            house_info = house.find_elements(By.CLASS_NAME, "part-1")[0]
            info = house_info.text.split("\n")
            deal_info["yr_month"] = info[0]
            # '111-10' to AD 2022-10
            deal_date = deal_info["yr_month"].split("-")
            deal_date = "{}-{}".format(int(deal_date[0]) + 1911, deal_date[1])
            deal_info["deal_date"] = datetime.datetime.strptime(deal_date, "%Y-%m")
            deal_info["floor"] = info[1]
            deal_info["uni_price"] = info[2]

            house_info = house.find_elements(By.CLASS_NAME, "part-2")[0]
            info = house_info.text.split("\n")
            deal_info["house_price"] = info[0]
            deal_info["house_size"] = info[1]
            deal_info["car_price"] = info[2]
            deal_info["car_size"] = info[3]
            deal_info["total_price"] = info[4]

            house_info = house.find_elements(By.CLASS_NAME, "part-3")[0]
            info = house_info.text.split("\n")
            deal_info["addr"] = info[0].replace(" | ", "")
            deal_info["uid"] = "591" + "_" + community_info['id'] + "_" + deal_info["yr_month"] + "_" + deal_info["addr"]
            deal_info["comm_id"] = community_info['id']
            deal_info["comm_name"] = community_info['name']
            deal_info["district"] = community_info['district']
            full_deal_info.append(deal_info)
        return full_deal_info


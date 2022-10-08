from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import datetime
import time
from pathlib import Path
from house import house_info
from house import house_agent_web
import re

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class yun_ching_web(house_agent_web):
    def __init__(self, webdriver, url, region = "永和") -> None:
        super().__init__(webdriver, url, region)
        self.agent_name = "YunChing"

    def get_house_list(self):
        self.webdriver.get(self.url)        
        WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "m-list-item")))

        self.house_list = self.webdriver.find_elements(By.XPATH, "/html/body/main/div[2]/ul")
        self.num_house = len(self.house_list[0].find_elements(By.CLASS_NAME, "m-list-item"))

        print("{} houses found ".format(self.num_house))

    # this function is used to screen shot house info from the house list 
    # the house list example can be found from below website
    # https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%B0%B8%E5%92%8C%E5%8D%80_c/3000-4900_price/
    def screen_shot_house_briefly(self, url):
        cnt = 0
        self.webdriver.get(url)

        for i in range(1, self.num_house):
            house = self.webdriver.find_element(By.XPATH, "/html/body/main/div[2]/ul/li[{}]".format(i))
            house_name = house.find_element(By.TAG_NAME, "a")
            print(house_name.accessible_name)
            obj_url = house_name.get_attribute('href')
            obj_number = obj_url.split("/")[-1]
            screen_shot_path = os.path.join("yunching", obj_number)
            os.system("mkdir {}".format(screen_shot_path))
            png_path = os.path.join(screen_shot_path, "{}_house.png".format(self.date_time_str))

            house.screenshot(png_path)
            cnt += 1

    # this function is to scan through houses in house list by search criteria and make a list for hosue_info_obj
    # the house list is like below
    # https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%B0%B8%E5%92%8C%E5%8D%80_c/3000-4900_price/
    def create_host_list(self):
        for i in range(1, self.num_house):
            try:
                house = self.webdriver.find_element(By.XPATH, "/html/body/main/div[2]/ul/li[{}]".format(i))
                # get price
                price_ojb = house.find_elements(By.CLASS_NAME, "price")

                # get the real price from "4,688 萬" like string
                house_price = re.findall("\d+", price_ojb[0].text.replace(",", ""))
                house_price = int(house_price[0])

                house_info_web_obj = house.find_element(By.TAG_NAME, "a")
                house_name  = house_info_web_obj.accessible_name.split(' ')[0]
                house_addr  = house_info_web_obj.accessible_name.split(' ')[1]

                obj_url = house_info_web_obj.get_attribute('href')
                obj_number = obj_url.split("/")[-1]

                house_obj = house_info(house_name, obj_number, obj_url, house_price, house_addr, self.now)
                self.house_obj_list.append(house_obj)
                if self.check_new_house(obj_number):
                    self.new_house_obj_list.append(house_obj)
            except Exception as e:
                print("While capturing {}th house", i)
                print("Exception happen {}", str(e))

    def screen_shot_house_and_save_house_info(self):
        for house_info_obj in self.house_obj_list:
            try:
                print(house_info_obj.name, house_info_obj.price, house_info_obj.url, house_info_obj.addr)
                self.webdriver.get(house_info_obj.url)
                obj_number = house_info_obj.url.split("/")[-1]

                house = self.webdriver.find_element(By.XPATH, "/html/body/main/section[1]")

                screen_shot_path = os.path.join("data", "yunching", self.region, obj_number)
                Path(screen_shot_path).mkdir(parents=True, exist_ok=True)

                png_path = os.path.join(screen_shot_path, "{}_house.png".format(self.date_time_str))
                json_path = os.path.join(screen_shot_path, "{}_house.json".format(obj_number))
                house_info_obj.save_house_info_to_json_data(json_path)
                house.screenshot(png_path)
                time.sleep(2)        
            except Exception as e:
                print("While screenshot {}", house_info_obj.url)
                print("Exception happen {}", str(e))

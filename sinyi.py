from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import datetime
import time
from pathlib import Path
from house import house_agent_web
from house import house_info
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re

class sinyi_web(house_agent_web):
    def __init__(self, webdriver, url, region = "永和") -> None:
        super().__init__(webdriver, url, region)
        self.agent_name = "Sinyi"

    def get_num_pages(self):
        self.webdriver.get(self.url)
        WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'pageLinkClassName')))
        pages_web_obj = self.webdriver.find_elements(By.CLASS_NAME, 'pageLinkClassName')
        self.num_pages = len(pages_web_obj)
        print("page " + str(self.num_pages))
        return self.num_pages

    def get_house_list(self):
        num_pages = self.get_num_pages()
        for p in range(1, num_pages + 1):
            self.webdriver.get(self.url + "{}".format(p))
            WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "buy-list-item")))
            self.house_list = self.webdriver.find_elements(By.CLASS_NAME, 'buy-list-item')
            self.num_house = len(self.house_list)
            print("{} houses found ".format(self.num_house))
            self.create_host_list()

    # this function is used to screen shot house info from the house list 
    # the house list example can be found from below website
    # https://www.sinyi.com.tw/buy/list/3000-4500-price/0-12-year/NewTaipei-city/234-zip/Taipei-R-mrtline/03-mrt/default-desc/index
    def screen_shot_house_briefly(self, url):
        pass

    # this function is to scan through houses in house list by search criteria and make a list for hosue_info_obj
    # the house list is like below
    # https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%B0%B8%E5%92%8C%E5%8D%80_c/3000-4900_price/
    def create_host_list(self):
        cnt = 1
        for house in self.house_list:
            try:
                obj_url = house.find_element(By.TAG_NAME, "a").get_attribute('href')

                price_obj = house.find_element(By.CLASS_NAME, "LongInfoCard_Type_Right")
                
                # '3,288萬\n(含車位價)\n加入最愛'
                # '2.28%\n4,380萬4,280萬\n(含車位價)\n加入最愛'

                house_price = re.findall("(\d,\d+萬)", price_obj.text)
                house_price = int(house_price[-1].replace(",", "").replace("萬", ""))

                house_info_web_obj = house.find_element(By.CLASS_NAME, "LongInfoCard_Type_Name")
                house_name  = house_info_web_obj.text
                house_info_web_obj = house.find_element(By.CLASS_NAME, "LongInfoCard_Type_Address")
                house_addr  = house_info_web_obj.text

                obj_number = obj_url.split("/")[-2]
                house_obj = house_info(house_name, obj_number, obj_url, house_price, house_addr, self.now)
                self.house_obj_list.append(house_obj)

                if self.check_new_house(obj_number):
                    self.new_house_obj_list.append(house_obj)                
                cnt += 1
            except Exception as e:
                print("While capturing {}th house", cnt)
                print("Exception happen {}", str(e))

    def screen_shot_house_and_save_house_info(self):
        for house_info_obj in self.house_obj_list:
            try:
                print(house_info_obj.name, house_info_obj.price, house_info_obj.url, house_info_obj.addr)
                if self.house_info_exist_in_db(house_info_obj):
                    print("{} is captured before at {}, skip".format(house_info_obj.name, self.date_time_str))
                else:
                    self.webdriver.get(house_info_obj.url)
                    # https://www.sinyi.com.tw/buy/house/20033T/?breadcrumb=list
                    obj_number = house_info_obj.url.split("/")[-2]

                    house = self.webdriver.find_element(By.XPATH, '//*[@id="__next"]/div/div/span/div[3]/div/div')

                    screen_shot_path = os.path.join("data", "sinyi", self.region, obj_number)
                    Path(screen_shot_path).mkdir(parents=True, exist_ok=True)

                    png_path = os.path.join(screen_shot_path, "{}_house.png".format(self.date_time_str))
                    json_path = os.path.join(screen_shot_path, "{}_house.json".format(obj_number))
                    house_info_obj.save_house_info_to_json_data(json_path)
                    house.screenshot(png_path)
                    time.sleep(2)
            except Exception as e:
                print("While screenshot {}", house_info_obj.url)
                print("Exception happen {}", str(e))


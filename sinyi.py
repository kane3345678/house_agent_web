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
from selenium.common.exceptions import NoSuchElementException

import re

class sinyi_web(house_agent_web):
    def __init__(self, webdriver, url, region = "永和") -> None:
        super().__init__(webdriver, url, region)
        self.agent_name = "Sinyi"

    def get_num_pages(self):
        for _ in range(3):
            try:
                self.webdriver.get(self.url)
                WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'pageLinkClassName')))
                pages_web_obj = self.webdriver.find_elements(By.CLASS_NAME, 'pageLinkClassName')
                self.num_pages = int(pages_web_obj[-1].text)
                print("page " + str(self.num_pages))
                break
            except Exception as e:
                print(e)
                print("Can't load the page successfully {}".format(self.url))
                self.num_pages = 0
        # this delay is necessary to avoid hang up
        time.sleep(3)
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
                # WA to skip invalid house
                if (obj_number == "house"):
                    continue

                house_obj = house_info(house_name, obj_number, obj_url, house_price, house_addr, self.now)
                self.house_obj_list.append(house_obj)

                if self.check_new_house(obj_number):
                    self.new_house_obj_list.append(house_obj)
                cnt += 1
            except Exception as e:
                print("While capturing {}th house", cnt)
                print("Exception happen {}", str(e))


    def get_web_obj_for_screen_shot(self, house_info_obj):
        self.webdriver.get(house_info_obj.url)
        WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div/span/div[3]/div/div')))
        house = self.webdriver.find_element(By.TAG_NAME, "body")
        return house

    def check_house_obj_close(self, url):
        self.webdriver.get(url)
        try:
            WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/span/div[3]/div/div/div[2]')))
            web_elem = self.webdriver.find_element(By.XPATH, '/html/body/div[1]/div/div/span/div[3]/div/div/div[2]')
        except NoSuchElementException:
            return False
        if "找不到這一頁" in web_elem.text or "繼續找好屋" in web_elem.text:
            return True
        return False

    def get_community_name(self):
        #/html/body/main/section[2]/section[4]/div[1]/ul/li[1]
        try:
            web_elem = self.webdriver.find_element(By.XPATH, '//*[@id="__next"]/div/div/span/div[3]/div/div/div[4]/div/div[1]/a/div')
            print(web_elem.text)
            return web_elem.text
        except NoSuchElementException:
            return "NULL"

    def get_house_age(self):
        for _ in range(3):
            try:
                WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'buy-content-detail-type')))
                web_elem = self.webdriver.find_element(By.CLASS_NAME, 'buy-content-detail-type')
                #ex: ''37.3年\n店面''
                if "年" in web_elem.text:
                    age = re.findall('\d+.\d+',web_elem.text)[0]
                    print("house age = " , age)
                    return float(age)
                elif "預售" in web_elem.text:
                    return 0
                else:
                    return -1
            except Exception as e:
                print("get_community_name, exception happen, sleep 2 min ")
                time.sleep(120)
        return -1

    def get_house_floor(self):
        for _ in range(3):
            try:
                WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'buy-content-detail-floor')))
                web_elem = self.webdriver.find_element(By.CLASS_NAME, 'buy-content-detail-floor')
                return web_elem.text

            except Exception as e:
                print("get_house_floor, exception happen, sleep 2 min ")
                time.sleep(120)
        return -1
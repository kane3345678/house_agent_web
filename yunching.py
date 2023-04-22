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
from selenium.common.exceptions import NoSuchElementException

class yun_ching_web(house_agent_web):
    def __init__(self, webdriver, url, region = "永和") -> None:
        super().__init__(webdriver, url, region)
        self.agent_name = "YunChing"


    def get_num_pages(self):
        for retry in range(3):
            try:
                self.webdriver.get(self.url)
                WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "下一頁")))
                pages_web_obj = self.webdriver.find_elements(By.XPATH, '/html/body/main/div[2]/div[4]/ul/li')
                for p in pages_web_obj:
                    # except 第一頁, 最末頁, the real page number string should be '1', '2'
                    if len(p.text) == 1:
                        self.num_pages += 1
                break
            except Exception as e:
                print(e)
                print("Can't load the page successfully {}".format(self.url))
                self.num_pages = 0
        return self.num_pages

    def get_house_list(self):
        num_pages = self.get_num_pages()
        for p in range(1, num_pages + 1):
            self.webdriver.get(self.url + "?pg={}".format(p))
            WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "m-list-item")))

            self.house_list = self.webdriver.find_elements(By.XPATH, "/html/body/main/div[2]/ul")
            self.num_house = len(self.house_list[0].find_elements(By.CLASS_NAME, "m-list-item"))
            print("{} houses found ".format(self.num_house))
            self.create_host_list()

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
            self.webdriver.execute_script("window.scrollTo(0, 800);")
            time.sleep(0.5)
            png_path = os.path.join(screen_shot_path, "{}_house2.png".format(self.date_time_str))

            house.screenshot(png_path)
            cnt += 1

    # this function is to scan through houses in house list by search criteria and make a list for hosue_info_obj
    # the house list is like below
    # https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%B0%B8%E5%92%8C%E5%8D%80_c/3000-4900_price/
    def create_host_list(self):
        retry = 0
        i = 1
        while i <= self.num_house:
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
                i+=1
            except Exception as e:
                print("While capturing {}th house", i)
                print("Exception happen {}", str(e))
                print("take a rest for 5 mins since we migh blocked by the server now, retry = {}".format(retry))

                time.sleep(300)
                if retry < 3:
                    retry += 1
                    continue
                print("Give up retry")
            retry = 0

    def get_web_obj_for_screen_shot(self, house_info_obj):
        self.webdriver.get(house_info_obj.url)
        WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/main/section[1]")))
        house = self.webdriver.find_element(By.TAG_NAME, "body")
        return house

    def check_house_obj_close(self, url):
        self.webdriver.get(url)
        try:
            web_elem = self.webdriver.find_element(By.XPATH, "/html/body/main/div/div/p")
        except NoSuchElementException:
            return False

        if "已經不存在" in web_elem.text:
            return True
        return False

    def get_community_name(self):
        # retry 3 times 
        for retry in range(3):
            #/html/body/main/section[2]/section[4]/div[1]/ul/li[1]
            try:
                WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'detail-list-lv1')))   
                web_elem = self.webdriver.find_element(By.CLASS_NAME, "m-house-detail-ins")
                #ex: '鴻運金大樓\n追蹤社區新案'
                if "追蹤社區" in web_elem.text:
                    print(web_elem.text.split("\n")[0])
                    return web_elem.text.split("\n")[0]
                else:
                    return 'NULL'
            except Exception as e:
                if self.check_house_obj_close(self.webdriver.current_url):
                    return "close"
                print("get_community_name, exception happen, sleep 2 min ")
                time.sleep(120)
        return "NULL"

    def get_house_age(self):
        for _ in range(3):
            #"/html/body/main/section[1]/div[1]/div[2]"
            try:
                WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'm-house-info-wrap')))
                web_elem = self.webdriver.find_element(By.CLASS_NAME, 'm-house-info-wrap')
                #'建物 32.43坪\n3房(室)2廳2衛\n41.0年 公寓 3~3/5樓'
                age_info = web_elem.text.split("\n")[-1]
                if "年" in age_info:
                    age = re.findall('\d+.\d+',age_info)[0]
                    print("house age = " , age)
                    return float(age)
                elif "預售" in age_info:
                    return 0

            except Exception as e:
                print("get_community_name, exception happen, sleep 2 min ")
                time.sleep(120)
        return -1

    def _check_floor_format(self, floor_string):
        pattern = r"^[Bb]?\d+[~-]?\d+/\d{1,2}樓$"
        match = re.match(pattern, floor_string)
        return match is not None

    def get_house_floor(self):
        for _ in range(3):
            try:
                WebDriverWait(self.webdriver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'm-house-info-wrap')))
                web_elem = self.webdriver.find_element(By.CLASS_NAME, 'm-house-info-wrap')
                #'建物 32.43坪\n3房(室)2廳2衛\n41.0年 公寓 3~3/5樓'
                floor = web_elem.text.split(" ")[-1]
                if self._check_floor_format(floor):
                    print("house floor = " , floor)
                    return floor
                else:
                    print("Floor format error, floor = {}".format(floor))
                    import pdb;pdb.set_trace()
                    return "NULL"

            except Exception as e:
                if self.check_house_obj_close(self.webdriver.current_url):
                    return "close"
                print("get_house_floor, exception happen, sleep 2 min ")
                time.sleep(120)
        return "NULL"
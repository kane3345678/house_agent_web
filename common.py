import json
from os import path
import os
from pathlib import Path
import datetime
import codecs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def save_json(data, filename):
    if not path.exists(os.path.dirname(filename)):
        Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

    # Open the file in write mode, using utf-8 encoding
    with codecs.open(filename, mode="w", encoding="utf-8") as f:
        # Use json.dump() to write the data to the file
        json.dump(data, f, indent=4, ensure_ascii=False)

def read_json( filename):
    try:
        f = open(filename, encoding='utf-8')
        return json.load(f)
    except Exception:
        return None

def get_config(config_name, default = None):
    data = read_json("config.json")
    if config_name in data:
        return data[config_name]
    else:
        return default

def get_region_from_addr(addr):
    try:
        return addr[0:6]
    except Exception:
        return "Unknown"

def str_to_date(s):
    import datetime
    d = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    return d

def find_files_in_dir(dir, file_pattern):
    import re
    file_list = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if re.match(file_pattern, file) != None:
                file_list.append(os.path.join(root, file))
    return file_list

# date_str = 111-12-13, return 2022-12
def roc_date_to_ad_date(date_str):
    year = int(date_str.split("/")[0]) + 1911
    month = date_str.split("/")[1]
    new_date = "{}/{}".format(year, month)
    new_date = datetime.datetime.strptime(new_date, "%Y/%m")
    return new_date

def download_json(webdriver, url):
    try:
        WebDriverWait(webdriver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        webdriver.get(url)
        json_content = webdriver.find_elements(By.TAG_NAME, "body")[0].text
        # Parse the JSON content
        parsed_json = json.loads(json_content)
        return parsed_json
    except Exception:
        print("Exception happen while loading {}".format(url))
        return {}
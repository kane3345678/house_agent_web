import json
from os import path
import os
from pathlib import Path
import glob, os

def save_json(data, filename):
    if not path.exists(os.path.dirname(filename)):
        Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

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
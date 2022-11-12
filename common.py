import json
from os import path
import os
from pathlib import Path

def save_json(data, filename):
    if not path.exists(os.path.dirname(filename)):
        Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def read_json( filename):
    try:
        f = open(filename)
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

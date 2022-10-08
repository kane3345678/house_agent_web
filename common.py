import json

def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def read_json( filename):
    try:
        f = open(filename)
        return json.load(f)
    except Exception:
        return None
  
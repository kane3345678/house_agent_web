import common
class house_info():
    def __init__(self, name, url, price, addr, timestamp, year = 0) -> None:
        self.url = url
        self.year = year
        self.name = name
        self.price = price
        self.addr = addr
        self.date_time_str = timestamp

    def house_info_to_json_data(self):
        price_history = {"date":self.date_time_str, "price":self.price}
        house_data = {"name":self.name, 'price':[price_history], 'addr':self.addr, 'url':self.url}
        return house_data

    def save_house_info_to_json_data(self, json_path):
        house_data = self.house_info_to_json_data()
        history = common.read_json(json_path)
        if history != None:
            house_data = history
            # since we have a history for this house, let's append the price to the history
            price_info = {"date":self.date_time_str, "price":self.price}
            # check if the price history exist or not
            for p_info in house_data['price']:
                if price_info["date"] not in p_info["date"]:
                    house_data['price'].append(price_info)
                else:
                    print("skip")
                    break

        common.save_json(house_data, json_path)

    def get_price(self):
        # get price
        pass

    def get_screenshot(self):
        pass

# Abstract class for house agent webcrawler
# will be used in future
class house_agent_web():
    def __init__(self, webdriver, url, region) -> None:
        pass

    def get_house_list(self):
        pass

    def screen_shot_house_briefly(self, url):
        pass

    def create_host_list(self):
        pass

    def screen_shot_house_and_save_house_info(self):
        pass

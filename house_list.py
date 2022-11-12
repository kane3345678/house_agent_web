from sinyi import sinyi_web
from yunching import yun_ching_web

all_agents = [
        {
            "agent":yun_ching_web,
            "website": [
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%B0%B8%E5%92%8C%E5%8D%80_c/2000-4900_price", "region":"永和"},
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E4%B8%AD%E5%92%8C%E5%8D%80_c/2000-4900_price/", "region":"中和"},
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%96%B0%E8%8E%8A%E5%8D%80_c/2000-4900_price/", "region":"新莊"},
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%9D%BF%E6%A9%8B%E5%8D%80_c/2000-4900_price/", "region":"板橋"},
                {"url":"https://buy.yungching.com.tw/region/%E5%8F%B0%E5%8C%97%E5%B8%82-%E5%8D%97%E6%B8%AF%E5%8D%80_c/2000-4900_price/", "region":"南港"}
            ]
        },
        {
            "agent":sinyi_web,
            "website": [
                {"url":"https://www.sinyi.com.tw/buy/list/2000-4500-price/NewTaipei-city/234-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"永和"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-4500-price/NewTaipei-city/242-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"新莊"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-4500-price/NewTaipei-city/235-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"中和"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-4500-price/NewTaipei-city/220-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"板橋"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-4900-price/Taipei-city/115-zip/Taipei-R-mrtline/03-mrt/default-desc/index","region":"南港"}

            ]
        }
]
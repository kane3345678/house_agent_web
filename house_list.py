from sinyi import sinyi_web
from yunching import yun_ching_web
from fivenineone import fivenineone_web

all_agents = [
        {
            "agent":yun_ching_web,
            "website": [
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%B0%B8%E5%92%8C%E5%8D%80_c/2000-6000_price", "region":"永和"},
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E4%B8%AD%E5%92%8C%E5%8D%80_c/2000-6000_price/", "region":"中和"},
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%96%B0%E8%8E%8A%E5%8D%80_c/2000-6000_price/", "region":"新莊"},
                {"url":"https://buy.yungching.com.tw/region/%E6%96%B0%E5%8C%97%E5%B8%82-%E6%9D%BF%E6%A9%8B%E5%8D%80_c/2000-6000_price/", "region":"板橋"},
                {"url":"https://buy.yungching.com.tw/region/%E5%8F%B0%E5%8C%97%E5%B8%82-%E5%8D%97%E6%B8%AF%E5%8D%80_c/2000-6000_price/", "region":"南港"},
                {"url":"https://buy.yungching.com.tw/region/%E5%8F%B0%E5%8C%97%E5%B8%82-%E5%A3%AB%E6%9E%97%E5%8D%80_c/2000-6000_price/", "region":"士林"},
                {"url":"https://buy.yungching.com.tw/region/新竹縣-竹北市_c/1500-6000_price/", "region":"竹北"}

            ]
        },
        {
            "agent":sinyi_web,
            "website": [
                {"url":"https://www.sinyi.com.tw/buy/list/2000-6000-price/NewTaipei-city/234-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"永和"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-6000-price/NewTaipei-city/242-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"新莊"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-6000-price/NewTaipei-city/235-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"中和"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-6000-price/NewTaipei-city/220-zip/Taipei-R-mrtline/03-mrt/default-desc/", "region":"板橋"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-6000-price/Taipei-city/115-zip/Taipei-R-mrtline/03-mrt/default-desc/","region":"南港"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-6000-price/Taipei-city/111-zip/Taipei-R-mrtline/03-mrt/default-desc/","region":"士林"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-6000-price/Taipei-city/100-zip/Taipei-R-mrtline/03-mrt/default-desc/","region":"中正"},
                {"url":"https://www.sinyi.com.tw/buy/list/2000-6000-price/Hsinchu-county/302-zip/Taipei-R-mrtline/03-mrt/default-desc/","region":"竹北"},
            ]
        }
]

gov_deal_591 = [
    {"url":"https://market.591.com.tw/list?regionId=3&sectionId=37&postType=8,2", "district":"新北市永和區"},
    {"url":"https://market.591.com.tw/list?regionId=3&sectionId=38&postType=2,8", "district":"新北市中和區"},
    {"url":"https://market.591.com.tw/list?regionId=3&sectionId=44&postType=2,8", "district":"新北市新莊區"},
    {"url":"https://market.591.com.tw/list?regionId=3&sectionId=26&postType=2,8", "district":"新北市板橋區"},
]

gov_deal_cpking = [
    {"url":"https://community.houseprice.tw/ws/list/新竹縣_city/竹北市_zip", "district":"新竹縣竹北市"},
    {"url":"https://community.houseprice.tw/ws/list/台北市_city/北投區_zip", "district":"台北市北投區"},
    {"url":"https://community.houseprice.tw/ws/list/%E6%96%B0%E5%8C%97%E5%B8%82_city/%E6%B0%B8%E5%92%8C%E5%8D%80_zip", "district":"新北市永和區"},
    {"url":"https://community.houseprice.tw/ws/list/%E6%96%B0%E5%8C%97%E5%B8%82_city/%E4%B8%AD%E5%92%8C%E5%8D%80_zip", "district":"新北市中和區"},
    {"url":"https://community.houseprice.tw/ws/list/%E6%96%B0%E5%8C%97%E5%B8%82_city/%E6%9D%BF%E6%A9%8B%E5%8D%80_zip", "district":"新北市板橋區"},
    {"url":"https://community.houseprice.tw/ws/list/%E6%96%B0%E5%8C%97%E5%B8%82_city/%E6%96%B0%E8%8E%8A%E5%8D%80_zip", "district":"新北市新莊區"},
    {"url":"https://community.houseprice.tw/ws/list/%E6%96%B0%E5%8C%97%E5%B8%82_city/%E6%96%B0%E5%BA%97%E5%8D%80_zip", "district":"新北市新店區"},
    {"url":"https://community.houseprice.tw/ws/list/%E6%96%B0%E5%8C%97%E5%B8%82_city/%E6%9E%97%E5%8F%A3%E5%8D%80_zip", "district":"新北市林口區"},
]
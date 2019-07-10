import re
import requests

class handle_lagou():
    # 初始化拉勾网爬虫
    def __init__(self):
        self.session=requests.session()
        self.header={
            'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 75.0.3770.100Safari / 537.36'
        }
        self.city_list = ""

    # 获取全部城市
    def handle_city(self):
        city_comp = re.compile(r'zhaopin/">(.*?)</a>')
        city_url = "https://www.lagou.com/jobs/allCity.html"
        city_result = self.handle_request(method="GET", url=city_url)
        self.city_list=city_comp.findall(city_result)

    # 定义获取方法
    def handle_request(self, method, url, data=None, info=None):
        if method=="GET":
            response = self.session.get(url=url, headers=self.header)
        return response.text


if __name__ == '__main__':
    lagou = handle_lagou()
    lagou.handle_city()
    print(lagou.city_list)
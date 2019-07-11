import re
import requests
import time
import json
import multiprocessing

from lagou.handle_insert_data import lagou_mysql

class handle_lagou():
    # 初始化拉勾网爬虫
    def __init__(self):
        # 使用session保存cookies信息
        self.session=requests.session()
        self.header={
            'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 75.0.3770.100Safari / 537.36'
        }
        self.city_list = ""

    # 获取全部城市
    def handle_city(self):
        city_comp = re.compile(r'www\.lagou\.com\/.*\/">(.*?)</a>')
        city_url = "https://www.lagou.com/jobs/allCity.html"
        city_result = self.handle_request(method="GET", url=city_url)

        self.city_list=set(city_comp.findall(city_result))
        self.session.cookies.clear()

    def handle_city_job(self, city):
        first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput="%city
        first_response = self.handle_request(method="GET", url=first_request_url)
        total_page_re = re.compile(r'class="span\stotalNum">(\d+)</span>')
        try:
            total_page = total_page_re.search(first_response).group(1)
        # 由于没有岗位信息造成的exception
        except:
            return
        else:
            for i in range(1,int(total_page)+1):
                data = {
                    "pn":i,
                    "kd":"python",
                }
                page_url = "https://www.lagou.com/jobs/positionAjax.json?city=%s&needAddtionalResult=false"%city
                refer_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput="%city
                self.header['Referer'] = refer_url.encode()
                response = self.handle_request(method="POST",url=page_url,data=data, info=city)
                lagou_data = json.loads(response)
                job_list = lagou_data['content']['positionResult']['result']
                for job in job_list:
                    print(job)
                    lagou_mysql.insert_item(job)

    # 定义获取方法
    def handle_request(self, method, url, data=None, info=None):
        proxy_http = "http://%s:%s@%s:%s"%('H16V841F925QY10P', 'BA4052012B735F7C', 'http-pro.abuyun.com', '9010')
        proxy = {
            'http':proxy_http,
            'https':proxy_http
        }
        # 遇到操作频繁的时候需要重复请求

        while True:
            try:
                if method=="GET":
                    response = self.session.get(url=url, headers=self.header, proxies=proxy, timeout=6)

                elif method=="POST":
                    response=self.session.post(url=url, headers=self.header, data=data, proxies=proxy, timeout=6)
            except:
                # 需要先清除cookies信息
                self.session.cookies.clear()
                # 重新获取cookies信息
                first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput=" % info
                self.handle_request(method="GET", url=first_request_url)
                time.sleep(10)
                continue
            response.encoding = 'utf-8'
            if "频繁" in response.text:
                print("请求频繁")
                # 需要先清除cookies信息再重新获取
                self.session.cookies.clear()
                first_request_url = "https://www.lagou.com/jobs/list_python?city=%s&cl=false&fromSearch=true&labelWords=&suginput=" %info
                self.handle_request(method="GET",url=first_request_url)
                time.sleep(10)
                continue
            return response.text


if __name__ == '__main__':
    lagou = handle_lagou()
    # 获取所有城市
    lagou.handle_city()

    #创建一个进程池
    pool = multiprocessing.Pool(2)

    # 通过多进程的方法加速抓取
    for city in lagou.city_list:
        print(city)
        pool.apply_async(lagou.handle_city_job(city))

    pool.close()
    pool.join()


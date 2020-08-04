"""
安居客租房房源信息分析
1.源码中可即可查看房源信息
2.数字(价格)字体加密
3.城市即加在域名前(二手房需加全拼)
"""
import requests
import gevent
from bs4 import BeautifulSoup
import re
import pandas as pd
from house.tools import get_result
Listings_Mapping = {
        '1': 'fang.anjuke.com/',
        '2': 'anjuke.com/sale/',
        '3': 'zu.anjuke.com/',
        '4': 'sydc.anjuke.com/xzl-zu/'
    }

class Anjuke(object):
    def __init__(self, listing, city, pages):
        self.listing = listing
        self.city = city
        self.pages = pages
        self.crawl_url = self._url_generator()
        self.data_field = {
            "title": [],
            "unit": [],
            "address": [],
            "price": [],
            "href": [],
        }
        self.headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        }
        self.proxy = {
            "https": f"https://{requests.get('https://dps.kdlapi.com/api/getdps/?orderid=979654705737339&num=1&pt=1&dedup=1&sep=1').text}"
        }

    def _url_generator(self):
        for page in range(self.pages):
            yield f"https://{self.city}.{Listings_Mapping[self.listing]}/fangyuan/p{page + 1}/"

    def zufang_process(self, url):
        response = requests.get(url, headers=self.headers, proxies=self.proxy)
        html = response.text
        # 获取base64字符加密串
        base64_code = re.findall("charset=utf-8;base64,(.*?)'\)", html)[0]
        if response.status_code != 200:
            return False
        # 提取房源信息
        soup = BeautifulSoup(html, 'lxml')
        info_soup_list = soup.find_all('div', class_='zu-itemmod')
        self.extract(info_soup_list, base64_code)

    def ershoufang_process(self, url):
        response = requests.get(url, headers=self.headers, proxies=self.proxy)
        html = response.text
        if response.status_code != 200:
            return False
        soup = BeautifulSoup(html, 'lxml')
        info_soup_list = soup.find_all('li', class_='list-item')
        for data in info_soup_list:
            info = data.find_all('div', class_='house-details')
            price = data.find_all('div', class_='pro-price')
            self.data_field['title'].append(re.sub(r'\n| ', '', info[0].find_all('a', class_='houseListTitle')[0].text))
            self.data_field['href'].append(info[0].find_all('a', class_='houseListTitle')[0]['href'])
            self.data_field['unit'].append(re.sub(r'\n| ', '', info[0].find_all('div', class_='details-item')[0].text))
            self.data_field['address'].append(re.sub(r'\n| |\xa0', '', info[0].find_all('span', class_='comm-address')[0].text))
            self.data_field['price'].append(re.sub(r'\n| |\xa0', '', price[0].text))
        data_frame = pd.DataFrame(self.data_field)
        data_frame.to_csv('./data/anjuke_ershou.csv')
    def extract(self, data_list, base64_code):
        for data in data_list:
            info = data.find_all('div', class_='zu-info')
            price = data.find_all('div', class_='zu-side')
            self.data_field['title'].append(info[0].select_one('h3 b').text)
            self.data_field['href'].append(info[0].select_one('h3 a')['href'])
            # 数字解密
            self.data_field['unit'].append(f"{get_result(info[0].select('p b')[0].text, base64_code)}室{get_result(info[0].select('p b')[1].text, base64_code)}厅, {get_result(info[0].select('p b')[2].text, base64_code)}㎡")
            self.data_field['address'].append(re.sub(r'\n| |\xa0','',info[0].select('address')[0].text.strip()))
            # 数字解密
            self.data_field['price'].append(get_result(price[0].select_one('b').text, base64_code))
        data_frame = pd.DataFrame(self.data_field)
        data_frame.to_csv('./data/anjuke_zu.csv')

    def crawl(self):
        crawl_mapping = {
            '2': self.ershoufang_process,
            '3': self.zufang_process
        }
        gevent.joinall([
            gevent.spawn(crawl_mapping[self.listing](url)) for url in self.crawl_url
        ])


if __name__ == '__main__':

    print(
        """
        1.新房
        2.二手房
        3.租房
        4.商铺写字楼
        """
    )
    listing = input('请选择类型：')
    city = input("请输入城市（首字母/二手房需全拼）：")
    page = int(input("请输入需要多少页数据："))
    scheduler = Anjuke(listing, city, page)
    scheduler.crawl()
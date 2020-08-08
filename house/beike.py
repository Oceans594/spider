import requests
import gevent
from lxml import etree
import re
import pandas as pd
"""
贝壳分析

"""
class Beike(object):
    def __init__(self, pages):
        self.pages = pages
        self.base_url = "https://cd.ke.com/ershoufang/"
        self.headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        }
        self.proxy = {
            "https": f"https://{requests.get('https://dps.kdlapi.com/api/getdps/?orderid=979654705737339&num=1&pt=1&sep=1').text}"
        }
        self.data_field = {
            "title": [],
            "unit": [],
            "address": [],
            "price": [],
            "href": [],
        }

    def _url_generator(self):
        for page in range(self.pages):
            yield self.base_url + 'pg' + str(page + 1)

    def process(self, url):
        response = requests.get(url, headers=self.headers, proxies=self.proxy)
        if response.status_code != 200:
            return False
        html = etree.HTML(response.text)
        info_list = html.xpath('//div[@class="info clear"]')
        self.extract(info_list)

    def extract(self, data_list):
        for data in data_list:
            title = data.xpath('./div[@class="title"]/a')[0].text
            href = data.xpath('./div[@class="title"]/a/@href')[0]
            address = data.xpath('./div[@class="address"]/div[@class="flood"]/div/a')[0].text
            unit = data.xpath('./div[@class="address"]/div[2]/text()')[1]
            total_price = data.xpath('./div[@class="address"]/div[@class="priceInfo"]/div[1]/span')[0].text
            unit_price = data.xpath('./div[@class="address"]/div[@class="priceInfo"]/div[2]/span')[0].text
            self.data_field['title'].append(title)
            self.data_field['address'].append(address)
            self.data_field['unit'].append(re.sub(r"\n| ", "", unit))
            self.data_field['price'].append("".join([total_price, '万', '|', unit_price]))
            self.data_field['href'].append(href)
        data_frame = pd.DataFrame(self.data_field)
        data_frame.to_csv('./data/beike_ershou.csv')
    def crawl(self):
        gevent.joinall([
            gevent.spawn(self.process(url)) for url in self._url_generator()
        ])


if __name__ == '__main__':
    page = int(input("请输入需要多少页数据："))
    scheduler = Beike(page)
    scheduler.crawl()
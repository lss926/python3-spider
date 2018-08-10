import requests
import re
import time
import json
from requests.exceptions import RequestException


class MaoYanSpider(object):
	'''抓取猫眼电影榜单TOP100的电影详情信息'''
	def __init__(self):
		self.url = 'http://maoyan.com/board/4?offset='
		self.headers = {
			'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
		}

	def load_page(self, url):
		'''获取页面源码'''		
		try:
			response = requests.get(url, headers=self.headers)
			return response.text
		except RequestException:
			return None

	def parse_page(self, html):
		'''使用正则表达式提取数据'''
		pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a.*?>(.*?)'
							+ '</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)</i>'
							+ '.*?fraction">(.*?)</i>.*?</dd>', re.S
							)
		items = re.findall(pattern, html)
		for item in items:
			yield{
				'index':item[0],
				'image':item[1],
				'title':item[2],
				'actor':item[3].strip()[3:],
				'time':item[4].strip()[5:],
				'score':item[5] + item[6]
			}

	def write_to_file(self, content):
		'''将提取的数据写入到文件'''
		with open('result.txt', 'a', encoding='utf-8') as f:
			f.write(json.dumps(content, ensure_ascii=False) + '\n')

	def spider(self):
		'''遍历所提取数据的页面'''
		for i in range(10):
			url = self.url + str(i*10)
			html = self.load_page(url)
			for item in self.parse_page(html):
				print(item)
				self.write_to_file(item)


if __name__ == '__main__':
	maoyan = MaoYanSpider()
	maoyan.spider()

		
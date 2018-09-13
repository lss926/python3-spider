#!/usr/bin/env python
# encoding: utf-8
"""
@author: lisaisai
@file: meitu.py
@time: 2018/9/13 11:04
"""
import requests
import os
from hashlib import md5
from urllib.parse import urlencode
from multiprocessing.pool import Pool


class MeiTuSpider(object):
    '''抓取今日头条街拍美图'''
    def __init__(self):
        self.url = 'https://www.toutiao.com/search_content/?'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }

    def load_page(self, offset):
        '''获取页面源代码'''
        params = {
            'offset':offset,
            'format':'json',
            'keyword':'街拍',
            'autoload':'true',
            'count':'20',
            'cur_tab':'1',
            'from':'search_tab',
        }
        try:
            response = requests.get(self.url + urlencode(params), headers = self.headers)
            if response.status_code == 200:
                return response.json()
        except requests.ConnectionError:
            return None

    def parse_page(self, json):
        '''从json文件中提取title和图片url'''
        if json.get('data'):
            data = json.get('data')
            for item in data:
                if item.get('cell_type') is not None:
                    continue
                title = item.get('title')
                images = item.get('image_list')
                for image in images:
                    yield{
                        'image':'https:' + image.get('url'),
                        'title':title
                    }

    def save_image(self, item):
        '''将图片保存在文件夹中，文件夹以title命名'''
        image_path = os.getcwd() + os.path.sep + 'img' + os.path.sep + item.get('title')
        if not os.path.exists(image_path):
            os.makedirs(image_path)
        try:
            response = requests.get(item.get('image'))
            if response.status_code == 200:
                file_path = image_path + os.path.sep + '{file_name}.{file_suffix}'.format(
                    file_name=md5(response.content).hexdigest(),
                    file_suffix='jpg')
                if not os.path.exists(file_path):
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    print('Downloaded image path is %s' % file_path)
                else:
                    print('Already Downloaded', file_path)
        except requests.ConnectionError:
            print('Failed to Save Image，item %s' % item)

    def spider(self, offset):
        json = self.load_page(offset)
        for item in self.parse_page(json):
            print(item)
            self.save_image(item)


if __name__ == '__main__':
    start = 0
    end = 7
    offset = [x * 20 for x in range(start, end + 1)]
    pool = Pool()
    meitu = MeiTuSpider()
    pool.map(meitu.spider, offset)
    pool.close()
    pool.join()
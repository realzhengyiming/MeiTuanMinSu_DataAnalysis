# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     test   
   Description :  
   Author :        zhengyimiing 
   date：          2020/4/8 
-------------------------------------------------
   Change Activity:
                   2020/4/8  
-------------------------------------------------
"""
import os

from .parseTool import parsePriceMain

__author__ = 'zhengyimiing'


if __name__ == '__main__':
    print(os.getcwd())
    import requests
    # url = input("请输入你的网页")
    url = "https://minsu.meituan.com/housing/2641002/"
    headers = {
        #     'cookie':cookiestr,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }

    html = requests.get(headers=headers, url=url).content
    # 获得price中的那段string

    # 增加beautifulsoup来处理，这一段scrapy中可以省略，scrapy中替换为 findall那个，还要加上cssPath 的查找才可以
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'lxml')
    j_gallery_text = soup.find("script", attrs={"id": "r-props-J-gallery"}).get_text()
    UserJson = j_gallery_text
    real_price,real_discount = parsePriceMain(UserJson)
    print()
    print("输出价格如下：")
    print(real_price)
    print(real_discount)

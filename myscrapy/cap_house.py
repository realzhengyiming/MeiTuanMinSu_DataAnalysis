# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     todo   
   Description :  
   Author :        zhengyimiing 
   date：          2020/3/24 
-------------------------------------------------
   Change Activity:
                   2020/3/24  
-------------------------------------------------
"""
__author__ = 'zhengyimiing'
# 这个todolist中有什么
from scrapy import cmdline


if __name__ == '__main__':
    cmdline.execute("scrapy crawl cap_house".split())
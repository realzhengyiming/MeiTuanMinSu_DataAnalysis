# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     scrapymain   
   Description :  
   Author :        zhengyimiing 
   date：          2019/12/26 
-------------------------------------------------
   Change Activity:
                   2019/12/26  
-------------------------------------------------
"""

__author__ = 'zhengyimiing'

from scrapy import cmdline
# cmdline.execute("scrapy crawl hotwordspider ".split())
# cmdline.execute("scrapy crawl hotel".split())
cmdline.execute("scrapy crawl cap_house".split())
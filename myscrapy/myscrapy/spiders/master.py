# -*- coding: utf-8 -*-
import traceback

import scrapy
# from ..items import KeywordItem  # 这个是关键词的item ，管道对item做一个
from urllib.parse import urljoin
import re
from bs4 import BeautifulSoup
# import json
import time

#from .parseTool import parsePriceMain
from hotelapp.models import City # 为提取方便建立的城市类
from ..items import urlItem  # 导入转变过的Houseitem类
#from h.models import City # 为提取方便建立的城市类
from fake_useragent import UserAgent
import json
from xpinyin import Pinyin


# master端是使用默认的，不需要变


class HotwordspiderSpider(scrapy.Spider):
    def __init__(self):
        self.ua = UserAgent()
        # for i in range(10):
        #     print(ua.random)

    name = 'master'
    allowed_domains = ['*']
    # start_urls = ['https://minsu.meituan.com/guangzhou/']

    custom_settings = {  # 每个爬虫使用各自的自定义的设置
        #### Scrapy downloader(下载器) 处理的最大的并发请求数量。 默认: 16
        'CONCURRENT_REQUESTS' : 2,
        #### 下载延迟的秒数，用来限制访问的频率,默认为0，没有延时
        # 'DOWNLOAD_DELAY' : 1,
        #### 每个域名下能够被执行的最大的并发请求数据量,默认8个
        'CONCURRENT_REQUESTS_PER_DOMAIN' : 2,
        #### 设置某个IP最大并发请求数量，默认0个
        'ONCURRENT_REQUESTS_PER_IP' : 2,
        'RETRY_ENABLED' :True,  #打开重试开关
        'RETRY_TIMES': 10 , #重试次数
        'DOWNLOAD_TIMEOUT': 60,
        'DOWNLOAD_DELAY': 2,  # 慢慢爬呗  ,这里写了下载延迟， 403就IP被封了 todo
        'RETRY_HTTP_CODES': [404,403,406],  #重试
        'HTTPERROR_ALLOWED_CODES': [403],  #上面报的是403，就把403加入。
        "ITEM_PIPELINES": {
            'MeiTuan_master.pipelines.urlItemPipeline': 300,  # 启用这个管道来保存数据

        },
        "DOWNLOADER_MIDDLEWARES":{   # 这样就可以单独每个使用不同的配置
        'MeiTuan_master.middlewares.RandomUserAgent': 100,   # 使用代理
        # 'MeiTuan.middlewares.proxyMiddleware': 301,  #  暂时不用代理来进行爬取测试下最多多少

        },
        "DEFAULT_REQUEST_HEADERS": {
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.meituan.com/',
            'X-Requested-With': "XMLHttpRequest",
            # "cookie":"lastCity=101020100; JSESSIONID=""; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1532401467,1532435274,1532511047,1532534098; __c=1532534098; __g=-; __l=l=%2Fwww.zhipin.com%2F&r=; toUrl=https%3A%2F%2Fwww.zhipin.com%2Fc101020100-p100103%2F; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1532581213; __a=4090516.1532500938.1532516360.1532534098.11.3.7.11"
            # 'Accept': 'application/json',
            # 'User-Agent': 'Mozilla/6.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Mobile Safari/537.36',
            # 'User-Agent':  self.ua.random  # 随机  好像还是需要通过中间件来 todo            
            # 'cookie':cookie self.ua

        }
    }

    def regexMaxNum(self,reg,text):  # 正则，返回匹配到的最大的数字就是页数了。
        temp = re.findall(reg,text)
        return max([int(num) for num in temp if num != ""])


    def start_requests(self):
        # fixpoint01 ->

        guangdong = '''广州市、韶关市、深圳市、珠海市、汕头市、佛山市、江门市、湛江市、茂名市、肇庆市、惠州市、梅州市、汕尾市、河源市、阳江市、清远市、东莞市、中山市、潮州市、揭阳市、雷州市、陆丰市、普宁市'''
        topcity = '北京、南京、上海、杭州、昆明市、大连市、厦门市、合肥市、福州市、哈尔滨市、济南市、温州市、长春市、石家庄市、常州市、泉州市、南宁市、贵阳市、南昌市、南通市、金华市、徐州市、太原市、嘉兴市、烟台市、保定市、台州市、绍兴市、乌鲁木齐市、潍坊市、兰州市。'

        pin = Pinyin()
        print("启动")
        guangdonglist = [pin.get_pinyin(i.replace("市", ""), "") for i in guangdong.split("、")]
        for onecity in City.objects.all():  # todo 城市这儿先设置0：2
            for i in range(1, 18):  # 这儿最大（1，18） 1~ 17的意思
                yield  scrapy.Request(url=f'https://minsu.meituan.com/{onecity.city_pynm}/pn{i}',
                dont_filter=True,
                callback=self.parse)   # 暂时还不是很懂发生了什么


    def parse(self, response):
        tempPageUrl = response.xpath("//a[@target='_blank']/@href").extract()
        tempPageUrl2 = [urljoin(response.url,url) for url in tempPageUrl if url.find("housing")!=-1]
        for url in tempPageUrl2:  # 一页里面的所有房源的链接
            print(url)
            item = urlItem()
            # yield scrapy.Request(url="https://minsu.meituan.com/housing/9969914/",callback=self.detail,dont_filter=True) # 直接转到详情上
            # yield scrapy.Request(url=url,callback=self.detail,dont_filter=True) # 直接转到详情上
            item['url'] = url
            yield item
            # 分布式master这儿是给items的--》pipline传到redis上共享。



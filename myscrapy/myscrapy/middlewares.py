# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
import random
import json
import re
# 这个是设置一个全局的变量
import time
import datetime

# 配一个常量用来做为备用代理ip的这样一台机子就够了

class EnvironmentIP:  # 这儿设置一个全局变量，单例模式
    _env = None

    def __init__(self):
        self.IP = 0   # 用那个计数的来操作就可以

    @classmethod
    def get_instance(cls):
        """
        返回单例 Environment 对象
        """
        if EnvironmentIP._env is None:
            cls._env == cls()
        return cls._env

    def set_flag(self, IP): # 里面放的是数字
        self.IP = IP

    def get_flag(self):
        return self.IP

envVarIP = EnvironmentIP()  # 这个变量是看是否切换使用代理的

class EnvironmentFlag:  # 这儿设置一个全局变量，单例模式
    _env = None
    def __init__(self):
        self.flag = False   # 默认不使用代理

    @classmethod
    def get_instance(cls):
        """
        返回单例 Environment 对象
        """
        if EnvironmentFlag._env is None:
            cls._env == cls()
        return cls._env

    def set_flag(self, flag):
        self.flag = flag

    def get_flag(self):
        return self.flag

envVarFlag = EnvironmentFlag()  # 这个变量是看是否切换使用代理的

class Environment:  # 这儿设置一个全局变量，单例模式
    _env = None
    def __init__(self):
        self.countTime = datetime.datetime.now()

    @classmethod
    def get_instance(cls):
        """
        返回单例 Environment 对象
        """
        if Environment._env is None:
            cls._env == cls()
        return cls._env

    def set_countTime(self, time):
        self.countTime = time

    def get_countTime(self):
        return self.countTime

envVar = Environment()  # 初始化一个默认的


class RandomUserAgent(object):  # ua中间件
    # def __init__(self):

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        ua = UserAgent()
        print(ua.random)
        request.headers['User-Agent'] = ua.random
        return None 

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        print(f"请求的状态码是  {response.status}")
        print("调试ing")
        print(request.url)
        HTML = response.body.decode("utf-8")
        # print(HTML)
        print(HTML[:200])
        try: 
            # print('进来中间件调试')
            if HTML.find("code")!=-1:
                if re.findall('(?<=code\\"\\:).*?(?=\\,)',HTML)[0]=='406':
                  # 自动会是双引号
                    print("正在重新请求（网络不好）")
                    return request
        except Exception as e:
            print(request.url)
            print(e)

        try:
            temp = json.loads(HTML)
            if temp['code'] == 406:  #
                print("正在重新请求（网络不好）状态码406")
                request.meta["code"] = 406
                return request    # 重新发给调度器，重新请求
        except Exception as e:
            print(e)
        return response


    def process_exception(self, request, exception, spider):
        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class proxyMiddleware(object):  # 代理中间件
    # 这儿是使用代理ip
    # MYTIME = 0   # 类变量用来设定切换代理的频率

    def __init__(self):
        # self.count = 0
        from redis import StrictRedis, ConnectionPool
        # 使用默认方式连接到数据库
        pool = ConnectionPool(host='localhost', port=6378, db=0,password='Zz123zxc')
        self.redis = StrictRedis(connection_pool=pool)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def get_proxy_address(self):
        proxyTempList = list(self.redis.hgetall("useful_proxy"))
        # proxyTempList = list(redis.hgetall("useful_proxy"))
        return str(random.choice(list(proxyTempList)), encoding="utf-8")

    def process_request(self, request, spider):
        # 这儿是用来代理的
        remote_iplist = ['47.115.131.115:8888','47.95.117.209:1521']
        print()
        print("proxyMiddleware")
        # print(proxyMiddleware.MYTIME)
        # print(type(proxyMiddleware.MYTIME))
        # proxyMiddleware.MYTIME += 1
        # print(self.count)
        now = datetime.datetime.now()
        print("flag")
        print("time")
        print(f"现在时间{now}")
        print(f"变量内时间{envVar.get_countTime()}")
        print("变量状态{True}才使用代理")
        print(envVarFlag.get_flag())
        print("相减少后的结果")
        print((now-envVar.get_countTime()).seconds / 40)
        if envVarFlag.get_flag() ==True:  #envVarFlag.get_flag() == True:  # 好像还不如不用这个代理呢，垃圾
            if (now-envVar.get_countTime()).seconds / 20 >= 1:
                envVarFlag.set_flag(not envVarFlag.get_flag())  # 切换为使用代理
                envVar.set_countTime(now)
            print("使用代理中池中的ip")
            proxy_address = None
            try:
                proxy_address = self.get_proxy_address()
                if proxy_address is not None:
                    print(f'代理IP --  {proxy_address}')
                    request.meta['proxy'] = f"http://{proxy_address}"   # 出现了302的话就有可能是因为代理的类型不对，有可能
                else:
                    print("代理池中没有代理ip存在")
            except Exception as e:
                print("检查到代理池里面已经没有ip了,使用本地")
        else:  # 不使用代理,这儿轮流使用本地ip和外面的ip
            if (now-envVar.get_countTime()).seconds / 40 >= 1:  # 这个进来是切换状态的
                envVarFlag.set_flag(not envVarFlag.get_flag())  # 切换为使用代理
                envVar.set_countTime(now)

            if envVarIP.get_flag() <= len(remote_iplist)-1:   ## 直接本地，也用用代理的吧
                remoteip = remote_iplist[envVarIP.get_flag()]
                print(f'使用远程ip --  {remoteip}')
                request.meta['proxy'] = f"http://{remoteip}"
                envVarIP.set_flag(envVarIP.get_flag()+1)
            else:
                envVarIP.set_flag(0)  # 把这个ip设置成0,这个是使用本地的ip
                print("使用到本地ip")
            pass

        #
        #
        # self.count +=1
        # if self.count <= 10:
        #     self.count+=1
        #     if self.count in [1,2,3,4,5,6,7]:
        #         return None
        #     else:   # 这个也是随机使用代理吗
        #         print("使用代理中")
        #         proxy_address = None
        #         try:
        #             proxy_address = self.get_proxy_address()
        #         except Exception as e:
        #             print("检查到代理池里面已经没有ip了")
        #
        #         if proxy_address!=None:
        #             print(f'代理IP --  {proxy_address}')
        #             request.meta['proxy'] = f"http://{proxy_address}"   # 出现了302的话就有可能是因为代理的类型不对，有可能
        # else:
        #     self.count = 0
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # 如果出错那就重新请求代理ip然后返回
        print("中间件出问题，代理这儿。")
        print(exception)
        proxy_address = self.get_proxy_address()
        request.meta['proxy'] = f"http://{proxy_address}"
        print(proxy_address)
        return request  # 所以这儿会无线重复的意思咯

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
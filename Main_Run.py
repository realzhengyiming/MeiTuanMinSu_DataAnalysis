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

import datetime
import multiprocessing
import os
import schedule
import time
from scrapy import cmdline


# if __name__ == '__main__':

# 同时启动所有的爬虫进行爬取工作。
# from Crawler.settings import CRAWLALL_RUN_TIME


import psutil
import subprocess

def checkprocess_cmdline(cmdline):  # 去掉那个指令后面的参数
    pl = psutil.pids()
    # print(pl)
    for pid in pl:
        if psutil.Process(pid).cmdline() == cmdline:
            #return pid
            print(" ".join(psutil.Process(pid).cmdline()))
            print(pid)
            return True
        else:
            return False  # 不存在
# nohup scrapy crawl hotel >/dev/null 2>&1 &

def main():  # 每两小时检查
    if checkprocess_cmdline("scrapy crawl hotel"):  # 主爬虫程序
        print("进程存在")
    else:
        print("")
        print("进程不存在,启动进程hotel spider")
        cmdline.execute("scrapy crawl hotel".split())
        print("启动完成")
        # subprocess.getoutput("nohup scrapy crawl hotel >/dev/null 2>&1 &")  # 启动它
    if checkprocess_cmdline("scrapy crawl hotel"): # 设置每两小时检查一下
        print("进程存在")
    else:
        print("")
        print("进程不存在, 启动进程 hotel cap_house")
        cmdline.execute("scrapy crawl cap_house".split())
        # result = subprocess.getoutput("nohup scrapy crawl cap_house >/dev/null 2>&1 &")
        # print("启动成功"+result)

def worker_1(interval):  # 每天执行这个，检查爬虫是否存在，顺便爬取
    print("开始所有爬虫工作")
    main()
    # cmdline.execute("scrapy crawlall".split())


class AutoRunAtTime:
    def job(self,name):   #这个是主线程把
        print("启动房源任务")
        print('这里是进程: %sd   父进程ID：%s' % (os.getpid(), os.getppid()))
        main()
        p1 = multiprocessing.Process(target=main, args=(6,))  # 直接执行主不就好了
        # # p3 = multiprocessing.Process(target=worker_3, args=(4,))
        p1.daemon = True
        # # p2.daemon = True
        p1.start()
        # # p2.start()
        # # p3.start()
        # print("The number of CPU is:" + str(multiprocessing.cpu_count()))
        # for p in multiprocessing.active_children():
        #     print("child   p.name:" + p.name + "\tp.id" + str(p.pid))
        p1.join()
        # p2.join()


    def startAutoRun(self,timeSet):         #24小时制的时间输入，传入一个时间的字符串
        name = "scrpy_hotelapp"
        schedule.every().day.at(timeSet).do(self.job, name)  # 应该也是24小时制的，记得  “输入24小时制的时间字符串
        while True:
            schedule.run_pending()
            # print("等待下一次...")
            time.sleep(1)


if __name__=="__main__":
    autoRun = AutoRunAtTime()
    print(time.strftime('%Y.%m.%d', time.localtime(time.time())))
    print("现在的时间是")
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # autoRun.startAutoRun("11:03") # 测试直接这儿写运行时间比较方便
    # result = subprocess.run("nohup scrapy crawl cap_house >/dev/null 2>&1 &",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",timeout=1)  # 启动它
    # print(result)
    # print("执行完毕")
    main()  # 进行测试只用
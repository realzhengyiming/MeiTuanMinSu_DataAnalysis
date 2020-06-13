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


# todo list 验证是否是scrapy的问题，阿里云的服务器怎么抓取不到，显示403


###### todo 把收藏夹搞定，===》》》
## 然后就是聚类的推荐算法


## todo 检查一下回复率是怎么回事,,,bug
## todo 前端总是加载不出的样子  ，总是显示一个不显示一个，不知道怎么回事。
## todo 把数据基本字段都搞定可视化
## todo 把数据处理一下，找一个算法用做价格的预测
## todo 还要写查询数据,多条件查询，   标签种出现最多的，找出来，朴素贝叶斯考虑一下




# todo 改成分析
# todo 写一个接口，每天凌晨自动调用一下网页的各个有缓存的地方，重新生成一些缓存备用之类的。
# todoed 把收藏的房子进行持续的追踪分析。喜欢的，已收藏的。
# todo 用request 写每日刷新的东西


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
        print("进程不存在")
        print("启动进程hotel")
        subprocess.getoutput("nohup scrapy crawl hotel >/dev/null 2>&1 &")  # 启动它
    if checkprocess_cmdline("scrapy crawl hotel"): # 设置每两小时检查一下
        print("进程存在")
    else:
        print("进程不存在")
        print("启动进程")
        subprocess.getoutput("nohup scrapy crawl cap_house >/dev/null 2>&1 &")
    # 还有收藏夹中的检查爬行

if __name__ == '__main__':
    # if isinstance(checkprocess("scrapy"), int):
    if checkprocess_cmdline: # 设置每两小时检查一下
        print("进程存在")
    else:
        print("进程不存在")
        print("启动进程")


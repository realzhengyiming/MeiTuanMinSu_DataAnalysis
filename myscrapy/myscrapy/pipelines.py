# -*- coding: utf-8 -*-
import redis
from hotelapp.models import House, Facility, Host, Labels  # settings中设置好了路径，这儿可以直接app导入django模型
import pymysql
from .items import HouseItem, CityItem  # 只导入这个演变的类就可以，其他几个是多对多
from .items import urlItem  # master专用
from scrapy.exceptions import DropItem


# todo 标签lable怎么又看不到了。

class urlItemPipeline(object):  # master专用管道
    def __init__(self):
        self.redis_url = "redis://Zz123zxc:@127.0.0.1:6378/"  # master端是本地redis的
        self.r = redis.Redis.from_url(self.redis_url, decode_response=True)

    def process_item(self, item, spider):
        if isinstance(item, urlItem):
            print("urlItem item")
            try:
                # item.save()
                self.r.lpush("Meituan:start_urls", item['url'])
            except Exception as e:
                print(e)
        return item


class cityItemPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, CityItem):
            print("CityItem item")
            try:
                item.save()
            except Exception as e:
                print(e)
        return item


class houseItemPipeline(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        if isinstance(item, HouseItem):
            print("HouseItem item")
            house = None
            try:
                house = item.save()  # 最后才可以save这个
                print("hosuse保存成功")

            except Exception as e:
                print("hosuse保存失败，后面的跳过保存")
                print(e)
                print(item)
                return item

            jsonString = item.get("jsonString")
            labelsList = jsonString['Labels']
            facilityList = jsonString['Facility']
            hostInfos = jsonString['Host']

            # house = House.objects.filter(**{'house_id':item.get("house_id"),"house_date":item.get("house_date")}).first()  
            # 查询一次就可以,多条件查询，查询两个联合的主键
            # 这儿是标签的多对多写入
            for onetype in labelsList:  # 1.添加所有标签的
                for one in labelsList[onetype]:  # one都是一个标签
                    try:  # 先找找有没有，然后把已经有的添加进来
                        label = Labels.objects.filter(
                            **{'label_name': one[0], "label_desc": one[1]})  # 找到的话就直接加入另一个Meiju对象中
                        # print("长度")
                        if len(label) == 0:
                            # print("需要创建后添加")
                            l = Labels()
                            l.label_name = one[0]
                            l.label_desc = one[1]
                            # print("检查label")
                            # print(f"onetype:{onetype}")
                            # print(one)
                            if onetype == "1":  # 优惠标签
                                l.label_type = 1  # 数字也行把，应该，这儿没改
                            else:
                                l.label_type = 0
                            l.save()
                            # label = Labels.objects.filter(**{'label_name':one[0],"label_desc":one[1]})  # 找到的话就直接加入另一个Meiju对象中
                            house.house_labels.add(l)  # 直接把刚才的添加进来
                        else:
                            # print("找到有直接添加")
                            # print(label)
                            house.house_labels.add(label.first())  # 这样添加进来的
                            # print("添加成功")
                    except Exception as e:
                        print(e)
                        print("label已存在，跳过插入")
                        # print(e)

            # 这儿开始是Facility的写入
            # print(facilityList)
            # 先全部写入一遍，然后再把有的添加起来就好，这个效率不太高的样子
            for facility in facilityList:
                if 'metaValue' in facility:
                    print()  # 执行先检查后添加
                    try:  # 先找找有没有，然后把已经有的添加进来
                        fac = Facility.objects.filter(**{'facility_name': facility['value']})  # 找到的话就直接加入另一个Meiju对象中
                        # print("长度")
                        if len(fac) == 0:
                            # print("需要创建后添加")
                            l = Facility()
                            l.facility_name = facility['value']
                            l.save()
                            # fac = Facility.objects.filter(**{'label_name':facility['value']})  # 找到的话就直接加入另一个Meiju对象中
                            # print(l)
                            house.house_facility.add(l)
                        else:
                            # print("找到有直接添加")
                            house.house_facility.add(fac.first())  # 这样添加进来的
                            # print("添加成功")
                    except Exception as e:
                        print("facility已经存在，跳过插入")
                        # print(e)

            print("下面开始host信息的添加")
            '''{'hostId': '36438164',
                 'host_RoomNum': '51',
                 'host_commentNum': '991',
                 'host_name': '【塔宿】醉美小蛮腰',
                 'host_replayRate': '100'}'''
            print(hostInfos)

            try:  # 先找找有没有，然后把已经有的添加进来,fixing
                hosts = Host.objects.filter(**{
                    'host_id': hostInfos['hostId'],
                    'host_updateDate': house.house_date})  # 找到的话就直接加入另一个Meiju对象中
                print("长度")
                print("输出查找到的结果")
                print(hosts)
                # if len(hosts) == 0:   # 都可以创建，可以看房东的评价变化
                try:
                    # print("需要创建后添加")
                    l = Host()
                    l.host_name = hostInfos['host_name']
                    l.host_id = hostInfos['hostId']
                    l.host_RoomNum = hostInfos['host_RoomNum']
                    l.host_commentNum = hostInfos['host_commentNum']
                    l.host_replayRate = hostInfos['host_replayRate']
                    l.save()  # 保存不成功会自然进行处理
                    # fac = Facility.objects.filter(**{'label_name':facility['value']})  # 找到的话就直接加入另一个Meiju对象中
                    # print("__label_")
                    # print(l)
                    house.house_host.add(l)
                except Exception as e:
                    print(e)
                    # else:
                    # print("不为空找到了")
                    # print("__label_")
                    # print(fac)
                    house.house_host.add(hosts.first())  # 这样添加进来的
                    print("已有的情况下添加成功")
            except Exception as e:
                print("以有这个host跳过插入")
                print(e)

            return item  # 这个暂时是无所谓的，因为只有一个管道
        return item

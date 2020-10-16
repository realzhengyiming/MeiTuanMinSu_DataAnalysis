# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from hotelapp.models import House, Host, Facility, Labels, City  # 这四个都是django的models
from scrapy_djangoitem import DjangoItem


# 这下面开始是四个orm对象，从django中结合进来的
class HouseItem(DjangoItem):
    django_model = House
    jsonString = scrapy.Field()  # 这儿需要增加临时字段过来，用来把多个其他对象的属性一次性传过来


class HostItem(DjangoItem):
    django_model = Host


class LabelsItem(DjangoItem):
    django_model = Facility


class FacilityItem(DjangoItem):
    django_model = Labels


class CityItem(DjangoItem):
    django_model = City


class urlItem(scrapy.Item):  # master专用item
    # define the fields for your item here like:
    url = scrapy.Field()

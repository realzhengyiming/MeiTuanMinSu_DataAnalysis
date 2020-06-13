# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     city_tags   
   Description :  
   Author :        zhengyimiing 
   date：          2020/4/28 
-------------------------------------------------
   Change Activity:
                   2020/4/28  
-------------------------------------------------
"""

__author__ = 'zhengyimiing'

from django import template

register = template.Library()
from hotelapp.models import City

@register.inclusion_tag('hotelapp/select.html')
def get_all_city():
    result = City.objects.all()
    return {'allcity': result, }

@register.inclusion_tag('hotelapp/select_cityName.html')
def get_all_cityName():
    result = City.objects.all()
    return {'allcity': result, }
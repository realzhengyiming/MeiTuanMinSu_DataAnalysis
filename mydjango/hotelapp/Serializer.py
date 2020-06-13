# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     Serializer   
   Description :  
   Author :        zhengyimiing 
   date：          2020/3/25 
-------------------------------------------------
   Change Activity:
                   2020/3/25  
-------------------------------------------------
"""
from django.contrib.auth.models import User
from .models import Favourite,City
from rest_framework import serializers, viewsets

__author__ = 'zhengyimiing'


class userSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = '__all__'


class citySerializer(serializers.Serializer):
    class Meta:
        model = City
        fields = "__all__"


# 序列化Favourite 方便进行接口上的增删查改(登陆后才可以进行的操作)
class FavouriteSerializer(serializers.Serializer):
    user = userSerializer(read_only=True, many=True)
    city = citySerializer(read_only=True, many=True)

    class Meta:
        model = Favourite
        fields = '__all__'
    # user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    # #     # fav_house = models.CharField(max_length=50,unique=True)   # 城市名字
    # fav_city = models.OneToOneField(City, unique=True, on_delete=models.CASCADE)  # 偏好城市,前端处理
    # fav_houses = models.ManyToManyField(House)


# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     urls   
   Description :  
   Author :        zhengyimiing 
   date：          2020/1/10 
-------------------------------------------------
   Change Activity:
                   2020/1/10  
-------------------------------------------------
"""
from . import drawviews

__author__ = 'zhengyimiing'
from django.urls import path,re_path
from . import views
from django.contrib.auth import views as auth_views

app_name = "hotelapp"    # 这儿需要设置这个来分辨不同的app

urlpatterns = [
    path("/test/",views.testindex,name="testindex"),
    path("", views.index, name='index'),
    path("/",views.index, name="index2"),
    path("/facilityPage/",views.facilityPage, name="facilityPage"),
    path("/loginpage/",views.loginPage, name="user_login"),
    path('/logout/',views.userLogout, name="user_logout"),
    path("/register/",views.register, name="user_register"),
    path('/password-change/', auth_views.PasswordChangeView,
         {'post_change_redirect': '/hotelapp/?success_info=password_change_success',
            'template_name':"hotelapp/password_change_form.html" #, 'extra_context':{"success_info":"password_change_success"}
          },name="password_change"),  # html页面默认在registration内，修改了页面
    path('/password-change-done/', auth_views.PasswordChangeDoneView,
         {'template_name':"hotelapp/index_chartspage.html"}, name="password_change_done"),
    path("/detail/",views.detailView,name="detail"),
    path("/detaillist/",views.detaillist,name="detaillist"),
    path("/host/",views.hostPage,name="host"),
    path("/consumer/",views.consumerPage,name="consumer"),
    path("/time/", views.timePage, name="time"),
    path("/price/", views.pricePage, name="price"),
    path('/favcount/',views.favcountPage,name="favcount"),  # todo
    path("/area/", views.area, name="area"), # todo
    path("/search/", views.searchPage, name="search"),
    # path("/get_picture/", drawviews.get_picture, name="get_picture"),
    path("/assess/", views.assessPage, name="assess"),
    path("/predict/", views.predictPage, name="predict"),


    path("/search_keyword/", views.getSearch, name="search_keyword"),
    path("/favourite/",views.favouriteHandler.as_view(),name="Favourite"),
    path("/get_fav_house_by_id/", views.get_fav_house_by_id.as_view(), name="get_fav_house_by_id"),
    path("/getHotTitle/", views.getHotTitle.as_view(), name="getHotTitle"),
    # 增加一个显示可视化的,下面是api类的接口resf
    path('/bar/', drawviews.ChartView.as_view(), name='bar'),
    path("/_price/",drawviews._price.as_view(),name='_price'),
    path("/pie/", drawviews.PieView.as_view(), name="pie"),
    path('/timeline/',drawviews.timeLineView.as_view(), name="timeline"),
    path('/getMonthPostTime/', drawviews.getMonthPostTime.as_view(), name='getMonthPostTime'),
    path('/getMonthPostTime2/', drawviews.getMonthPostTime2.as_view(), name='getMonthPostTime2'),
    path("/drawmap/",drawviews.drawMap.as_view(), name="drawMap"),
    path("/getcitycount/",drawviews.getCityCount.as_view(), name="getcitycount"),
    path("/houseTimeLineView/",drawviews.houseTimeLineView.as_view(),name="houseTimeLineView"),
    path("/houseScoreLine/",drawviews.houseScoreLine.as_view(), name="houseScoreLine"),  # 使用api的都是这样的
    path("/house_firstOnSale/", drawviews.get_twoLatestYear.as_view(), name="house_firstOnSale"),
    path("/get_postTimeLine/", drawviews.get_postTimeLine.as_view(), name="get_postTimeLine"),
    path("/get_hostDraw/",drawviews.get_hostDraw.as_view(),name="get_hostDraw"),
    path("/get_hostReplay/",drawviews.get_hostReplay.as_view(),name="get_hostReplay"),
    path("/_price_bar/",drawviews._price_bar.as_view(),name="_price_bar"),  # 这个是画歌饼的
    path("/_price_boxplot/",drawviews._price_boxplot.as_view(),name="_price_boxplot"),  # 这个是画box图的
    path("/_price_heatmap/",drawviews._price_heatmap.as_view(),name="_price_heatmap"),
    path("/_postTime_cityName/", drawviews._postTime_cityName.as_view(), name="_postTime_cityName"),
    path("/diffcity_hostNum/", drawviews.diffcity_hostNum.as_view(), name="diffcity_hostNum"), # 这个是测试的host地域
    path("/_facility/", drawviews._facility.as_view(), name="_facility"),  # 这个是测试的host地域
    path("/_facility_price/", drawviews._facility_price.as_view(), name="_facility_price"),  # 这个是测试的host地域
    path("/area_bar/", drawviews.area_bar.as_view(), name="area_bar"),  # 这个是测试的host地域
    path("/area_price_scatter/", drawviews.area_price_scatter.as_view(), name="area_price_scatter"),  # 散点图
    path("/area_price_location_scatter/", drawviews.area_price_location_scatter.as_view(),
         name="area_price_location_scatter"),  # 散点图
    path("/house_content/", drawviews.house_content.as_view(),
         name="house_content"),  # 散点图
    path("/predictPrice/", drawviews.predictPrice.as_view(),
         name="predictPrice"),  # 房价预测线性模型




]

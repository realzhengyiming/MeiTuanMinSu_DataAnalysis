import base64
import datetime
from io import BytesIO

import pandas as pd
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from numpy.matlib import randn
from pandas import DataFrame
import uuid
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db import connection
# from pyecharts.globals import ThemeType
from django.urls import reverse
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType, ChartType
from django.core.cache import cache  # 导入缓存对象,redis存储
# from rest_framework.response import Response
# from requests import Response
from rest_framework_extensions.cache.decorators import cache_response
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import linear_model
from sklearn.model_selection import train_test_split

from .forms import LoginForm, RegistrationForm
# from .Serializer import UserSerializer
from .models import House
import time
from django.db.models import Avg, Max, Min, Count, Sum  # 直接使用models中的统计类来进行统计查询操作
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # 用来分页饿

##### 后面开始pyechart绘图
import json
from random import randrange
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.views import APIView
from pyecharts.charts import Bar, Pie, Line, Geo, BMap, Grid
from pyecharts import options as opts


def fetchall_sql(sql) -> dict:  # 这儿唯一有一个就是显示页面的
    # latest_question_list = KeyWordItem # 换成直接使用sql来进行工作
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()
        # columns = [col[0] for col in cursor.description]  # 提取出column_name
        # return [dict(zip(columns, row)) for row in cursor.fetchall()][0]
        return row


def fetchall_sql_dict(sql) -> [dict]:  # 这儿唯一有一个就是显示页面的
    # latest_question_list = KeyWordItem # 换成直接使用sql来进行工作
    with connection.cursor() as cursor:
        cursor.execute(sql)
        # row = cursor.fetchall()
        columns = [col[0] for col in cursor.description]  # 提取出column_name
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def response_as_json(data):
    json_str = json.dumps(data)
    response = HttpResponse(
        json_str,
        content_type="application/json",
    )
    response["Access-Control-Allow-Origin"] = "*"
    return response


def json_response(data, code=200):
    data = {
        "code": code,
        "msg": "success",
        "data": data,
    }
    return response_as_json(data)


def json_error(error_string="error", code=500, **kwargs):
    data = {
        "code": code,
        "msg": error_string,
        "data": {}
    }
    data.update(kwargs)
    return response_as_json(data)


JsonResponse = json_response
JsonError = json_error


# 这个是 登陆,不用这种，这种是高耦合
# def login(request):
#     if request.method == 'GET':
#         print("get进来的")
#         return HttpResponse("fuck you ")
#     if request.method == 'POST':  # 当提交表单时
#         print("post进来了")
#         dic = {"flag":1}  # 这个是什么东西
#         判断是否传参
#         # if request.POST:
#         #     password = request.POST.get('password')
#         #     account = request.POST.get('account')
#             判断参数中是否含有a和b
#             # print(password)
#             # print(account)
#             # return HttpResponse(dic)
#         else:
#         # return HttpResponse('输入错误')
#
#     else:
#         return HttpResponse('方法错误')

## 数据概略处的图
# 最近7天爬虫数据爬取
def bar_base() -> Bar:  # 返回给前端用来显示图的json设置,按城市分组来统计数量
    nowdate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    count_total_city = House.objects.filter(house_date=nowdate).values("house_cityName").annotate(
        count=Count("house_cityName")).order_by("-count")
    # for i in count_total_city:
    #     print(i['house_cityName']," ",str(i['count']))
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.WONDERLAND))
            .add_xaxis([city['house_cityName'] for city in count_total_city])
            .add_yaxis("房源数量", [city['count'] for city in count_total_city])
            # .add_yaxis("商家B", [randrange(0, 100) for _ in range(6)])
            # .set_global_opts(title_opts=opts.TitleOpts(title="总房屋类型"))
            .set_global_opts(title_opts=opts.TitleOpts(title="今天城市房源数量", subtitle="如图"),
                             xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                             )
            .set_global_opts(
            datazoom_opts={'max_': 2, 'orient': "horizontal", 'range_start': 10, 'range_end': 20, 'type_': "inside"})
            .dump_options_with_quotes()
    )
    return c


class ChartView(APIView):  # 这个就是返回的组件
    def get(self, request, *args, **kwargs):
        return JsonResponse(json.loads(bar_base()))  # 这儿这个是返回json数据用来装到bar中的


class PieView(APIView):  # 房型饼图
    def get(self, request, *args, **kwargs):
        result = fetchall_sql(
            "select house_type,count(house_type) from (select distinct house_id ,house_type from hotelapp_house  group by house_id,house_type ) hello group by house_type")
        c = (
            Pie()
                .add("", [z for z in zip([i[0] for i in result], [i[1] for i in result])])
                # .add("",[list(z) for z in zip([x['house_type'] for x in house_type_count],[x['count'] for x in house_type_count])])
                .set_global_opts(title_opts=opts.TitleOpts(title="总房屋类型"))
                .set_series_opts(label_opts=opts.LabelOpts(
                formatter="{b}: {c} | {d}%",
            ))
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


## 这几个都是API 可以直接网页读取出来的
class getCityCount(APIView):  # 读取城市数量的api
    def get(self, request, *args, **kwargs):
        result = fetchall_sql(
            """ select house_cityName,count(house_cityName) from  (SELECT distinct(house_id),house_cityName FROM `hotelapp_house`  ) hello group by house_cityName""")
        return json_response({"data": result})


# 这个是按月的查询
class getMonthPostTime(APIView):  # 理论上这个按年份来进行统计
    def get(self, request, *args, **kwargs):
        result = fetchall_sql('''select DATE_FORMAT(house_firstOnSale,'%Y-%m')
          as mydate,count(DATE_FORMAT(house_firstOnSale,'%Y-%m'))as 
         mydate_count from hotelapp_house group by mydate ORDER BY mydate'''
                              )
        context = {"result": result}
        return JsonResponse(context)


class getMonthPostTime2(APIView):  # 按各个月份来进行统计
    def get(self, request, *args, **kwargs):
        result = fetchall_sql(
            '''select DATE_FORMAT(house_firstOnSale,'%m') as mydate,count(DATE_FORMAT(house_firstOnSale,'%Y-%m'))as mydate_count from hotelapp_house group by mydate ORDER BY mydate'''
        )
        context = {"result": result}
        # for i in result:
        #     print(i)
        return JsonResponse(context)


class timeLineView(APIView):
    def get(self, request, *args, **kwargs):
        # week_name_list = getLatestSevenDay()  # 获得最近七天的日期 时间列折线图
        # 七天前的那个日期
        today = datetime.datetime.now()
        # // 计算偏移量
        offset = datetime.timedelta(days=-6)
        # // 获取想要的日期的时间
        re_date = (today + offset).strftime('%Y-%m-%d')
        house_sevenday = House.objects.filter(house_date__gte=re_date).values("house_date"). \
            annotate(count=Count("house_date")).order_by("house_date")
        week_name_list = [day['house_date'] for day in house_sevenday]
        date_count = [day['count'] for day in house_sevenday]
        c = (
            Line(init_opts=opts.InitOpts(width="1600px", height="800px"))
                .add_xaxis(xaxis_data=week_name_list)
                .add_yaxis(
                series_name="抓取的数量",
                # y_axis=high_temperature,
                y_axis=date_count,
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="最大值"),
                        opts.MarkPointItem(type_="min", name="最小值"),
                    ]
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="average", name="平均值")]
                ),
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(title="最近七天抓取情况", subtitle=""),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            )
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


class _postTime_cityName(APIView):  # todo 各个城市新增的东西 经纬度再加上价格这样展示怎么样，发布时间也可以再增加一个来分析
    def get(self, request, *args, **kwargs):
        temp_df = cache.get('price_cityName', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict('''SELECT distinct house_id,year( house_firstOnSale) house_year,
                house_cityName FROM hotelapp_house ''')
            # 都使用df来进行处理和显示
            temp_df = pd.DataFrame(result)
            cache.set('price_cityName', temp_df, 3600 * 12)  # 设置缓存

        from pyecharts import options as opts
        from pyecharts.charts import Map, Timeline
        temp = temp_df.groupby(["house_cityName", "house_year"]).count().sort_values(["house_cityName", "house_year"],
                                                                                     ascending=True)  # 不同的数量的东西
        temp = temp.groupby('house_cityName').cumsum()
        tl = Timeline()
        from time import strftime, localtime
        year = strftime("%Y", localtime())

        s = set()
        templist = []
        for i in list(temp.index):
            s.add(str(i[0]))
        templist = list(s)
        newlist = {}
        for city in templist:
            # print(city)
            temp_list = []
            for i in range(2017, 2021):
                # print("当前年份" + str(i))
                try:
                    # print(temp.loc[city].loc[i].values)
                    # print(type(temp.loc[city].loc[i].values))
                    temp_list.append(int(temp.loc[city].loc[i].values[0]))
                except Exception as e:
                    print(e)
                    temp_list.append(0)
            newlist[city] = temp_list
        j = 0
        print([newlist[i][j] for i in newlist])

        for i in range(2017, int(year) + 1):  # 写死了这里
            map0 = (
                Geo()
                    .add_schema(maptype="china")
                    .add(
                    "geo",
                    [list(z) for z in zip([str(i) for i in newlist.keys()], [newlist[i][j] for i in newlist])],
                    type_=ChartType.HEATMAP,
                )
                    .set_global_opts(
                    visualmap_opts=opts.VisualMapOpts(),
                    title_opts=opts.TitleOpts(title=f"2017到{year}发布房源数量热力图"),
                )
            )
            j += 1
            tl.add(map0, "{}年".format(i))
        c = (tl.dump_options_with_quotes())
        return JsonResponse(json.loads(c))  # f安徽这个


class drawMap(APIView):  # 要加apiview # 美团房源数量热力图
    def get(self, request, *args, **kwargs):
        from pyecharts import options as opts
        from pyecharts.charts import Map
        from pyecharts.faker import Faker

        result = cache.get('house_city', None)  # 使用缓存，可以共享真好。
        if result is None:  # 如果无，则向数据库查询数据
            print("使用缓存房源城市统计")
            result = fetchall_sql(
                """select house_cityName,count(house_cityName) as count from  (SELECT distinct(house_id),house_cityName FROM  hotelapp_house) hello group by house_cityName""")
            cache.set('house_city', result, 3600 * 12)  # 设置缓存

        else:
            pass
        c = (
            Geo()
                .add_schema(maptype="china")
                .add(
                "房源",
                [z for z in zip([i[0] for i in result], [i[1] for i in result])],
                type_=ChartType.HEATMAP,
            )
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(),
                title_opts=opts.TitleOpts(title="美团民宿房源热力图"),
            )
                .dump_options_with_quotes()
        )

        return JsonResponse(json.loads(c))  # f安徽这个


# 下面是详情页的函数
# 房子持续的价格变化折线图
class houseTimeLineView(APIView):
    def get(self, request, *args, **kwargs):
        house_id = request.GET.get("house_id")  # 提取出house_id
        result = fetchall_sql(f'select house_date,house_oriprice,house_discountprice,' +
                              f'house_avarageScore,house_img from hotelapp_house where house_id="{house_id}"  ' +
                              f'and house_oriprice !=0.00 and house_discountprice!=0.00  order by house_date limit 0,7')
        week_name_list = [house[0] for house in result]
        oriprice = [house[1] for house in result]
        discountprice = [house[2] for house in result]
        house_avarageScore = [house[3] for house in result]  # 平均分列表

        c = (
            Line(init_opts=opts.InitOpts(width="1600px", height="800px"))
                .add_xaxis(xaxis_data=week_name_list)
                .add_yaxis(
                series_name="初始价",
                # y_axis=high_temperature,
                y_axis=oriprice,
                markpoint_opts=opts.MarkPointOpts(
                    # data=[
                    #     opts.MarkPointItem(type_="max", name="最低价"),
                    #     opts.MarkPointItem(type_="min", name="最高价"),
                    # ]

                )
            )
                .add_yaxis(
                series_name="现价",
                # y_axis=high_temperature,
                is_connect_nones=True,
                y_axis=discountprice,
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        # opts.MarkPointItem(type_="max", name=""),
                        opts.MarkPointItem(type_="min", name="最低价"),
                    ]
                )
            )
                # .add_yaxis(
                # series_name="折扣价",
                # y_axis=high_temperature,
                # is_connect_nones=True,
                # y_axis = house_avarageScore,
                # markpoint_opts=opts.MarkPointOpts(
                # data=[
                #     opts.MarkPointItem(type_="max", name="最低价"),
                #     opts.MarkPointItem(type_="min", name="最高价"),
                # ]
                # )
                # markline_opts=opts.MarkLineOpts(
                #     data=[opts.MarkLineItem(type_="average", name="平均值")]
                # ),
                # )
                .set_global_opts(
                title_opts=opts.TitleOpts(title="最近房源数据价格", subtitle=""),
                # tooltip_opts=opts.TooltipOpts(trigger="axis"),
                # toolbox_opts=opts.ToolboxOpts(is_show=True),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            )
                # .render("temperature_change_line_chart.html")
                .dump_options_with_quotes()  # 这个是序列化为json必须加上的参数最后
        )
        return JsonResponse(json.loads(c))


# 详情页评分折线图
class houseScoreLine(APIView):
    def get(self, request):
        house_id = request.GET.get("house_id")
        result = fetchall_sql(
            f'select house_date,house_avarageScore,house_img,house_descScore,house_hygieneScore,house_positionScore,house_talkScore from hotelapp_house where house_id="{house_id}"  '
            f'and house_oriprice !=0.00 and house_discountprice!=0.00  order by house_date limit 0,7')  # todo 这个很有意思
        # print()
        # print(result)
        week_name_list = [house[0] for house in result]
        avarageScore = [house[1] for house in result]
        # discountprice = [house[2] for house in result]
        descScore = [house[3] for house in result]
        hygieneScore = [house[4] for house in result]
        positionScore = [house[5] for house in result]
        talkScore = [house[6] for house in result]

        c = (
            Line(init_opts=opts.InitOpts(width="1600px", height="800px", theme=ThemeType.LIGHT))
                .add_xaxis(xaxis_data=week_name_list)
                # .add_xaxis(xaxis_data=date_count)
                .add_yaxis(
                series_name="平均分",
                # y_axis=high_temperature,
                y_axis=avarageScore,
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="最高分"),
                        #     opts.MarkPointItem(type_="min", name="最高价"),
                    ]

                )
            )
                .add_yaxis(
                series_name="描述得分",
                is_connect_nones=True,
                y_axis=descScore,
                # markpoint_opts=opts.MarkPointOpts(
                #     data=[
                #         opts.MarkPointItem(type_="max", name="最低价"),
                #         opts.MarkPointItem(type_="min", name="最高价"),
                #     ]
                # )
            )
                .add_yaxis(
                series_name="沟通得分",
                is_connect_nones=True,
                y_axis=talkScore,

                # markpoint_opts=opts.MarkPointOpts(
                #     data=[
                #         opts.MarkPointItem(type_="max", name="最低价"),
                #         opts.MarkPointItem(type_="min", name="最高价"),
                #     ]
                # )
            ).add_yaxis(
                series_name="卫生得分",
                is_connect_nones=True,
                y_axis=hygieneScore,
                # markpoint_opts=opts.MarkPointOpts(
                #     data=[
                #         opts.MarkPointItem(type_="max", name="最低价"),
                #         opts.MarkPointItem(type_="min", name="最高价"),
                #     ]
                # )
            )
                .add_yaxis(
                series_name="位置得分",
                is_connect_nones=True,
                y_axis=positionScore,
                # markpoint_opts=opts.MarkPointOpts(
                #     data=[
                #         opts.MarkPointItem(type_="max", name="最低价"),
                #         opts.MarkPointItem(type_="min", name="最高价"),
                #     ]
                # )
            )

                .set_global_opts(
                title_opts=opts.TitleOpts(title="最近房源评价情况", subtitle="满分5分"),
                # tooltip_opts=opts.TooltipOpts(trigger="axis"),
                # toolbox_opts=opts.ToolboxOpts(is_show=True),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            )
                # .render("temperature_change_line_chart.html")
                .dump_options_with_quotes()  # 这个是序列化为json必须加上的参数最后
        )
        return JsonResponse(json.loads(c))


# 发布时间分析，获得最近两年的发布数量的情况
class get_twoLatestYear(APIView):  # 按各个月份来进行统
    # @cache_response(timeout=60 * 60*3, cache='default')
    def get(self, request, *args, **kwargs):
        yearRange = request.GET.get("yearRange")
        oneYear = yearRange.split("-")[0]
        twoYear = yearRange.split("-")[1]
        print(yearRange)

        temp_df = cache.get('house_firstOnSale_df', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("没有缓存，重新查询,house_firstOnSale_df")
            result = fetchall_sql_dict('''SELECT distinct(id),house_firstOnSale FROM hotelapp_house ''')
            temp_df = pd.DataFrame(result)
            temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            # type(df.id.resample("1M").count())  # huode 按月份来
            # df.id.resample("Y").count()
            # df.id.resample("M").count()
            # df.id.resample("D").count()  # 忽略为0的值来处理
            # df.resample("Q-DEC").count()  # 季度
            cache.set('house_firstOnSale_df', temp_df, 3600 * 12)  # 设置缓存

        dff = temp_df.id.resample("QS-JAN").count().to_period("Q")  # 加上这个就好了 .to_period('Q')  # 季度

        import pyecharts.options as opts
        from pyecharts.charts import Line
        c = (
            Line(init_opts=opts.InitOpts(width="1600px", height="800px"))
                .add_xaxis(
                # xaxis_data=[str(j) for j in dff[oneYear].index],
                xaxis_data=[str(twoYear) + "Q" + str(j) for j in range(1, 5)],
            )
                .extend_axis(
                # xaxis_data=[str(j) for j in dff[twoYear].index],
                xaxis_data=[str(oneYear) + "Q" + str(jx) for jx in range(1, 5)],

                xaxis=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                    axisline_opts=opts.AxisLineOpts(
                        is_on_zero=False, linestyle_opts=opts.LineStyleOpts(color="#6e9ef1")
                    ),
                    axispointer_opts=opts.AxisPointerOpts(
                        is_show=True,
                        # label=opts.LabelOpts(formatter=JsCode(js_formatter)
                        #                      )
                    ),
                ),
            )
                .add_yaxis(
                series_name=f"{oneYear}",
                is_smooth=True,
                symbol="emptyCircle",
                is_symbol_show=False,
                # xaxis_index=1,
                color="#d14a61",
                # y_axis=[2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3],
                y_axis=[int(x) for x in dff[oneYear].values],

                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(width=2),
            )
                .add_yaxis(
                series_name=f"{twoYear}",
                is_smooth=True,
                symbol="emptyCircle",
                is_symbol_show=False,
                color="#6e9ef1",
                # y_axis=[3.9, 5.9, 11.1, 18.7, 48.3, 69.2, 231.6, 46.6, 55.4, 18.4, 10.3, 0.7],
                y_axis=[int(x) for x in dff[twoYear].values],

                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(width=2),
            )

                .set_global_opts(
                legend_opts=opts.LegendOpts(),
                title_opts=opts.TitleOpts(title=f"{yearRange}期间发布房源的数量", subtitle="单位个"),
                tooltip_opts=opts.TooltipOpts(trigger="none", axis_pointer_type="cross"),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                    axisline_opts=opts.AxisLineOpts(
                        is_on_zero=False, linestyle_opts=opts.LineStyleOpts(color="#d14a61")
                    ),
                    axispointer_opts=opts.AxisPointerOpts(
                        # is_show=True, label=opts.LabelOpts(formatter=JsCode(js_formatter))
                    ),
                ),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(
                        is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=1)
                    ),
                ),
            )
                .dump_options_with_quotes()  # 这个是序列化为json必须加上的参数最后
        )

        return JsonResponse(json.loads(c))


# 封装好的按月份或则年份来分的时间折线图
class get_postTimeLine(APIView):  # 按月份分，或者按年分
    # @cache_response(timeout=60 * 60*3, cache='default')
    def get(self, request, *args, **kwargs):
        timeFreq = request.GET.get("timeFreq")
        # print(timeFreq)
        temp_df = cache.get('house_firstOnSale_df', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("没有缓存,重新查询")
            result = fetchall_sql_dict('''SELECT distinct(id),house_firstOnSale FROM hotelapp_house ''')
            temp_df = pd.DataFrame(result)
            temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            # type(df.id.resample("1M").count())  # huode 按月份来
            # df.id.resample("Y").count()
            # df.id.resample("M").count()
            # df.id.resample("D").count()  # 忽略为0的值来处理
            # df.resample("Q-DEC").count()  # 季度
            cache.set('house_firstOnSale_df', temp_df, 3600 * 12)  # 设置缓存
        else:
            pass
        # if timeFreq!="" or timeFreq!=None:
        label = ""
        title = ""
        if timeFreq == "month":
            timeFreq = "M"
            label = "月新增房源"
        if timeFreq == "year":
            timeFreq = 'A'
            label = "年新增房源"
        if timeFreq == "season":
            timeFreq = 'Q-DEC'
            label = "季度新增房源"
        dff = temp_df.house_firstOnSale.resample(f"{timeFreq}").count().to_period(
            f"{timeFreq}")  # 加上这个就好了 .to_period('Q')  # 季度

        # dff.resample('A').mean().to_period('A')

        x_data = [str(y) for y in dff.index]
        y_data = [str(x) for x in dff.values]

        c = (
            Line()
                .add_xaxis(xaxis_data=x_data)
                .add_yaxis(
                series_name=label,
                stack="新增房源数量",
                y_axis=y_data,
                label_opts=opts.LabelOpts(is_show=False),
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(title="房源发布时间序列分析"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            )
                .dump_options_with_quotes()  # 这个是序列化为json必须加上的参数最后
        )

        return JsonResponse(json.loads(c))


class get_hostDraw(APIView):  # 按月份分，或者按年分
    # @cache_response(timeout=60 * 60*3, cache='default')
    def get(self, request, *args, **kwargs):
        # timeFreq = request.GET.get("timeFreq")
        # print(timeFreq)
        temp_df = cache.get('host_result', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                '''SELECT distinct host_id,host_name,host_RoomNum,host_replayRate,host_commentNum FROM `hotelapp_host` order by host_RoomNum DESC''')
            temp_df = pd.DataFrame(result)
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            cache.set('host_result', temp_df, 3600 * 12)  # 设置缓存
        else:
            pass
        from pyecharts.charts import Bar
        from pyecharts.faker import Faker
        from pyecharts.globals import ThemeType
        print("显示数据")
        # print(temp_df)
        # print(list(temp_df.host_name.values)[:50])
        # print(list(temp_df.host_RoomNum.values)[:50])
        # for i in :

        #
        # (type(i))
        # temp_df = temp_df.sort_values(by='host_RoomNum',ascending=False)
        c = (
            Bar()
                .add_xaxis(list(temp_df.host_name.values)[:10])
                .add_yaxis("房东昵称", [int(i) for i in list(temp_df.host_RoomNum.values)[:10]])
                # .add_yaxis("商家B", [randrange(0, 100) for _ in range(6)])

                .set_global_opts(title_opts=opts.TitleOpts(title="房源数量Top10的房东", subtitle="如图"),
                                 datazoom_opts=opts.DataZoomOpts(),
                                 xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                                 )
                # .set_global_opts(datazoom_opts={ 'orient': "horizontal", 'range_start': 1, 'range_end': 8,
                #                                 'type_': "inside"})
                # title_opts=opts.TitleOpts(title="Bar-DataZoom（slider-水平）"),
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


######  房东图表

# 最常在线回复的前100房东
class get_hostReplay(APIView):
    # @cache_response(timeout=60 * 60*3, cache='default')
    def get(self, request, *args, **kwargs):
        # timeFreq = request.GET.get("timeFreq")
        # print(timeFreq)
        temp_df = cache.get('host_result', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                '''SELECT distinct host_id,host_name,host_RoomNum,host_replayRate,host_commentNum FROM `hotelapp_host` order by host_RoomNum DESC''')
            temp_df = pd.DataFrame(result)
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            cache.set('host_result', temp_df, 3600 * 12)  # 设置缓存
        else:
            pass
        from pyecharts.charts import Bar
        from pyecharts.faker import Faker
        from pyecharts.globals import ThemeType
        print("显示数据")
        temp_df = temp_df.sort_values(by=['host_replayRate', 'host_commentNum'], ascending=False)
        c = (
            Bar()
                .add_xaxis(list(temp_df.host_name.values)[:10])
                # .add_yaxis("房东回复率%", [int(i) for i in list(temp_df.host_replayRate.values)[:10]])  # 先取消
                .add_yaxis("房东评论数", [int(i) for i in list(temp_df.host_commentNum.values)[:10]])

                .set_global_opts(title_opts=opts.TitleOpts(title="热情Top10的房东", subtitle="如图"),
                                 datazoom_opts=opts.DataZoomOpts(),
                                 xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                                 )
                # .set_global_opts(datazoom_opts={ 'orient': "horizontal", 'range_start': 1, 'range_end': 8,
                #                                 'type_': "inside"})
                # title_opts=opts.TitleOpts(title="Bar-DataZoom（slider-水平）"),
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


# 最常在线回复的前100房东
class _price(APIView):
    # @cache_response(timeout=60 * 60*3, cache='default')
    def get(self, request, *args, **kwargs):
        pass

        temp_df = cache.get('_price_house_oriprice', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                "select DISTINCT house_id,house_oriprice,house_cityName,house_type from hotelapp_house " +
                "where house_oriprice>0.00")
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('_price_house_oriprice', temp_df, 3600 * 12)  # 设置缓存

        df_price = pd.cut(temp_df['house_oriprice'],
                          bins=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000]).value_counts()  # 这个用什么你
        df_price = df_price.sort_index()
        from pyecharts import options as opts
        from pyecharts.charts import Bar
        from pyecharts.faker import Faker
        x = [str(x) for x in list(df_price.index)]
        y = [str(y) for y in list(df_price.values)]
        c = (
            Bar()
                .add_xaxis(x)
                .add_yaxis("房源价格水平频数分析", y, category_gap=0, color=Faker.rand_color())
                .set_global_opts(title_opts=opts.TitleOpts(title="房源价格分段"),
                                 xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                                 )
                # .render("bar_histogram_color.html")
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


class diffcity_hostNum(APIView):  # 不同城市中的房东数量
    def get(self, request, *args, **kwargs):
        from pyecharts import options as opts
        from pyecharts.charts import Map
        from pyecharts.faker import Faker

        temp_df = cache.get('diffcity_hostNum', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("diffcity_hostNum,重新查询")

            result = fetchall_sql_dict(
                '''SELECT
                        house_cityName,
                        count( house_cityName ) count_city 
                    FROM
                        (
                        SELECT
                            host_name,
                            house_cityName,
                            count( house_cityName ) total 
                        FROM
                            (
                            SELECT DISTINCT
                                a.house_id,
                                a.house_title,
                                b.host_name,
                                b.host_id,
                                a.house_cityName 
                            FROM
                                hotelapp_house a
                                JOIN hotelapp_house_house_host c ON c.house_id = a.id
                                JOIN hotelapp_host b ON b.id = c.host_id 
                            ) result    
                        GROUP BY
                            host_name,
                            house_cityName -- 	house_id
                            ORDER BY       --   host_name,
                            total DESC 
                        ) result2 
                    GROUP BY
                        house_cityName 
                    ORDER BY
                        count_city DESC''')
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('diffcity_hostNum', temp_df, 3600 * 12)  # 设置缓存
        c = (
            Map()
                .add(
                "各个城市房东的数量",
                [list(z) for z in zip([str(i) for i in temp_df.house_cityName],
                                      [int(i) for i in temp_df.count_city])],
                "china-cities",
                label_opts=opts.LabelOpts(is_show=False),
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(title="抓取的的城市中各城市房东数量"),
                visualmap_opts=opts.VisualMapOpts(),
            )
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


##### 价格分析图表
class _price_bar(APIView):
    # @cache_response(timeout=60 * 60*3, cache='default')
    def get(self, request, *args, **kwargs):
        temp_df = cache.get('_price_house_oriprice', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                "select DISTINCT house_id,house_oriprice,house_cityName,house_type from hotelapp_house " +
                "where house_oriprice>0.00")
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('_price_house_oriprice', temp_df, 3600 * 12)  # 设置缓存
        from pyecharts import options as opts
        from pyecharts.charts import Bar

        temp1 = temp_df[['house_cityName', 'house_oriprice']]
        temp1.house_oriprice = temp1.house_oriprice.astype("float")  # 类型不同
        temp_median = temp1.groupby('house_cityName').median().sort_values(['house_oriprice'], ascending=False)
        x = temp_median.index
        y = temp_median['house_oriprice']

        c = (
            Bar()
                .add_xaxis([str(i) for i in list(x)])
                .add_yaxis("各城市房价中位数/元", [str(j) for j in list(y)], gap="100%"
                           )
                # .add_yaxis("商家B", Faker.values(), gap="0%")
                .set_global_opts(
                title_opts={"text": "含该设施的房源价格均值",
                            "subtext": "价格高说明含有某个设施的房价比较高"}, )
                .set_global_opts(datazoom_opts={'max_': 2,
                                                'orient': "horizontal",
                                                'range_start': 10,
                                                'range_end': 20,
                                                'type_': "inside"})
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


class _price_boxplot(APIView):
    def get(self, request, *args, **kwargs):
        import pyecharts.options as opts
        from pyecharts.charts import Grid, Boxplot, Scatter
        temp_df = cache.get('_price_house_oriprice', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                "select DISTINCT house_id,house_oriprice,house_cityName,house_type from hotelapp_house " +
                "where house_oriprice>0.00")
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('_price_house_oriprice', temp_df, 3600 * 12)  # 设置缓存
        temp_df['house_oriprice'] = temp_df['house_oriprice'].astype("float")  # 价格要变，不然全都是泡沫
        type1 = temp_df[temp_df['house_type'] == "单间"].house_oriprice  # 就是一个模板啊，可以自动进行处理，可视化操作等
        type2 = temp_df[temp_df['house_type'] == "合住"].house_oriprice  # 就是一个模板啊，可以自动进行处理，可视化操作等
        type3 = temp_df[temp_df['house_type'] == "整套"].house_oriprice  # 就是一个模板啊，可以自动进行处理，可视化操作等

        y_data = [  # 多少个图，多少段数据，三种类型
            [x for x in type1.values],
            [x for x in type2.values],
            [x for x in type3.values],
        ]

        # scatter_data = [650, 620, 720, 720, 950, 970]
        from pyecharts import options as opts
        from pyecharts.charts import Boxplot

        v1 = [
            [x for x in type1.values],
            [x for x in type2.values],
            [x for x in type3.values],
        ]
        # v2 = [
        #     [890, 810, 810, 820, 800, 770, 760, 740, 750, 760, 910, 920],
        #     [890, 840, 780, 810, 760, 810, 790, 810, 820, 850, 870, 870],
        # ]

        c = Boxplot()
        b = (
            c.add_xaxis(["单间", "合住", "整套"])
                .add_yaxis("房源", c.prepare_data(v1))
                # .add_yaxis("B", c.prepare_data(v2))
                .set_global_opts(title_opts=opts.TitleOpts(title="三种房型房价箱型图"),
                                 # axis_opts=opts.AxisOpts(
                                 #     type_="value",
                                 #     name="单位/元",
                                 #     splitarea_opts=opts.SplitAreaOpts(
                                 #     is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                                 #     ))
                                 )
                # c.render("boxplot_base.html")

                .dump_options_with_quotes()
        )

        return JsonResponse(json.loads(b))


class _price_heatmap(APIView):  # 经纬度再加上价格这样展示怎么样，这个是啥 todo 这个并没有用到
    def get(self, request, *args, **kwargs):
        import random
        from pyecharts import options as opts
        from pyecharts.charts import HeatMap
        from pyecharts.faker import Faker

        temp_df = cache.get('_price_house_oriprice', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                "select DISTINCT house_id,house_oriprice,house_cityName,house_type from hotelapp_house " +
                "where house_oriprice>0.00")
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('_price_house_oriprice', temp_df, 3600 * 12)  # 设置缓存

        # 这是一个反过来的
        value = [[i, j, random.randint(0, 50)] for i in range(24) for j in range(7)]
        c = (
            HeatMap()
                .add_xaxis(Faker.clock)  # y
                .add_yaxis("相关性", Faker.week, value)  # x  还有值
                .set_global_opts(
                title_opts=opts.TitleOpts(title="其余字段与价格字典的相关性"),
                visualmap_opts=opts.VisualMapOpts(),
            )
                .dump_options_with_quotes()
        )

        return JsonResponse(json.loads(c))


class _facility(APIView):  # 设施饼图
    def get(self, request, *args, **kwargs):
        temp_df = cache.get('_facility_count', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                '''SELECT
                        facility_name,total 
                    FROM
                        ( SELECT facility_id, count( facility_id ) total FROM hotelapp_house_house_facility
                    GROUP BY facility_id ) result
                        LEFT JOIN hotelapp_facility ON result.facility_id = hotelapp_facility.id 
                    ORDER BY
                        total desc''')
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('_facility_count', temp_df, 3600 * 12)  # 设置缓存
        # temp_df.percentage = temp_df.count/
        import pyecharts.options as opts
        from pyecharts.charts import WordCloud
        # data = [(x,y) for x,y in ]
        data = zip([str(i) for i in temp_df.facility_name], [str(i) for i in temp_df.total])
        c = (
            WordCloud()
                .add(series_name="房屋设施分析", data_pair=data, word_size_range=[6, 66])
                .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="房屋设施分析", title_textstyle_opts=opts.TextStyleOpts(font_size=23),
                    subtitle="字体越大设施占比越普遍",
                ),
                tooltip_opts=opts.TooltipOpts(is_show=True),
            )
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


class _facility_price(APIView):  # 设施饼图
    def get(self, request, *args, **kwargs):
        temp_df = cache.get('_facility_price', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                '''select AVG(house_oriprice) avg_price,facility_name from (
select a.house_oriprice,b.facility_id from hotelapp_house a JOIN hotelapp_house_house_facility b ON a.id = b.house_id  ) result JOIN hotelapp_facility c ON result.facility_id = c.id group by  facility_name 
order by avg_price desc''')
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('_facility_price', temp_df, 3600 * 12)  # 设置缓存
        # temp_df.percentage = temp_df.count/
        import pyecharts.options as opts
        # temp_df.house_oriprice = temp_df.house_oriprice.astype("float")  # 类型不同
        # temp = temp_df[['facility_name',"house_oriprice"]]
        # temp_df = temp.groupby(["facility_name"]).mean().sort_values(["house_oriprice"],ascending=False)
        # temp_df .house_oriprice = temp_df.house_oriprice.map(lambda x:int(x))
        temp_df.avg_price = temp_df.avg_price.map(lambda x: int(x))
        print(type(temp_df))
        # print(temp_df)
        # data = [(x,y) for x,y in ]
        # data = zip([str(i) for i in temp_df.facility_name],[float(i) for i in temp_df.house_oriprice])
        from pyecharts.charts import Bar
        from pyecharts.faker import Faker
        from pyecharts.globals import ThemeType
        c = (
            Bar({"theme": ThemeType.MACARONS})
                # .add_xaxis([str(i) for i in temp_df.index])  # 转变/成了index
                .add_xaxis([str(i) for i in temp_df.facility_name])  # 转变成了index

                .add_yaxis("房源设施", [float(i) for i in temp_df.avg_price])
                # .add_yaxis("商家B", Faker.values())
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                title_opts={"text": "含该设施的房源价格均值(单位/元)", "subtext": "价格高说明含有某个设施的房价比较高"},
                datazoom_opts=opts.DataZoomOpts()
            )
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


class _label(APIView):  # 计算最必须的设施,这个漏了  todo
    def get(self, request, *args, **kwargs):
        temp_df = cache.get('_label_result', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                '''select facility_name,count from (SELECT facility_id,
                count(facility_id) count FROM `hotelapp_house_house_facility` group by facility_id )
                 result left join 
                hotelapp_facility on result.facility_id= hotelapp_facility.id order by count desc ''')
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('_label_result', temp_df, 3600 * 12)  # 设置缓存

        return JsonResponse(json.loads(temp_df))


# todo 这个也是 面积的可视化，
# 1.面积中位数
# 2.划分区间，各个区间面积的价格均值
# 3.连续型那就画点图。  ，并且做一条线性拟合的直线。  api 也可以设置访问频率的。

class beiyong(APIView):  # 计算最必须的设施,这个漏了  todo
    def get(self, request, *args, **kwargs):
        temp_df = cache.get('_label_result', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                '''select facility_name,count from (SELECT facility_id,
                count(facility_id) count FROM `hotelapp_house_house_facility` group by facility_id ) result left join 
                hotelapp_facility on result.facility_id= hotelapp_facility.id order by count desc ''')
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('_label_result', temp_df, 3600 * 12)  # 设置缓存
        return JsonResponse(json.loads(temp_df))


class area_bar(APIView):
    def get(self, request, *args, **kwargs):
        temp_df = cache.get('area_result', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                '''select house_area,house_oriprice from hotelapp_house''')
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('area_result', temp_df, 3600 * 12)  # 设置缓存

        df_area = pd.cut(temp_df['house_area'],
                         bins=[0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]
                         ).value_counts()  # 这个用什么你
        df_area = df_area.sort_index()
        from pyecharts import options as opts
        from pyecharts.charts import Bar
        from pyecharts.faker import Faker
        x = [str(x) for x in list(df_area.index)]
        y = [str(y) for y in list(df_area.values)]
        c = (
            Bar()
                .add_xaxis(x)
                .add_yaxis("频数", y, category_gap=0, color=Faker.rand_color())
                .set_global_opts(title_opts=opts.TitleOpts(title="房源面积分布", subtitle="面积单位m²"),
                                 xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                                 )
                # .render("bar_histogram_color.html")
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


class area_price_scatter(APIView):  # 价格和面积的散点图
    def get(self, request, *args, **kwargs):
        temp_df = cache.get('area_price_scatter', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                '''select house_area,house_oriprice,house_cityName from hotelapp_house''')
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('area_price_scatter', temp_df, 3600 * 12)  # 设置缓存
        from pyecharts import options as opts
        from pyecharts.charts import Scatter
        from pyecharts.faker import Faker
        print(temp_df.columns.values.tolist())
        temp_df = temp_df[(temp_df['house_area'] < 200.00) & (temp_df['house_oriprice'] < 1000)]
        # (temp_df['house_cityName'] == "惠州")]  # 200平方米都是不对的了
        temp_df = temp_df.sort_values(by="house_area")
        c = (
            Scatter()
                .add_xaxis([int(x) for x in temp_df['house_area'].values])
                .add_yaxis("价格", [int(x) for x in temp_df['house_oriprice']])
                .set_global_opts(
                title_opts=opts.TitleOpts(title="房价点图"),
                xaxis_opts=opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=True)),
                # yaxis_opts=opts.AxisOpts(splitline_opts=opts.SplitLineOpts(is_show=True)),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),

            )
                .set_global_opts(
                datazoom_opts={'max_': 2, 'orient': "horizontal", 'range_start': 10, 'range_end': 20,
                               'type_': "inside"})

                # .set_global_opts(
                # datazoom_opts={'max_': 2, 'orient': "vertical", 'range_start': 10, 'range_end': 20,
                #                'type_': "inside"})
                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


class area_price_location_scatter(APIView):  # 绘制出了 matplotlibd的图
    def get(self, request, *args, **kwargs):
        temp_df = cache.get('area_price_location_scatter', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                '''select house_title,house_area,house_cityName,house_oriprice,house_type
                 from hotelapp_house''')
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('area_price_location_scatter', temp_df, 3600 * 12)  # 设置缓存
        from pyecharts import options as opts
        from pyecharts.charts import Geo

        temp_df = temp_df[(temp_df['house_area'] < 500.00) & (temp_df['house_oriprice'] < 6000)]  # &
        #                   (temp_df['house_cityName'] == "惠州")]  # 200平方米都是不对的了
        temp_df['house_oriprice'] = temp_df['house_oriprice'].astype("float")
        temp_df['house_area'] = temp_df['house_area'].astype("float")

        from matplotlib import pyplot as plt
        import seaborn as sns

        plt.rcParams['font.sans-serif'] = ['simhei']  # 解决中文显示问题-设置字体为黑体
        plt.rcParams['font.family'] = 'simhei'
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

        # plt.rcParams['font.sans-serif'] = ['SimHei']
        # plt.rcParams['axes.unicode_minus'] = False
        # sns.set(font='SimHei')  # 解决Seaborn中文显示问题
        # sns.set_style({'font.sans-serif': ['simhei']})

        plt.figure(figsize=(15, 10))
        plt.title('面积 - 房价 散点图')
        plt.xlabel('房屋面积/m²')
        plt.ylabel('房屋价格/元')
        sns.set(color_codes=True)

        # ax.set(xlabel="房屋面积/m²")
        # ax.set(ylabel="房屋价格/元")
        # sns.scatterplot(temp_df['house_area'],
        #                 temp_df['house_oriprice'],
        #                 # hue = temp_df['house_cityName'],
        #                 size=temp_df['house_oriprice'].astype(int),
        #                 # fit_reg=False,
        #                 # x_jitter=0.2, y_jitter=0.2, alpha= 1 / 3
        #                 )  # 右图，加上hue参数              #  hue=temp_df['e']
        # plt.plot(randn(50).cumsum(), 'k--')
        # model = linear_model.LinearRegression()
        # model.fit(temp_df['house_area'], temp_df['house_oriprice'])
        # y2 = model.predict(temp_df['house_area'])
        # plt.plot(temp_df['house_area'], y2, 'g-')
        plt.figure(figsize=(15, 10))
        plt.subplots_adjust(hspace=0.8)

        sns.set(font='simhei', font_scale=1.5)

        ax = sns.lmplot(x="house_area", y="house_oriprice",
                        hue="house_type",
                        col="house_type",
                        sharex=True,
                        col_wrap=1,
                        x_jitter=True,
                        y_jitter=True,
                        # col="house_type",

                        # size=3,
                        data=temp_df, aspect=3, height=4, ci=0.90,
                        palette="husl",
                        scatter_kws={'alpha': 0.20}
                        # markers=["o", "x",''],
                        # palette="Set1"
                        )

        # ax = sns.regplot(data=temp_df,
        #                  # hue = "house_type",
        #                  x='house_area',
        #                  y='house_oriprice',
        #                  fit_reg=True,
        #          x_jitter=0.2, y_jitter=0.2, scatter_kws={'alpha': 1 / 5})
        ax.set(xlabel='房屋面积/平方', ylabel='房屋价格/元')
        # ax.set_titles("不同类型房源面积和房价的线性回归关系")
        plt.legend(loc='center right', bbox_to_anchor=(1, 0.1), ncol=1)

        # 这部分是图片转化为base64 还能这样用厉害了
        buffer = BytesIO()  # 这个是从io中来导入这个东西
        plt.savefig(buffer)
        plot_data = buffer.getvalue()
        imb = base64.b64encode(plot_data)  # 对plot_data进行编码
        ims = imb.decode()
        imd = "data:image/png;base64," + ims
        context = {
            'img': imd,
        }
        # return render(request,'test.html',context)
        return JsonResponse({"data": imd})


# 房屋的主要内容分析
class house_content(APIView):
    def get(self, request, *args, **kwargs):
        temp_df = cache.get('house_content', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict('''
            SELECT distinct house_id, house_type, house_oriprice, house_capacity, 
                                house_area,house_kitchen, house_living_room,
                                 house_bedroom, house_toilet FROM
                hotelapp_house''')
            # 都使用df来进行处理和显示
            temp_df = pd.DataFrame(result)
            cache.set('house_content', temp_df, 3600 * 12)  # 12小时
        print(len(temp_df))
        from pyecharts import options as opts
        from pyecharts.charts import Grid, Liquid
        from pyecharts.commons.utils import JsCode

        temp_toilet = round(len(temp_df[temp_df['house_toilet'] > 0]) / len(temp_df), 2)
        temp_living = round(len(temp_df[temp_df['house_living_room'] > 0]) / len(temp_df), 2)
        temp_kitchen = round(len(temp_df[temp_df['house_kitchen'] > 0]) / len(temp_df), 2)

        l1 = (
            Liquid().add("房源厨房占比",
                         [temp_kitchen],
                         center=["20%", "30%"],
                         # shape="roundRect",
                         label_opts=opts.LabelOpts(
                             font_size=20,
                             formatter="房源厨房占比:{c}",
                             position="inside",
                         ), is_outline_show=False,
                         )
            # .set_global_opts(title_opts=opts.TitleOpts(title="多个 Liquid 显示"))
        )

        l2 = Liquid().add(
            "房源客厅占比",
            [temp_living],  # 在这个是 的
            center=["50%", "30%"],
            label_opts=opts.LabelOpts(
                font_size=20,
                formatter="房源客厅占比:{c}",
                position="inside",
            ),
            is_outline_show=False,
        )

        l3 = Liquid().add(
            "房源厕所占比",
            [temp_toilet],  # 在这个是 的
            center=["80%", "30%"],
            label_opts=opts.LabelOpts(
                font_size=20,
                formatter="房源厕所占比:{c}",
                position="inside",
            ),
            is_outline_show=False,
        )

        c = (
            Grid()
                .add(l1, grid_opts=opts.GridOpts())
                .add(l2, grid_opts=opts.GridOpts())
                .add(l3, grid_opts=opts.GridOpts())

                .dump_options_with_quotes()
        )
        return JsonResponse(json.loads(c))


# 生成线性预测模型
def make_linear_model(cityName, house_type, predict_point, df):
    if type(predict_point) == "str":
        predict_point = float(predict_point)
    from sklearn.linear_model import LinearRegression  # 导入线性模型sklearn
    df_city = df[(df['house_cityName'] == cityName) & (df['house_type'] == house_type)]
    temp_data = df_city[['house_area', 'house_oriprice']]
    temp_data = temp_data[(temp_data['house_area'] > 0) & (temp_data['house_oriprice'] > 0)]

    # 保留80%的中间房价的数据，去掉两头的离群太远的点   这个先不管，清洗的东西
    # a, b = temp_data.house_oriprice.quantile([0.1, 0.9])
    # temp_data = temp_data[(temp_data['house_oriprice'] >= a) & (temp_data['house_oriprice'] <= b)]

    # temp_data.info()
    # 选择指定的城市
    if len(temp_data) == 0:
        return None
    temp_data['house_area'] = temp_data['house_area'].astype(float).copy()

    # 划分训练集
    train_X, test_X, train_y, test_y = train_test_split(temp_data['house_area'].values,
                                                        temp_data['house_oriprice'].values,
                                                        test_size=0.2,
                                                        random_state=0)  # 种子
    print(u'划分行数:', "[总数据量]", len(temp_data), "   [训练集]", len(train_X), "   [测试集]", len(test_X))
    temp_massage = f"[总数据量]:{len(temp_data)}   [训练集]:{len(train_X)}   [测试集]:{len(test_X)}"

    # 训练模型
    clf = LinearRegression()
    clf.fit(train_X.reshape(-1, 1), train_y)  # 注: 训练数据)
    print("得到的回归方程的参数")
    #     print(clf.coef_ )  # 得到[\beta _{1},\beta _{2},...\beta _{k}]    ax+b
    #     print(clf.intercept_  )# \beta _{0}，截距，默认有截距
    temp_y = ""
    if clf.intercept_ < 0:
        print(f"{round(clf.coef_[0], 4)}*x{round(clf.intercept_, 4)}")
        temp_y = f"{round(clf.coef_[0], 4)}*x{round(clf.intercept_, 4)}"
    else:
        print(f"{round(clf.coef_[0], 4)}*x+{round(clf.intercept_, 4)}")
        temp_y = f"{round(clf.coef_[0], 4)}*x+{round(clf.intercept_, 4)}"

    plt.figure(figsize=(15, 10))
    plt.xlim(10, 200)
    plt.ylim(10, 1000)
    plt.rcParams['font.sans-serif'] = ['simhei']  # 解决中文显示问题-设置字体为黑体
    plt.rcParams['font.family'] = 'simhei'
    plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
    alpha_num = 0.2
    if len(temp_data) < 100:
        alpha_num = 0.8
    plt.scatter(train_X, train_y, color="blue", alpha=alpha_num, label="训练集")  # , marker='^
    plt.scatter(test_X, test_y, color="green", alpha=alpha_num, label="测试集")  # , marker='^
    predict_y = clf.predict([[predict_point]])
    predict_y = round(float(predict_y[0]), 2)  # 保留了两位小数
    #     print(f"预测结果{predict_y}")
    plt.text(predict_point, predict_y, (predict_point, predict_y), color='r', fontsize=20, fontweight="heavy")  # 标记出来
    plt.scatter(predict_point, predict_y, marker="x", s=200, color="red",
                label=f"预测点\n({predict_point},{predict_y})")  # , marker='^
    plt.plot(train_X, clf.predict(train_X.reshape(-1, 1)), label=f"训练的回归直线\n{temp_y}")

    #     plt.scatter(predict_y, predict_y[0], color="red",label="预测点" ) # , marker='^

    plt.legend(loc="upper right", prop={'size': 20})
    plt.xlabel("房源面积", fontsize=20)
    plt.ylabel("房源价格", fontsize=20)
    plt.title(f"{cityName}-{house_type}-房源面积-价格 线性回归预测", fontsize=20)
    #     plt.savefig('graph.svg')

    # 增加得到图片的功能
    buffer = BytesIO()  # 这个是从io中来导入这个东西
    plt.savefig(buffer)
    plot_data = buffer.getvalue()
    imb = base64.b64encode(plot_data)  # 对plot_data进行编码
    ims = imb.decode()
    imd = "data:image/png;base64," + ims  # 这个很重要不然显示不了

    print("测试得分")
    print(clf.score(test_X.reshape(-1, 1), test_y))  # 测试的结果R2的预测值是这么多，所以还是比较可信的
    temp_Score = clf.score(test_X.reshape(-1, 1), test_y)
    return clf, temp_massage, temp_y, temp_Score, imd, predict_y, temp_massage  # 模型，条件消息，训练得到的参数，训练R方结果，输出的图片,面积预测的结果


# type(make_linear_model("深圳", "单间", 40))

from rest_framework.authentication import SessionAuthentication, BasicAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class predictPrice(APIView):  # 绘制出了 matplotlibd的图
    # @method_decorator(csrf_exempt)  # 给类里面的方法加装饰器  需要导入一个方法method_decorator
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        house_cityName = request.data.get('cName')
        house_type = request.data.get('htype')
        house_area = request.data.get('harea')
        if house_type == None or house_area == "":
            return JsonError({"info": "请携带正确的参数后进行预测"})

        # house_cityName = request.GET.get("cName")  # 提取出house_id
        # house_type = request.GET.get("htype")  # 提取出house_id  只有三种类型，或者根据
        # house_area = request.GET.get("harea")  # 提取出house_id
        print("house_area")
        print(house_area)
        if house_cityName == None or house_type == None or house_area == None:
            return JsonError({"info": "请携带正确的参数后进行预测"})
        house_area = float(house_area)  # 转为float

        temp_df = cache.get('predict_area_price', None)  # 使用缓存，可以共享真好。
        if temp_df is None:  # 如果无，则向数据库查询数据
            print("host,重新查询")
            result = fetchall_sql_dict(
                '''select distinct house_id,house_area,house_oriprice,house_cityName,house_type from 
                hotelapp_house where house_oriprice>0 and house_area>0''')
            # 都使用df来进行处理和显示
            # temp_df.index = pd.to_datetime(temp_df.house_firstOnSale)
            temp_df = pd.DataFrame(result)
            cache.set('predict_area_price', temp_df, 3600 * 12)  # 设置缓存

        # temp_df = temp_df[(temp_df['house_area'] < 500.00) & (temp_df['house_oriprice'] < 6000)]  # &
        temp_df['house_oriprice'] = temp_df['house_oriprice'].astype("float")
        temp_df['house_area'] = temp_df['house_area'].astype("float")
        # print(type(temp_df['house_oriprice']))
        # print(type(temp_df['house_area']))
        print(temp_df.info())
        from matplotlib import pyplot as plt
        import seaborn as sns

        plt.rcParams['font.sans-serif'] = ['simhei']  # 解决中文显示问题-设置字体为黑体
        plt.rcParams['font.family'] = 'simhei'
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

        model_result = make_linear_model(house_type=house_type,
                                         cityName=house_cityName,
                                         predict_point=house_area,
                                         df=temp_df)
        if model_result == None:
            return JsonError({"info": f"{house_cityName}没“{house_type}”的数据，请选择其他房源“类型”"})

        # ax.set_titles("不同类型房源面积和房价的线性回归关系")
        # plt.legend(loc='center right', bbox_to_anchor=(1, 01), ncol=1)
        # 模型，条件消息，训练得到的参数表达式，训练R方结果，输出的图片,面积预测的结果
        model, message, y_function, R2, imd, predict_result, temp_massage = model_result
        context = {
            'img': imd,
            # 'message':message,
            'y_function': y_function,
            'R2': R2,
            'predict_result': predict_result,  # 训练的结果
            'temp_massage': temp_massage,
        }
        return JsonResponse(context)

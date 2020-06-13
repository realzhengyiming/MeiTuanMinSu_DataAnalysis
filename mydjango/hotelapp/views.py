import datetime
import uuid
from typing import List

import jieba as jieba
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db import connection
# from pyecharts.globals import ThemeType
import pandas as pd
from django.urls import reverse
from django.views.decorators.http import require_http_methods
# from django_redis import cache
from django.core.cache import cache  #导入缓存对象,redis存储

from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType, ChartType
from rest_framework.response import Response
# from requests import Response
from .forms import LoginForm, RegistrationForm
from .Serializer import FavouriteSerializer
from .Serializer import userSerializer
from .Serializer import citySerializer
from .models import House
from .models import City
from .models import Favourite
import time
from django.db.models import Avg, Max, Min, Count, Sum  # 直接使用models中的统计类来进行统计查询操作
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger  # 用来分页饿
import json
from random import randrange
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.views import APIView
from pyecharts.charts import Bar, Pie, Line, Geo, BMap, Grid
from pyecharts import options as opts


@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def detailView(request):  # 详情页
    house_id = request.GET.get("house_id")
    houseList = House.objects.filter(Q(house_id=house_id)).order_by("-house_date")
    labels = houseList[0].house_labels.all()
    # print(labels)
    facility = houseList[0].house_facility.all()
    return render(request,"hotelapp/index_chartspage_detail.html",
                  context={"house":houseList,
                           "house_id":house_id,
                           "labels":labels,
                           "facility":facility,
                           "app_name":"房源详情"
                           })


def testindex(request):  # 测试页
    # todo 提取不重复的日期的东西，然后进行年月日绘制图片进行查看可视化，同比环比，这个也是可以的
    result = fetchall_sql_dict("SELECT distinct(id),house_firstOnSale FROM `hotelapp_house` ")
    # print(result)
    # 然后转换成pandas进行一系列的筛选等
    from django_pandas.io import read_frame
    # qs_dataframe = read_frame(qs=result)
    # print(qs_dataframe)

    import pandas as pd
    from pandas import DataFrame

    df = pd.DataFrame(result)
    # print(df)
    # 按月份
    df.index = pd.to_datetime(df.house_firstOnSale)
    # type(df.id.resample("1M").count())  # huode 按月份来
    # print(df.id.resample("M").count().to_period("M"))

    return render(request,'hotelapp/test.html',context={"article":result})


@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def detaillist(request):  # 数据列表页分页
    # userObj = models.Asset.objects.filter(~Q(asset_id='')
    username = request.user.username
    # 提取收藏夹
    tempUser = User.objects.filter(username=username).first()
    # print(tempUser)
    # print(type(tempUser))
    fav = tempUser.favourite.fav_houses.all()
    # 提取出价格，面积，城市，并且高分的


    if len(fav)==0:
        house_list = House.objects.filter(~Q(house_oriprice=0.00)).order_by("-house_date").order_by("-id")
    else:
        temp_city = []
        temp_area = []
        temp_price = []
        for house in fav:
            # print(house)
            temp_city.append(house.house_cityName)
            temp_area.append(house.house_area)
            temp_price.append(house.house_oriprice)

        import pandas as pd
        # print(temp_city)
        # print(temp_area)
        # print(temp_price)
        # print(pd.DataFrame(temp_city))
        import random
        ran_li = random.sample(temp_city, 1)
        # print("temo")
        # print(ran_li)
        medianprice = int(pd.DataFrame(temp_price)[0].median())
        # print(medianprice)  # Q(house_oriprice_lt=medianprice)
        # 根据标签总数，来对比，
        house_list = House.objects.filter(Q(house_cityName=ran_li[0])).order_by("-house_favcount").order_by("-id")

    # print(fav)
    # tempfav = Favourite.objects.filter(User=request.user).first()
    # print(tempfav)




    house_listMain = House.objects.filter(~Q(house_oriprice=0.00)).order_by("-house_date").order_by("-id")
    # house_list = house_list+house_listMain
    a = []

    a.extend(house_list)

    a.extend(house_listMain)

    paginator = Paginator(a,20)  # 2个一页的意思
    page = request.GET.get("page")
    try:
        current_page = paginator.page(page)
        articles = current_page.object_list
    except PageNotAnInteger:
        current_page = paginator.page(1)
        articles = current_page.object_list
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
        articles = current_page.object_list
    return render(request, "hotelapp/index_chartspage_detaillist.html",
                  context={"app_name":"详细数据","articles":articles,"page":current_page})
    # 这两个是必须要带上的属性


def fetchall_sql(sql)->tuple:  # 这儿唯一有一个就是显示页面的
    # latest_question_list = KeyWordItem # 换成直接使用sql来进行工作
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchall()
        # columns = [col[0] for col in cursor.description]  # 提取出column_name
        # return [dict(zip(columns, row)) for row in cursor.fetchall()][0]
        return row

def fetchall_sql_dict(sql)-> [dict]:  # 这儿唯一有一个就是显示页面的
    # latest_question_list = KeyWordItem # 换成直接使用sql来进行工作
    print("check sql")
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        # row = cursor.fetchall()
        columns = [col[0] for col in cursor.description]  # 提取出column_name
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def index(request):  # 这儿唯一有一个就是显示页面的
    success_info = None
    if request.GET.get("success_info"):
        success_info = request.GET.get("success_info")
        print(success_info)

    nowdate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    count_today = House.objects.filter(house_date=nowdate).aggregate(count = Count("house_id"))
    count_today_city = House.objects.filter(house_date=nowdate).aggregate(count =Count("house_cityName",distinct=True))
    count_total_city = House.objects.aggregate(count =Count("house_cityName",distinct=True))
    context = {
        'app_name': "💒美团酒店民宿数据",
        # 'latest_question_list': result,
        'count_today':count_today,
        'count_today_city':count_today_city,   # 今天总共爬了多少个城市
        'count_total_city':count_total_city,
        'success_info':success_info
    }
    return render(request, 'hotelapp/index_chartspage.html', context)


# 增加一个使用修改密码
def password_change(request):
    pass
    #  if request.method == "POST":
    #     login_form = LoginForm(request.POST)  # 这个
    #     if login_form.is_valid():
    #         cd = login_form.cleaned_data  # 转化成字段来方便提取
    #         user = authenticate(username=cd['username'],password=cd['password'])
    #         if user:
    #             login(request, user)
    #             # return HttpResponse("Wellcome!")
    #             return redirect('/hotelapp')
    #         else:
    #             return render(request, 'hotelapp/loginPage.html', context={'form':login_form,"error":"账号或者密码错误！"})

def loginPage(request): # 登陆界面的,这个是自定义的
    if request.method == "GET":
        success_info = None
        if request.session.get("success_info"):
            success_info = request.session.get("success_info")
            print("正在输出")
            print(request.session.get("success_info"))
            del request.session['success_info']  # 用完就删掉
            print("删除后")
            print(request.session.get("success_info"))
        login_form = LoginForm()
        return render(request, 'hotelapp/loginPage.html', context={'form':login_form,'success_info':success_info})
    if request.method == "POST":
        login_form = LoginForm(request.POST)  # 这个
        if login_form.is_valid():
            cd = login_form.cleaned_data  # 转化成字段来方便提取
            user = authenticate(username=cd['username'],password=cd['password'])
            if user:
                login(request, user)
                # return HttpResponse("Wellcome!")
                return redirect('/hotelapp')
            else:
                return render(request, 'hotelapp/loginPage.html', context={'form':login_form,"error":"账号或者密码错误！"})
        else:
            error = "请检查输入的账号和密码是否正确"
            login_form = LoginForm()
            return render(request, 'hotelapp/loginPage.html', context={'form':login_form,"error":error})


def register(request): # 注册用户User
    if request.method == "POST":
        user_form = RegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data["password"])
            # new_user.
            new_user.save()
            # 这儿放登陆注册的
            # loginForm = LoginForm()
            request.session['success_info'] = 'register_success'
            return redirect('/hotelapp/loginpage/')
        else:
            return render(request,"hotelapp/register.html", {"form":user_form,
                                                             "error_message":"提交的账号密码不合法"})  # 这个是get的方式进来
    else:
        user_form = RegistrationForm()
        return render(request,"hotelapp/register.html", {"form":user_form})  # 这个是get的方式进来

def userLogout(request):  # 登出
    logout(request)
    return redirect("/hotelapp/loginpage/")

@login_required(login_url='/hotelapp/loginpage/')  # 爬虫数据页
def facilityPage(request):
    context = {
        'app_name':"房源设施分析"
        # result
    }
    return render(request, 'hotelapp/index_chartspage_facility.html', context)

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

class loginView(APIView):  # 使用不同的试图来进行封装
    def get(self,request,*args,**kwargs):
        # return Response("fuck")
        password = self.request.query_params.get("password")
        username = self.request.query_params.get("account")
        password = "1234567890zzz"
        username = "robotor"
        user = User.objects.filter(username=username).first()
        print(user)
        # return JsonResponse({"result":userSerializer.data})  # 这样就只是单纯的js就可以做到
        return Response(userSerializer.data)

    def post(self,request,*args,**kwargs):
        password = self.request.query_params.get("password")
        username = self.request.query_params.get("account")
        print("port")
        print(password)
        print(username)
        user = User.objects.filter(username=username,password=password).first()

        return JsonResponse({"result":user.data})

@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def hostPage(request):
    return render(request,'hotelapp/index_chartspage_host.html',context={"app_name":"房东专区"})

@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def consumerPage(request):
    return render(request,'hotelapp/index_chartspage_consumer.html',context={"app_name":"房客专区"})

# 详细的页面
@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def timePage(request):
    return render(request,'hotelapp/index_chartspage_time.html',context={"app_name":"房源发布时间分析"})

# 详细的页面
@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def pricePage(request):
    return render(request,'hotelapp/index_chartspage_price.html',context={"app_name":"房源价格分析"})

# 详细的页面
@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def favcountPage(request):
    return render(request,'hotelapp/index_chartspage_price.html',context={"app_name":"热门房源分析"})

# 搜索的页面
@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def searchPage(request):
    return render(request,'hotelapp/index_chartspage_search.html',context={"app_name":"查找房源"})


# 房源面积的页面
@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def assessPage(request):
    return render(request,'hotelapp/index_chartspage_assess.html',context={"app_name":"房源价格评估"})


# 房源面积的页面
@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def area(request):
    return render(request,'hotelapp/index_chartspage_area.html',context={"app_name":"房源面积分析"})

# 房源面积的页面
@login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def predictPage(request):
    return render(request,'hotelapp/index_chartspage_predict.html',context={"app_name":"房源价格预估"})



# 详细的页面
# @login_required(login_url='/hotelapp/loginpage/')  # 默认主页
def trainPage(request):
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error, r2_score
    return render(request,'hotelapp/test.html',context={"app_name":"test"})


def genFavtag(favourite):  # 输入一个fav对象，生成一个house tag
    i = favourite
    # content = "content"
    tag = f'''<tr id='tr-{i.house_id}'>
            <td>{i.house_id}</td>
            <td>{i.house_cityName}</td>
            <td>{i.house_discountprice}</td>
            <td><a target="_blank" href="/hotelapp/detail/?house_id={i.house_id}">{i.house_title}</a></td>
              <td>
                  <button  onclick="delete_btn({i.house_id})"
                        id="{i.house_id}"  name="del_button"
                          class="mdui-color-theme-accent mdui-btn mdui-btn-icon mdui-ripple mdui-ripple-white">
                  <i class="mdui-icon material-icons">delete_forever</i></button></td>
          </tr>'''
    return tag

# 加入收藏和删除收藏的功能
class favouriteHandler(APIView):  # 使用不同的试图来进行封装
    def get(self,request,*args,**kwargs):
        # print("get 进来了")
        method = self.request.query_params.get('method', None)
        if method is not None:
            username = self.request.query_params.get("username", 0)
            house_id = self.request.query_params.get("del_house_id", 0)
            if method == "add":
                if username != 0 and house_id != 0:
                    import traceback
                    user = User.objects.filter(username=username).first()  #
                    house = House.objects.filter(house_id=house_id).first()  # 找到这个房子
                    # print(user)
                    # print(house)
                    if user is not None and house is not None:
                        try:
                            f1 = Favourite.objects.get(user=user)   # 找到一个收藏夹对象
                            # 这儿可能重复
                            # print(f1.fav_houses.all())
                            for i in list(f1.fav_houses.all()):
                                # print("输出里面的{}".format(i))
                                if str(i.house_id)==house_id:
                                    # print("已经有了")
                                    return json_response({"result": "已在收藏夹 √   😀", 'tag': ""})
                            f1.fav_houses.add(house)
                            f1.save()  # 增加收藏
                            # print("添加成功")
                            return json_response({"result": "加入收藏 √   👌",'tag':genFavtag(house)})
                        except Favourite.DoesNotExist:  # 创建
                            # 没有收藏时候
                            print(traceback.print_exc())
                            city = City.objects.filter(city_nm="广州").first()  # 默认广州
                            try:
                                f1 = Favourite.objects.create(fav_city=city,user=user)
                                f1.fav_houses.add(house)
                                f1.save()
                                # print("加入收藏成功")
                                return json_response({"result": "加入收藏 √   👌", 'tag': genFavtag(house)})
                            except Exception as e:
                                print(e)
                                print(traceback.print_exc())
                                print("请检查")
                        except Exception as e:
                            # print("出现问题")
                            print(e)
                return json_response({"result":"出现问题",'tag':""})
            if method == "del":
                user = User.objects.filter(username=username).first()  #
                house = House.objects.filter(house_id=house_id).first()  # 找到这个房子
                if user is not None and house is not None:
                    try:
                        f1 = Favourite.objects.get(user=user)  # 找到一个收藏夹对象
                        f1.fav_houses.remove(house)
                        f1.save()  # 增加收藏
                        # print("删除成功")
                        return json_response({"result": "删除成功 √  👌"})
                    except Favourite.DoesNotExist:  # 创建
                        print("没有收藏夹")
                else:
                    return json_response({"result": "未找到此房子！！！"})
        else:
            return json_response({"result": "未找到参数"})
            # return "None"

    def post(self,request,*args,**kwargs):
        return json_response({"result": "请通过get"})


# 写个接口，返回监控的房子id,理论上是所有id与单个用户无关
class get_fav_house_by_id(APIView):   # 这儿是给爬虫用的。爬虫调用这边，使用这种通讯
    def get(self, request, *args, **kwargs):
        # print("get 进来了")
        userid = self.request.query_params.get('api', None)
        if userid is not None and userid == "asdsewrzt!dfe":
            result = fetchall_sql(f'''SELECT b.house_id FROM `hotelapp_favourite_fav_houses` a left join 
												hotelapp_house b on a.house_id= b.id''')  # 这个时候传进来
            return json_response({"result": result})
        else:
            return json_response({"result": ""})  # 失败的话
            # return "None"
    # def post(self, request, *args, **kwargs):
    #     return json_response({"result": "请通过get"})

# 如何取号标题
class getHotTitle(APIView):  #  突然觉得这个功能没有必要
    def get(self,request,*args,**kwargs):
        result = ""  # 前1000个最受欢迎的放原标题的分析，更好的设计自己的标题
        result = fetchall_sql_dict("select DISTINCT house_id,house_title,house_favcount from hotelapp_house ORDER BY "+
                                   "house_favcount desc limit 1000")
        alltitle = ""  # 如何取好标题
        for i in result:
            # for title in i['house_title']:
            print(i['house_title'])
            alltitle += i['house_title']
        import jieba.analyse
        jieba.analyse.set_stop_words('hotelapp/stopword1.txt')
        # 词语数组
        wordList = []
        # 用于统计词频
        wordCount = {}

        # 从分词后的源文件中读取数据
        # sourceData = readFile(sourceFile)
        # 利用空格分割成数组
        # wordList = sourceData.split(' ')
        wordList = jieba.lcut(alltitle)

        # 遍历数组进行词频统计，这里使用wordCount 对象，出发点是对象下标方便查询
        for item in wordList:
            if item not in wordCount:
                wordCount[item] = 1
            else:
                wordCount[item] += 1
        # 循环结束，wordCount 对象将保存所有的词语和词频
        # method = self.request.query_params.get('method', None)
        dic1SortList = sorted(wordCount.items(), key=lambda x: x[1], reverse=True)

        return JsonResponse({"data":dic1SortList})


# 如何取号标题
from django.views.decorators.csrf import csrf_exempt

# 这个组件是组装搜索结果的
def maketable(result):
    head = '''
    <table class="mdui-table">
    <thead>
      <tr>
          <th>价格(￥)</th>
        <th>房源名</th>
        <th>地理位置</th>

        <th>喜欢数</th>
          <th>预览</th>
      </tr>
    </thead>
    <tbody>
    '''
    temp = ""
    for object in result:
        temp+=f'''
     <tr>
         <td>{ object['house_discountprice'] }</td>
        <td ><a href="/hotelapp/detail/?house_id={ object['house_id'] }" target="_blank" >{ object['house_title'] }</a></td>
        <th>{ object['house_location_text'] }</th>

        <td>{object['house_favcount'] }</td>
        <td style="width:300px;height:auto;"><img class="mdui-img-fluid" src="{ object['house_img'] }"  /></td>
     </tr>
    '''
    tail  = '''</tbody></table>'''
    return head+temp+tail


@csrf_exempt  # 这个跳过csrf验证
@require_http_methods(["POST"])
def getSearch(request):  #  突然觉得这个功能没有必要
    if request.method == "POST":
        # keyword =  request.GET.get('keyword')  # 前端判断呗
        keyword = request.POST.get('keyword')
        money_range = request.POST.get('money_range')

        print("提取到keyword")
        print(keyword)
        print(money_range)

        # 找找有没有地理位置，有就抠出来

        if keyword==None:
            return JsonResponse({"data":"请输出关键词"})
        result = ""  # 前1000个最受欢迎的放原标题的分析，更好的设计自己的标题
        result = fetchall_sql_dict(f'''
                    select house_url,house_title,house_favcount,house_discountprice,house_img,house_cityName,
                    house_location_text,house_id FROM
										( SELECT house_url,house_title,house_favcount,house_discountprice,house_img,
                    house_location_text,house_id,house_cityName FROM `hotelapp_house` 
                    where house_discountprice<={float(money_range)} ) result 
										where house_title like "%{keyword}%" or  house_cityName like "%{keyword}%"
										or house_location_text like "%{keyword}%" ORDER BY house_discountprice desc,house_favcount desc''')
        # print(result)
        # 后端组装好table后再传给前端，直接添加就可以
        # print(maketable(result))
        # print(result)
        if len(result)==0:
            return JsonResponse({"table":"<h3 class='mdui-text-center'>未找到相关房源，请重新输入😂</h3>"})
        return JsonResponse({'table':maketable(result)})





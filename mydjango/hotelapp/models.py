import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.safestring import mark_safe
from django.utils import timezone
import django
from django.contrib.auth.models import User, Group
from rest_framework import serializers


class City(models.Model):
    city_nm = models.CharField(max_length=50,unique=True)   # 城市名字
    city_pynm = models.CharField(max_length=50,unique=True)  # 减少冗余的代价是时间代价
    city_statas = models.BooleanField(default=False)
    # 这个是让爬虫选择是否进行爬取的城市（缩小爬取范围才可以全部爬下来）

    def __str__(self):
        return self.city_nm + "  " + self.city_pynm
 

class Labels(models.Model):
    TYPE_CHOICE = (
        (0, "普通标签"),
        (1, "优惠标签"),
        )
    label_type = models.IntegerField(choices=TYPE_CHOICE)  # 类型1为营销， 0 为默认标签
    label_name = models.CharField(max_length=191,unique=True) 
    label_desc = models.CharField(max_length=191,unique=True)  # 减少冗余的代价是时间代价

    def __str__(self):
        return str(self.label_type)+"  "+self.label_name+"  "+self.label_desc

    class Meta:
        # 联合约束 独立性约束
        unique_together = ('label_name',"label_desc")


class Host(models.Model):
    '''自己会自动创建一个id的'''
    host_name = models.CharField(max_length=191)  # 房东名字
    host_id = models.IntegerField()  # 房东id
    host_replayRate = models.IntegerField(default=0)  # 回复率
    host_commentNum = models.IntegerField(default=0)  # 评价总数 ,会变也要存，这样可以看变化率
    host_RoomNum = models.IntegerField(default=0)  # 不同时间段的房子含有数量
    host_updateDate = models.DateField(default=timezone.now)  # 自动创建时间，不可修改

    def __str__(self):
        return str(self.host_id)+ " "+self.host_name

    class Meta:
            # 各一个房子一天最多一天数据（一个价格）
        unique_together = ('host_id',"host_updateDate") 

class Facility(models.Model):  
    ''' 设施类型 85个设施 
        todo django如何设置不用外键约束，这样可以更高效，暂时还是使用外键约束的。
    '''
    facility_name = models.CharField(max_length=50,unique=True)   # 设施名字

    def __str__(self):
        return self.facility_name


# 这个是用来酒店公寓的model类
class House(models.Model):
    '''
    house_id 为主键，然后unique_together(house_id,date) 为联合 唯一约束，一天只能插入一次这种
    然后这儿每天的房子都不一定一样，那么要设置好一个爬取的时间，每天凌晨的12点。
    '''

    house_img = models.CharField(max_length=191,default="static/media/default.jpg")  # 这个是预览图，默认就是谁

    house_id =  models.IntegerField(default=0)   # 用来标识唯一房子的，可以
    house_cityName = models.CharField(max_length=50,default="未知城市")
    house_title = models.CharField(max_length=191)   # 我确实想存YMR
    house_url = models.CharField(max_length=191) # 这个好像是最长的了？不知道会不会被截断啊
    house_date = models.DateField(default=timezone.now)   # 爬取时间
    house_firstOnSale = models.DateTimeField(default=datetime.datetime(1970, 1, 1, 1, 1, 1, 499454)) # 发布时间
    # 用户评价 
    house_favcount = models.IntegerField(default=0)  # 房子页面的点赞数
    house_commentNum = models.IntegerField(default=0)  # 评分人数（也是评论人数）
    
    house_descScore = models.FloatField(default=0)  # 房子四个分数
    house_talkScore = models.FloatField(default=0)
    house_hygieneScore = models.FloatField(default=0)
    house_positionScore = models.FloatField(default=0)
    house_avarageScore = models.FloatField(default=0)  # 总的平均分5.0满分,0分当成未评价

    # 房子的具体内容信息
    house_type = models.CharField(max_length=50,default="未分类")  # 整套/单间/合住
    house_area = models.IntegerField(default=0)   # 房子的面积单位m²
    house_kitchen = models.IntegerField(default=0)  # 厨房数量0就是没
    house_living_room =  models.IntegerField(default=0)  # 客厅数量、
    house_toilet = models.IntegerField(default=0)  # 卫生间数量
    house_bedroom = models.IntegerField(default=0)  # 卧室数量
    house_capacity = models.IntegerField()  # 可以容纳的人数
    house_bed = models.IntegerField(default=1)  # 床的数量

    # 房子的价格信息
    house_oriprice = models.DecimalField(max_digits=16,decimal_places=2)  # 刚发布价格
    house_discountprice = models.DecimalField(max_digits=16,decimal_places=2,default=0.00)
    # 现在价格,这个可能搞不定，如果这个discountPrice没有的话，那就等于现价

    # 房源位置
    house_location_text = models.CharField(max_length=191) # 因为使用utf8mb4格式，char最长为191，四个字节为一个字符
    house_location_lat = models.DecimalField(max_digits=16,decimal_places=6) # 纬度，小数点后6位
    house_location_lng = models.DecimalField(max_digits=16,decimal_places=6) # 经度

    #房源设施
    house_facility = models.ManyToManyField(Facility)  # 一堆多外键，但是这样好像增加保存的难度了，不过可以一次性的进行显示等。

    #房东信息
    house_host = models.ManyToManyField(Host)  # 多对多

    #普通标签和优惠标签
    house_labels = models.ManyToManyField(Labels)

    earliestCheckinTime = models.TimeField(default="00:00")  # 这个时间有没有

    def __str__(self):
        return str(self.house_id)+":" +f"{str(self.house_cityName)}" + ":"+ f"{str(self.house_title[0:15])}..." + ":"+str(self.house_oriprice) + "￥/晚"

    class Meta:
            # 联合约束 独立性约束
        unique_together = ('house_id',"house_date")  # 各一个房子一天最多一天数据（一个价格）

        # 联合索引,优化的东西先不搞，索引先不建立
        # index_together = ["user", "good"]

# class TestUser(models.Model):
#     account = models.IntegerField(default=0)
#     password = models.CharField(max_length=191)


class Favourite(models.Model):  # 收藏夹
    user =  models.OneToOneField(User,unique=True,on_delete=models.CASCADE)
#     # fav_house = models.CharField(max_length=50,unique=True)   # 城市名字

    fav_city = models.ForeignKey(City, on_delete=models.CASCADE)  # 偏好城市,前端处理 ,默认都是广州
    fav_houses = models.ManyToManyField(House)

    def __str__(self):
        return str(self.user.username) + ":" + str(self.fav_city)


from django.contrib import admin
from hotelapp.models import Labels
from hotelapp.models import House, Host, Facility, City
from hotelapp.models import Favourite
from django.contrib.auth.models import User


class extendHouse(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('house_id', 'house_title', 'house_date', 'house_oriprice', "house_cityName")
    search_fields = ('house_date',)
    #
    # fieldsets = (
    #     ['House_main_info', {
    #         'fields': ('house_title', 'house_oriprice', 'house_type',
    #                    'house_area',
    #                    'house_kitchen',
    #                    'house_living_room',
    #                    'house_toilet',
    #                    'house_bedroom',
    #                    'house_capacity',
    #                    'house_bed',),
    #     }],
    #     ["House_address", {
    #         'fields': ('house_location_text',
    #                    'house_location_lat',
    #                    'house_location_lng',)
    #     }],
    #     ["City", {
    #         'fields': ('house_cityName',)
    #     }],
    #     ["Host_info", {
    #         'fields': ('house_host',)
    #     }],
    #     ["House_labels", {
    #         'fields': ('house_labels',)
    #     }],
    #     ["house_facility", {
    #         'fields': ('house_facility',)
    #     }],
    #     ["house_Scores", {
    #         'classes': ("collapse",),  # css 收缩
    #         'fields': (
    #             # 'house_favcount',
    #                    'house_commentNum',
    #                    'house_descScore',
    #                    'house_talkScore',
    #                    'house_hygieneScore',
    #                    'house_positionScore',
    #                    'house_avarageScore',)
    #     }],
    #     ['Advance', {
    #         'classes': ('collapse',),  # CSS
    #         'fields': (
    #             # 'house_id',
    #                    'house_url',
    #                    'house_date',
    #                    'house_firstOnSale',
    #                    'house_location_lat',
    #                    'house_location_lng',
    #                    'earliestCheckinTime',
    #                    ),
    #     }]
    # )


class extendHost(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('host_id', 'host_name', 'host_replayRate',
                    'host_commentNum', "host_RoomNum",  # 'host_RoomNumNow'
                    )

    fieldsets = (
        ['Main', {
            'fields': ('name', 'email'),
        }],
        ['Advance', {
            'classes': ('collapse',),  # CSS
            'fields': ('age',),
        }]
    )

    # def host_RoomNumNow(self,host_id):
    #     num = House.objects.filter(house_host=Host.objects.filter(host_id = host_id).first())
    #     return str(len(num))
    # 设置哪些字段可以点击进入编辑界面，默认是第一个字段
    # list_display_links = ('house_id', 'house_date','house_oriprice',"house_cityName")   能否点击的意思
    # 还可以通过函数来定制更多的功能


class extendCity(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('city_nm', 'city_pynm', 'city_statas',)


class extendFavourite(admin.ModelAdmin):
    list_display = ("user", 'fav_city', "fav_house_number",)

    def fav_house_number(self, obj):  # 好方便啊
        num = len(obj.fav_houses.all())
        return str(num)


admin.site.register(Host, extendHost)
admin.site.register(Labels)  # 这个是注册看排位的chouse_date
admin.site.register(Facility)
admin.site.register(House, extendHouse)
admin.site.register(City, extendCity)
admin.site.register(Favourite, extendFavourite)

# -*- coding: utf-8 -*-
import scrapy
# from ..items import KeywordItem  # 这个是关键词的item ，管道对item做一个
from urllib.parse import urljoin
import re
from bs4 import BeautifulSoup
import json
import time
from ..items import HouseItem,CityItem  # 导入转变过的Houseitem类

class HotwordspiderSpider(scrapy.Spider):
    name = 'hotelcity'
    allowed_domains = ['*']
    start_urls = ['https://minsu.meituan.com/']

    custom_settings = {  # 每个爬虫使用各自的自定义的设置
        "ITEM_PIPELINES": {
            'myscrapy.pipelines.cityItemPipeline': 300,  # 启用这个管道来保存数据

        },
        # "DOWNLOADER_MIDDLEWARES":{   # 这样就可以单独每个使用不同的配置
        # 'JobCrawl.middlewares.proxyMiddleware': 100,   # 使用代理
        # 'tutorial.middlewares.ProxyMiddleware':301
        # },
        'DOWNLOAD_DELAY': 1.5,  # 慢慢爬呗  ,这里写了下载延迟
        'DOWNLOAD_TIMEOUT':60,
        "DEFAULT_REQUEST_HEADERS": {
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.zhipin.com/',
            'X-Requested-With': "XMLHttpRequest",
            # "cookie":"lastCity=101020100; JSESSIONID=""; Hm_lvt_194df3105ad7148dcf2b98a91b5e727a=1532401467,1532435274,1532511047,1532534098; __c=1532534098; __g=-; __l=l=%2Fwww.zhipin.com%2F&r=; toUrl=https%3A%2F%2Fwww.zhipin.com%2Fc101020100-p100103%2F; Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a=1532581213; __a=4090516.1532500938.1532516360.1532534098.11.3.7.11"
            # 'Accept': 'application/json',
            'User-Agent': 'Mozilla/6.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Mobile Safari/537.36',
            # 'cookie':cookie

        }
    }

    def regexMaxNum(self,reg,text):  # 正则，返回匹配到的最大的数字就是页数了。
        temp = re.findall(reg,text)
        return max([int(num) for num in temp if num!=""])

    def parse(self, response):
        cityJsonString = response.xpath("//*[@id='r-props-J-searchbox']/text()").extract_first()
        cityJson =json.loads(cityJsonString.replace("<!--","").replace("-->",""))
        # print(cityJson)
        guangdong = '''广州市、韶关市、深圳市、珠海市、汕头市、佛山市、江门市、湛江市、茂名市、肇庆市、惠州市、梅州市、汕尾市、河源市、阳江市、清远市、东莞市、中山市、潮州市、揭阳市、雷州市、陆丰市、普宁市、'''
        topcity = '北京、南京、上海、杭州、昆明市、大连市、厦门市、合肥市、福州市、哈尔滨市、济南市、温州市、长春市、石家庄市、常州市、泉州市、南宁市、贵阳市、南昌市、南通市、金华市、徐州市、太原市、嘉兴市、烟台市、保定市、台州市、绍兴市、乌鲁木齐市、潍坊市、兰州市'
        total = guangdong+topcity
        for onecity in cityJson['cities']:
            item = CityItem()
            for city in total.split("、"):
                # print("输出了city")
                # print(city)
                if onecity['nm'] in city:
                    print("重点城市，插入中")
                    print(onecity['nm'])
                    item['city_nm'] = onecity['nm']
                    item['city_pynm'] = onecity['pynm']
                    yield item


    def getRSXFPrice(self,RSXF_TOKEN):  # 提取
        import datetime
        import requests
        import time
        url = 'https://minsu.meituan.com/gw/corder/api/v1/order/productPricePreview'
        data  ={
            "currentTimeMillis":int(round(time.time() * 1000)),   # 获得当前时间的毫秒
                "sourceType":7,
                "checkinGuests":1,
                "checkinDate":datetime.datetime.now().strftime("%Y%m%d"),  # 获得今天
                "checkoutDate":(datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y%m%d"), # 获得明天
                "productId":2645048,
                "autoChooseDiscount":'true',
                "avgMoneyFormat":'true',
                "deviceInfoByWeb":{
                    "ua":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
                    "touchPoint":"",
                    "browserPlugins":"Microsoft Edge PDF Plugin,Microsoft Edge PDF Viewer,Native Client",
                    "colorDepth":24,"pixelDepth":24,"screenWith":1280,"screenHeight":720,"browserPageWidth":653,"browserPageHeight":615}}
        header ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
                'Referer':'https://minsu.meituan.com/housing/2645048/'}
        cookies = {"XSRF-TOKEN":RSXF_TOKEN}
        result = requests.post(url,headers=header,data=data,cookies = cookies).content
        return result


    def detail(self, response):
        print(response.url)
        # from pprint import pprint
        item = HouseItem()
        print("获得是住房设施")
        tempDic = []
        facility = response.xpath("//*[@class='page-card']/*[@id='r-props-J-facility']").extract()
        all = BeautifulSoup(facility[0],'lxml').find("script",attrs={"id":"r-props-J-facility"}).get_text().strip("<!--").strip("-->")
        facilityDic = json.loads(all) # 设施可以提取录入
        for i in facilityDic:
            for j in facilityDic[i]:
                try:
                    for x in   j['group']:
        #                 print(x)
                        tempDic.append(x)
                except Exception as e :
                    break

        print("获得第一步发布的时间")
        text = facility[0]
        firstOnSaleTime = text[text.find('"firstOnSaleTime":')+18:18+13+text.find('"firstOnSaleTime":')]
        print(firstOnSaleTime)

        try: 
            # print("怎么回事")
            tempInt = int(firstOnSaleTime)  # 这个是房源信息第一次发布的时间
            # print(tempInt)
            import time 
            firstOnSale = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(tempInt/1000))
            # print(firstOnSale)
            # print("正常")
        except Exception as e:
            print(e)
            tempInt = 0 # 默认1970年1月1日的毫秒
            firstOnSale = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(tempInt/1000))
            print(firstOnSale)
            print("元年，没找到时间吼")


        print("获取房主数据")
        tempUserScript = response.xpath("//*[@id='r-props-J-gallery']").xpath("text()")
        UserJson = tempUserScript.extract()[0]
        # print(UserJson)
        UserJson = UserJson.replace('"',"'")  # 这儿替换是为了让下面统一以单引号来进行提取操作。
        # print(UserJson)
        # 的这里又变成了双引号,而且自动把间隙的空格去掉了
        house_id = re.findall("(?<=housing\\/)[0-9]*?(?=\\/)",response.url)[0]
        HostId = re.findall("(?<=hostId\\'\\:).*?(?=\\,)",UserJson)
        price = re.findall("(?<=price\\'\\:).*?(?=\\,)",UserJson)
        try:
            price = float(price[0])/100
        except Exception as e:
            print("price 出错")
            print(price)
            price = 0.00

        discountprice = re.findall("(?<=discountPrice\\'\\:).*?(?=\\,)",UserJson)
        title = response.xpath("//head/title").xpath("string(.)").extract()
        fullAddress = re.findall("(?<=fullAddress\\'\\:\\').*?(?=\\'\\,)",UserJson)  # 又有了，之前怎么回事，这个找不到怎么回事
        layoutRoom =  re.findall("(?<=layoutRoom\\'\\:).*?(?=\\,)",UserJson)
        layoutKitchen =  re.findall("(?<=layoutKitchen\\'\\:).*?(?=\\,)",UserJson)       
        layoutHall =  re.findall("(?<=layoutHall\\'\\:).*?(?=\\,)",UserJson)       
        layoutWc =  re.findall("(?<=layoutWc\\'\\:).*?(?=\\,)",UserJson)       
        maxGuestNumber =  re.findall("(?<=maxGuestNumber\\'\\:).*?(?=\\,)",UserJson)       
        bedCount =  re.findall("(?<=bedCount\\'\\:).*?(?=\\,)",UserJson)       
        roomArea =  re.findall("(?<=usableArea\\'\\:\\').*?(?=\\'\\,)",UserJson)  
        longitude = re.findall("(?<=longitude\\'\\:).*?(?=\\,)",UserJson)
        latitude = re.findall("(?<=latitude\\'\\:).*?(?=\\}\\,)",UserJson)
        cityName = re.findall("(?<=cityName\\'\\:\\').*?(?=\\'\\,)",UserJson)
        earliestCheckinTime = re.findall("(?<=earliestCheckinTime\\'\\:\\').*?(?=\\')",UserJson)

        house_type = response.xpath("//*[@class='spec-item spec-room'][1]/div/div[@class='value']/text()").extract()[0]
        if house_type==None:
            house_type = "未分类"
        house_commentNum = re.findall("(?<=count\\'\\:)[0-9]*?(?=\\,)",UserJson)
        if house_commentNum ==None:
            house_commentNum = 0

        print("房子面积开始")    # todo 有 bug，换了店后有些就找不到了。这个需要处理好来，re     
        # print(roomArea)
        # print(house_id)
        # print(price)
        # print(HostId)
        # 折扣价格和原价这个有区别。
        # print(discountprice)  # 这个确实没有了，因为找不到现在的价格。
        # print(title)
        # print(fullAddress)
        # print(longitude)
        # print(latitude)
        # print(layoutWc)
        # print(layoutHall)
        # print(layoutRoom)   # 卧室数量
        # print(layoutKitchen)
        # print(maxGuestNumber)
        # print(bedCount)
        # print(house_commentNum)
        
        print("下面是促销和普通的标签")
        tagList =  re.findall("(?<=productTagList\\').*?(?=\\'productTagInfoList\\')",UserJson)       
        tempJson = json.loads("".join(tagList).replace("'",'"').strip().strip(":").strip(","))
        # display(tempJson)
        discountList = {"1":[],"0":[]}
        for i in tempJson:
            if  i['bizType']==6:
                print(i['tagName'],i['detailList'][0],1)
                discountList['1'].append([i['tagName'],i['detailList'][0]])   # 这儿管道需要先检查后添加进来
            else:
                discountList['0'].append([i['tagName'],i['detailList'][0]])   # 这儿管道需要先检查后添加进来
        print(discountList)
        print("喜爱数量")
        favCount =  re.findall("(?<=favCount\\'\\:).*?(?=\\,)",UserJson)
        # 这个也是可能为0的，就是新房子
        if favCount==None:
            favCount = 0
        print(favCount)

        print()
        print("下面是房主的信息（我猜估计很多都是二次房主）")
        host_name = response.xpath("//a[@class='nick-name S--host-link']/text()").extract()
        host_name = host_name[0].replace(" ","").replace("\n","")
        host_main = response.xpath("//ul[@class='host-score-board']")
        host_infos = []  # 评价数，回复率，房源数
        for div in host_main.xpath("li"):
            temp = div.xpath("*[@class='value']/span/text()").extract()[0]
            if temp!=None or temp .find("%")!=-1:
                temp = temp.replace("%","")
                print(div.xpath("*[@class='value']/span/text()").extract())
            else:
                temp = 0  # 如果没有评价，或者没有回复（新房主）那就是0   
            host_infos.append(temp)



        # print(host_infos)
        print("房主信息")

        # print(HostId)  # 这些是房主的信息
        # print(host_infos[0])
        # print(host_infos[1])
        # print(host_infos[2])

        host_commentNum = host_infos[0]
        host_replayRate =  host_infos[1]
        host_RoomNum = host_infos[2]


        # pointer_num = response.xpath("//span[@class='zg-price']/text()").extract()
        # print(pointer_num[0])
        # print(pointer_num[1])
        # print(pointer_num[2])

        # print("这个也不是每个都有的。")
        # print("这个是平均分")
        avarageScore = response.xpath("//*[@class='sum-score-circle']/text()").extract()
        # 新房子
        if avarageScore==None:
            print(f"新房子，检查一下{response.url}")
            avarageScore = 0
        # print(avarageScore)


        fourScore = []   # 描述，沟通，卫生，位置的评分
        for score in response.xpath("//ul[@class='score-chart']").xpath("li"):
            tempscore = score.xpath("div/div[@class='score']/text()").extract()
            if tempscore==None:
                tempscore = 0 
            fourScore.append(tempscore)
        # print(fourScore)
        house_descScore = fourScore[0][0]
        house_talkScore = fourScore[1][0]
        house_hygieneScore = fourScore[2][0]
        house_positionScore = fourScore[3][0]

        # print(house_descScore)
        # print(house_talkScore)
        # print(house_hygieneScore)
        # print(house_positionScore)

        #print("这儿是提取rsxf")
        # print("提取价格这个好难啊，看看还有没有别的什么")  todo 有空再来琢磨一下
        # print("rsxf")
        # RSXF_TOKEN = response.xpath("//meta[@name='csrf-token']/@content").extract()[0]
        # print(RSXF_TOKEN)
        # result = self.getRSXFPrice(RSXF_TOKEN)
        # print(result)
        ## 进行请求


        item['house_cityName'] = cityName[0]
        item['earliestCheckinTime'] = earliestCheckinTime[0]
        item['house_url'] = response.url
        item['house_id'] =house_id
        item['house_oriprice'] = price





        item['house_title'] = title[0].replace(" ","").replace("\n","")
        item['house_type'] = house_type  # 房子的类型



        # item['house_date'] = fullAddress   # 爬取的时间，这个因为自动now就可以
        item['house_firstOnSale'] = firstOnSale   # 这个是最早发布的时间
        item['house_favcount'] = favCount[0]
        item['house_commentNum'] = house_commentNum[0]

        item['house_descScore'] = house_descScore # 房子四个分数
        item['house_talkScore'] = house_talkScore
        item['house_hygieneScore'] = house_hygieneScore
        item['house_positionScore'] = house_positionScore
        item['house_avarageScore'] = avarageScore[0] 

        # item['house_avarageScore'] = avarageScore  # 平均分
        # item['house_type'] = None
        item['house_area'] = roomArea[0]
        item['house_toilet'] = layoutWc[0]
        item['house_kitchen'] = layoutKitchen[0]
        item['house_living_room'] = layoutHall[0]  # 客厅
        item['house_bedroom'] = layoutRoom[0]
        item['house_capacity'] = maxGuestNumber[0]  #  容纳多少个人
        item['house_bed'] = bedCount[0]
        item['house_location_text'] = fullAddress[0]
        item['house_location_lat'] = latitude[0]
        item['house_location_lng'] = longitude[0]
        # item['house_facility'] = None
        # item['house_host'] =   None



        jsonString = {}  # 这个一次性打包带过去，然后再那边再一起组装起来就好
        jsonString['Host'] = {
            'hostId':HostId[0],
            'host_name':host_name,
            'host_replayRate':host_replayRate,
            'host_commentNum':host_commentNum,
            "host_RoomNum":host_RoomNum
        }

        jsonString['Labels'] = discountList  # list类型内包含其他的
        jsonString['Facility'] = tempDic  # Lise类型包含其他的
        item['jsonString'] = jsonString
        # print("这全部的东西要传到一个item里面才可以啊")
        yield item

        print(house_type)

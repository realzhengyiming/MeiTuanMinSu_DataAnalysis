# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     parseTool   
   Description :  这个文件用来处理美团字体解密的，
   Author :        zhengyimiing 
   date：          2020/4/8 
-------------------------------------------------
   Change Activity:
                   2020/4/8  
-------------------------------------------------
"""
import pickle
import sys

import requests

__author__ = 'zhengyimiing'


from fontTools.ttLib import TTFont
import os
import json
import re


# 获得j-gallery这段的字符串
def getFontUrl(UserJson):
    j_gallery_text = UserJson  # 这儿再处理一遍去掉可能出现的东西
    UserJson = j_gallery_text.replace("'",'"').replace("\\","")   # 这样才可以去掉了这一个杠杠
    test = re.findall('(?<=cssPath\\"\\:\\").*?(?=\\}\\,)',UserJson)[0]

    print()
    wofflist = re.findall('(?<=\\(\\").*?(?=\\)\\;)',test)   # j-gallery 那段string放进去就可以找到了
#     print(wofflist)
    print()
    font_url = ''
    for woffurl in wofflist:
        if woffurl.find("woff")!=-1:
            tempwoff = re.findall('(?<=\\").*?(?=\\")',woffurl)
    #         print(tempwoff)
            for j in tempwoff:
                if j.find("woff")!=-1:
                    print("https:"+j)
                    font_url = "https:"+ j

    # 提取字体成功
#     print(font_url)
    return font_url


def download_font(img_url,imgName,path=None):
    headers = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
              }   ##浏览器请求头（大部分网站没有这个请求头会报错、请务必加上哦）
    try:
        img = requests.get(img_url, headers=headers)
        dPath = os.path.join("woff",imgName)  # imgName传进来不需要带时间
        # print(dPath)
        print("字体的文件名 "+dPath)
        f = open(dPath, 'ab')
        f.write(img.content)
        f.close()
        print("下载成功")
        return dPath
    except Exception as e:
        print(e)


# 从字体文件中获得字形数据用来备用待对比
def getGlyphCoordinates(filename):
    """
    获取字体轮廓坐标,手动修改key值为对应数字
    """
    font = TTFont("woff/"+f'{filename}')  # 自动带上了woff文件夹
    # font.saveXML("bd10f635.xml")
    glyfList = list(font['glyf'].keys())
    data = dict()
    for key in glyfList:
        # 剔除非数字的字体
        if key[0:3] == 'uni':  # 这样对比都行，我感觉有
            data[key] = list(font['glyf'][key].coordinates)
    return data


def getFontData(font_url):
    # 合并两个操作，如果有的话就不用下载
    filename = os.path.basename(font_url)
    font_data = None
    if os.path.exists("woff/"+filename):
        # 直接读取
        font_data = getGlyphCoordinates(filename)  # 读取时候自带woff文件夹
    else:
        # 先下载再读取
        download_font(font_url, filename, path=None)
        font_data = getGlyphCoordinates(filename)
    if font_data == None:
        print("字题文件读取出错，请检查")
    else:
        #         print(font_data)
        return font_data


# font_data = getFontData(font_url)/
# font_data
# 再整合一下


# 自动分割并且大写,这两个要连着来调用，那么全部封装成一个对象好了
def splitABC(price_unicode):
    raw_price = price_unicode.split("&amp;")
    temp_price_unicode = []
    for x in raw_price:
        if x != "":
            temp_price_unicode.append(x.upper().replace("#X", "").replace(";", ""))
    return temp_price_unicode  # 提取出简化大写的  4 0  这个是原价 ，折扣价才是280 所以


def getBothSplit(UserJson):
    UserJson = UserJson.replace("\\", "").replace("'", '"')
    result_price = []
    result_discountprice = []
    try:
        price_unicode = re.findall('(?<=price\\"\\:\\").*?(?=\\"\\,)', UserJson)[0]  # 原假数字400
        result_price = splitABC(price_unicode)
    except Exception as e:
        print("没有找到价格")
        print(e)

    try:  # 可能没有找到，那就会有☞
        discountprice_unicode = re.findall('(?<=discountPrice\\"\\:\\").*?(?=\\"\\,)', UserJson)[0]  # 原假数字400
        result_discountprice = splitABC(discountprice_unicode)
    except Exception as e:
        print("没有找到折扣价")
        print(e)
    #     print(discountprice_unicode)
    #     print(price_unicode)
    if result_discountprice == [] and result_price != []:
        result_discountprice = result_price  # 如果折扣价为0的话，那么就等于原价好了
    return result_price,result_discountprice  # 如果没有折扣那就,这个只是返回处理后的价格编码


# price_unicode_list = splitABC(price_unicode)
# discountprice_unicode_list = splitABC(discountprice_unicode)
# price_unicode_list, discountprice_unicode_list = getBothPrice(UserJson)
# print(price_unicode_list)
# print(discountprice_unicode_list)
def pickdict(dict):  # 序列化这个字典
    with open(os.path.join(os.path.abspath('.'),"label_dict.pickle"), "wb") as f:
        pickle.dump(dict, f)


def unpickdict() -> dict:
    d = {}
    with open(os.path.join(os.path.abspath('.'),"label_dict.pickle"), "rb") as f:

        d = pickle.load(f)
    return d

def parseNum(price_unicode_list,font_data):   # 只需要输入处理后的价格的unicode_list 就可以了
    temp_woff_value = ""
    label_dict = unpickdict()   # 直接文件中提取这个
    for i in price_unicode_list:
        for key in font_data:
            # 加一个对小数点的判断
            if i.find(".")!=-1:
                # 找到有小数点的，
                temp_i = i.replace(".","")  # 先去掉，后面再加回来
                if key[3:] == temp_i:
                    for label in label_dict:
                        if label_dict[label]==font_data[key]:
                            # print(label)
                            temp_woff_value = temp_woff_value+ str(label)+"."
            else:
                if key[3:] == i:
                    # print(font_data[key])  # 再用这个数据和识别了字形数据的数据进行就可以了,第二次对比
                    for label in label_dict:
                        if label_dict[label]==font_data[key]:
                            # print(label)
                            # print(str(label))
                            temp_woff_value += str(label)
    return float(temp_woff_value)

# print(parseNum(price_unicode_list,font_data))
# print(parseNum(discountprice_unicode_list,font_data))
# 下面的是main了（）
def parsePriceMain(UserJson): # 测试用
    print("testing")
    print(os.path.abspath("."))
    # 这个就相当于是main函数了 ，代码块
    font_url = getFontUrl(UserJson)  # 获得字体url
    # 获得处理后的 price,discountprice 的unicode_list
    price_unicode_list, discountprice_unicode_list = getBothSplit(UserJson)
    font_data = getFontData(font_url)
    real_price = parseNum(price_unicode_list,font_data)
    real_discount = parseNum(discountprice_unicode_list,font_data)
    print(real_price)
    print(real_discount)
    return real_price,real_discount


if __name__ == '__main__':
    print(os.path.abspath('.'))
    import requests
    # url = input("请输入你的网页") todo 记得这个把woff文件给改了

    url = "https://minsu.meituan.com/housing/2641002/"
    headers = {
        #     'cookie':cookiestr,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }

    html = requests.get(headers=headers, url=url).content
    # 获得price中的那段string

    # 增加beautifulsoup来处理，这一段scrapy中可以省略，scrapy中替换为 findall那个，还要加上cssPath 的查找才可以
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'lxml')
    j_gallery_text = soup.find("script", attrs={"id": "r-props-J-gallery"}).get_text()
    UserJson = j_gallery_text
    real_price,real_discount = parsePriceMain(UserJson)
    print()
    print("输出价格如下：")
    print(real_price)
    print(real_discount)
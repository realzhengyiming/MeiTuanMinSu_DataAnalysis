"""mydjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from . import views
# from mydjango.hotelapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",views.index,),
    path('hotelapp',include("hotelapp.urls")),
    # path('site/',include("siteapp.urls")),  # 这样就可以一次性导入一整个应用的映射 ,app_name="siteapp"
    # path("seoapp/",include("seoapp.urls")),  # 这个是引入seoapp的url
]

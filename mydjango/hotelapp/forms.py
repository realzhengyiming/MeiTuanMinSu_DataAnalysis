# -*- coding: utf-8 -*-

"""
-------------------------------------------------
   File Name：     forms   
   Description :  
   Author :        zhengyimiing 
   date：          2020/3/26 
-------------------------------------------------
   Change Activity:
                   2020/3/26  
-------------------------------------------------
"""
from django.contrib.auth.models import User

__author__ = 'zhengyimiing'
from django import forms
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'mdui-textfield-input', 'placeholder':"用户名"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'mdui-textfield-input', 'placeholder':"密码"}))  # 秘密啊


class RegistrationForm(forms.ModelForm):  # 这个是注册表单的,表单继承model就是modelform
    username =  forms.CharField(label="用户名",widget=forms.TextInput(attrs={'class': 'mdui-textfield-input', 'placeholder':"用户名"}))
    password = forms.CharField(label="密码",widget=forms.PasswordInput(attrs={'class': 'mdui-textfield-input',
                                                                            'pattern':"^.*(?=.{8,})(?=.*[a-z])(?=.*[A-Z]).*$",'placeholder':"密码"}))
    password2 = forms.CharField(label="再次输入密码",widget=forms.PasswordInput(attrs={'class': 'mdui-textfield-input',
                                                                            'pattern':"^.*(?=.{8,})(?=.*[a-z])(?=.*[A-Z]).*$",'placeholder':"密码"}))
    email = forms.CharField(label='邮箱',widget=forms.EmailInput(attrs={'type':"email",'class': 'mdui-textfield-input', 'placeholder':"密码"})
                            ,error_messages={'required': "邮箱不能为空"})



    class Meta:
        model = User
        fields = ("username","email")

        def clean_password2(self):
            cd = self.cleaned_data
            if cd['password'] != cd['password2']:
                raise forms.ValidationError("两次输入的密码不相同")
            return cd["password2"]


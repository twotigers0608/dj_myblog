# -*- coding:utf8 -*-
from django.urls import re_path
from . import views

urlpatterns = [
    re_path('index/$', views.Home.as_view()),
    re_path('getajax/$', views.getajax),
    re_path('getajax/Userjson/$', views.UserJson),
    re_path('index/weekjson$', views.Weekjson),
]

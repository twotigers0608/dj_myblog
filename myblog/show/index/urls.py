# -*- coding:utf8 -*-
from django.urls import re_path
from . import views

urlpatterns = [
    re_path('$', views.Home.as_view()),
    re_path('getjson/$', views.Json.as_view()),
]
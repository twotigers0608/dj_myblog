# -*- coding:utf8 -*-
from django.urls import re_path
from . import views

urlpatterns = [
    re_path('index/', views.Home.as_view()),
]
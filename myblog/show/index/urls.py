# -*- coding:utf8 -*-
from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^testshow/$', views.testshow),
    re_path(r'^ajax/get_metrics/$', views.ajax_get_data),
    re_path(r'^$', views.Index.as_view()),
    # re_path(r'^article/$' ,views.Article.as_view()),
    re_path(r'^test/', views.test),
]

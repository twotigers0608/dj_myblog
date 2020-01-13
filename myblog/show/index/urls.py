# -*- coding:utf8 -*-
from django.urls import re_path, path
from . import views

app_name = 'index'
urlpatterns = [
    re_path('^$', views.Index.as_view(), name='index'),
    re_path('^testshow/$', views.testshow),
    re_path('^ajax/get_metrics/$', views.ajax_get_data),
    path('article/', views.show_article),
    # path('article/<int:pk>/', views.Article),
    re_path('^article/(?P<pk>\d+)/$', views.Article, name='article'),
    re_path('^tools/', views.testshow),
    re_path('^aboutme/', views.Aboutme),
]

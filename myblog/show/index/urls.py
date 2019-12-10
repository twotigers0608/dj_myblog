# -*- coding:utf8 -*-
from django.urls import re_path, path
from . import views

app_name = 'index'
urlpatterns = [
    re_path('^$', views.Index.as_view(), name='index'),
    re_path('^testshow/$', views.testshow),
    re_path('^ajax/get_metrics/$', views.ajax_get_data),
    re_path('^article/$', views.show_article),
    # path('article/<int:pk>/', views.Article),
    path('article/<int:pk>/', views.detail, name='article'),
    path('classify/<str:classify>', views.classify),
    re_path('^tools/$', views.testshow),
    re_path('^aboutme/$', views.Aboutme),
]

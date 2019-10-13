from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
import json
from .models import Post


# Create your views here.
def testshow(request):
    if request.method == "GET":
        return render(request, "text.html")


def ajax_get_data(request):
    if request.method == "POST":
        data = [{
            'patch_id': '123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': "2019-07-09 19:44:01",
        }, {
            'patch_id': '123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': '2019-07-19 19:44:01',
        }, {
            'patch_id': '123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': '2019-07-19 19:44:01',
        }, {
            'patch_id': '123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': '2019-07-29 19:44:01',
        }, {
            'patch_id': '123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': '2019-08-19 19:44:01',
        }, {
            'patch_id': '123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': '2019-08-19 19:44:01',
        }, ]
        return JsonResponse({"state": 200, "msg": "OK",
                             "Result": data
                             })


def get_news(request):
    if request.method == "GET":
        return JsonResponse({"state": 200, "msg": "OK",
                             "Result": {"name": ["2019-21", "2019-21", "2019-21", "2019-22", "2019-22", "2019-22"],
                                        "value": [5, 20, 36, 10, 10, 20]}})


def Weekjson(request):
    if request.method == "POST":
        data = [{
            'patch_id':'123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': 2019-22,
        },{
            'patch_id': '123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': 2019-23,
        },{
            'patch_id': '123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': 2019-24,
        },{
            'patch_id': '123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': 2019-25,
        },{
            'patch_id': '123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': 2019-26,
        },{
            'patch_id': '123456',
            'total_duration': 15,
            'review_duration': 23,
            'merge_duration': 34,
            'rel_duration': 25,
            'released_time': 2019-21,
        }, ]
        return JsonResponse({"status": "200", "msg": "OK", "data": data})


class Index(View):
   def get(self, request):
        # post_list = Post.objects.all().order_by('-create_time')
        # return render(request, "index1.html",context={'post_list':post_list})
        pass


class Article(View):
    def get(self, request):
        return render(request, "column1.html")
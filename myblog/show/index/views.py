from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
import json


# Create your views here.
def testshow(request):
    if request.method == "GET":
        return render(request, "text.html")


def ajax_get_data(request):
    if request.method == "GET":
        return JsonResponse({"state": 200, "msg": "OK",
                             "Result": {
                                 "name": ["2019-21", "2019-22", "2019-23", "2019-24", "2019-25", "2019-26", "2019-27",
                                          "2019-28", "2019-29", "2019-30"],
                                 "new": [320, 302, 301, 334, 390, 330, 320],
                                 "reviewing": [120, 132, 101, 134, 90, 230, 210],
                                 "approved": [220, 182, 191, 234, 290, 330, 310],
                                 "merged": [150, 212, 201, 154, 190, 330, 410],
                                 "released": [820, 832, 901, 934, 1290, 1330, 1320],
                             },
                             })


def get_news(request):
    if request.method == "GET":
        return JsonResponse({"state": 200, "msg": "OK",
                             "Result": {"name": ["2019-21", "2019-21", "2019-21", "2019-22", "2019-22", "2019-22"],
                                        "value": [5, 20, 36, 10, 10, 20]}})


def Weekjson(request):
    if request.method == "GET":
        data = [{
            "week": "2019-21",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 0,
            "merged": 2,
            "released": 19,
        }, {
            "week": "2019-21",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 0,
            "merged": 2,
            "released": 19,
        }, {
            "week": "2019-22",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 2,
            "merged": 2,
            "released": 19,
        }, {
            "week": "2019-22",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 2,
            "merged": 2,
            "released": 19,
        }, {
            "week": "2019-23",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 3,
            "merged": 3,
            "released": 19,
        }, {
            "week": "2019-23",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 3,
            "merged": 3,
            "released": 19,
        }, {
            "week": "2019-24",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 4,
            "merged": 4,
            "released": 19,
        }, {
            "week": "2019-25",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 5,
            "merged": 5,
            "released": 19,
        }, ]
        return JsonResponse({"status": "200", "msg": "OK", "data": data})


class Index(View):
   def get(self, request):

       return render(request, "index1.html")
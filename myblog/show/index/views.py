from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
import json


# Create your views here.

class Home(View):
    def get(self, request):
        week = {
            '2018.51': {'num': '21',
                        'NO': 1,
                        'BeforeReview': '0 Day(s) 1 Hour(s) (13%)',
                        'Review': '0 Day(s) 1 Hour(s) (13%)',
                        'Maintainer': '0 Day(s) 0 Hour(s) (0%)',
                        'SubmitToMerge': '0 Day(s) 5 Hour(s) (63%)',
                        'Merge': '0 Day(s) 1 Hour(s) (13%)',
                        'PatchId': '13 / 09 / 19',
                        'Date': 0,
                        'Before': 1,
                        'Submit': 4,
                        },
            '2018.52': {'num': '45',
                        'NO': 2,
                        'BeforeReview': '0 Day(s) 9 Hour(s) (13%)',
                        'Review': '0 Day(s) 4 Hour(s) (13%)',
                        'Maintainer': '0 Day(s) 0 Hour(s) (67%)',
                        'SubmitToMerge': '0 Day(s) 4 Hour(s) (3%)',
                        'Merge': '0 Day(s) 7 Hour(s) (23%)',
                        'PatchId': '13 / 09 / 19',
                        'Date': 0,
                        'Before': 1,
                        'Submit': 4,
                        },
        }

        context = {'week': week}
        return render(request, 'text.html', context=context)


def getajax(request):
    if request.method == "GET":
        return render(request, 'testajax.html')


def UserJson(request):
    # 测试 ajax 请求
    if request.method == "GET":
        data = [
            {
                "name": "SheyPang",
                "rolename": "管理员",
                "status": "1",
                "isActive": "1",
                "createTime": "2018-01-01",
                "lastLogin": "2018-02-02"
            }, {
                "name": "PPPPPPP",
                "rolename": "管理员",
                "status": "1",
                "isActive": "1",
                "createTime": "2018-01-01",
                "lastLogin": "2018-02-02"
            }, {
                "name": "AAAAAA",
                "rolename": "管理员",
                "status": "1",
                "isActive": "1",
                "createTime": "2017-01-01",
                "lastLogin": "2017-02-02"
            }, {
                "name": "VVVVVVVV",
                "rolename": "管理员",
                "status": "1",
                "isActive": "1",
                "createTime": "2018-06-04",
                "lastLogin": "2018-02-02"
            }
        ]
    return JsonResponse({"status": "200", "msg": "OK", "data": data})


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
        },{
            "week": "2019-21",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 0,
            "merged": 2,
            "released": 19,
        },{
            "week": "2019-21",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 0,
            "merged": 2,
            "released": 19,
        },{
            "week": "2019-21",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 0,
            "merged": 2,
            "released": 19,
        },{
            "week": "2019-21",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 0,
            "merged": 2,
            "released": 19,
        },{
            "week": "2019-21",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 0,
            "merged": 2,
            "released": 19,
        },{
            "week": "2019-21",
            "branch": "Android",
            "new": 0,
            "reviewing": 0,
            "approved": 0,
            "merged": 2,
            "released": 19,
        },]
        return JsonResponse({"status": "200", "msg": "OK", "data": data})

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
import json


class Json(View):
    def get(self, request):
        #count = {"State": 1, "Message": "成功",
                 #"Result": {"name": ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"], "value": [5, 20, 36, 10, 10, 20]}}

        # return HttpResponse(json.dumps(count, ensure_ascii=False), content_type="application/json,charset=utf-8")
        return JsonResponse({"State": 1, "Message": "成功", "Result": {"name": ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"],
                                                                     "value": [5, 20, 36, 10, 10, 20]}})


def apis(request):
    print("hello input")
    # p={"word":"data"}
    # 查看客户端发来的请求,前端的数据
    print("request.body={}".format(request.body))
    # 返回给客户端的数据
    result = "success"
    if request.method == "POST":
        print(request.POST)

    return JsonResponse({"status": 200, "msg": "OK", "data": result})
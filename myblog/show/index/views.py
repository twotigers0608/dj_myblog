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


class Json(View):
    def get(self, request):
        count = {
            "State": 1,
            "Message": "成功",
            "Result": {
                "name": [
                    "衬衫",
                    "羊毛衫",
                    "雪纺衫",
                    "裤子",
                    "高跟鞋",
                    "袜子"
                ],
                "value": [
                    5,
                    20,
                    36,
                    10,
                    10,
                    20
                ]
            }
        }

        # return HttpResponse(json.dumps(count, ensure_ascii=False), content_type="application/json,charset=utf-8")
        # return JsonResponse(count)
        return JsonResponse(count, safe=False)


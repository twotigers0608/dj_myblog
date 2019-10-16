from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
import json
from .models import Post


# Create your views here.
def testshow(request):
    if request.method == "GET":
        return render(request, "metrics.html")


def ajax_get_data(request):
    if request.method == "POST":
        data = [{
            'id': '28',
            'total_duration': 15000,
            'verify_duration': 10000,
            'review_duration': 23000,
            'merge_duration': 34000,
            'rel_duration': 25000,
            'released_time': 1570144176912,
        }, {
            'id': '29',
            'total_duration': 15000,
            'verify_duration': 10000,
            'review_duration': 23000,
            'merge_duration': 34000,
            'rel_duration': 25000,
            'released_time': 1570144176912,
        }, {
            'id': '29',
            'total_duration': 15000,
            'verify_duration': 10000,
            'review_duration': 23000,
            'merge_duration': 34000,
            'rel_duration': 25000,
            'released_time': 1571100176912,
        }, {
            'id': '31',
            'total_duration': 15000,
            'verify_duration': 10000,
            'review_duration': 23000,
            'merge_duration': 34000,
            'rel_duration': 25000,
            'released_time': 571100176912,
        }, {
            'id': '31',
            'total_duration': 15000,
            'verify_duration': 10000,
            'review_duration': 23000,
            'merge_duration': 34000,
            'rel_duration': 25000,
            'released_time': 571144106912,
        }, {
            'id': '34',
            'total_duration': 15000,
            'verify_duration': 10000,
            'review_duration': 23000,
            'merge_duration': 34000,
            'rel_duration': 25000,
            'released_time': 571144176912,
        }, ]
        return JsonResponse({"data": data})


class Index(View):
    def get(self, request):
        # post_list = Post.objects.all().order_by('-create_time')
        # return render(request, "index1.html",context={'post_list':post_list})
        pass


class Article(View):
    def get(self, request):
        return render(request, "column1.html")


def test(request):
    if request.method == 'GET':
        return render(request, 'week1.html')

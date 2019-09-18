from django.shortcuts import render
from django.views import View


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
        context = {'week':week}
        return render(request, 'week1.html', context=context)


    '''var data = [{
            month: "1月",
            value: 2500,
            ratio: 14.89
        },

        {
            month: "2月",
            value: 2800,
            ratio: 79.49
        },

        {
            month: "3月",
            value: 3000,
            ratio: 75.8
        },

        {
            month: "4月",
            value: 2600,
            ratio: 19.8
        },

        {
            month: "5月",
            value: 3500,
            ratio: 44.5
        },


        {
            month: "6月",
            value: 2500,
            ratio: 87.3
        },
        {
            month: "7月",
            value: 3200,
            ratio: 87.3
        },
        {
            month: "8月",
            value: 3100,
            ratio: 87.3
        },
        {
            month: "9月",
            value: 2900,
            ratio: 87.3
        },
        {
            month: "10月",
            value: 2500,
            ratio: 87.3
        },
        {
            month: "11月",
            value: 3600,
            ratio: 87.3
        },
        {
            month: "12月",
            value: 3400,
            ratio: 87.3
        },
        {
            month: "1月",
            value: 2800,
            ratio: 87.3
        },
        {
            month: "2月",
            value: 3000,
            ratio: 87.3
        },
        {
            month: "3月",
            value: 2400,
            ratio: 87.3
        },

    ];'''

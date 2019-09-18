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
        return render(request, 'text.html', context=context)

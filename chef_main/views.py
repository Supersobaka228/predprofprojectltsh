from django.shortcuts import render

from admin_main.models import BuyOrder


# Create your views here.


def chef(request):

    context = {
        'orders': BuyOrder.objects.all(),
    }


    return render(request, 'chef_main/chef_main.html')
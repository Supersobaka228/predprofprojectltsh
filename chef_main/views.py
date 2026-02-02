from django.shortcuts import render

# Create your views here.


def chef(request):
    return render(request, 'chef_main/chef_main.html')
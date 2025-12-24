from django.shortcuts import render

# Create your views here.
def menu(request):
    if request.method == 'POST' or request.method == 'GET':
        return render(request, 'menu/menu.html')
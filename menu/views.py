from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
@login_required
def menu(request):
    print(request.user.email)
    return render(request, 'menu/menu.html')
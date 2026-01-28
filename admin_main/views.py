from tkinter import Menu

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from admin_main.models import BuyOrder, Notification
from menu.models import MenuItem


@csrf_exempt
@login_required
def admin(request):
    menu = MenuItem.objects.all()
    user = request.user
    context = {
        'current_user': user,
        'notifications': Notification.objects.all(),
        'buyorders': BuyOrder.objects.all(),
        'menu': menu,
    }
    return render(request, 'admin_main/admin_main.html', context)

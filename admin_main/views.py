from datetime import datetime
from tkinter import Menu

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from admin_main.models import BuyOrder, Notification
from menu.models import MenuItem, Order


@csrf_exempt
@login_required
def admin(request):
    menu = MenuItem.objects.all()
    user = request.user
    context = {
        'current_user': user,
        'notifications': Notification.objects.all(),
        'buyorders': BuyOrder.objects.all(),
        'buyorders_count': len(BuyOrder.objects.all()),
        'data': orders_by_date(),
        'menu': len(menu),
        'summ': sum_orders_count(),
        'sum_comes': sum_comes()
    }
    return render(request, 'admin_main/admin_main.html', context)

def sum_orders_count():
    summ = 0
    for order in Order.objects.all():
        summ += order.price
    return summ

def sum_comes():
    summ = set()
    for order in Order.objects.all():
        summ.add(order.price)
    return len(summ)

def orders_by_date():
    dates = [0] * 5
    for order in Order.objects.all():
        date_obj_1 = datetime.strptime(order.day, "%Y-%m-%d").date()  # .date() убирает время
        dates[date_obj_1.weekday()] += order.price

    return dates
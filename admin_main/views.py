from datetime import datetime, timedelta
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
        'sum_comes': sum_comes(),
        'comes_by_date': comes_by_date(),
        'orders_by_day': orders_by_day(),
        'comes_by_day': comes_by_day(),

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


def comes_by_date():
    dates = [set(), set(), set(), set(), set()]
    for order in Order.objects.all():
        date_obj_1 = datetime.strptime(order.day, "%Y-%m-%d").date().weekday()
        dates[date_obj_1].add(order.user)
    return list(map(lambda x: len(x), dates))


def orders_by_day():
    dates = {}
    for order in Order.objects.all():
        date_obj_1 = datetime.strptime(order.day, "%Y-%m-%d").date()
        if date_obj_1 not in dates:
            dates[date_obj_1] = order.price
        else:
            dates[date_obj_1] += order.price
    min_date = min(dates)
    max_date = max(dates)
    result = {}
    ans = {}
    current_date = min_date - timedelta(days=(min_date.weekday()))
    while current_date <= max_date + timedelta(days=(5 - max_date.isoweekday())):
        if current_date.weekday() < 5:
            date_str = current_date.strftime("%Y-%m-%d")
            result[date_str] = dates.get(current_date, 0)
        current_date += timedelta(days=1)
    for i in range(0, len(result), 5):
        dates = result

        d = list(dates.keys())
        ans[f'{d[i]} {d[i + 4]}'] = [dates[j] for j in list(dates.keys())[i:i + 5]]

    return ans


def comes_by_day():
    dates = {}
    # 1. Собираем множества уникальных пользователей для каждой даты
    for order in Order.objects.all():
        date_obj_1 = datetime.strptime(order.day, "%Y-%m-%d").date()
        if date_obj_1 not in dates:
            dates[date_obj_1] = {order.user}  # Используем set для уникальности
        else:
            dates[date_obj_1].add(order.user)

    if not dates:
        return {}

    min_date = min(dates)
    max_date = max(dates)
    result = {}
    ans = {}

    current_date = min_date - timedelta(days=(min_date.weekday()))
    while current_date <= max_date + timedelta(days=(5 - max_date.isoweekday())):
        if current_date.weekday() < 5:
            date_str = current_date.strftime("%Y-%m-%d")
            result[date_str] = len(dates.get(current_date, set()))
        current_date += timedelta(days=1)

    d_keys = list(result.keys())
    for i in range(0, len(d_keys), 5):
        week_slice = d_keys[i:i + 5]
        ans[f'{week_slice[0]} {week_slice[-1]}'] = [result[j] for j in week_slice]

    return ans


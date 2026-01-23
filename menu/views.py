from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django import template
from users.views import register
from .forms import ReviewForm, OrderForm
from .models import MenuItem, DayOrder, Review, Order
from datetime import datetime, timedelta
import locale
from users.models import User
from datetime import datetime, timedelta

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    pass


@csrf_exempt
@login_required
def menu(request):
    date_str = request.GET.get('date')
    if request.method == 'POST':
        if 'allergens' in request.POST:
            update_allergens(request)
        elif 'price' in request.POST:
            order(request)
        else:
            s = dict(request.POST.items())
            s.pop('csrfmiddlewaretoken', None)


            s['day'] = str(format_russian_date(datetime.strptime(date_str, '%Y-%m-%d').date()))
            form = ReviewForm(s)
            if form.is_valid():
                form.save()


    if date_str:
        try:
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = datetime.today().date()
    else:
        current_date = datetime.today().date()

    current_day = current_date.isoweekday()



    try:
        day_order = DayOrder.objects.get(day=current_day)

    except DayOrder.DoesNotExist:
        day_order = None


    if day_order:
        menu_items_dict = {item.id: item for item in MenuItem.objects.filter(id__in=day_order.order)}
        menu_items = [menu_items_dict[int(id)] for id in day_order.order if int(id) in menu_items_dict]
    else:
        menu_items = []

    

    date_display = format_russian_date(current_date)


    prev_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        orders = Order.objects.filter(Q(user_id=request.user.id))
    except Order.DoesNotExist:
        orders = None
    orders_d = dict_orders(orders)


    context = {
        'menu_items': menu_items,
        'date_display': date_display,
        'current_date': current_date.strftime('%Y-%m-%d'),
        'prev_date': prev_date,
        'next_date': next_date,
        'review_items': Review.objects.all(),
        'orders': orders_d,
        'orders_keys': orders_d.keys()
    }
    return render(request, 'menu/menu.html', context)


@login_required
def order(request):
    if request.method == 'POST':
        ordered_menu = dict(request.POST.items())
        ordered_menu.pop('csrfmiddlewaretoken', None)
        ordered_menu['user'] = request.user.id
        form = OrderForm(ordered_menu)
        if form.is_valid():
            form.save()
    return



@login_required
def update_allergens(request):
    """Обновление аллергенов пользователя"""
    if request.method == 'POST':
        # Получаем список выбранных аллергенов
        selected_allergens = request.POST.getlist('allergens')
        from django.db.models import Q
        # Удаляем старые аллергены пользователя

        user = User.objects.get(Q(username=request.user.username))
        user.not_like = selected_allergens
        user.save()

    return JsonResponse({'success': False, 'error': 'Неправильный метод запроса'})



def dict_orders(orders):
    ans = dict()
    for i in orders.all():
        current_date = datetime.strptime(i.day, '%Y-%m-%d').date()
        r = format_russian_date(current_date)
        if r in ans.keys():
            ans[r].append(i)
        else:
            ans[r] = [i]
    return ans


def format_russian_date(date_obj):
    months = ['янв.', 'февр.', 'мар.', 'апр.', 'мая', 'июня', 'июля', 'авг.', 'сент.', 'окт.', 'нояб.', 'дек.']
    days = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']

    day = date_obj.day
    month = months[date_obj.month - 1]
    year = date_obj.year
    weekday = days[date_obj.isoweekday() - 1]

    return f"{day} {month} {year}, {weekday}"

